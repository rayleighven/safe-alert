from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.choices import UserRole, UserStatus

from .models import User, UserAddress


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT login serializer to:
    - reject login for users whose status is not Active
    - embed role, status, barangay_id, and user_id as extra claims in the token
    - return a compact user object alongside the tokens for the frontend to store
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.user_id)
        token['username'] = user.username
        token['role'] = user.role
        token['status'] = user.status
        token['barangay_id'] = str(user.barangay_id) if user.barangay_id else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.status != UserStatus.ACTIVE:
            raise serializers.ValidationError(
                'This account is not active. Contact your Barangay Secretary for assistance.'
            )

        data['user'] = {
            'user_id': str(self.user.user_id),
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'status': self.user.status,
            'barangay_id': str(self.user.barangay_id) if self.user.barangay_id else None,
        }
        return data


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            'address_id', 'street', 'sitio', 'barangay',
            'municipality', 'province', 'address_type',
        ]
        read_only_fields = ['address_id']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Self-service profile serializer. Role, status, and barangay are
    read-only here — only a Barangay Secretary (via UserAdminSerializer)
    can change those.
    """
    addresses = UserAddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'role', 'status', 'barangay', 'addresses',
        ]
        read_only_fields = ['user_id', 'username', 'role', 'status', 'barangay']


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Full account management serializer for the Barangay Secretary:
    create/edit any user's role, barangay assignment, and status.
    """
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'role', 'barangay', 'status', 'assigned_purok', 'password',
        ]
        read_only_fields = ['user_id']

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value

    def validate(self, attrs):
        role = attrs.get('role', getattr(self.instance, 'role', None))
        if 'barangay' in attrs:
            barangay = attrs['barangay']
        elif self.instance:
            barangay = self.instance.barangay
        else:
            barangay = None

        if role == UserRole.MDRRMO_OFFICER:
            if barangay:
                raise serializers.ValidationError({
                    'barangay': 'MDRRMO Officer accounts are municipal-level and must not be tied to a specific barangay.'
                })
        else:
            if not barangay:
                raise serializers.ValidationError({
                    'barangay': 'This role must be tied to a specific barangay — every account except MDRRMO Officer requires one.'
                })
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Password is required when creating a new account.'})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CreateResidentAccountSerializer(serializers.Serializer):
    """
    Residents are never self-registered — the Barangay Secretary creates
    this account explicitly, tied to a specific household, when (or shortly
    after) encoding that household. This is the only way a Resident account
    can come into existence.
    """
    household_id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_household_id(self, value):
        # Imported here (not at module level) to avoid accounts/households
        # ever forming a circular import — same pattern as core/utils.py.
        from households.models import Household

        try:
            household = Household.objects.get(pk=value, is_archived=False)
        except Household.DoesNotExist:
            raise serializers.ValidationError('Household not found.')
        if household.resident_user_id:
            raise serializers.ValidationError('This household already has a linked Resident account.')
        self._household = household
        return value

    def create(self, validated_data):
        household = self._household
        password = validated_data.pop('password')
        validated_data.pop('household_id')

        user = User(
            role=UserRole.RESIDENT,
            barangay=household.barangay,
            status=UserStatus.ACTIVE,
            **validated_data,
        )
        user.set_password(password)
        user.save()

        household.resident_user = user
        household.save(update_fields=['resident_user'])

        return user