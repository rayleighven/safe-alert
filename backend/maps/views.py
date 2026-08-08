from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response

from core.choices import AuditAction, UserRole
from core.utils import write_audit_log

from .models import HazardMap
from .permissions import HazardMapPermission
from .serializers import HazardMapSerializer


class HazardMapViewSet(viewsets.ModelViewSet):
    serializer_class = HazardMapSerializer
    permission_classes = [HazardMapPermission]

    def get_queryset(self):
        user = self.request.user
        qs = HazardMap.objects.filter(is_archived=False).order_by('hazard_type', 'map_title')
        if user.role == UserRole.MDRRMO_OFFICER:
            return qs  # sees both barangays
        return qs.filter(barangay=user.barangay)

    def perform_create(self, serializer):
        instance = serializer.save(barangay=self.request.user.barangay, uploaded_by=self.request.user)
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='hazard_maps', record_id=instance.map_id, request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='hazard_maps', record_id=instance.map_id, request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete — archive instead, consistent with every other module."""
        hazard_map = self.get_object()
        hazard_map.is_archived = True
        hazard_map.archived_at = timezone.now()
        hazard_map.save()
        write_audit_log(
            user=request.user, action=AuditAction.ARCHIVE,
            table_affected='hazard_maps', record_id=hazard_map.map_id, request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)