from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Barangay
from .serializers import BarangaySerializer


class BarangayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only barangay lookup, for populating pickers where a user must
    choose among barangays rather than being scoped to their own — e.g. the
    MDRRMO Officer's barangay selector when authoring an announcement, since
    that role isn't tied to a single barangay.
    """
    serializer_class = BarangaySerializer
    permission_classes = [IsAuthenticated]
    queryset = Barangay.objects.all().order_by('name')
