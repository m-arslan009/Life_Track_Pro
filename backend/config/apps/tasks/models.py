from django.db import models
from config.apps.projects.models import Projects, TeamMembers
from config.apps.milestones.models import Milestone


class Task(models.Model):
    STATUS_TODO = "todo"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_BLOCKED = "blocked"

    STATUS_CHOICES = [
        (STATUS_TODO, "To Do"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
        (STATUS_BLOCKED, "Blocked"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TODO,
    )
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    assignee = models.ForeignKey(
        TeamMembers,
        on_delete=models.SET_NULL,
        related_name="tasks",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.title} [{self.status}]"
