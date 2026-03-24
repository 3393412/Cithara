from django.urls import path, include
from rest_framework.routers import DefaultRouter


from django.urls import path
from . import views

urlpatterns = [
    path('songs/', views.songs_api, name='get_songs'),
]