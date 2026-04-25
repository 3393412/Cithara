from django.urls import path
from . import views
urlpatterns = [path('login/', views.login_view, name='auth_login'), path('callback/', views.callback_view, name='auth_callback'), path('logout/', views.logout_view, name='auth_logout'), path('me/', views.me_view, name='auth_me'), path('tour-complete/', views.tour_complete_view, name='auth_tour_complete')]
