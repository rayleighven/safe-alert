from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.choices import UserRole

CENTER_KAGAWAD_ALLOWED_FIELDS = {'capacity', 'current_occupancy', 'status'}


class EvacuationCenterPermission(BasePermission):
    """
    - Barangay Secretary: full CRUD (encodes the center), own barangay.
    - Barangay Kagawad/Tanod: can only PATCH an EXISTING center, and only
      capacity/current_occupancy/status (enforced via field-filtering in the
      view) — matches "field validation, evacuation center management" from
      the actor list without giving Kagawad the ability to create/archive
      centers outright.
    - BDRRMC Chairperson, Barangay Healthworker: read-only.
    - MDRRMO Officer: read-only, both barangays (queryset-level).
    - Resident: read-only, own barangay only — this is the "public info" a
      resident can see (per the standing barangay-scoping rule, own barangay
      only, not literally public/unauthenticated).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True  # everyone can read; barangay scoping happens in get_queryset

        if request.user.role == UserRole.BARANGAY_SECRETARY:
            return True

        if request.user.role == UserRole.BARANGAY_KAGAWAD_TANOD:
            return getattr(view, 'action', None) in ['update', 'partial_update']

        return False


class DisasterPermission(BasePermission):
    """
    - Barangay Secretary, BDRRMC Chairperson: full CRUD (declare/resolve disasters).
    - Everyone else (authenticated): read-only.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in [UserRole.BARANGAY_SECRETARY, UserRole.BDRRMC_CHAIRPERSON]


class EvacuationRecordPermission(BasePermission):
    """
    - Barangay Secretary, Barangay Kagawad/Tanod: full CRUD — field personnel
      logging households checking in/out of a center during an active disaster.
    - Everyone else (authenticated): read-only.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in [UserRole.BARANGAY_SECRETARY, UserRole.BARANGAY_KAGAWAD_TANOD]