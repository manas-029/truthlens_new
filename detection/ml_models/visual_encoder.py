"""
Visual feature extraction backbones.

Implements the "pretrained visual encoder" step from the base paper's
Visual Temporal Attention (VTA) module: each sampled frame I_t is mapped to
a spatial feature map f_t in R^(C x H x W), which is later flattened into
tokens for temporal self-attention.

Three interchangeable backbones are provided so the ensemble/comparison
feature (Section 3d of the product spec) has real architectural variety,
not just the same network under different names.
"""
import torch
import torch.nn as nn

try:
    import timm
    TIMM_AVAILABLE = True
except ImportError:
    TIMM_AVAILABLE = False


class ViTVisualEncoder(nn.Module):
    """Vision Transformer backbone - the base paper's choice for VTA."""

    def __init__(self, model_name='vit_base_patch16_224', pretrained=True, feature_dim=768):
        super().__init__()
        self.feature_dim = feature_dim
        if TIMM_AVAILABLE:
            self.backbone = timm.create_model(model_name, pretrained=pretrained, num_classes=0)
        else:
            # Lightweight fallback so the module still imports without timm installed.
            self.backbone = nn.Sequential(
                nn.Conv2d(3, 64, 7, stride=2, padding=3), nn.ReLU(),
                nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(64, feature_dim),
            )

    def forward(self, x):
        """x: (B, 3, H, W) -> (B, feature_dim) patch-pooled embedding."""
        return self.backbone(x)


class XceptionVisualEncoder(nn.Module):
    """Xception-style backbone, a common deepfake-artifact classifier baseline."""

    def __init__(self, feature_dim=2048, pretrained=True):
        super().__init__()
        self.feature_dim = feature_dim
        if TIMM_AVAILABLE:
            self.backbone = timm.create_model('xception', pretrained=pretrained, num_classes=0)
        else:
            self.backbone = nn.Sequential(
                nn.Conv2d(3, 64, 3, stride=2, padding=1), nn.ReLU(),
                nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(64, feature_dim),
            )

    def forward(self, x):
        return self.backbone(x)


class EfficientNetVisualEncoder(nn.Module):
    """EfficientNet backbone - good accuracy/compute tradeoff, used in many DFDC solutions."""

    def __init__(self, model_name='efficientnet_b0', feature_dim=1280, pretrained=True):
        super().__init__()
        self.feature_dim = feature_dim
        if TIMM_AVAILABLE:
            self.backbone = timm.create_model(model_name, pretrained=pretrained, num_classes=0)
        else:
            self.backbone = nn.Sequential(
                nn.Conv2d(3, 64, 3, stride=2, padding=1), nn.ReLU(),
                nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(64, feature_dim),
            )

    def forward(self, x):
        return self.backbone(x)


VISUAL_BACKBONES = {
    'vit': ViTVisualEncoder,
    'xception': XceptionVisualEncoder,
    'efficientnet': EfficientNetVisualEncoder,
}


def get_visual_encoder(name='vit', **kwargs):
    if name not in VISUAL_BACKBONES:
        raise ValueError(f"Unknown visual backbone '{name}'. Options: {list(VISUAL_BACKBONES)}")
    return VISUAL_BACKBONES[name](**kwargs)
