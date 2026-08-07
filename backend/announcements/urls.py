# backend/announcements/urls.py
from rest_framework.routers import DefaultRouter

from .views import AnnouncementViewSet, SMSNotificationViewSet

router = DefaultRouter()
router.register('announcements', AnnouncementViewSet, basename='announcement')
router.register('sms-notifications', SMSNotificationViewSet, basename='sms-notification')

urlpatterns = router.urls