from django.db import models
from django.conf import settings

class Business(models.Model):
    CATEGORY_CHOICES = [
        ('Restaurant', 'Restaurant'),
        ('Hotel', 'Hotel'),
        ('E-commerce', 'E-commerce'),
        ('Retail', 'Retail'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Services', 'Services'),
        ('Other', 'Other'),
    ]

    TONE_CHOICES = [
        ('Professional', 'Professional'),
        ('Friendly', 'Friendly'),
        ('Warm', 'Warm'),
        ('Formal', 'Formal'),
        ('Casual', 'Casual'),
    ]

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    tone = models.CharField(max_length=50, choices=TONE_CHOICES, default='Professional')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
