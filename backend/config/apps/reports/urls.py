from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.reportsOverview, name='reports-overview'),
]
