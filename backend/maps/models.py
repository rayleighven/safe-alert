import uuid
from django.conf import settings
from django.db import models

from core.choices import HazardType
from core.models import Barangay


class HazardMap(models.Model):
    map_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='hazard_maps')
    map_title = models.CharField(max_length=255)
    hazard_type = models.CharField(max_length=20, choices=HazardType.choices)
    source = models.CharField(max_length=100)  # e.g. "Project NOAH", "PHIVOLCS"
    map_url = models.TextField()
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='hazard_maps_uploaded',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'hazard_maps'
        constraints = [
            models.CheckConstraint(condition=models.Q(hazard_type__in=HazardType.values), name='hazard_maps_type_valid'),
        ]

    def __str__(self):
        return self.map_title