import secrets
from django.conf import settings
from django.db import models


def generate_api_key():
    return secrets.token_urlsafe(32)


class Profile(models.Model):
    """Extra fields attached to every user, plus their API access."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    api_key = models.CharField(max_length=64, unique=True, default=generate_api_key)
    plan = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('pro', 'Pro'), ('research', 'Research')],
        default='free',
    )
    scans_this_month = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.plan})"
