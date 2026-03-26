from django.db import models
from song_api.models import Song

# Create your models here.
class ShareLink(models.Model):
    song = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name='share_link',
        null=True,
        blank=True
    )

    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.token}"