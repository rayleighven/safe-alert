from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from .models import HazardMap


class HazardMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = HazardMap
        fields = [
            'map_id', 'barangay', 'map_title', 'hazard_type', 'source',
            'map_url', 'map_image', 'description', 'uploaded_by', 'uploaded_at',
            'is_archived', 'archived_at',
        ]
        # barangay/uploaded_by set server-side, same pattern as every other module.
        read_only_fields = ['map_id', 'barangay', 'uploaded_by', 'uploaded_at', 'is_archived', 'archived_at']
        # map_url is only required when no image is uploaded (see validate()).
        extra_kwargs = {'map_url': {'required': False}}

    def validate_map_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError('Map URL must be a valid http(s) link (e.g. a Project NOAH map page).')
        return value

    def validate_map_image(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Hazard map image must be 5 MB or smaller.')
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
        map_url = attrs.get('map_url', getattr(self.instance, 'map_url', ''))
        map_image = attrs.get('map_image', getattr(self.instance, 'map_image', None))
        if not map_url and not map_image:
            raise serializers.ValidationError({'map_url': 'Provide a map URL or upload a map image.'})
        return attrs
