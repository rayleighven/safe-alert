from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.choices import AuditAction, DeliveryStatus, SMSStatus, UserRole
from core.utils import write_audit_log
from households.models import Household

from .models import Announcement, SMSLog, SMSNotification
from .permissions import AnnouncementPermission, SMSNotificationPermission
from .serializers import AnnouncementSerializer, AuthorizeSMSSerializer, SMSNotificationSerializer
from .sms_gateway import send_sms

# Maps Semaphore's own status vocabulary (+ our synthetic 'Simulated') onto
# the app's DeliveryStatus choices.
SEMAPHORE_STATUS_MAP = {
    'Sent': DeliveryStatus.DELIVERED,
    'Queued': DeliveryStatus.PENDING,
    'Pending': DeliveryStatus.PENDING,
    'Failed': DeliveryStatus.FAILED,
    'Refunded': DeliveryStatus.FAILED,
    'Simulated': DeliveryStatus.SIMULATED,
}

# RecipientType values ('High Priority'/'Medium'/'Low') map to
# Household.evacuation_priority values ('High'/'Medium'/'Low') — different
# strings by design (RecipientType reads naturally in a dropdown), so this
# translates between the two vocabularies.
RECIPIENT_TYPE_TO_PRIORITY = {
    'High Priority': 'High',
    'Medium': 'Medium',
    'Low': 'Low',
}


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [AnnouncementPermission]

    def get_queryset(self):
        user = self.request.user
        qs = Announcement.objects.filter(is_archived=False).order_by('-created_at')
        if user.role != UserRole.MDRRMO_OFFICER:
            qs = qs.filter(barangay=user.barangay)
        if user.role == UserRole.RESIDENT:
            qs = qs.filter(is_public=True)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save(barangay=self.request.user.barangay, posted_by=self.request.user)
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='announcements', record_id=instance.announcement_id, request=self.request,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        write_audit_log(
            user=self.request.user, action=AuditAction.UPDATE,
            table_affected='announcements', record_id=instance.announcement_id, request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        announcement = self.get_object()
        announcement.is_archived = True
        announcement.archived_at = timezone.now()
        announcement.save()
        write_audit_log(
            user=request.user, action=AuditAction.ARCHIVE,
            table_affected='announcements', record_id=announcement.announcement_id, request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SMSNotificationViewSet(viewsets.ModelViewSet):
    """
    Dual-authorization SMS broadcast workflow:
      1. Secretary: POST /api/sms-notifications/ — STAGES a broadcast
         (status=Pending, nothing sent yet).
      2. BDRRMC Chairperson: POST /api/sms-notifications/{id}/authorize/ —
         the ONLY action that actually triggers sending. Resolves the
         recipient list, sends each SMS (live or dry-run per
         settings.SMS_DRY_RUN), writes one SMS_Log row per recipient, and
         updates the notification's counts/status.

    No PATCH/PUT/DELETE on staged records — a staged broadcast is either
    authorized or left pending; it's not edited in place.
    """
    serializer_class = SMSNotificationSerializer
    permission_classes = [SMSNotificationPermission]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = SMSNotification.objects.filter(is_archived=False).order_by('-created_at')
        if user.role == UserRole.MDRRMO_OFFICER:
            return qs
        return qs.filter(barangay=user.barangay)

    def perform_create(self, serializer):
        instance = serializer.save(
            barangay=self.request.user.barangay,
            status=SMSStatus.PENDING,
        )
        write_audit_log(
            user=self.request.user, action=AuditAction.CREATE,
            table_affected='sms_notifications', record_id=instance.sms_id, request=self.request,
        )

    def _resolve_recipients(self, sms_notification, household_ids=None):
        qs = Household.objects.filter(barangay=sms_notification.barangay, is_archived=False)
        recipient_type = sms_notification.recipient_type

        if recipient_type == 'All':
            return qs
        if recipient_type == 'Custom':
            return qs.filter(household_id__in=household_ids) if household_ids else qs.none()

        priority = RECIPIENT_TYPE_TO_PRIORITY.get(recipient_type)
        return qs.filter(evacuation_priority=priority)

    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        sms_notification = self.get_object()

        if sms_notification.status != SMSStatus.PENDING:
            raise ValidationError('This broadcast has already been authorized.')

        serializer = AuthorizeSMSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        household_ids = serializer.validated_data.get('household_ids')

        recipients = list(self._resolve_recipients(sms_notification, household_ids))

        sent_count = 0
        failed_count = 0

        for household in recipients:
            result = send_sms(household.contact_number, sms_notification.message_body)
            mapped_status = SEMAPHORE_STATUS_MAP.get(result['status'], DeliveryStatus.PENDING)

            SMSLog.objects.create(
                sms=sms_notification,
                household=household,
                contact_number=household.contact_number,
                delivery_status=mapped_status,
                gateway_response=result.get('gateway_response', ''),
                sent_at=timezone.now(),
            )

            if mapped_status in [DeliveryStatus.DELIVERED, DeliveryStatus.SIMULATED]:
                sent_count += 1
            elif mapped_status == DeliveryStatus.FAILED:
                failed_count += 1

        total = len(recipients)
        if total == 0:
            final_status = SMSStatus.FAILED
        elif failed_count == 0:
            final_status = SMSStatus.SENT
        elif sent_count == 0:
            final_status = SMSStatus.FAILED
        else:
            final_status = SMSStatus.PARTIALLY_SENT

        sms_notification.total_recipients = total
        sms_notification.sent_count = sent_count
        sms_notification.failed_count = failed_count
        sms_notification.status = final_status
        sms_notification.initiated_by = request.user
        sms_notification.sent_at = timezone.now()
        sms_notification.save()

        write_audit_log(
            user=request.user, action=AuditAction.UPDATE,
            table_affected='sms_notifications', record_id=sms_notification.sms_id, request=request,
        )

        return Response(SMSNotificationSerializer(sms_notification).data, status=status.HTTP_200_OK)