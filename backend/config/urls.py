# backend/config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('households.urls')),
    path('api/', include('evacuation_centers.urls')),
    path('api/', include('announcements.urls')),
    path('api/', include('maps.urls')),
    path('api/reports/', include('reports.urls')),
]