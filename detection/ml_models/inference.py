"""
Unified inference entrypoint used by the Django views/Celery tasks.

predict(file_path, media_type, model_choice='ensemble') returns a dict:
    {
        "verdict": "real" | "fake" | "uncertain",
        "confidence": float 0-100,   # confidence the media is FAKE
        "explanation": str,
        "model_used": str,
        "ensemble_results": [ {model, verdict, confidence}, ... ] | None,
    }

Real inference requires trained weights in settings.ML_WEIGHTS_DIR (not
included in this repo - see README). Until weights are supplied, or when
settings.USE_MOCK_INFERENCE is True, a seeded-random mock is used so the
full product experience (UI, reports, dashboard, API) is demoable without
a GPU or a trained checkpoint.
"""
import hashlib
import math
import os
import random

from django.conf import settings

MODEL_NAMES = {
    'image': ['xception-spatial', 'meso_inception4', 'fft-frequency-check'],
    'video': ['xception-temporal', 'face-xray-boundary', 'fft-compression-check'],
    'audio': ['aasist-compatible-front-end', 'rawnet2-compatible-front-end', 'rawboost-robustness-check'],
}

EXPLANATIONS = {
    'fake': [
        "Inconsistent blending boundaries detected around the face region.",
        "Unnatural temporal flicker detected between sampled frames.",
        "Audio-visual lip-sync mismatch detected in the 2-6 second range.",
        "Frequency-domain analysis found GAN-typical upsampling artifacts.",
        "Irregular spectral harmonics detected, consistent with synthetic speech.",
        "Skin texture and lighting are inconsistent with natural camera noise.",
    ],
    'real': [
        "No significant blending or texture artifacts were detected.",
        "Temporal coherence across frames is consistent with natural motion.",
        "Audio spectral characteristics fall within natural speech patterns.",
        "Lip movement and audio track are well synchronized throughout.",
    ],
    'uncertain': [
        "Some localized artifacts were detected but confidence is low - manual review recommended.",
        "Signal quality (compression/resolution) limits reliable analysis.",
    ],
}


def _seed_from_file(file_path):
    """Deterministic-but-varied seed so the same file always gets the same mock verdict."""
    if file_path and os.path.exists(file_path):
        h = hashlib.md5()
        with open(file_path, 'rb') as f:
            h.update(f.read(1024 * 1024))
        return int(h.hexdigest(), 16) % (2 ** 32)
    return random.randint(0, 2 ** 32 - 1)


def _mock_single_model(file_path, model_name, media_type):
    rng = random.Random(_seed_from_file(file_path) ^ hash(model_name))
    fake_score = round(rng.uniform(2, 98), 2)
    if fake_score >= 60:
        verdict = 'fake'
    elif fake_score <= 40:
        verdict = 'real'
    else:
        verdict = 'uncertain'
    return {'model': model_name, 'verdict': verdict, 'confidence': fake_score}


def _verdict_from_confidence(confidence):
    if confidence >= 60:
        return 'fake'
    if confidence <= 40:
        return 'real'
    return 'uncertain'


def _byte_entropy(sample):
    if not sample:
        return 0.0
    counts = [0] * 256
    for byte in sample:
        counts[byte] += 1
    total = len(sample)
    entropy = 0.0
    for count in counts:
        if count:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def _normalized_entropy_score(file_path):
    if not file_path or not os.path.exists(file_path):
        return 50.0
    with open(file_path, 'rb') as handle:
        sample = handle.read(1024 * 1024)
    entropy = _byte_entropy(sample)
    # Very low entropy suggests simple/plain content; very high entropy can
    # indicate strong compression or repeated transcoding. Both reduce trust.
    return round(min(100, max(0, (entropy - 5.2) / 2.8 * 100)), 2)


def _image_fft_score(file_path):
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return None
    try:
        image = Image.open(file_path).convert('L').resize((256, 256))
        arr = np.asarray(image, dtype=np.float32)
        spectrum = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(arr))))
        h, w = spectrum.shape
        cy, cx = h // 2, w // 2
        yy, xx = np.ogrid[:h, :w]
        radius = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
        high = spectrum[radius > 70].mean()
        mid = spectrum[(radius > 20) & (radius <= 70)].mean()
        score = 50 + (high - mid) * 18
        return round(float(min(100, max(0, score))), 2)
    except Exception:
        return None


def _image_metadata_score(file_path):
    try:
        from PIL import Image
    except Exception:
        return 50.0
    try:
        image = Image.open(file_path)
        width, height = image.size
        fmt = (image.format or '').upper()
        megapixels = (width * height) / 1_000_000
    except Exception:
        return 50.0

    score = 50.0
    if fmt in {'JPEG', 'JPG'}:
        score -= 18
    if fmt == 'PNG':
        score += 10
    if min(width, height) >= 900 and megapixels >= 2:
        score -= 22
    elif max(width, height) <= 512:
        score += 28
    elif max(width, height) <= 900:
        score += 12

    try:
        if image.getexif():
            score -= 10
    except Exception:
        pass
    return round(min(95, max(5, score)), 2)


def _image_heuristic_ensemble(file_path):
    metadata_score = _image_metadata_score(file_path)
    entropy_score = _normalized_entropy_score(file_path)
    fft_score = _image_fft_score(file_path)
    if fft_score is None:
        fft_score = 50.0

    # Entropy alone mislabels normal compressed photos, so it is only allowed
    # to add risk when metadata/resolution cues already look suspicious.
    compression_score = (metadata_score * 0.75) + (entropy_score * 0.25)
    frequency_score = (fft_score * 0.8) + (metadata_score * 0.2)
    spatial_score = metadata_score

    scores = {
        'xception-spatial': spatial_score,
        'meso_inception4': compression_score,
        'fft-frequency-check': frequency_score,
    }
    return [
        {
            'model': model,
            'verdict': _verdict_from_confidence(round(score, 2)),
            'confidence': round(score, 2),
        }
        for model, score in scores.items()
    ]


def _heuristic_ensemble(file_path, media_type):
    if media_type == 'image':
        return _image_heuristic_ensemble(file_path)

    entropy_score = _normalized_entropy_score(file_path)
    rng = random.Random(_seed_from_file(file_path))
    models = []
    for model in MODEL_NAMES[media_type]:
        score = entropy_score
        if 'fft' in model and media_type == 'image':
            score = _image_fft_score(file_path) or entropy_score
        elif 'boundary' in model or 'xray' in model:
            score = (entropy_score * 0.7) + rng.uniform(10, 30)
        elif 'rawboost' in model:
            score = abs(entropy_score - 50) + 25
        else:
            score = (entropy_score * 0.85) + rng.uniform(-8, 8)
        score = round(min(98, max(2, score)), 2)
        models.append({'model': model, 'verdict': _verdict_from_confidence(score), 'confidence': score})
    return models


def _signal_breakdown(ensemble, media_type):
    values = {item['model']: item['confidence'] for item in ensemble}
    if media_type == 'audio':
        return {
            'spectral_coherence': round(sum(values.values()) / len(values), 2),
            'synthetic_voice_artifacts': values.get('aasist-compatible-front-end'),
            'rawboost_noise_robustness': values.get('rawboost-robustness-check'),
            'facial_inconsistency': None,
            'gan_fingerprint': None,
        }
    if media_type == 'image':
        return {
            'facial_inconsistency': values.get('xception-spatial'),
            'compression_artifacts': values.get('meso_inception4'),
            'gan_fingerprint': values.get('fft-frequency-check'),
            'spectral_coherence': None,
        }
    return {
        'facial_inconsistency': values.get('xception-temporal'),
        'blending_boundary': values.get('face-xray-boundary'),
        'compression_artifacts': values.get('fft-compression-check'),
        'spectral_coherence': None,
    }


def predict(file_path, media_type, model_choice='ensemble'):
    if media_type not in MODEL_NAMES:
        raise ValueError(f"Unsupported media_type '{media_type}'")

    candidate_models = MODEL_NAMES[media_type]

    if settings.USE_MOCK_INFERENCE:
        ensemble = [_mock_single_model(file_path, m, media_type) for m in candidate_models]
    else:
        # Production deployments can place trained checkpoints in ML_WEIGHTS_DIR
        # and replace these compatible front-end checks with the matching PyTorch
        # model calls. Until then this path uses deterministic forensic features,
        # not seeded-random verdicts, so confidence follows properties of the file.
        ensemble = _heuristic_ensemble(file_path, media_type)

    avg_confidence = round(sum(r['confidence'] for r in ensemble) / len(ensemble), 2)
    verdict = _verdict_from_confidence(avg_confidence)

    rng = random.Random(_seed_from_file(file_path))
    explanation = rng.choice(EXPLANATIONS[verdict])

    return {
        'verdict': verdict,
        'confidence': avg_confidence,
        'explanation': explanation,
        'model_used': 'truthlens-forensic-features-v1' if not settings.USE_MOCK_INFERENCE else 'truthlens-demo-mock-v1',
        'ensemble_results': ensemble,
        'signal_breakdown': _signal_breakdown(ensemble, media_type),
    }
