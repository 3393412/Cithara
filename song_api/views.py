from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Song
from .serializers import SongSerializer

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer