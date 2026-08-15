from rest_framework import serializers

from .models import Household, HouseholdMember, VulnerabilityIndicator


class HouseholdMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdMember
        fields = [
            'member_id', 'full_name', 'birth_date', 'age', 'sex', 'relationship', 'occupation',
            'is_senior_citizen', 'is_pwd', 'is_pregnant', 'is_child',
            'created_at', 'is_archived', 'archived_at',
        ]
        read_only_fields = ['member_id', 'created_at', 'is_archived', 'archived_at']


class VulnerabilityIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VulnerabilityIndicator
        fields = [
            'indicator_id',
            'has_senior_citizen', 'has_pwd', 'has_pregnant_member', 'has_child',
            'house_material', 'roof_material', 'hazard_zone',
            'flood_prone', 'storm_surge_prone', 'landslide_prone', 'coastal_zone',
            'assessed_by', 'assessed_at', 'updated_at', 'is_archived', 'archived_at',
        ]
        read_only_fields = ['indicator_id', 'assessed_by', 'assessed_at', 'updated_at', 'is_archived', 'archived_at']


class HouseholdListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — no nested members/indicators."""

    class Meta:
        model = Household
        fields = [
            'household_id', 'household_number', 'head_of_family', 'purok',
            'total_members', 'evacuation_priority', 'priority_score', 'barangay',
        ]


class HouseholdDetailSerializer(serializers.ModelSerializer):
    members = HouseholdMemberSerializer(many=True, required=False)
    vulnerability_indicators = VulnerabilityIndicatorSerializer(many=True, read_only=True)
    resident_account = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = [
            'household_id', 'barangay', 'household_number', 'head_of_family',
            'contact_number', 'address', 'purok', 'total_members',
            'evacuation_priority', 'priority_score', 'encoded_by',
            'created_at', 'updated_at', 'is_archived', 'archived_at',
            'members', 'vulnerability_indicators', 'resident_account',
        ]
        # barangay and encoded_by are set server-side (from the requesting
        # user) in the view, not accepted from the client — prevents a
        # Secretary from encoding a household into another barangay.
        # evacuation_priority/priority_score are CART outputs, never client-set.
        # resident_account is derived (read-only) — linking happens through
        # the dedicated create-resident-account endpoint, not through this serializer.
        read_only_fields = [
            'household_id', 'barangay', 'evacuation_priority', 'priority_score', 'encoded_by',
            'created_at', 'updated_at', 'is_archived', 'archived_at',
        ]

    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        if not members_data:
            raise serializers.ValidationError({'members': 'Add at least the head of the family.'})
        validated_data['total_members'] = len(members_data)
        household = Household.objects.create(**validated_data)
        HouseholdMember.objects.bulk_create([
            HouseholdMember(household=household, **member_data)
            for member_data in members_data
        ])
        return household

    def update(self, instance, validated_data):
        # Member changes use the dedicated nested member endpoints. This keeps
        # updates to existing household records explicit and auditable.
        validated_data.pop('members', None)
        return super().update(instance, validated_data)

    def get_resident_account(self, obj):
        if obj.resident_user_id:
            return {
                'user_id': str(obj.resident_user.user_id),
                'username': obj.resident_user.username,
                'status': obj.resident_user.status,
            }
        return None
