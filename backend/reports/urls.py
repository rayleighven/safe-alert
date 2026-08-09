from django.urls import path

from .views import EvacuationCenterReportView, HouseholdReportView, MyHouseholdReportView

urlpatterns = [
    path('households/', HouseholdReportView.as_view(), name='household-report'),
    path('evacuation-centers/', EvacuationCenterReportView.as_view(), name='evacuation-center-report'),
    path('my-household/', MyHouseholdReportView.as_view(), name='my-household-report'),
]