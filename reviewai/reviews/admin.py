from django.contrib import admin
from .models import Review, ReviewAnalysis, AIReply

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'business', 'rating', 'sentiment', 'status', 'created_at')
    list_filter = ('rating', 'sentiment', 'status', 'source')
    search_fields = ('customer_name', 'review_text', 'business__name')

@admin.register(ReviewAnalysis)
class ReviewAnalysisAdmin(admin.ModelAdmin):
    list_display = ('review', 'sentiment', 'confidence', 'created_at')
    list_filter = ('sentiment',)

@admin.register(AIReply)
class AIReplyAdmin(admin.ModelAdmin):
    list_display = ('review', 'is_saved', 'created_at')
    list_filter = ('is_saved',)
