from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from core.choices import UserRole, UserStatus
from core.models import Barangay

from .serializers import EvacuationCenterSerializer


class EvacuationCenterCapacityValidationTests(TestCase):
    """
    Regression coverage for rejecting capacity <= 0 with a clean 400
    validation error, instead of allowing 0 through and crashing with an
    unhandled IntegrityError on negative values.
    """

    def setUp(self):
        self.barangay = Barangay.objects.create(
            name='Poblacion',
            municipality='Baclayon',
            province='Bohol',
            contact_number='09171234567',
        )
        self.secretary = User.objects.create_user(
            username='capacity_test_secretary',
            password='Correct-Horse-Battery-Staple-123!',
            role=UserRole.BARANGAY_SECRETARY,
            barangay=self.barangay,
            status=UserStatus.ACTIVE,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.secretary)

    def _payload(self, capacity):
        return {
            'name': 'Test Center',
            'address': '123 Test St.',
            'capacity': capacity,
            'current_occupancy': 0,
        }

    def test_serializer_rejects_zero_capacity(self):
        serializer = EvacuationCenterSerializer(data=self._payload(0))
        self.assertFalse(serializer.is_valid())
        self.assertIn('capacity', serializer.errors)

    def test_serializer_rejects_negative_capacity(self):
        serializer = EvacuationCenterSerializer(data=self._payload(-5))
        self.assertFalse(serializer.is_valid())
        self.assertIn('capacity', serializer.errors)

    def test_serializer_accepts_positive_capacity(self):
        serializer = EvacuationCenterSerializer(data=self._payload(10))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_api_rejects_zero_capacity_with_clean_400(self):
        response = self.client.post(reverse('evacuation-center-list'), self._payload(0))
        self.assertEqual(response.status_code, 400)
        self.assertIn('capacity', response.json())

    def test_api_rejects_negative_capacity_with_clean_400(self):
        response = self.client.post(reverse('evacuation-center-list'), self._payload(-1))
        self.assertEqual(response.status_code, 400)
        self.assertIn('capacity', response.json())

    def test_api_accepts_positive_capacity(self):
        response = self.client.post(reverse('evacuation-center-list'), self._payload(50))
        self.assertEqual(response.status_code, 201)
