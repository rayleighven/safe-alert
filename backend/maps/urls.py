from rest_framework.routers import DefaultRouter

from .views import HazardMapViewSet

router = DefaultRouter()
router.register('hazard-maps', HazardMapViewSet, basename='hazard-map')

urlpatterns = router.urls