from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from detection.models import Scan, Feedback
from detection.tasks import run_detection
from .serializers import ScanSerializer, FeedbackSerializer


class ScanViewSet(viewsets.ModelViewSet):
    """
    Programmatic access to TruthLens scans.

    POST a file + media_type to create a scan (kicks off async detection),
    then GET /api/scans/{id}/ to poll for the result.
    """
    serializer_class = ScanSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Scan.objects.filter(user=user).order_by('-created_at')
        return Scan.objects.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        scan = serializer.save(user=user, source_type='upload')
        run_detection.delay(str(scan.id))

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        scan = self.get_object()
        Feedback.objects.create(
            scan=scan, user=request.user, comment=request.data.get('comment', ''),
        )
        return Response({'status': 'flagged'}, status=status.HTTP_201_CREATED)
