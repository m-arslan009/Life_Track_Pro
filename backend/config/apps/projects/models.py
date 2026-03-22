from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Projects(models.Model):
    project_name = models.CharField(max_length=100)
    project_description = models.TextField()
    status = models.CharField(max_length=15, choices=[('active', 'Active'), ('on_track', "On_Track"), ('at_risk', "At_Risk"), ('complete', 'Complete')])
    progress = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    start_date = models.DateField()
    due_date = models.DateField()
    owner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_projects")

class TeamMembers(models.Model):
    Projects = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="teamMembers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

