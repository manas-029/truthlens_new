# TruthLens Model Card

## Current Version

`truthlens-forensic-features-v1`

This version does not claim trained deepfake-classifier accuracy. It uses deterministic forensic feature checks when `USE_MOCK_INFERENCE=False`, including byte-entropy/compression cues and image FFT high-frequency energy where Pillow and NumPy are available. These signals are suitable for product integration, UI validation, and PBL demonstration, but they are not a substitute for trained checkpoint evaluation.

## Intended Use

TruthLens provides probabilistic forensic signals for human review. Results should not be treated as certified proof of authenticity, identity, intent, or legal truth.

## Planned Checkpoints

| Modality | Target model | Training/evaluation data |
| --- | --- | --- |
| Image | XceptionNet or EfficientNet-B4/B7, MesoInception4, FFT frequency check | FaceForensics++, DFDC, WildDeepfake |
| Video | Frame CNN plus temporal attention and Face X-ray boundary signal | FaceForensics++, Celeb-DF v2, DFDC, WildDeepfake |
| Audio | AASIST or RawNet2 with RawBoost augmentation | ASVspoof 2019 LA |
| Fusion | Learned MLP over audio/visual embeddings | Held-out multimodal validation split |

## Metrics

No trained-checkpoint metrics are reported in this repository yet. Before production claims are made, record at minimum:

- AUC and EER per modality.
- Cross-dataset performance on Celeb-DF v2, DFDC, and WildDeepfake.
- Calibration curves for real/fake/uncertain thresholds.
- Failure modes by compression level, resolution, language/accent, background noise, and manipulation family.

## Known Limitations

- Dataset access for FaceForensics++ requires an academic-use agreement.
- Lab-set accuracy often overstates real-world performance.
- Compressed or low-resolution media can produce uncertain or unstable scores.
- Audio-only and image-only scans cannot evaluate audio-visual consistency.
- Current feature fallback should be replaced with trained checkpoints before any high-stakes deployment.
