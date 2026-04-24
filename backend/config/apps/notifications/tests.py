from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Notification

User = get_user_model()


class NotificationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_get_notifications_empty(self):
        """Test getting notifications when none exist"""
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_count"], 0)
        self.assertEqual(response.data["unread_count"], 0)
        self.assertEqual(len(response.data["notifications"]), 0)

    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type="project_created",
            title="Test Project Created",
            message="A new test project has been created",
            project_name="Test Project",
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.notification_type, "project_created")
        self.assertFalse(notification.is_read)

    def test_get_notifications_with_data(self):
        """Test getting notifications with data"""
        Notification.objects.create(
            user=self.user,
            notification_type="project_created",
            title="Test Project Created",
            message="A new test project has been created",
            project_name="Test Project",
        )
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_count"], 1)
        self.assertEqual(response.data["unread_count"], 1)
        self.assertEqual(len(response.data["notifications"]), 1)

    def test_mark_as_read(self):
        """Test marking a notification as read"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type="project_created",
            title="Test Project Created",
            message="A new test project has been created",
            project_name="Test Project",
        )
        response = self.client.post(
            f"/api/notifications/mark-as-read/{notification.id}/"
        )
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_as_read(self):
        """Test marking all notifications as read"""
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                notification_type="project_created",
                title=f"Test Project {i}",
                message=f"Test message {i}",
            )
        response = self.client.post("/api/notifications/mark-all-as-read/")
        self.assertEqual(response.status_code, 200)
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_delete_notification(self):
        """Test deleting a notification"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type="project_created",
            title="Test Project Created",
            message="A new test project has been created",
        )
        response = self.client.delete(
            f"/api/notifications/delete/{notification.id}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Notification.objects.filter(id=notification.id).exists())

    def test_delete_all_notifications(self):
        """Test deleting all notifications"""
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                notification_type="project_created",
                title=f"Test Project {i}",
                message=f"Test message {i}",
            )
        response = self.client.post("/api/notifications/delete-all/")
        self.assertEqual(response.status_code, 200)
        count = Notification.objects.filter(user=self.user).count()
        self.assertEqual(count, 0)

    def test_filter_unread_notifications(self):
        """Test filtering unread notifications"""
        notif1 = Notification.objects.create(
            user=self.user,
            notification_type="project_created",
            title="Test 1",
            message="Message 1",
        )
        notif2 = Notification.objects.create(
            user=self.user,
            notification_type="project_created",
            title="Test 2",
            message="Message 2",
            is_read=True,
        )
        response = self.client.get("/api/notifications/?is_read=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["notifications"]), 1)
