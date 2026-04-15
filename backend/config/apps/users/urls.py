from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('', views.signup_user, name='signup-user'),
    path('<int:pk>/', views.user_detail, name='user-detail'),
    path('login/', views.user_login, name='user-login'),
    path('users/', views.getUsers, name='get-users'),
    path('me/', views.current_user, name='current-user'),
]