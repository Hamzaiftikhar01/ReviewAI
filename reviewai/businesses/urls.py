from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.business_setup_view, name='business_setup'),
    path('settings/', views.business_settings_view, name='business_settings'),
]
