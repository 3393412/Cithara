from django.db import models
from users.models import User

class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    duration = models.IntegerField()
    occasion = models.CharField(max_length=255)
    prompt = models.TextField()
    story = models.TextField()
    vocal = models.CharField(max_length=20)
    mood = models.CharField(max_length=100)
    path = models.FileField(upload_to='audio/', blank=True)
    audio_url = models.URLField(blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

class GenerationJob(models.Model):
    """Track one generation request through its lifecycle.

    สำหรับ mock → จบที่ SUCCESS ทันที
    สำหรับ suno → เริ่มที่ PENDING แล้วค่อย ๆ ขยับถึง SUCCESS ผ่าน poll
    """
    STATUS_PENDING = 'PENDING'
    STATUS_TEXT_SUCCESS = 'TEXT_SUCCESS'
    STATUS_FIRST_SUCCESS = 'FIRST_SUCCESS'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_FAILED = 'FAILED'
    STATUS_CHOICES = [(STATUS_PENDING, 'Pending'), (STATUS_TEXT_SUCCESS, 'Text success'), (STATUS_FIRST_SUCCESS, 'First success'), (STATUS_SUCCESS, 'Success'), (STATUS_FAILED, 'Failed')]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    provider = models.CharField(max_length=20)
    task_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    prompt = models.TextField()
    title = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=64, blank=True)
    mood = models.CharField(max_length=64, blank=True)
    vocal = models.CharField(max_length=64, blank=True)
    occasion = models.CharField(max_length=64, blank=True)
    story = models.TextField(blank=True)
    audio_url = models.URLField(blank=True)
    song = models.ForeignKey('Song', on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    error_message = models.TextField(blank=True)
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.provider}] {self.status} · {self.task_id or '(no task)'}"
