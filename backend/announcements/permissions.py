from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.choices import UserRole


class AnnouncementPermission(BasePermission):
    """
    - Barangay Secretary: full CRUD, own barangay.
    - BDRRMC Chairperson, Kagawad/Tanod, Healthworker, MDRRMO: read-only —
      see both public and non-public announcements.
    - Resident: read-only, PUBLIC announcements only, own barangay (queryset-scoped).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == UserRole.BARANGAY_SECRETARY


class SMSNotificationPermission(BasePermission):
    """
    Dual-authorization workflow:
      - Barangay Secretary: can STAGE a broadcast (create only — no edit/delete
        of a staged record; the only thing that happens to it next is authorization).
      - BDRRMC Chairperson: the ONLY role that can call the `authorize` action,
        which is what actually triggers sending.
      - Barangay Kagawad/Tanod, Barangay Healthworker, MDRRMO Officer: read-only.
      - Resident: no access — this is operational staff data, not "public info".
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == UserRole.RESIDENT:
            return False

        if request.method in SAFE_METHODS:
            return True

        action_name = getattr(view, 'action', None)

        if action_name == 'authorize':
            return request.user.role == UserRole.BDRRMC_CHAIRPERSON

        if action_name == 'create':
            return request.user.role == UserRole.BARANGAY_SECRETARY

        return False