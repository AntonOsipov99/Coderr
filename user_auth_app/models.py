import datetime
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
  id = models.BigAutoField(primary_key=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  username = models.CharField(max_length=255, null=True, blank=True)
  first_name = models.CharField(max_length=255, null=True, blank=True)
  last_name = models.CharField(max_length=255, null=True, blank=True)
  file = models.FileField(upload_to='uploads/', null=True, blank=True)
  location = models.CharField(max_length=255, blank=True)
  tel = models.CharField(max_length=20, blank=True)
  description = models.TextField(blank=True)
  working_hours = models.CharField(max_length=255, blank=True)
  type = models.CharField(max_length=20, choices=[('business', 'Business'), ('customer', 'Customer')])
  email = email = models.EmailField(null=True, blank=True)
  created_at = models.DateTimeField(default=datetime.datetime.now)

  def save(self, *args, **kwargs):
        if not self.id and self.user:
            self.id = self.user.id
        super().save(*args, **kwargs)