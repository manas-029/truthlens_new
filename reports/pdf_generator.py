"""
Generates a forensic PDF report for a completed Scan.

Uses WeasyPrint to render an HTML template to PDF, so the same design
language (fonts/colors) as the site can be reused for the report.
"""
from django.template.loader import render_to_string


def render_report_html(scan):
    return render_to_string('reports/report.html', {'scan': scan})


def _generate_reportlab_pdf(scan):
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph('TruthLens Forensic Report', styles['Title']),
        Spacer(1, 8),
        Paragraph(f'<b>Verdict:</b> {scan.verdict.upper() if scan.verdict else "PENDING"}', styles['Heading2']),
        Paragraph(f'<b>Fake-likelihood confidence:</b> {scan.confidence or 0}%', styles['Normal']),
        Spacer(1, 12),
    ]

    metadata = [
        ['Scan ID', str(scan.id)],
        ['Filename/source', scan.original_filename],
        ['Media type', scan.get_media_type_display()],
        ['Source type', scan.get_source_type_display()],
        ['Model used', scan.model_used],
        ['Completed', str(scan.completed_at or '-')],
        ['Processing time', f'{scan.processing_time_ms or "-"} ms'],
    ]
    table = Table(metadata, colWidths=[42 * mm, 110 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eef4f3')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#16202c')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#ccd6dd')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    story.extend([table, Spacer(1, 14), Paragraph('Explanation', styles['Heading2'])])
    story.append(Paragraph(scan.explanation or 'No explanation available.', styles['BodyText']))

    if scan.signal_breakdown:
        story.extend([Spacer(1, 14), Paragraph('Signal Breakdown', styles['Heading2'])])
        rows = [['Signal', 'Score']]
        for key, value in scan.signal_breakdown.items():
            rows.append([key.replace('_', ' ').title(), 'Not applicable' if value is None else f'{value}%'])
        signal_table = Table(rows, colWidths=[76 * mm, 76 * mm])
        signal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111820')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#ccd6dd')),
            ('PADDING', (0, 0), (-1, -1), 7),
        ]))
        story.append(signal_table)

    story.extend([
        Spacer(1, 18),
        Paragraph(
            'Disclaimer: This automated report is provided for investigative review only. '
            'TruthLens outputs probabilistic forensic signals and should not be treated as definitive proof without expert human review.',
            styles['Italic'],
        ),
    ])
    doc.build(story)
    return buffer.getvalue()


def generate_pdf(scan):
    html_string = render_report_html(scan)
    try:
        from weasyprint import HTML
        return HTML(string=html_string).write_pdf()
    except (ImportError, OSError):
        # WeasyPrint has native dependencies on Windows. Fall back to a real
        # PDF generated with ReportLab so the download remains valid.
        return _generate_reportlab_pdf(scan)
