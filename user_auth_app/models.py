import datetime
from django.contrib.auth.models import User
from django.db import models

class BusinessPartner(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  file = models.FileField(upload_to='uploads/', null=True, blank=True)
  location = models.CharField(max_length=255, blank=True)
  tel = models.CharField(max_length=20, blank=True)
  description = models.TextField(blank=True)
  working_hours = models.CharField(max_length=255, blank=True)
  type = models.CharField(default='business', editable=False, max_length=10)
  email = models.EmailField(null=True, blank=True)
  created_at = models.DateTimeField(default=datetime.datetime.now)

  def save(self, *args, **kwargs):
        if not self.id and self.user:
            self.id = self.user.id
        super().save(*args, **kwargs)
        
class Customer(models.Model):    
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  file = models.FileField(upload_to='uploads/', null=True, blank=True)
  uploaded_at = models.DateTimeField(auto_now_add=True)
  type = models.CharField(default='customer', editable=False, max_length=10)
  
  def save(self, *args, **kwargs):
        if not self.id and self.user:
            self.id = self.user.id
        super().save(*args, **kwargs)