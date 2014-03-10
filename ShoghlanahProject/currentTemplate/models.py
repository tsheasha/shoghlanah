from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class UserActivity(models.Model):
    current_template = models.TextField(max_length=256, null=True, blank=True)
    latest_activity = models.DateTimeField(default = datetime(2000, 1, 1))
    user = models.OneToOneField(User)
