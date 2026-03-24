from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    duration = models.IntegerField()
    
    occasion = models.CharField(max_length = 255)
    prompt = models.TextField()
    story = models.TextField()
    vocal = models.CharField(max_length=20)
    mood = models.CharField(max_length=100)

    path = models.FileField(upload_to='audio/')

    create_at = models.DateTimeField(auto_now_add=True)