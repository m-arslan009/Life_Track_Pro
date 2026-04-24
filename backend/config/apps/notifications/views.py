from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from .serializers import NotificationSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getNotifications(request):
    """Get all notifications for the current user with filters"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Optional filter by read status
    is_read = request.query_params.get("is_read", None)
    if is_read is not None:
        is_read_bool = is_read.lower() == "true"
        notifications = notifications.filter(is_read=is_read_bool)
    
    # Optional filter by notification type
    notification_type = request.query_params.get("type", None)
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    serializer = NotificationSerializer(notifications, many=True)
    
    # Get summary stats
    total_notifications = Notification.objects.filter(user=request.user).count()
    unread_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()
    
    return Response(
        {
            "notifications": serializer.data,
            "total_count": total_notifications,
            "unread_count": unread_count,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def markAsRead(request, notification_id):
    """Mark a single notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id, user=request.user
        )
        notification.is_read = True
        notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response(
            {"error": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def markAllAsRead(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True
    )
    
    unread_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()
    
    return Response(
        {"message": "All notifications marked as read", "unread_count": unread_count},
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteNotification(request, notification_id):
    """Delete a specific notification"""
    try:
        notification = Notification.objects.get(
            id=notification_id, user=request.user
        )
        notification.delete()
        return Response(
            {"message": "Notification deleted successfully"},
            status=status.HTTP_200_OK,
        )
    except Notification.DoesNotExist:
        return Response(
            {"error": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deleteAllNotifications(request):
    """Delete all notifications for the current user"""
    Notification.objects.filter(user=request.user).delete()
    
    return Response(
        {"message": "All notifications deleted successfully"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getRecentNotifications(request):
    """Get recent notifications (last 24 hours) for quick view"""
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    notifications = Notification.objects.filter(
        user=request.user, created_at__gte=twenty_four_hours_ago
    )[:10]
    
    serializer = NotificationSerializer(notifications, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
