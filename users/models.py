from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(blank=True)
    tour_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.username
