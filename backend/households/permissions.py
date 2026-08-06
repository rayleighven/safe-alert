from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.choices import UserRole

from .models import Household


def _household_belongs_to_resident(obj, user):
    """obj may be a Household itself, or anything with a `.household` FK (Member, VulnerabilityIndicator)."""
    household = obj if isinstance(obj, Household) else obj.household
    return household.resident_user_id == user.pk


class HouseholdPermission(BasePermission):
    """
    - Barangay Secretary: full CRUD, own barangay.
    - Barangay Kagawad/Tanod, Barangay Healthworker: read-only on Households
      themselves (their write access lives on VulnerabilityIndicator).
    - MDRRMO Officer: read-only, both barangays.
    - Resident: read-only, and ONLY for the single household their account is
      linked to (accounts are created by the Secretary via a dedicated
      "create Resident account" action — there is no self-registration, and
      no way for a Resident to end up without a household link). Enforced
      here at the object level; list-level scoping happens in the
      viewset's get_queryset().
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.role in [
                UserRole.BARANGAY_SECRETARY,
                UserRole.BARANGAY_KAGAWAD_TANOD,
                UserRole.BARANGAY_HEALTHWORKER,
                UserRole.MDRRMO_OFFICER,
                UserRole.RESIDENT,
            ]

        return request.user.role == UserRole.BARANGAY_SECRETARY

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.RESIDENT:
            return _household_belongs_to_resident(obj, request.user)
        return True


class VulnerabilityIndicatorPermission(BasePermission):
    """
    - Barangay Secretary: full access.
    - Barangay Kagawad/Tanod: creates the record and sets hazard/structural
      fields during field validation.
    - Barangay Healthworker: edits ONLY the 4 health fields (enforced via
      field-filtering in the view, not here), and only within their
      assigned_purok (enforced via has_object_permission below).
    - MDRRMO Officer: read-only.
    - Resident: read-only, only for their own linked household.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.role in [
                UserRole.BARANGAY_SECRETARY,
                UserRole.BARANGAY_KAGAWAD_TANOD,
                UserRole.BARANGAY_HEALTHWORKER,
                UserRole.MDRRMO_OFFICER,
                UserRole.RESIDENT,
            ]

        if getattr(view, 'action', None) == 'create':
            # BHW cannot create fresh records — only edit existing ones
            # that Kagawad/Secretary already set up.
            return request.user.role in [UserRole.BARANGAY_SECRETARY, UserRole.BARANGAY_KAGAWAD_TANOD]

        return request.user.role in [
            UserRole.BARANGAY_SECRETARY,
            UserRole.BARANGAY_KAGAWAD_TANOD,
            UserRole.BARANGAY_HEALTHWORKER,
        ]

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.user.role == UserRole.RESIDENT:
                return _household_belongs_to_resident(obj, request.user)
            return True

        if request.user.role == UserRole.BARANGAY_HEALTHWORKER:
            return obj.household.purok == request.user.assigned_purok

        return True