import uuid
from django.db import models
from song_api.models import Song
from users.models import User

def _generate_token():
    return uuid.uuid4().hex[:24]

class ShareLink(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='share_links', null=True, blank=True)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_links', null=True, blank=True)
    token = models.CharField(max_length=64, unique=True, default=_generate_token)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner = self.shared_by.username if self.shared_by else '?'
        return f'{owner} → {self.song.title} ({self.token})'
