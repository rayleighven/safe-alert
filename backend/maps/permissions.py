from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.choices import UserRole


class HazardMapPermission(BasePermission):
    """
    - Barangay Secretary: full CRUD, own barangay.
    - Everyone else — Chairperson, Kagawad, BHW, MDRRMO, and Resident — is
      read-only. Unlike SMS broadcasts or evacuation records, hazard map
      references are genuinely public disaster-awareness info, so Resident
      gets the same read access as staff roles here (still barangay-scoped
      per the standing rule, not literally unauthenticated-public).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == UserRole.BARANGAY_SECRETARY