from django.contrib import admin

from .models import Barangay, Disaster, EmergencyContact


@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ('name', 'municipality', 'province', 'contact_number', 'created_at')
    search_fields = ('name', 'municipality', 'province')


@admin.register(Disaster)
class DisasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'declared_at', 'resolved_at')
    list_filter = ('type', 'status')
    search_fields = ('name',)


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'barangay', 'contact_number', 'is_active')
    list_filter = ('role', 'barangay', 'is_active')
    search_fields = ('name', 'organization')