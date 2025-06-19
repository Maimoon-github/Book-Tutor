from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

import os
import tempfile
import io
import PyPDF2
from PIL import Image

from .models import Document, Chapter, Section, Content
from .services import PDFContentExtractor
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    ChapterSerializer,
    SectionSerializer,
    ContentSerializer
)

def home_view(request):
    """Home page view with document list and upload form"""
    documents = Document.objects.all().order_by('-upload_date')
    return render(request, 'tutor_app/home.html', {'documents': documents})

def document_detail_view(request, document_id):
    """Document detail view"""
    try:
        document = Document.objects.get(id=document_id)
        return render(request, 'tutor_app/document_preview.html', {'document': document})
    except Document.DoesNotExist:
        return render(request, 'tutor_app/404.html', status=404)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentSerializer
    
    @action(detail=True, methods=['post'], url_path='extract-content')
    def extract_content(self, request, pk=None):
        """Extract content from the PDF and store it in the database"""
        document = self.get_object()
        
        try:
            # Use the advanced content extractor
            extractor = PDFContentExtractor(document)
            result = extractor.extract_all_content()
            
            if result['status'] == 'success':
                return Response({
                    "message": result['message'],
                    "pages_processed": result['pages_processed']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='preview')
    def preview(self, request, pk=None):
        """Generate a preview of the document content"""
        document = self.get_object()
        
        # Check if HTML view is requested vs API response
        format_param = request.query_params.get('format', None)
        
        if format_param == 'html':
            return render(request, 'tutor_app/document_preview.html', {'document': document})
        
        # Default to API response
        serializer = self.get_serializer(document)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    
    def get_queryset(self):
        queryset = Chapter.objects.all()
        document_id = self.request.query_params.get('document', None)
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        return queryset


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    
    def get_queryset(self):
        queryset = Section.objects.all()
        chapter_id = self.request.query_params.get('chapter', None)
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        return queryset


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    
    def get_queryset(self):
        queryset = Content.objects.all()
        section_id = self.request.query_params.get('section', None)
        chapter_id = self.request.query_params.get('chapter', None)
        
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        elif chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
            
        return queryset
