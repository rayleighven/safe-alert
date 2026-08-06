import uuid
from django.db import models

from core.choices import StaffRole, DisasterType, DisasterStatus


class TimeStampedModel(models.Model):
    """Abstract base providing created_at / updated_at."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ArchivableModel(models.Model):
    """Abstract base providing soft-delete fields."""
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Barangay(models.Model):
    barangay_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'barangay'
        verbose_name_plural = 'Barangays'

    def __str__(self):
        return f"{self.name}, {self.municipality}"


class EmergencyContact(TimeStampedModel, ArchivableModel):
    contact_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=50, choices=StaffRole.choices)
    contact_number = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'emergency_contacts'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=StaffRole.values),
                name='emergency_contacts_role_valid',
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.role})"


class Disaster(models.Model):
    disaster_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=DisasterType.choices)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=DisasterStatus.choices, default=DisasterStatus.ONGOING)
    declared_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'disasters'
        constraints = [
            models.CheckConstraint(condition=models.Q(type__in=DisasterType.values), name='disasters_type_valid'),
            models.CheckConstraint(condition=models.Q(status__in=DisasterStatus.values), name='disasters_status_valid'),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"