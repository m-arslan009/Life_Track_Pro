from django.db import models
from config.apps.projects.models import Projects, TeamMembers


class Milestone(models.Model):
    STATUS_PLANNED = "planned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_DELAYED = "delayed"

    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_DELAYED, "Delayed"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
    )
   
    start_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    members = models.ManyToManyField(
        TeamMembers,
        related_name="milestones",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "id"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"