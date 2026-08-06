# backend/households/views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.choices import AuditAction, UserRole
from core.utils import write_audit_log

from .models import Household, HouseholdMember, VulnerabilityIndicator
from .permissions import HouseholdPermission, VulnerabilityIndicatorPermission
from .serializers import (
    HouseholdDetailSerializer,
    HouseholdListSerializer,
    HouseholdMemberSerializer,
    VulnerabilityIndicatorSerializer,
)

BHW_ALLOWED_FIELDS = {'has_senior_citizen', 'has_pwd', 'has_pregnant_member', 'has_child'}


def _verify_resident_household_access(request, household_pk):
    """
    Nested list endpoints (members/, vulnerability/) filter by household_pk
    from the URL directly — DRF never calls has_object_permission() for list
    actions, so without this check a Resident could read another household's
    data just by changing the UUID in the URL. Explicit check closes that gap.
    """
    if request.user.role == UserRole.RESIDENT:
        household = get_object_or_404(Household, pk=household_pk)
        if household.resident_user_id != request.user.pk:
            raise PermissionDenied('You do not have access to this household.')


class HouseholdViewSet(viewsets.ModelViewSet):
    permission_classes = [HouseholdPermission]

    def get_serializer_class(self):
        if self.action == 'list':
            return HouseholdListSerializer
        return HouseholdDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Household.objects.filter(is_archived=False).order_by('household_number')
        if user.role == UserRole.MDRRMO_OFFICER:
            return qs  # sees both barangays
        if user.role == UserRole.RESIDENT:
            return qs.filter(resident_user=user)
        return qs.filter(barangay=user.barangay)

    def perform_create(self, serializer):
        instance = serializer.save(encoded_by=self.request.user, barangay=self.request.user.barangay)
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='households', record_id=instance.household_id, request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='households', record_id=instance.household_id, request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete — archive instead of hard delete, per the schema's is_archived pattern."""
        household = self.get_object()
        household.is_archived = True
        household.archived_at = timezone.now()
        household.save()
        write_audit_log(
            user=request.user, action=AuditAction.ARCHIVE,
            table_affected='households', record_id=household.household_id, request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class HouseholdMemberViewSet(viewsets.ModelViewSet):
    """Nested under a household: /api/households/{household_pk}/members/"""
    serializer_class = HouseholdMemberSerializer
    permission_classes = [HouseholdPermission]

    def get_queryset(self):
        _verify_resident_household_access(self.request, self.kwargs['household_pk'])
        return HouseholdMember.objects.filter(
            household_id=self.kwargs['household_pk'], is_archived=False
        ).order_by('full_name')

    def perform_create(self, serializer):
        instance = serializer.save(household_id=self.kwargs['household_pk'])
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='household_members', record_id=instance.member_id, request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='household_members', record_id=instance.member_id, request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        member = self.get_object()
        member.is_archived = True
        member.archived_at = timezone.now()
        member.save()
        write_audit_log(
            user=request.user, action=AuditAction.ARCHIVE,
            table_affected='household_members', record_id=member.member_id, request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class VulnerabilityIndicatorViewSet(viewsets.ModelViewSet):
    """
    Nested under a household: /api/households/{household_pk}/vulnerability/

    Saving a record (create or update) triggers the CART classifier via a
    post_save signal (see households/signals.py), which recomputes the
    parent Household's evacuation_priority and priority_score automatically.
    """
    serializer_class = VulnerabilityIndicatorSerializer
    permission_classes = [VulnerabilityIndicatorPermission]

    def get_queryset(self):
        _verify_resident_household_access(self.request, self.kwargs['household_pk'])
        return VulnerabilityIndicator.objects.filter(
            household_id=self.kwargs['household_pk'], is_archived=False
        ).order_by('-assessed_at')

    def _enforce_bhw_field_restriction(self, request):
        if request.user.role == UserRole.BARANGAY_HEALTHWORKER:
            submitted_fields = set(request.data.keys())
            disallowed = submitted_fields - BHW_ALLOWED_FIELDS
            if disallowed:
                raise ValidationError({
                    field: 'Barangay Healthworkers may only edit health-related indicator fields '
                           '(has_senior_citizen, has_pwd, has_pregnant_member, has_child).'
                    for field in disallowed
                })

    def perform_create(self, serializer):
        # BHW can't reach this method anyway (VulnerabilityIndicatorPermission
        # blocks 'create' for BHW at the permission-class level), but the
        # check stays here too as defense in depth.
        self._enforce_bhw_field_restriction(self.request)
        instance = serializer.save(
            household_id=self.kwargs['household_pk'],
            assessed_by=self.request.user,
        )
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='vulnerability_indicators', record_id=instance.indicator_id, request=self.request,
        )

    def perform_update(self, serializer):
        self._enforce_bhw_field_restriction(self.request)
        instance = serializer.save(assessed_by=self.request.user)
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='vulnerability_indicators', record_id=instance.indicator_id, request=self.request,
        )