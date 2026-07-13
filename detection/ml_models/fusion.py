"""
Multimodal Fusion & Classification (Section III-C of the base paper).

Concatenates the global visual embedding v and global audio embedding a,
then passes [a; v] through a lightweight MLP head to predict the
real/fake probability (Eq. 9).
"""
import torch
import torch.nn as nn


class FusionClassifier(nn.Module):
    def __init__(self, visual_dim=768, audio_dim=512, hidden_dim=256, num_classes=2):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(visual_dim + audio_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, audio_embed, visual_embed):
        fused = torch.cat([audio_embed, visual_embed], dim=-1)   # [a; v]
        return self.mlp(fused)


class TruthLensVideoModel(nn.Module):
    """End-to-end video model: VTA + AFE + fusion head, matching Figure 1 of the paper."""

    def __init__(self, visual_encoder, temporal_attention, audio_encoder, fusion_classifier):
        super().__init__()
        self.visual_encoder = visual_encoder
        self.temporal_attention = temporal_attention
        self.audio_encoder = audio_encoder
        self.fusion_classifier = fusion_classifier

    def forward(self, frames, mel_spectrogram):
        """
        frames: (B, T, 3, H, W) sampled video frames
        mel_spectrogram: (B, 1, F, T_a)
        """
        b, t = frames.shape[:2]
        flat_frames = frames.view(b * t, *frames.shape[2:])
        feats = self.visual_encoder(flat_frames)                 # (B*T, D)
        d = feats.shape[-1]
        feats = feats.view(b, t, 1, d)                            # treat as L=1 token/frame (pooled backbone)

        x_hat = self.temporal_attention(feats)                    # (B, T, 1, D)
        v = self.temporal_attention.pool(x_hat)                   # (B, D)

        z = self.audio_encoder(mel_spectrogram)                   # (B, T_a, D_a)
        a = self.audio_encoder.pool_time(z)                       # (B, D_a)

        logits = self.fusion_classifier(a, v)
        return logits
