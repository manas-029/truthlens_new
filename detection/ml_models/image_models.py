"""
Standalone single-image deepfake/artifact classifiers.

Not covered by the base paper (video-only). Powers TruthLens's image-upload
flow, where there is no temporal dimension to exploit and detection must
rely purely on spatial artifacts (blending boundaries, texture statistics,
GAN frequency fingerprints).
"""
import torch
import torch.nn as nn


class MesoInception4(nn.Module):
    """Lightweight mesoscopic-feature CNN (MesoNet family) tuned for face-swap artifacts."""

    def __init__(self, num_classes=2):
        super().__init__()

        def inception_block(c_in, c_out):
            return nn.ModuleList([
                nn.Conv2d(c_in, c_out, 1),
                nn.Conv2d(c_in, c_out, 3, padding=1),
                nn.Conv2d(c_in, c_out, 3, padding=2, dilation=2),
                nn.Conv2d(c_in, c_out, 3, padding=3, dilation=3),
            ])

        self.block1 = inception_block(3, 8)
        self.bn1 = nn.BatchNorm2d(32)
        self.block2 = inception_block(32, 8)
        self.bn2 = nn.BatchNorm2d(32)
        self.pool = nn.MaxPool2d(2)
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(32, 16), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(16, num_classes),
        )

    def _run_block(self, block, bn, x):
        out = torch.cat([conv(x) for conv in block], dim=1)
        return self.pool(torch.relu(bn(out)))

    def forward(self, x):
        x = self._run_block(self.block1, self.bn1, x)
        x = self._run_block(self.block2, self.bn2, x)
        return self.classifier(x)


class FrequencyDomainNet(nn.Module):
    """
    Combines an RGB CNN branch with a DCT/frequency-domain branch, in the
    spirit of F3-Net, to catch GAN up-sampling fingerprints invisible in
    the pixel domain alone.
    """

    def __init__(self, num_classes=2):
        super().__init__()
        self.rgb_branch = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
        )
        self.freq_branch = nn.Sequential(
            nn.Conv2d(1, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
        )
        self.classifier = nn.Linear(128, num_classes)

    def forward(self, rgb, freq):
        r = self.rgb_branch(rgb)
        f = self.freq_branch(freq)
        return self.classifier(torch.cat([r, f], dim=1))


IMAGE_MODELS = {
    'meso_inception4': MesoInception4,
    'frequency_net': FrequencyDomainNet,
}
