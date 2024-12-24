import datetime
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  username = models.CharField(max_length=255, null=True, blank=True)
  first_name = models.CharField(max_length=255, null=True, blank=True)
  last_name = models.CharField(max_length=255, null=True, blank=True)
  file = models.FileField(upload_to='uploads/', null=True, blank=True)
  location = models.CharField(max_length=255, blank=True)
  tel = models.CharField(max_length=20, blank=True)
  description = models.TextField(blank=True)
  working_hours = models.CharField(max_length=255, blank=True)
  user_type = models.CharField(max_length=20, choices=[('business', 'Business'), ('individual', 'Individual')], default='individual')
  email = email = models.EmailField(null=True, blank=True)
  created_at = models.DateTimeField(default=datetime.datetime.now)

  def __str__(self):
    return f"{self.username} - {self.email}"