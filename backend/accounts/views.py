from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.choices import AuditAction
from core.utils import write_audit_log

from .models import User
from .permissions import IsBarangaySecretary
from .serializers import (
    ChangePasswordSerializer,
    CreateResidentAccountSerializer,
    CustomTokenObtainPairSerializer,
    UserAdminSerializer,
    UserProfileSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                write_audit_log(
                    user=user,
                    action=AuditAction.LOGIN,
                    table_affected='users',
                    record_id=user.user_id,
                    request=request,
                )
            except User.DoesNotExist:
                pass
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user,
            action=AuditAction.UPDATE,
            table_affected='users',
            record_id=instance.user_id,
            request=self.request,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        write_audit_log(
            user=request.user,
            action=AuditAction.UPDATE,
            table_affected='users',
            record_id=request.user.user_id,
            request=request,
        )
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    Full account management for the Barangay Secretary: create, list,
    retrieve, update, archive, and restore any user account.
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsBarangaySecretary]

    def perform_create(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user,
            action=AuditAction.CREATE,
            table_affected='users',
            record_id=instance.user_id,
            request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user,
            action=AuditAction.UPDATE,
            table_affected='users',
            record_id=instance.user_id,
            request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Hard delete is disabled — accounts are archived instead, so audit
        history and FK-protected records (households encoded, centers
        managed, etc.) are never orphaned.
        """
        return Response(
            {'detail': 'Accounts cannot be deleted. Use the archive action instead.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        user = self.get_object()
        user.status = 'Archived'
        user.is_active = False
        user.save()
        write_audit_log(
            user=request.user,
            action=AuditAction.ARCHIVE,
            table_affected='users',
            record_id=user.user_id,
            request=request,
        )
        return Response(UserAdminSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        user = self.get_object()
        user.status = 'Active'
        user.is_active = True
        user.save()
        write_audit_log(
            user=request.user,
            action=AuditAction.RESTORE,
            table_affected='users',
            record_id=user.user_id,
            request=request,
        )
        return Response(UserAdminSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='create-resident')
    def create_resident(self, request):
        """
        The only way a Resident account can be created — no public signup
        flow exists. Links the new account to a specific household in the
        same transaction, so it's never possible to end up with an orphaned
        Resident account with no household.
        """
        serializer = CreateResidentAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        write_audit_log(
            user=request.user,
            action=AuditAction.CREATE,
            table_affected='users',
            record_id=user.user_id,
            request=request,
        )
        return Response(UserAdminSerializer(user).data, status=status.HTTP_201_CREATED)