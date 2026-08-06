from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.choices import UserRole


class IsBarangaySecretary(BasePermission):
    message = 'Only the Barangay Secretary can perform this action.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.BARANGAY_SECRETARY
        )


class IsBDRRMCChairperson(BasePermission):
    message = 'Only the BDRRMC Chairperson can perform this action.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.BDRRMC_CHAIRPERSON
        )


class IsMDRRMOOfficer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.MDRRMO_OFFICER
        )


class IsBarangayKagawadTanod(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.BARANGAY_KAGAWAD_TANOD
        )


class IsBarangayHealthworker(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.BARANGAY_HEALTHWORKER
        )


class IsResident(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.RESIDENT
        )


class ReadOnlyForMDRRMO(BasePermission):
    """
    MDRRMO Officer has read-only access across every endpoint in the system.
    Combine with other permission classes (AND logic) on any viewset MDRRMO
    should be able to view.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.role == UserRole.MDRRMO_OFFICER:
            return request.method in SAFE_METHODS
        return True  # defer to other permission classes for non-MDRRMO users


class IsSelfOrBarangaySecretary(BasePermission):
    """
    Object-level permission: a user can view/edit their own profile;
    the Barangay Secretary can view/edit anyone's.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.BARANGAY_SECRETARY:
            return True
        return obj == request.user