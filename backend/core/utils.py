def get_client_ip(request):
    """Extract the client IP address, respecting X-Forwarded-For if present."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def write_audit_log(user, action, table_affected=None, record_id=None, request=None):
    """
    Central helper for writing to AuditLog. Every create/update/archive/
    restore/login action in every module should call this.

    Import is done inside the function (not at module level) to avoid a
    circular import between core and accounts.
    """
    from accounts.models import AuditLog

    AuditLog.objects.create(
        user=user,
        action=action,
        table_affected=table_affected,
        record_id=record_id,
        ip_address=get_client_ip(request) if request else None,
    )