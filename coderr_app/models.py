from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_as_business_user')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_as_reviewer')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.id} for {self.business_user}"

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to='uploads/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_delivery_time = models.IntegerField()
    details = models.ManyToManyField('OfferDetail', related_name='offers')

    def __str__(self):
        return self.title
    
class OfferDetail(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='detail')
    title = models.CharField(max_length=200)
    revisions = models.IntegerField(default=-1)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=20, choices=[
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ], default='basic')