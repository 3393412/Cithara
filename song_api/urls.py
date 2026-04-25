from django.urls import path
from . import views
urlpatterns = [path('songs/', views.songs_api, name='get_songs'), path('songs/<int:song_id>/download/', views.download_song, name='download_song'), path('generate/', views.generate_song, name='generate_song'), path('generate/<int:job_id>/status/', views.generation_status, name='generation_status')]
