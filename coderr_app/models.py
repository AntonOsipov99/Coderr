from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
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
    image = models.FileField(upload_to='uploads/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_delivery_time = models.IntegerField()

    def clean(self):
        details = self.details.all()
        if len(details) != 3:
            raise ValidationError("Exactly three offer details are required.")
        
        types = set(detail.offer_type for detail in details)
        required_types = {'basic', 'standard', 'premium'}
        if types != required_types:
            raise ValidationError("Exactly one detail of each type (basic, standard, premium) is required.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class OfferDetail(models.Model):
    TYPES = (
    ('basic', 'Basic'),
    ('standard', 'Standard'),
    ('premium', 'Premium')
    )
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details', null=True, blank=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPES, null=True, blank=True)
    revisions = models.IntegerField(default=-1)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    class Meta:
        unique_together = ['offer', 'type']
        ordering = ['price']

    def clean(self):
        # Validierung der Revisionen
        if self.revisions < -1:
            raise ValidationError("Revisions must be -1 (unlimited) or a positive number.")
            
        # Validierung der Features
        if not self.features or len(self.features) == 0:
            raise ValidationError("At least one feature must be specified.")

        # Validierung der Lieferzeit
        if self.delivery_time_in_days < 1:
            raise ValidationError("Delivery time must be a positive number.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.offer.title} - {self.type}"
    
class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)