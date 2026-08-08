from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_view, name='analytics_view'),
    path('insights/', views.ai_insights_view, name='ai_insights_view'),
]
