"""
Temporal multi-head self-attention over sampled video frames.

Mirrors Eq. (1)-(4) of the base paper: for each spatial token position l,
the sequence of that token's features across T sampled frames is attended
over with multi-head self-attention, capturing cross-frame dynamic
inconsistencies (unnatural motion, blending flicker, lip-sync drift)
independently of spatial position.
"""
import torch
import torch.nn as nn


class TemporalSelfAttention(nn.Module):
    def __init__(self, dim=768, num_heads=8, num_layers=2, dropout=0.1):
        super().__init__()
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=dim, nhead=num_heads, dim_feedforward=dim * 4,
            dropout=dropout, batch_first=True,
        )
        self.temporal_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

    def forward(self, x):
        """
        x: (B, T, L, D) - batch, time steps, spatial tokens, feature dim.
        Attention is applied along T independently for every spatial token L,
        per Eq. (4) of the base paper.
        Returns: (B, T, L, D) enhanced representation X_hat.
        """
        b, t, l, d = x.shape
        x = x.permute(0, 2, 1, 3).reshape(b * l, t, d)      # (B*L, T, D)
        x = self.temporal_encoder(x)                         # attend across T
        x = x.reshape(b, l, t, d).permute(0, 2, 1, 3)        # back to (B, T, L, D)
        return x

    @staticmethod
    def pool(x_hat):
        """Average pool across time and space -> (B, D) global visual embedding (Eq. 7)."""
        return x_hat.mean(dim=(1, 2))
