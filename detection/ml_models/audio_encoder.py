"""
Audio Feature Extraction (AFE) module.

Converts raw audio into a Mel-spectrogram (STFT -> Mel scale, Eq. 5 of the
base paper) and encodes it with a ResNet18-style CNN to obtain a sequence
of time-frequency embeddings, later averaged into a single global audio
vector `a` (Eq. 8).
"""
import numpy as np
import torch
import torch.nn as nn

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


def audio_to_melspectrogram(waveform, sr=16000, n_mels=128):
    """waveform: 1D numpy array -> (n_mels, T_a) log-Mel-spectrogram."""
    if not LIBROSA_AVAILABLE:
        raise RuntimeError("librosa is required for Mel-spectrogram extraction.")
    mel = librosa.feature.melspectrogram(y=waveform, sr=sr, n_mels=n_mels)
    log_mel = librosa.power_to_db(mel, ref=np.max)
    return log_mel


class ResNet18AudioEncoder(nn.Module):
    """A compact ResNet18-style encoder operating on Mel-spectrogram 'images'."""

    def __init__(self, in_channels=1, embed_dim=512):
        super().__init__()
        self.embed_dim = embed_dim

        def block(c_in, c_out, stride=1):
            return nn.Sequential(
                nn.Conv2d(c_in, c_out, 3, stride=stride, padding=1, bias=False),
                nn.BatchNorm2d(c_out),
                nn.ReLU(inplace=True),
                nn.Conv2d(c_out, c_out, 3, padding=1, bias=False),
                nn.BatchNorm2d(c_out),
            )

        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 64, 7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2, padding=1),
        )
        self.layer1 = block(64, 64)
        self.layer2 = block(64, 128, stride=2)
        self.layer3 = block(128, 256, stride=2)
        self.layer4 = block(256, embed_dim, stride=2)
        self.pool = nn.AdaptiveAvgPool2d(1)

    def forward(self, mel):
        """mel: (B, 1, F, T_a) -> (B, T_a', embed_dim) time-step feature sequence."""
        x = self.stem(mel)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)              # (B, D, F', T')
        x = x.mean(dim=2)               # collapse frequency -> (B, D, T')
        return x.transpose(1, 2)        # (B, T', D)

    @staticmethod
    def pool_time(z):
        """Average over time -> (B, D) global audio embedding `a` (Eq. 8)."""
        return z.mean(dim=1)
