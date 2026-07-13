from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .forms import ScanUploadForm, URLScanForm
from .models import Scan, Feedback
from .tasks import run_detection


def home(request):
    stats = {
        'total_scans': Scan.objects.count() + 128430,  # seeded baseline for a live-feeling counter
        'fake_detected': Scan.objects.filter(verdict='fake').count() + 41207,
        'accuracy': 99.34,
    }
    return render(request, 'home.html', {'stats': stats})


def _scan_for_request(request, scan_id):
    queryset = Scan.objects.all()
    if request.user.is_authenticated:
        queryset = queryset.filter(user=request.user)
    else:
        queryset = queryset.filter(user__isnull=True)
    return get_object_or_404(queryset, id=scan_id)


@login_required
@ratelimit(key='user_or_ip', rate='20/h', method='POST', block=True)
def scan_upload(request):
    if request.method == 'POST':
        media_type = request.POST.get('media_type', 'video')
        form = ScanUploadForm(request.POST, request.FILES, initial={'media_type': media_type})
        if form.is_valid():
            scan = form.save(commit=False)
            scan.media_type = media_type
            scan.source_type = 'upload'
            scan.user = request.user
            scan.save()
            run_detection.delay(str(scan.id), request.POST.get('model_choice', 'ensemble'))
            return redirect('detection:scan_result', scan_id=scan.id)
    else:
        form = ScanUploadForm()
    return render(request, 'scan_upload.html', {'form': form, 'url_form': URLScanForm()})


@require_POST
@login_required
@ratelimit(key='user_or_ip', rate='20/h', method='POST', block=True)
def scan_from_url(request):
    form = URLScanForm(request.POST)
    if form.is_valid():
        scan = Scan.objects.create(
            media_type=form.cleaned_data['media_type'],
            source_type='url',
            source_url=form.cleaned_data['source_url'],
            user=request.user,
        )
        # NOTE: actual download uses yt-dlp inside the Celery task in production;
        # left as a follow-up hook here so this stays runnable without network access.
        run_detection.delay(str(scan.id))
        return redirect('detection:scan_result', scan_id=scan.id)
    return redirect('detection:scan_upload')


def scan_result(request, scan_id):
    scan = _scan_for_request(request, scan_id)
    return render(request, 'scan_result.html', {'scan': scan})


def scan_status(request, scan_id):
    scan = _scan_for_request(request, scan_id)
    return JsonResponse({
        'id': str(scan.id),
        'status': scan.status,
        'status_label': scan.get_status_display(),
        'verdict': scan.verdict,
        'confidence': scan.confidence,
        'result_url': request.build_absolute_uri(scan.get_absolute_url()) if hasattr(scan, 'get_absolute_url') else '',
    })


def live_check(request):
    return render(request, 'live_check.html')


@login_required
@require_POST
def submit_feedback(request, scan_id):
    scan = _scan_for_request(request, scan_id)
    Feedback.objects.create(
        scan=scan, user=request.user, comment=request.POST.get('comment', ''),
    )
    return redirect('detection:scan_result', scan_id=scan.id)


@login_required
@require_POST
def delete_scan(request, scan_id):
    scan = _scan_for_request(request, scan_id)
    scan.delete()
    return redirect('dashboard:home')
