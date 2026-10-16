from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.choices import AuditAction, UserRole
from core.utils import write_audit_log
from accounts.permissions import IsBarangaySecretary

from .models import HazardMap
from .permissions import HazardMapPermission
from .serializers import HazardMapSerializer


class HazardMapViewSet(viewsets.ModelViewSet):
    serializer_class = HazardMapSerializer
    permission_classes = [HazardMapPermission]

    def get_permissions(self):
        if self.action in ['archived', 'restore']:
            return [IsBarangaySecretary()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def archived(self, request):
        maps = HazardMap.objects.filter(is_archived=True, barangay=request.user.barangay).order_by('hazard_type', 'map_title')
        return Response(self.get_serializer(maps, many=True).data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        hazard_map = get_object_or_404(HazardMap, pk=pk, barangay=request.user.barangay, is_archived=True)
        hazard_map.is_archived = False
        hazard_map.archived_at = None
        hazard_map.save()
        write_audit_log(user=request.user, action=AuditAction.RESTORE, table_affected='hazard_maps', record_id=hazard_map.map_id, request=request)
        return Response(self.get_serializer(hazard_map).data, status=status.HTTP_200_OK)

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
