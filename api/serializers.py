from rest_framework import serializers
from detection.models import Scan, Feedback


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = [
            'id', 'media_type', 'source_type', 'file', 'source_url',
            'status', 'verdict', 'confidence', 'model_used', 'explanation',
            'ensemble_results', 'signal_breakdown', 'processing_time_ms',
            'created_at', 'completed_at',
        ]
        read_only_fields = [
            'id', 'status', 'verdict', 'confidence', 'model_used',
            'explanation', 'ensemble_results', 'signal_breakdown',
            'processing_time_ms', 'created_at', 'completed_at',
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'scan', 'comment', 'reviewed', 'created_at']
        read_only_fields = ['id', 'reviewed', 'created_at']
