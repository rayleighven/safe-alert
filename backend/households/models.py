import uuid
from django.conf import settings
from django.db import models

from core.choices import Priority, HouseMaterial, RoofMaterial, Sex
from core.models import Barangay, TimeStampedModel, ArchivableModel


class Household(TimeStampedModel, ArchivableModel):
    household_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='households')
    household_number = models.CharField(max_length=20, unique=True)
    head_of_family = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    purok = models.CharField(max_length=50)
    total_members = models.IntegerField()
    # evacuation_priority / priority_score are written by the CART algorithm (Phase 3),
    # so both are nullable until a household has been assessed.
    evacuation_priority = models.CharField(max_length=10, choices=Priority.choices, blank=True, null=True)
    priority_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    encoded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='households_encoded',
    )
    resident_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resident_household',
        help_text='The Resident account linked to this household. Created by the Barangay '
                   'Secretary via the "create Resident account" action — there is no public '
                   'signup flow, so this is only ever set through that controlled path.',
    )

    class Meta:
        db_table = 'households'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(evacuation_priority__in=Priority.values) | models.Q(evacuation_priority__isnull=True),
                name='households_evacuation_priority_valid',
            ),
            models.CheckConstraint(condition=models.Q(total_members__gte=0), name='households_total_members_non_negative'),
        ]

    def __str__(self):
        return f"{self.household_number} - {self.head_of_family}"


class HouseholdMember(TimeStampedModel, ArchivableModel):
    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10, choices=Sex.choices)
    relationship = models.CharField(max_length=50)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    is_senior_citizen = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)
    is_pregnant = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)

    class Meta:
        db_table = 'household_members'
        constraints = [
            models.CheckConstraint(condition=models.Q(sex__in=Sex.values), name='household_members_sex_valid'),
            models.CheckConstraint(condition=models.Q(age__gte=0), name='household_members_age_non_negative'),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.household.household_number})"


class VulnerabilityIndicator(models.Model):
    """
    Primary inputs to the CART Decision Tree Algorithm (Phase 3), which
    computes Household.evacuation_priority and Household.priority_score.

    hazard_zone and the has_* fields are no longer client-set (see
    serializers.VulnerabilityIndicatorSerializer read_only_fields) — they are
    derived automatically in save() below, but remain real stored columns
    because cart_classifier._vectorize() reads them directly as part of the
    trained model's fixed feature schema.
    """
    HAZARD_TYPE_FIELDS = ['flood_prone', 'storm_surge_prone', 'landslide_prone', 'coastal_zone']

    indicator_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='vulnerability_indicators')
    has_senior_citizen = models.BooleanField(default=False)
    has_pwd = models.BooleanField(default=False)
    has_pregnant_member = models.BooleanField(default=False)
    has_child = models.BooleanField(default=False)
    house_material = models.CharField(max_length=20, choices=HouseMaterial.choices)
    roof_material = models.CharField(max_length=20, choices=RoofMaterial.choices)
    hazard_zone = models.CharField(max_length=10, choices=Priority.choices)
    flood_prone = models.BooleanField(default=False)
    storm_surge_prone = models.BooleanField(default=False)
    landslide_prone = models.BooleanField(default=False)
    coastal_zone = models.BooleanField(default=False)
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='vulnerability_assessments',
        help_text='The BHW who performed this assessment.',
    )
    assessed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'vulnerability_indicators'
        constraints = [
            models.CheckConstraint(condition=models.Q(house_material__in=HouseMaterial.values), name='vuln_house_material_valid'),
            models.CheckConstraint(condition=models.Q(roof_material__in=RoofMaterial.values), name='vuln_roof_material_valid'),
            models.CheckConstraint(condition=models.Q(hazard_zone__in=Priority.values), name='vuln_hazard_zone_valid'),
        ]

    def _derive_hazard_zone(self):
        """
        hazard_zone feeds cart_classifier.HAZARD_ZONE_SCORES as its own
        feature slot (independent of the flood/storm_surge/landslide/coastal
        booleans, which occupy separate slots) — so it still has to be a
        Low/Medium/High value. Derived from how many of the 4 hazard-type
        checkboxes are selected, using the same 0.3/0.6 ratio thresholds
        cart_classifier._label_from_score already uses for the bootstrap
        training labels: 0-1 selected -> Low, 2 -> Medium, 3-4 -> High.
        """
        selected = sum(1 for field in self.HAZARD_TYPE_FIELDS if getattr(self, field))
        ratio = selected / len(self.HAZARD_TYPE_FIELDS)
        if ratio >= 0.6:
            return Priority.HIGH
        if ratio >= 0.3:
            return Priority.MEDIUM
        return Priority.LOW

    def _derive_member_flags(self):
        members = HouseholdMember.objects.filter(household_id=self.household_id, is_archived=False)
        return {
            'has_senior_citizen': members.filter(is_senior_citizen=True).exists(),
            'has_pwd': members.filter(is_pwd=True).exists(),
            'has_pregnant_member': members.filter(is_pregnant=True).exists(),
            'has_child': members.filter(is_child=True).exists(),
        }

    def save(self, *args, **kwargs):
        self.hazard_zone = self._derive_hazard_zone()
        if self.household_id:
            for field, value in self._derive_member_flags().items():
                setattr(self, field, value)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vulnerability - {self.household.household_number}"
