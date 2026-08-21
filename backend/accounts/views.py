from datetime import timedelta

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from axes.models import AccessAttempt
from core.choices import AuditAction
from core.utils import get_client_ip, write_audit_log

from .models import User
from .permissions import IsBarangaySecretary
from .serializers import (
    ChangePasswordSerializer,
    CreateResidentAccountSerializer,
    CustomTokenObtainPairSerializer,
    UserAdminSerializer,
    UserProfileSerializer,
)


def _is_locked_out(username, ip_address):
    """
    Checks axes' own AccessAttempt table directly instead of going through
    AxesProxyHandler/AxesBackend, whose exact API has shifted across axes
    versions. Reading the table's own fields (username, ip_address,
    failures_since_start, attempt_time) is stable regardless of version,
    and lets LoginView return a clear 403 + message instead of relying on
    axes' default silent fallthrough, which produces an identical generic
    401 for both "wrong password" and "locked out" and can't be
    distinguished by the frontend.
    """
    if not username:
        return False

    # Keep this explicit response in sync with django-axes. AXES_COOLOFF_TIME
    # is the setting django-axes 8.x actually reads.
    cooldown = getattr(settings, 'AXES_COOLOFF_TIME', timedelta(hours=1))
    if not isinstance(cooldown, timedelta):
        # AXES_COOLOFF_TIME can be configured as hours (int/float) in some
        # setups — normalize to a timedelta either way so this check works
        # regardless of how it's expressed in settings.
        cooldown = timedelta(hours=cooldown)

    failure_limit = getattr(settings, 'AXES_FAILURE_LIMIT', 3)
    cutoff = timezone.now() - cooldown

    failures = (
        AccessAttempt.objects.filter(
            username=username,
            ip_address=ip_address,
            attempt_time__gte=cutoff,
        ).aggregate(total=Sum('failures_since_start'))['total']
        or 0
    )
    return failures >= failure_limit


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        ip_address = get_client_ip(request)

        if _is_locked_out(username, ip_address):
            return Response(
                {'detail': 'Maximum attempts tried. Try again in 1 minute.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
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
        # A password change must end every existing refresh-token session,
        # including sessions on other devices. Existing access tokens are
        # short-lived (15 minutes) and cannot be revoked statelessly.
        for token in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=token)
        write_audit_log(
            user=request.user,
            action=AuditAction.UPDATE,
            table_affected='users',
            record_id=request.user.user_id,
            request=request,
        )
        return Response(
            {
                'detail': 'Password changed successfully. Please sign in again.',
                'reauthentication_required': True,
            },
            status=status.HTTP_200_OK,
        )


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    Full account management for the Barangay Secretary: create, list,
    retrieve, update, archive, and restore any user account.
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsBarangaySecretary]

    def get_queryset(self):
        """Never expose accounts outside the requesting secretary's barangay."""
        if not self.request.user.barangay_id:
            return User.objects.none()
        return User.objects.filter(barangay_id=self.request.user.barangay_id).order_by('username')

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
        serializer = CreateResidentAccountSerializer(data=request.data, context={'request': request})
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
