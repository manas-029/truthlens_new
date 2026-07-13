# TruthLens

TruthLens is a Django deepfake-forensics web app for image, video, and audio review. It includes account-scoped scan history, async-ready Celery processing, PDF reports, a dashboard, a DRF API, and a model abstraction layer under `detection/ml_models/`.

## What Ships Now

- Signup, login, logout, password reset, and per-user scan access.
- Upload and URL scan flows with CSRF, login protection, server-side file extension/size checks, and magic-byte verification.
- Celery task integration with status polling on the result page. Development can run tasks eagerly; Docker runs web + worker + Redis.
- Result pages with verdict, fake-likelihood confidence, signal breakdown, model comparison, explanation, model info disclaimer, feedback, report download, and delete.
- Dashboard with user-scoped metrics, verdict distribution, 30-day trend, average processing time, filters, search, pagination, individual delete, bulk delete, and CSV export.
- WeasyPrint report template with fallback to HTML bytes if native WeasyPrint libraries are unavailable on the host.
- Retention command: `python manage.py purge_old_media --days 30`.
- Deterministic forensic feature inference by default. `USE_MOCK_INFERENCE=True` is still available for demo-only seeded scores.

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Docker

```bash
copy .env.example .env
docker compose up --build
```

The compose stack runs Postgres, Redis, Django, and a Celery worker. Uploaded media is shared between web and worker through the `media_storage` volume.

## Real Model Checkpoints

This repo does not include trained FaceForensics++, Celeb-DF, DFDC, WildDeepfake, or ASVspoof checkpoints. Those datasets/checkpoints require access approval, GPU training or fine-tuning, and measured evaluation. The default inference path uses deterministic file-derived forensic features so the product is usable without fabricating accuracy claims.

Planned checkpoint targets:

- Image/video spatial: XceptionNet or EfficientNet-B4/B7 fine-tuned on FaceForensics++.
- Lightweight visual secondary: MesoInception4.
- Frequency signal: FFT-based artifact checks inspired by Frank/Durall-style frequency analysis.
- Video temporal: sampled frames plus Xception/EfficientNet and temporal attention.
- Boundary signal: Face X-ray-style blending-boundary detector.
- Audio: AASIST or RawNet2 pretrained/fine-tuned on ASVspoof 2019 LA, with RawBoost augmentation.
- Fusion: learned MLP fusion head with calibrated thresholds and EER/AUC reporting.

Place trained `.pth` or `.pt` files under `detection/ml_models/weights/`, replace the compatible front-end block in `detection/ml_models/inference.py` with the real model loads/forward passes, and document the measured metrics in `MODEL_CARD.md`.

## Key Commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py purge_old_media --dry-run
celery -A truthlens worker -l info
```

## Main URLs

| Path | Purpose |
| --- | --- |
| `/scan/` | Upload or URL analysis |
| `/scan/<uuid>/` | Result and report actions |
| `/dashboard/` | User scan history and analytics |
| `/dashboard/export.csv` | CSV history export |
| `/api/docs/` | Swagger API docs |
| `/admin/` | Admin review |

## Notes

WeasyPrint needs native Pango/Cairo libraries. Docker is the recommended path for PDF generation. On Windows without those libraries, report downloads return the print-optimized HTML content instead of crashing.
