from django.contrib import admin
from .models import Business

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'location', 'created_at')
    search_fields = ('name', 'owner__email', 'location')
    list_filter = ('category', 'tone')
