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
    """
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

    def __str__(self):
        return f"Vulnerability - {self.household.household_number}"
