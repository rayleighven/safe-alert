import uuid
from django.conf import settings
from django.db import models

from core.choices import AnnouncementCategoryTag, RecipientType, SMSStatus, DeliveryStatus
from core.models import Barangay, TimeStampedModel, ArchivableModel
from households.models import Household


class Announcement(TimeStampedModel, ArchivableModel):
    announcement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='announcements')
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_public = models.BooleanField(default=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='announcements_posted',
    )
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'announcements'

    def __str__(self):
        return self.title


class AnnouncementCategory(models.Model):
    """
    Normalizes multi-category tagging out of Announcements (one
    announcement can carry multiple category tags via multiple rows here).
    """
    announcement_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='categories')
    category = models.CharField(max_length=20, choices=AnnouncementCategoryTag.choices)

    class Meta:
        db_table = 'announcement_categories'
        constraints = [
            models.CheckConstraint(condition=models.Q(category__in=AnnouncementCategoryTag.values), name='announcement_category_valid'),
        ]
        unique_together = ('announcement', 'category')

    def __str__(self):
        return f"{self.announcement.title} - {self.category}"


class SMSNotification(TimeStampedModel, ArchivableModel):
    sms_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='sms_notifications')
    subject = models.CharField(max_length=255)
    message_body = models.TextField()
    recipient_type = models.CharField(max_length=20, choices=RecipientType.choices)
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=SMSStatus.choices, default=SMSStatus.PENDING)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sms_notifications_initiated',
        help_text='The BDRRMC Chairperson who authorized this broadcast.',
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sms_notifications'
        constraints = [
            models.CheckConstraint(condition=models.Q(recipient_type__in=RecipientType.values), name='sms_notif_recipient_type_valid'),
            models.CheckConstraint(condition=models.Q(status__in=SMSStatus.values), name='sms_notif_status_valid'),
        ]

    def __str__(self):
        return f"{self.subject} ({self.status})"


class SMSLog(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sms = models.ForeignKey(SMSNotification, on_delete=models.CASCADE, related_name='logs')
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name='sms_logs')
    contact_number = models.CharField(max_length=20)
    delivery_status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING)
    gateway_response = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sms_logs'
        constraints = [
            models.CheckConstraint(condition=models.Q(delivery_status__in=DeliveryStatus.values), name='sms_logs_delivery_status_valid'),
        ]

    def __str__(self):
        return f"{self.household.household_number} - {self.delivery_status}"