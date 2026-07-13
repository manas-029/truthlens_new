from celery import shared_task
from django.utils import timezone

from .models import Scan
from .ml_models.inference import predict


@shared_task
def run_detection(scan_id, model_choice='ensemble'):
    try:
        scan = Scan.objects.get(id=scan_id)
    except Scan.DoesNotExist:
        return

    scan.status = 'processing'
    scan.save(update_fields=['status'])

    started_at = timezone.now()
    file_path = scan.file.path if scan.file else None
    try:
        result = predict(file_path, scan.media_type, model_choice=model_choice)
    except Exception as exc:
        scan.status = 'failed'
        scan.explanation = f'Analysis failed: {exc}'
        scan.completed_at = timezone.now()
        scan.save(update_fields=['status', 'explanation', 'completed_at'])
        raise

    scan.verdict = result['verdict']
    scan.confidence = result['confidence']
    scan.explanation = result['explanation']
    scan.model_used = result['model_used']
    scan.ensemble_results = result['ensemble_results']
    scan.signal_breakdown = result.get('signal_breakdown')
    scan.processing_time_ms = int((timezone.now() - started_at).total_seconds() * 1000)
    scan.status = 'complete'
    scan.completed_at = timezone.now()
    scan.save()
    return str(scan.id)
