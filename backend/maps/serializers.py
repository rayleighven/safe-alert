from rest_framework import serializers

from .models import HazardMap


class HazardMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = HazardMap
        fields = [
            'map_id', 'barangay', 'map_title', 'hazard_type', 'source',
            'map_url', 'description', 'uploaded_by', 'uploaded_at',
            'is_archived', 'archived_at',
        ]
        # barangay/uploaded_by set server-side, same pattern as every other module.
        read_only_fields = ['map_id', 'barangay', 'uploaded_by', 'uploaded_at', 'is_archived', 'archived_at']

    def validate_map_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError('Map URL must be a valid http(s) link (e.g. a Project NOAH map page).')
        return value