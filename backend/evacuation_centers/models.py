import uuid
from django.conf import settings
from django.db import models

from core.choices import CenterStatus, EntryStatus
from core.models import Barangay, Disaster
from households.models import Household


class EvacuationCenter(models.Model):
    center_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='evacuation_centers')
    name = models.CharField(max_length=100)
    address = models.TextField()
    capacity = models.IntegerField()
    current_occupancy = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=CenterStatus.choices, default=CenterStatus.ACTIVE)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='evacuation_centers_managed',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'evacuation_centers'
        constraints = [
            models.CheckConstraint(condition=models.Q(status__in=CenterStatus.values), name='centers_status_valid'),
            models.CheckConstraint(condition=models.Q(capacity__gte=0), name='centers_capacity_non_negative'),
            models.CheckConstraint(condition=models.Q(current_occupancy__gte=0), name='centers_occupancy_non_negative'),
        ]

    def __str__(self):
        return self.name


class EvacuationRecord(models.Model):
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disaster = models.ForeignKey(Disaster, on_delete=models.PROTECT, related_name='evacuation_records')
    center = models.ForeignKey(EvacuationCenter, on_delete=models.PROTECT, related_name='evacuation_records')
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='evacuation_records')
    entry_status = models.CharField(max_length=20, choices=EntryStatus.choices, default=EntryStatus.CHECKED_IN)
    entered_at = models.DateTimeField()
    has_water = models.BooleanField(default=False)
    has_electricity = models.BooleanField(default=False)
    has_medical = models.BooleanField(default=False)
    has_food = models.BooleanField(default=False)
    discharged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'evacuation_records'
        constraints = [
            models.CheckConstraint(condition=models.Q(entry_status__in=EntryStatus.values), name='evac_records_entry_status_valid'),
        ]

    def __str__(self):
        return f"{self.household.household_number} @ {self.center.name}"