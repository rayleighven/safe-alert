from datetime import timedelta

from axes.models import AccessAttempt
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from core.choices import UserRole, UserStatus
from core.models import Barangay

from .models import User
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

    def test_login_rejects_a_barangay_that_does_not_match_the_account(self):
        response = self.client.post(self.login_url, {
            'username': self.user.username,
            'password': 'Correct-Horse-Battery-Staple-123!',
            'access_area': 'Cambanac',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('access_area', response.json())


class BarangayAccountScopeTests(TestCase):
    def setUp(self):
        self.cambanac = Barangay.objects.create(name='Cambanac', municipality='Baclayon', province='Bohol', contact_number='09171234567')
        self.poblacion = Barangay.objects.create(name='Poblacion', municipality='Baclayon', province='Bohol', contact_number='09171234568')
        self.secretary = self.create_user('cambanac_secretary', UserRole.BARANGAY_SECRETARY, self.cambanac)
        self.local_user = self.create_user('cambanac_bhw', UserRole.BARANGAY_HEALTHWORKER, self.cambanac)
        self.remote_user = self.create_user('poblacion_bhw', UserRole.BARANGAY_HEALTHWORKER, self.poblacion)
        self.client = APIClient()
        self.client.force_authenticate(self.secretary)

    @staticmethod
    def create_user(username, role, barangay):
        return User.objects.create_user(
            username=username,
            password='Correct-Horse-Battery-Staple-123!',
            role=role,
            barangay=barangay,
            status=UserStatus.ACTIVE,
        )

    def test_secretary_only_receives_accounts_from_own_barangay(self):
        response = self.client.get(reverse('user-admin-list'))
        self.assertEqual(response.status_code, 200)
        usernames = {account['username'] for account in response.json()}
        self.assertEqual(usernames, {'cambanac_secretary', 'cambanac_bhw'})

    def test_secretary_cannot_retrieve_another_barangays_account(self):
        response = self.client.get(reverse('user-admin-detail', args=[self.remote_user.user_id]))
        self.assertEqual(response.status_code, 404)

    def test_secretary_cannot_create_an_account_for_another_barangay(self):
        response = self.client.post(reverse('user-admin-list'), {
            'username': 'not_allowed',
            'password': 'Correct-Horse-Battery-Staple-123!',
            'role': UserRole.BARANGAY_HEALTHWORKER,
            'barangay': self.poblacion.name,
            'status': UserStatus.ACTIVE,
        })
        self.assertEqual(response.status_code, 400)

    def test_secretary_can_create_an_account_in_own_barangay(self):
        response = self.client.post(reverse('user-admin-list'), {
            'username': 'new_cambanac_tanod',
            'password': 'Correct-Horse-Battery-Staple-123!',
            'role': UserRole.BARANGAY_KAGAWAD_TANOD,
            'status': UserStatus.ACTIVE,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['barangay'], self.cambanac.name)

    def test_secretary_can_change_a_local_accounts_status(self):
        response = self.client.patch(
            reverse('user-admin-detail', args=[self.local_user.user_id]),
            {'status': UserStatus.INACTIVE},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.local_user.refresh_from_db()
        self.assertEqual(self.local_user.status, UserStatus.INACTIVE)


class PasswordChangeSecurityTests(TestCase):
    def setUp(self):
        barangay = Barangay.objects.create(
            name='Password Test Barangay',
            municipality='Baclayon',
            province='Bohol',
            contact_number='09171234569',
        )
        self.user = User.objects.create_user(
            username='password_security_test',
            password='Correct-Horse-Battery-Staple-123!',
            role=UserRole.BARANGAY_HEALTHWORKER,
            barangay=barangay,
            status=UserStatus.ACTIVE,
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_password_change_revokes_all_outstanding_refresh_tokens(self):
        response = self.client.post(
            reverse('change-password'),
            {
                'current_password': 'Correct-Horse-Battery-Staple-123!',
                'new_password': 'New-Correct-Horse-Battery-Staple-456!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['reauthentication_required'])
        self.assertTrue(
            BlacklistedToken.objects.filter(token__jti=self.refresh_token['jti']).exists()
        )
