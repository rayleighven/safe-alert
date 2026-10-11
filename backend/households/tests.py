from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from core.choices import UserRole, UserStatus
from core.models import Barangay

from .models import Household


class BDRRMCChairpersonHouseholdAccessTests(TestCase):
    """
    Regression coverage for the fix allowing BDRRMC Chairperson read-only
    access to Households (previously missing from HouseholdPermission's
    SAFE_METHODS allow-list, causing a 403 on all household reads).
    """

    def setUp(self):
        self.barangay = Barangay.objects.create(
            name='Poblacion',
            municipality='Baclayon',
            province='Bohol',
            contact_number='09171234567',
        )
        self.secretary = User.objects.create_user(
            username='chairperson_test_secretary',
            password='Correct-Horse-Battery-Staple-123!',
            role=UserRole.BARANGAY_SECRETARY,
            barangay=self.barangay,
            status=UserStatus.ACTIVE,
        )
        self.chairperson = User.objects.create_user(
            username='chairperson_test_user',
            password='Correct-Horse-Battery-Staple-123!',
            role=UserRole.BDRRMC_CHAIRPERSON,
            barangay=self.barangay,
            status=UserStatus.ACTIVE,
        )
        self.household = Household.objects.create(
            barangay=self.barangay,
            household_number='HH-CHAIR-001',
            head_of_family='Juan Dela Cruz',
            contact_number='09170000000',
            address='123 Test St.',
            purok='Purok 1',
            total_members=4,
            encoded_by=self.secretary,
        )
        self.client = APIClient()

    def test_chairperson_can_list_households(self):
        self.client.force_authenticate(self.chairperson)
        response = self.client.get(reverse('household-list'))
        self.assertEqual(response.status_code, 200)
        household_numbers = {item['household_number'] for item in response.json()}
        self.assertIn('HH-CHAIR-001', household_numbers)

    def test_chairperson_can_view_household_detail(self):
        self.client.force_authenticate(self.chairperson)
        response = self.client.get(reverse('household-detail', args=[self.household.household_id]))
        self.assertEqual(response.status_code, 200)

    def test_chairperson_cannot_create_household(self):
        self.client.force_authenticate(self.chairperson)
        response = self.client.post(reverse('household-list'), {
            'household_number': 'HH-CHAIR-002',
            'head_of_family': 'Maria Santos',
            'contact_number': '09171111111',
            'address': '456 Test St.',
            'purok': 'Purok 2',
            'total_members': 2,
        })
        self.assertEqual(response.status_code, 403)

    def test_chairperson_cannot_update_household(self):
        self.client.force_authenticate(self.chairperson)
        response = self.client.patch(
            reverse('household-detail', args=[self.household.household_id]),
            {'head_of_family': 'Changed Name'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)
