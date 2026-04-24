from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("project_created", "Project Created"),
        ("project_updated", "Project Updated"),
        ("project_completed", "Project Completed"),
        ("milestone_created", "Milestone Created"),
        ("milestone_completed", "Milestone Completed"),
        ("task_assigned", "Task Assigned"),
        ("task_completed", "Task Completed"),
        ("task_blocked", "Task Blocked"),
        ("team_member_added", "Team Member Added"),
        ("project_at_risk", "Project At Risk"),
        ("project_overdue", "Project Overdue"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    project_id = models.IntegerField(null=True, blank=True)
    project_name = models.CharField(max_length=100, null=True, blank=True)
    task_id = models.IntegerField(null=True, blank=True)
    task_name = models.CharField(max_length=120, null=True, blank=True)
    milestone_id = models.IntegerField(null=True, blank=True)
    milestone_name = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
