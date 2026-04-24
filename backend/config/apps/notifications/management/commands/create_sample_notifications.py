from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification
from projects.models import Projects
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample notifications for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="Username to create notifications for",
        )

    def handle(self, *args, **options):
        username = options["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User '{username}' does not exist")
            )
            return

        sample_notifications = [
            {
                "notification_type": "project_created",
                "title": "New Project Created",
                "message": "Your new project has been successfully created and is ready to use.",
                "project_name": "Q1 Marketing Campaign",
            },
            {
                "notification_type": "task_assigned",
                "title": "Task Assigned to You",
                "message": "You have been assigned a new task that requires your attention.",
                "task_name": "Design landing page mockups",
                "project_name": "Q1 Marketing Campaign",
            },
            {
                "notification_type": "milestone_completed",
                "title": "Milestone Completed",
                "message": "A key milestone has been completed successfully!",
                "milestone_name": "Phase 1: Planning Complete",
                "project_name": "Q1 Marketing Campaign",
            },
            {
                "notification_type": "project_at_risk",
                "title": "Project Status Alert",
                "message": "Your project is marked as at risk. Please review and take necessary actions.",
                "project_name": "Website Redesign",
            },
            {
                "notification_type": "task_blocked",
                "title": "Task Blocked",
                "message": "A task has been marked as blocked and requires immediate attention.",
                "task_name": "Backend API Integration",
                "project_name": "Mobile App Development",
            },
            {
                "notification_type": "team_member_added",
                "title": "Team Member Added",
                "message": "A new team member has been added to your project.",
                "project_name": "Q1 Marketing Campaign",
            },
            {
                "notification_type": "project_completed",
                "title": "Project Completed",
                "message": "Congratulations! Your project has been completed successfully.",
                "project_name": "Q1 Marketing Campaign",
            },
        ]

        for i, notif_data in enumerate(sample_notifications):
            created_at = timezone.now() - timedelta(hours=i * 2)
            is_read = i > 3  # First 3 are unread

            notification = Notification.objects.create(
                user=user,
                notification_type=notif_data["notification_type"],
                title=notif_data["title"],
                message=notif_data["message"],
                project_name=notif_data.get("project_name"),
                task_name=notif_data.get("task_name"),
                milestone_name=notif_data.get("milestone_name"),
                is_read=is_read,
                created_at=created_at,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(sample_notifications)} sample notifications for user '{username}'"
            )
        )
