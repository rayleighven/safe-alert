from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.permissions import IsResident
from core.choices import AuditAction, UserRole
from core.utils import write_audit_log
from evacuation_centers.models import EvacuationCenter
from households.models import Household

from .permissions import CanViewEvacuationCenterReport, CanViewHouseholdReport
from .pdf_utils import build_pdf_report


HOUSEHOLD_HEADERS = ['Household #', 'Head of Family', 'Purok', 'Members', 'Priority', 'Score']
CENTER_HEADERS = ['Name', 'Status', 'Capacity', 'Occupancy', 'Contact Person', 'Contact Number']


def _household_row(household):
    return [
        household.household_number,
        household.head_of_family,
        household.purok,
        household.total_members,
        household.evacuation_priority or '—',
        household.priority_score if household.priority_score is not None else '—',
    ]


def _center_row(center):
    return [
        center.name,
        center.status,
        center.capacity,
        center.current_occupancy,
        center.contact_person or '—',
        center.contact_number or '—',
    ]


class HouseholdReportView(APIView):
    """
    GET /api/reports/households/
    GET /api/reports/households/?priority=High
    Barangay-scoped for everyone except MDRRMO (sees both barangays).
    """
    permission_classes = [IsAuthenticated, CanViewHouseholdReport]

    def get(self, request):
        queryset = Household.objects.filter(is_archived=False)

        if request.user.role != UserRole.MDRRMO_OFFICER:
            queryset = queryset.filter(barangay=request.user.barangay)

        priority = request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(evacuation_priority=priority)

        queryset = queryset.order_by('household_number')
        rows = [_household_row(h) for h in queryset]

        subtitle = 'All Barangays' if request.user.role == UserRole.MDRRMO_OFFICER else str(request.user.barangay)
        if priority:
            subtitle += f' — {priority} Priority'

        buffer = build_pdf_report(
            title='Household Report',
            subtitle=subtitle,
            headers=HOUSEHOLD_HEADERS,
            rows=rows,
            generated_by=request.user.get_full_name() or request.user.username,
        )

        write_audit_log(
            user=request.user,
            action=AuditAction.CREATE,
            table_affected='households',
            record_id=None,
            request=request,
        )

        return FileResponse(buffer, as_attachment=True, filename='household_report.pdf')


class EvacuationCenterReportView(APIView):
    """
    GET /api/reports/evacuation-centers/
    Barangay-scoped for everyone except MDRRMO (sees both barangays).
    """
    permission_classes = [IsAuthenticated, CanViewEvacuationCenterReport]

    def get(self, request):
        queryset = EvacuationCenter.objects.filter(is_archived=False)

        if request.user.role != UserRole.MDRRMO_OFFICER:
            queryset = queryset.filter(barangay=request.user.barangay)

        queryset = queryset.order_by('name')
        rows = [_center_row(c) for c in queryset]

        subtitle = 'All Barangays' if request.user.role == UserRole.MDRRMO_OFFICER else str(request.user.barangay)

        buffer = build_pdf_report(
            title='Evacuation Center Report',
            subtitle=subtitle,
            headers=CENTER_HEADERS,
            rows=rows,
            generated_by=request.user.get_full_name() or request.user.username,
        )

        write_audit_log(
            user=request.user,
            action=AuditAction.CREATE,
            table_affected='evacuation_centers',
            record_id=None,
            request=request,
        )

        return FileResponse(buffer, as_attachment=True, filename='evacuation_center_report.pdf')


class MyHouseholdReportView(APIView):
    """
    GET /api/reports/my-household/
    Resident-only, PDF of their own linked household (via Household.resident_user).
    """
    permission_classes = [IsAuthenticated, IsResident]

    def get(self, request):
        household = getattr(request.user, 'resident_household', None)
        if household is None or household.is_archived:
            raise Http404('No household is linked to this account.')

        buffer = build_pdf_report(
            title='My Household Report',
            subtitle=str(household.barangay),
            headers=HOUSEHOLD_HEADERS,
            rows=[_household_row(household)],
            generated_by=request.user.get_full_name() or request.user.username,
        )

        write_audit_log(
            user=request.user,
            action=AuditAction.CREATE,
            table_affected='households',
            record_id=household.household_id,
            request=request,
        )

        return FileResponse(buffer, as_attachment=True, filename='my_household_report.pdf')