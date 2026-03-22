from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=20,choices=[('manager', 'Manager'), ('developer', 'Developer'), ('viewer', 'Viewer')], default='developer')
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    account_status = models.CharField(max_length=30, choices=[('active', 'Active'), ('suspended', 'Suspended')], default='active')