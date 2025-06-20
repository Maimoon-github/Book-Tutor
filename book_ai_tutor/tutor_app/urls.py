from django.urls import path
from . import views

urlpatterns = [
    # Legacy URLs for backward compatibility
    path('', views.upload_book, name='upload_book'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    
    # New structured content URLs
    path('textbook/upload/', views.TextbookUploadView.as_view(), name='textbook_upload'),
    path('textbook/<int:pk>/', views.TextbookDetailView.as_view(), name='textbook_detail'),
    
    # API endpoints for structured content
    path('api/textbooks/', views.api_textbook_list, name='api_textbook_list'),
    path('api/textbooks/<int:textbook_id>/content/', views.api_textbook_content, name='api_textbook_content'),
    path('api/textbooks/<int:textbook_id>/chapters/', views.api_textbook_chapters, name='api_textbook_chapters'),
    path('api/textbooks/<int:textbook_id>/questions/', views.api_textbook_questions, name='api_textbook_questions'),
    path('api/textbooks/<int:textbook_id>/status/', views.api_processing_status, name='api_processing_status'),
    path('api/textbooks/<int:textbook_id>/reprocess/', views.api_reprocess_textbook, name='api_reprocess_textbook'),
    
    # Search and filter endpoints
    path('api/search/', views.api_search_content, name='api_search_content'),
]
