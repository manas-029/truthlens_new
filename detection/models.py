import uuid
from django.conf import settings
from django.db import models


class Scan(models.Model):
    """A single deepfake-detection request and its result."""

    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    SOURCE_TYPES = [
        ('upload', 'File upload'),
        ('url', 'Remote URL'),
        ('webcam', 'Live webcam'),
    ]
    VERDICT_CHOICES = [
        ('real', 'Real'),
        ('fake', 'Fake'),
        ('uncertain', 'Uncertain'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='scans',
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES, default='upload')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    source_url = models.URLField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    verdict = models.CharField(max_length=10, choices=VERDICT_CHOICES, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True, help_text='0-100 confidence that the media is FAKE')
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)

    model_used = models.CharField(max_length=100, default='truthlens-fusion-v1')
    explanation = models.TextField(blank=True, default='')
    heatmap = models.ImageField(upload_to='heatmaps/%Y/%m/%d/', null=True, blank=True)
    ensemble_results = models.JSONField(null=True, blank=True)
    signal_breakdown = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Scan {self.id} ({self.media_type}) - {self.verdict or self.status}"

    @property
    def is_fake(self):
        return self.verdict == 'fake'

    @property
    def original_filename(self):
        if not self.file:
            return self.source_url or 'Remote media'
        return self.file.name.rsplit('/', 1)[-1]


class Feedback(models.Model):
    """User-reported disagreement with a verdict, used for future retraining."""
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='feedback_entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True)
    reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on {self.scan_id}"
