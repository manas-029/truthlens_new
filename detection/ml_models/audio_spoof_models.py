"""
Standalone audio-only spoof/deepfake detection models.

Not part of the base paper (which only analyzes audio inside a video). This
lets TruthLens accept audio-only uploads (e.g. voice-cloning / AI call
scams) and score them directly, using architectures common in the
ASVspoof anti-spoofing literature.
"""
import torch
import torch.nn as nn


class LCNN(nn.Module):
    """Light CNN with Max-Feature-Map activations - a classic ASVspoof baseline."""

    class MFM(nn.Module):
        def forward(self, x):
            a, b = torch.chunk(x, 2, dim=1)
            return torch.max(a, b)

    def __init__(self, in_channels=1, num_classes=2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 64, 5, stride=1, padding=2), self.MFM(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 96, 3, padding=1), self.MFM(),
            nn.MaxPool2d(2),
            nn.Conv2d(48, 128, 3, padding=1), self.MFM(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, mel):
        x = self.features(mel)
        x = torch.flatten(x, 1)
        return self.classifier(x)


class RawNetLite(nn.Module):
    """Simplified RawNet-style model operating directly on the raw audio waveform."""

    def __init__(self, num_classes=2):
        super().__init__()
        self.sinc_like = nn.Conv1d(1, 64, kernel_size=251, stride=4, padding=125)
        self.res_blocks = nn.Sequential(
            nn.BatchNorm1d(64), nn.ReLU(),
            nn.Conv1d(64, 128, 3, stride=2, padding=1), nn.BatchNorm1d(128), nn.ReLU(),
            nn.Conv1d(128, 256, 3, stride=2, padding=1), nn.BatchNorm1d(256), nn.ReLU(),
        )
        self.gru = nn.GRU(256, 128, batch_first=True, bidirectional=True)
        self.classifier = nn.Linear(256, num_classes)

    def forward(self, waveform):
        """waveform: (B, 1, N) raw samples."""
        x = self.sinc_like(waveform)
        x = self.res_blocks(x)
        x = x.transpose(1, 2)
        _, h = self.gru(x)
        h = torch.cat([h[0], h[1]], dim=-1)
        return self.classifier(h)


AUDIO_SPOOF_MODELS = {
    'lcnn': LCNN,
    'rawnet': RawNetLite,
}
