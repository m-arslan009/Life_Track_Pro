from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.taskListCreate, name='task-list-create'),
    path('tasks/<int:pk>/', views.taskDetail, name='task-detail'),
    path('tasks/<int:pk>/status/', views.taskStatusUpdate, name='task-status-update'),
]
