from rest_framework.routers import DefaultRouter

from .views import BarangayViewSet

router = DefaultRouter()
router.register('barangays', BarangayViewSet, basename='barangay')

urlpatterns = router.urls
