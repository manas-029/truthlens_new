import json
import csv
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from detection.models import Scan


@login_required
def dashboard_home(request):
    scans = Scan.objects.filter(user=request.user).order_by('-created_at')
    verdict = request.GET.get('verdict', '')
    media_type = request.GET.get('media_type', '')
    q = request.GET.get('q', '').strip()
    if verdict:
        scans = scans.filter(verdict=verdict)
    if media_type:
        scans = scans.filter(media_type=media_type)
    if q:
        scans = scans.filter(file__icontains=q)

    all_user_scans = Scan.objects.filter(user=request.user)
    since = timezone.now() - timezone.timedelta(days=30)
    total = scans.count()
    fake_count = all_user_scans.filter(verdict='fake').count()
    real_count = all_user_scans.filter(verdict='real').count()
    uncertain_count = all_user_scans.filter(verdict='uncertain').count()
    avg_processing = all_user_scans.exclude(processing_time_ms=None).aggregate(avg=Avg('processing_time_ms'))['avg'] or 0

    timeline = list(
        all_user_scans.filter(created_at__gte=since).exclude(confidence=None)
        .order_by('created_at')
        .values_list('created_at', 'confidence')[:50]
    )
    timeline_labels = json.dumps([t[0].strftime('%b %d %H:%M') for t in timeline])
    timeline_values = json.dumps([t[1] for t in timeline])
    page_obj = Paginator(scans, 10).get_page(request.GET.get('page'))

    context = {
        'scans': page_obj.object_list,
        'page_obj': page_obj,
        'total': total,
        'fake_count': fake_count,
        'real_count': real_count,
        'uncertain_count': uncertain_count,
        'avg_processing_seconds': round(avg_processing / 1000, 2),
        'timeline_labels': timeline_labels,
        'timeline_values': timeline_values,
        'filters': {'verdict': verdict, 'media_type': media_type, 'q': q},
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def export_history_csv(request):
    scans = Scan.objects.filter(user=request.user).order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="truthlens-history.csv"'
    writer = csv.writer(response)
    writer.writerow(['created_at', 'filename', 'media_type', 'status', 'verdict', 'confidence', 'model_used', 'processing_time_ms'])
    for scan in scans:
        writer.writerow([
            scan.created_at.isoformat(),
            scan.original_filename,
            scan.media_type,
            scan.status,
            scan.verdict or '',
            scan.confidence if scan.confidence is not None else '',
            scan.model_used,
            scan.processing_time_ms or '',
        ])
    return response


@login_required
@require_POST
def bulk_delete_scans(request):
    ids = request.POST.getlist('scan_ids')
    if ids:
        Scan.objects.filter(user=request.user, id__in=ids).delete()
    return redirect('dashboard:home')
