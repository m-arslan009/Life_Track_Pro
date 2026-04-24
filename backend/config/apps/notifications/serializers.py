from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "project_id",
            "project_name",
            "task_id",
            "task_name",
            "milestone_id",
            "milestone_name",
            "created_at",
            "is_read",
            "time_ago",
        ]
    
    def get_time_ago(self, obj):
        """Return human-readable time difference"""
        from django.utils import timezone
        from datetime import timedelta

        created_at = obj.created_at
        if timezone.is_naive(created_at):
            created_at = timezone.make_aware(
                created_at,
                timezone.get_current_timezone(),
            )

        diff = timezone.now() - created_at
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = int(diff.total_seconds() / 86400)
            return f"{days}d ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")
