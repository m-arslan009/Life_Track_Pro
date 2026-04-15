from django.urls import path
from . import views

urlpatterns = [
    path('milestones/', views.milestoneListCreate, name='milestone-list-create'),
    path('create/', views.milestoneListCreate, name='milestone-create'),
    path('<int:pk>/', views.milestoneDetail, name='milestone-detail'),
    path('<int:pk>/status/', views.milestoneStatusUpdate, name='milestone-status-update'),
]
