"""
Static reference content for the /learn/datasets and /learn/models pages.
Kept as plain Python data structures so it's trivial to edit without
touching views/templates, and easy to later migrate into real DB models
or a fixture if the content needs to be admin-editable.
"""

DATASETS = [
    {
        'name': 'Inclusion-Global Multimedia Deepfake Challenge',
        'org': 'Ant Group',
        'modalities': ['Video', 'Audio'],
        'size': '241,990 training / 79,508 testing videos',
        'description': (
            'The benchmark used by TruthLens\u2019s underlying research. Each video has a '
            'paired audio track, enabling multimodal audio-visual detection research rather '
            'than visual-only analysis.'
        ),
    },
    {
        'name': 'FaceForensics++',
        'org': 'Technical University of Munich et al.',
        'modalities': ['Video', 'Image'],
        'size': '~1.8M manipulated images from 1,000 videos',
        'description': (
            'One of the earliest and most widely used deepfake benchmarks, covering four '
            'manipulation methods (Deepfakes, Face2Face, FaceSwap, NeuralTextures) at multiple '
            'compression levels.'
        ),
    },
    {
        'name': 'Celeb-DF (v1 / v2)',
        'org': 'City University of New York',
        'modalities': ['Video'],
        'size': '~6,000 videos (v2)',
        'description': (
            'Focused on high-visual-quality celebrity deepfakes, designed to be harder to '
            'detect than earlier datasets and to better reflect real-world forgery quality.'
        ),
    },
    {
        'name': 'DFDC (DeepFake Detection Challenge)',
        'org': 'Meta, AWS, Microsoft, academic partners',
        'modalities': ['Video', 'Audio'],
        'size': '100,000+ clips',
        'description': (
            'One of the largest public deepfake datasets, produced from a Kaggle-hosted '
            'challenge with a wide diversity of subjects, backgrounds, and forgery methods.'
        ),
    },
    {
        'name': 'WildDeepfake',
        'org': 'Chinese Academy of Sciences',
        'modalities': ['Video'],
        'size': '7,314 face sequences from 707 real-world videos',
        'description': (
            'Collected entirely from real internet videos rather than lab-generated forgeries, '
            'making it a strong test of generalization to \u201cin the wild\u201d deepfakes.'
        ),
    },
    {
        'name': 'ASVspoof (2019 / 2021)',
        'org': 'ASVspoof Consortium',
        'modalities': ['Audio'],
        'size': 'Tens of thousands of bona fide + spoofed utterances',
        'description': (
            'The standard benchmark for audio anti-spoofing/deepfake-voice detection, covering '
            'text-to-speech, voice conversion, and replay attacks.'
        ),
    },
    {
        'name': 'DeeperForensics-1.0',
        'org': 'Nanyang Technological University',
        'modalities': ['Video'],
        'size': '60,000 videos / 17.6M frames',
        'description': (
            'Adds real-world perturbations (compression, blur, noise, color variation) on top '
            'of high-fidelity forgeries to stress-test robustness, not just raw accuracy.'
        ),
    },
]

MODELS = {
    'Image': [
        {'name': 'XceptionNet', 'summary': 'Depthwise-separable CNN; a long-standing baseline for face-forgery classification.'},
        {'name': 'EfficientNet (B0\u2013B7)', 'summary': 'Compound-scaled CNN family balancing accuracy and compute; common in top DFDC solutions.'},
        {'name': 'ResNet-50/101', 'summary': 'Classic residual CNN backbone, frequently fine-tuned for binary real/fake classification.'},
        {'name': 'MesoNet / MesoInception-4', 'summary': 'Lightweight CNNs designed specifically to capture mesoscopic-level face-swap artifacts.'},
        {'name': 'Capsule Networks', 'summary': 'Capture spatial-hierarchy and pose relationships that plain CNNs can miss.'},
        {'name': 'F3-Net (frequency domain)', 'summary': 'Combines RGB and DCT/frequency features to catch GAN upsampling fingerprints.'},
        {'name': 'CLIP-based zero-shot detectors', 'summary': 'Vision-language pretraining used for detecting forgery types unseen during training.'},
    ],
    'Video / Temporal': [
        {'name': '3D CNNs (C3D, I3D)', 'summary': 'Convolve jointly over space and time to capture motion artifacts.'},
        {'name': 'LSTM/GRU + CNN hybrids', 'summary': 'CNN feature extractor followed by a recurrent network to model frame-to-frame inconsistency.'},
        {'name': 'ViT + Temporal Self-Attention', 'summary': 'The base-paper approach: multi-head attention along the temporal axis per spatial token, capturing long-range dependencies.'},
        {'name': 'Video Swin Transformer', 'summary': 'Hierarchical transformer capturing both local and global temporal dependencies.'},
        {'name': 'TimeSformer', 'summary': 'Separates space and time attention for efficient video classification.'},
        {'name': 'rPPG-based models', 'summary': 'Extract remote photoplethysmography (blood-flow) signals that GANs struggle to replicate.'},
        {'name': 'Eye-blink LSTM detectors', 'summary': 'Track eye-aspect-ratio over time; early deepfakes notoriously under-blinked.'},
    ],
    'Audio': [
        {'name': 'RawNet2 / RawNet3', 'summary': 'Operate directly on raw waveforms; widely used in ASVspoof anti-spoofing challenges.'},
        {'name': 'LCNN (Light CNN)', 'summary': 'Max-Feature-Map activations on spectrograms; a common ASVspoof baseline.'},
        {'name': 'AASIST', 'summary': 'Graph attention network integrating spectral and temporal cues; near state-of-the-art on ASVspoof.'},
        {'name': 'wav2vec 2.0 / HuBERT embeddings', 'summary': 'Self-supervised speech representations fine-tuned as spoof-detection features.'},
        {'name': 'ResNet-on-spectrogram', 'summary': 'Treats the Mel-spectrogram as an image for CNN classification (used in TruthLens\u2019s AFE module).'},
    ],
    'Multimodal Fusion': [
        {'name': 'SyncNet-style audio-visual sync networks', 'summary': 'Detect lip-sync mismatch between audio and video streams.'},
        {'name': 'Late/early fusion ensembles', 'summary': 'Combine independently-trained modality models via voting or stacking.'},
        {'name': 'Cross-attention transformer fusion', 'summary': 'Lets audio and visual streams inform each other\u2019s predictions jointly - the direction TruthLens\u2019s own architecture builds on.'},
    ],
}
