from django.urls import path
from . import views
urlpatterns = [path('share/', views.create_share_link), path('share/<str:token>/', views.get_share_link), path('share/<str:token>/download/', views.download_shared_song), path('share/<str:token>/deactivate/', views.deactivate_share_link)]
