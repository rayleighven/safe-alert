from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.choices import AuditAction, UserRole
from core.models import Disaster
from core.utils import write_audit_log

from .models import EvacuationCenter, EvacuationRecord
from .permissions import (
    CENTER_KAGAWAD_ALLOWED_FIELDS,
    DisasterPermission,
    EvacuationCenterPermission,
    EvacuationRecordPermission,
)
from .serializers import DisasterSerializer, EvacuationCenterSerializer, EvacuationRecordSerializer


class EvacuationCenterViewSet(viewsets.ModelViewSet):
    serializer_class = EvacuationCenterSerializer
    permission_classes = [EvacuationCenterPermission]

    def get_queryset(self):
        user = self.request.user
        qs = EvacuationCenter.objects.filter(is_archived=False).order_by('name')
        if user.role == UserRole.MDRRMO_OFFICER:
            return qs  # sees both barangays
        # Everyone else — including Resident, per the standing barangay-scoping
        # rule — sees only their own account's barangay, no picker involved.
        return qs.filter(barangay=user.barangay)

    def _enforce_kagawad_field_restriction(self, request):
        if request.user.role == UserRole.BARANGAY_KAGAWAD_TANOD:
            submitted_fields = set(request.data.keys())
            disallowed = submitted_fields - CENTER_KAGAWAD_ALLOWED_FIELDS
            if disallowed:
                raise ValidationError({
                    field: 'Barangay Kagawad/Tanod may only update capacity, current_occupancy, and status.'
                    for field in disallowed
                })

    def perform_create(self, serializer):
        extra = {'barangay': self.request.user.barangay}
        if 'managed_by' not in serializer.validated_data:
            extra['managed_by'] = self.request.user
        instance = serializer.save(**extra)
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='evacuation_centers', record_id=instance.center_id, request=self.request,
        )

    def perform_update(self, serializer):
        self._enforce_kagawad_field_restriction(self.request)
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='evacuation_centers', record_id=instance.center_id, request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete — archive instead, consistent with every other module."""
        center = self.get_object()
        center.is_archived = True
        center.archived_at = timezone.now()
        center.save()
        write_audit_log(
            user=request.user, action=AuditAction.ARCHIVE,
            table_affected='evacuation_centers', record_id=center.center_id, request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DisasterViewSet(viewsets.ModelViewSet):
    """
    Not part of the original phase list by name, but EvacuationRecord is
    meaningless without it, and the model already exists from Phase 1 —
    included here as a minimal supporting module. Flagged for Dawn's review.
    """
    serializer_class = DisasterSerializer
    permission_classes = [DisasterPermission]
    queryset = Disaster.objects.all().order_by('-declared_at')

    def perform_create(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='disasters', record_id=instance.disaster_id, request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='disasters', record_id=instance.disaster_id, request=self.request,
        )


class EvacuationRecordViewSet(viewsets.ModelViewSet):
    """Households checking in/out of a center during an active disaster."""
    serializer_class = EvacuationRecordSerializer
    permission_classes = [EvacuationRecordPermission]

    def get_queryset(self):
        user = self.request.user
        qs = EvacuationRecord.objects.all().order_by('-entered_at')
        if user.role == UserRole.MDRRMO_OFFICER:
            return qs
        return qs.filter(center__barangay=user.barangay)

    def perform_create(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='evacuation_records', record_id=instance.record_id, request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='evacuation_records', record_id=instance.record_id, request=self.request,
        )