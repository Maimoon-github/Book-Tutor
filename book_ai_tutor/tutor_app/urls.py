from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, ChapterViewSet, SectionViewSet, ContentViewSet,
    home_view, document_detail_view
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'contents', ContentViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
    path('document/<uuid:document_id>/', document_detail_view, name='document_detail'),
    path('', home_view, name='home'),
]
