from django.urls import path
from . import views

urlpatterns = [
    path("share/", views.create_share_link),                
    path("share/<str:token>/", views.get_share_link),       
    path("share/delete/<str:token>/", views.delete_share_link),  
]