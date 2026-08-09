from rest_framework.permissions import BasePermission

from core.choices import UserRole


class CanViewHouseholdReport(BasePermission):
    """Secretary, Kagawad/Tanod, BHW, and MDRRMO can pull the household report."""
    message = 'You are not authorized to view the household report.'

    ALLOWED_ROLES = {
        UserRole.BARANGAY_SECRETARY,
        UserRole.BARANGAY_KAGAWAD_TANOD,
        UserRole.BARANGAY_HEALTHWORKER,
        UserRole.MDRRMO_OFFICER,
    }

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )


class CanViewEvacuationCenterReport(BasePermission):
    """Secretary, Kagawad/Tanod, BDRRMC Chairperson, and MDRRMO can pull the center report."""
    message = 'You are not authorized to view the evacuation center report.'

    ALLOWED_ROLES = {
        UserRole.BARANGAY_SECRETARY,
        UserRole.BARANGAY_KAGAWAD_TANOD,
        UserRole.BDRRMC_CHAIRPERSON,
        UserRole.MDRRMO_OFFICER,
    }

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )