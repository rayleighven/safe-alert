from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from core.models import Disaster

from .models import EvacuationCenter, EvacuationRecord


class EvacuationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvacuationCenter
        fields = [
            'center_id', 'barangay', 'name', 'address', 'capacity', 'current_occupancy',
            'status', 'contact_person', 'contact_number', 'managed_by', 'photo', 'photo_url',
            'created_at', 'updated_at', 'is_archived', 'archived_at',
        ]
        # barangay is set server-side from the requesting user, same pattern
        # as Household — prevents encoding a center into another barangay.
        read_only_fields = ['center_id', 'barangay', 'created_at', 'updated_at', 'is_archived', 'archived_at']
        # managed_by defaults to the requesting user (see
        # EvacuationCenterViewSet.perform_create) when omitted — it must not
        # be required, otherwise that fallback can never be reached because
        # serializer validation rejects the request first.
        extra_kwargs = {'managed_by': {'required': False}}

    def validate_photo(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Evacuation center photo must be 5 MB or smaller.')
        try:
            image = Image.open(value)
            image.verify()
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise serializers.ValidationError('Upload a valid image file.')
        finally:
            # Pillow verification consumes the stream; rewind it so Django can
            # save the validated image afterward.
            value.seek(0)
        return value

    def validate(self, attrs):
        capacity = attrs.get('capacity', getattr(self.instance, 'capacity', None))
        occupancy = attrs.get('current_occupancy', getattr(self.instance, 'current_occupancy', None))
        if capacity is not None and occupancy is not None and occupancy > capacity:
            raise serializers.ValidationError({'current_occupancy': 'Current occupancy cannot exceed capacity.'})
        # An uploaded photo takes precedence over an image URL — don't persist
        # both at once, so there's never ambiguity over which one is shown.
        if attrs.get('photo'):
            attrs['photo_url'] = ''
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