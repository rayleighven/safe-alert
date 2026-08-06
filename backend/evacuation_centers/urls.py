from rest_framework.routers import DefaultRouter

from .views import DisasterViewSet, EvacuationCenterViewSet, EvacuationRecordViewSet

router = DefaultRouter()
router.register('evacuation-centers', EvacuationCenterViewSet, basename='evacuation-center')
router.register('disasters', DisasterViewSet, basename='disaster')
router.register('evacuation-records', EvacuationRecordViewSet, basename='evacuation-record')

urlpatterns = router.urls