from django.shortcuts import render
from .data import DATASETS, MODELS

ARTICLES = [
    {
        'slug': 'how-deepfakes-are-made',
        'title': 'How Deepfakes Are Made',
        'summary': 'A plain-language walkthrough of GANs, diffusion models, and voice cloning.',
        'body': (
            'Most deepfakes are produced with generative adversarial networks (GANs) or, '
            'increasingly, diffusion models. A generator network learns to produce convincing '
            'fake faces or voices while a discriminator network learns to catch it - the two '
            'compete until the generator\u2019s output is hard to distinguish from real footage. '
            'Face-swap tools also rely heavily on facial landmark detection and blending '
            'algorithms to seamlessly merge a synthesized face onto a target video.'
        ),
    },
    {
        'slug': 'how-to-spot-a-deepfake-yourself',
        'title': 'How to Spot a Deepfake Yourself',
        'summary': 'Visual and audio cues you can check for before reaching for a tool.',
        'body': (
            'Look for unnatural blinking patterns, inconsistent lighting or shadows on the '
            'face versus the background, blurry or warped boundaries around the hairline and '
            'ears, and audio that doesn\u2019t quite match lip movement. Synthetic voices often '
            'have unnaturally even pacing and lack the small breathing sounds and pitch '
            'variation of real speech.'
        ),
    },
    {
        'slug': 'why-generalization-is-the-hard-part',
        'title': 'Why Generalization Is the Hard Part of Deepfake Detection',
        'summary': 'Detectors trained on one generator often fail on the next one.',
        'body': (
            'A classifier trained on a specific GAN\u2019s output tends to overfit to that '
            'generator\u2019s particular artifacts, and can fail badly on deepfakes made with a '
            'newer or different generation method. This is why current research increasingly '
            'looks at frequency-domain features, biological signals, and self-supervised '
            'pretraining - these tend to transfer better across unseen generators.'
        ),
    },
]


def datasets_page(request):
    return render(request, 'datasets.html', {'datasets': DATASETS})


def models_page(request):
    return render(request, 'models.html', {'model_groups': MODELS})


def article_list(request):
    return render(request, 'knowledge_base/list.html', {'articles': ARTICLES})


def article_detail(request, slug):
    article = next((a for a in ARTICLES if a['slug'] == slug), None)
    return render(request, 'knowledge_base/detail.html', {'article': article})
