from rest_framework import serializers
from .models import Document, Chapter, Section, Content

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'content_type', 'text_content', 'image', 'page_number', 'position_order']

class SectionSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'title', 'number', 'contents']

class ChapterSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    direct_contents = ContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'number', 'sections', 'direct_contents']

class DocumentSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'author', 'description', 'pdf_file', 'upload_date', 'chapters']

class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'author', 'description', 'pdf_file']
