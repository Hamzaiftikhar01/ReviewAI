from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from businesses.models import Business

class Review(models.Model):
    SOURCE_CHOICES = [
        ('Manual', 'Manual'),
        ('CSV Import', 'CSV Import'),
        ('Google', 'Google'),
        ('Other', 'Other'),
    ]

    SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
        ('Pending', 'Pending'),
    ]

    STATUS_CHOICES = [
        ('Unanalyzed', 'Unanalyzed'),
        ('Analyzed', 'Analyzed'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='Manual')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='Pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unanalyzed')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'created_at']),
            models.Index(fields=['business', 'sentiment']),
            models.Index(fields=['business', 'status']),
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.rating}★"


class ReviewAnalysis(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='analysis')
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField(default=1.0)
    issues = models.JSONField(default=list, blank=True)
    positive_aspects = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Review ID {self.review.id} ({self.sentiment})"


class AIReply(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='ai_reply')
    reply_text = models.TextField()
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Reply for Review ID {self.review.id}"
