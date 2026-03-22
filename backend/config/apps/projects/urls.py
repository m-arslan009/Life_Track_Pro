from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createProject, name='create-project'),
    path('projects/', views.getAllProjects, name='get_all_projects'),
    path('<int:pk>/', views.projectDetail, name='project-detail'),
]
