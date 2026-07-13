from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from detection.models import Scan
from .pdf_generator import generate_pdf


def download_report(request, scan_id):
    scan = get_object_or_404(Scan, id=scan_id, status='complete')
    pdf_bytes = generate_pdf(scan)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="truthlens-report-{scan.id}.pdf"'
    response['Cache-Control'] = 'no-store'
    return response
