from datetime import timedelta

from axes.models import AccessAttempt
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.choices import UserRole, UserStatus
from core.models import Barangay

from .serializers import UserAdminSerializer


@override_settings(
    AXES_ENABLED=True,
    AXES_FAILURE_LIMIT=3,
    AXES_COOLOFF_TIME=timedelta(minutes=1),
    AXES_LOCKOUT_PARAMETERS=[['username', 'ip_address']],
    AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT=False,
)
class LoginLockoutTests(TestCase):
    """Regression coverage for accounts created through UserAdminSerializer."""

    def setUp(self):
        self.barangay = Barangay.objects.create(
            name='Poblacion',
            municipality='Test Municipality',
            province='Test Province',
            contact_number='09171234567',
        )
        serializer = UserAdminSerializer(data={
            'username': 'bhw_lockout_test',
            'password': 'Correct-Horse-Battery-Staple-123!',
            'role': UserRole.BARANGAY_HEALTHWORKER,
            'barangay': self.barangay.name,
            'status': UserStatus.ACTIVE,
        })
        serializer.is_valid(raise_exception=True)
        self.user = serializer.save()
        self.login_url = reverse('login')
        self.client_ip = '198.51.100.10'

    def login(self, username, password):
        return self.client.post(
            self.login_url,
            {'username': username, 'password': password},
            REMOTE_ADDR=self.client_ip,
        )

    def assert_lockout_and_recovery(self, user, password):
        for _ in range(3):
            self.login(user.username, 'not-the-password')

        attempt = AccessAttempt.objects.get(
            username=user.username,
            ip_address=self.client_ip,
        )
        self.assertEqual(attempt.failures_since_start, 3)

        locked_response = self.login(user.username, 'not-the-password')
        self.assertEqual(locked_response.status_code, 403)
        self.assertEqual(
            locked_response.json(),
            {'detail': 'Maximum attempts tried. Try again in 1 minute.'},
        )

        attempt.attempt_time = timezone.now() - timedelta(seconds=61)
        attempt.save(update_fields=['attempt_time'])

        recovered_response = self.login(user.username, password)
        self.assertEqual(recovered_response.status_code, 200)

    def test_created_user_is_locked_after_three_failures_and_recovers_after_cooloff(self):
        self.assert_lockout_and_recovery(
            self.user,
            'Correct-Horse-Battery-Staple-123!',
        )

    def test_superuser_has_the_same_lockout_and_recovery_behavior(self):
        superuser = self.user.__class__.objects.create_superuser(
            username='admin_lockout_test',
            password='Correct-Horse-Battery-Staple-456!',
        )
        self.assert_lockout_and_recovery(
            superuser,
            'Correct-Horse-Battery-Staple-456!',
        )
