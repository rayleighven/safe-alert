from rest_framework import serializers

from core.models import Disaster

from .models import EvacuationCenter, EvacuationRecord


class EvacuationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvacuationCenter
        fields = [
            'center_id', 'barangay', 'name', 'address', 'capacity', 'current_occupancy',
            'status', 'contact_person', 'contact_number', 'managed_by',
            'created_at', 'updated_at', 'is_archived', 'archived_at',
        ]
        # barangay is set server-side from the requesting user, same pattern
        # as Household — prevents encoding a center into another barangay.
        read_only_fields = ['center_id', 'barangay', 'created_at', 'updated_at', 'is_archived', 'archived_at']

    def validate(self, attrs):
        capacity = attrs.get('capacity', getattr(self.instance, 'capacity', None))
        occupancy = attrs.get('current_occupancy', getattr(self.instance, 'current_occupancy', None))
        if capacity is not None and occupancy is not None and occupancy > capacity:
            raise serializers.ValidationError({'current_occupancy': 'Current occupancy cannot exceed capacity.'})
        return attrs


class DisasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disaster
        fields = ['disaster_id', 'type', 'name', 'status', 'declared_at', 'resolved_at']
        read_only_fields = ['disaster_id', 'declared_at']


class EvacuationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvacuationRecord
        fields = [
            'record_id', 'disaster', 'center', 'household', 'entry_status', 'entered_at',
            'has_water', 'has_electricity', 'has_medical', 'has_food', 'discharged_at',
        ]
        read_only_fields = ['record_id']