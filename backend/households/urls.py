from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import HouseholdMemberViewSet, HouseholdViewSet, VulnerabilityIndicatorViewSet

router = DefaultRouter()
router.register('households', HouseholdViewSet, basename='household')

household_member_list = HouseholdMemberViewSet.as_view({'get': 'list', 'post': 'create'})
household_member_detail = HouseholdMemberViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})

vulnerability_list = VulnerabilityIndicatorViewSet.as_view({'get': 'list', 'post': 'create'})
vulnerability_detail = VulnerabilityIndicatorViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})

urlpatterns = router.urls + [
    path('households/<uuid:household_pk>/members/', household_member_list, name='household-members-list'),
    path('households/<uuid:household_pk>/members/<uuid:pk>/', household_member_detail, name='household-members-detail'),
    path('households/<uuid:household_pk>/vulnerability/', vulnerability_list, name='household-vulnerability-list'),
    path('households/<uuid:household_pk>/vulnerability/<uuid:pk>/', vulnerability_detail, name='household-vulnerability-detail'),
]