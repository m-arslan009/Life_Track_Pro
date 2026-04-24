from django.urls import path
from . import views

urlpatterns = [
    path("", views.getNotifications, name="notifications-list"),
    path("recent/", views.getRecentNotifications, name="notifications-recent"),
    path("mark-as-read/<int:notification_id>/", views.markAsRead, name="notification-mark-read"),
    path("mark-all-as-read/", views.markAllAsRead, name="notifications-mark-all-read"),
    path("delete/<int:notification_id>/", views.deleteNotification, name="notification-delete"),
    path("delete-all/", views.deleteAllNotifications, name="notifications-delete-all"),
]
