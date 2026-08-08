from django.urls import path
from . import views

urlpatterns = [
    path('', views.reviews_list, name='reviews_list'),
    path('create/', views.review_create, name='review_create'),
    path('<int:pk>/', views.review_detail, name='review_detail'),
    path('<int:pk>/analyze/', views.review_analyze_ai, name='review_analyze_ai'),
    path('<int:pk>/reply/generate/', views.review_generate_reply_ai, name='review_generate_reply_ai'),
    path('<int:pk>/reply/save/', views.review_save_reply, name='review_save_reply'),
    path('<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('import/csv/', views.csv_import_upload, name='csv_upload'),
    path('import/csv/confirm/', views.csv_import_confirm, name='csv_confirm'),
]
