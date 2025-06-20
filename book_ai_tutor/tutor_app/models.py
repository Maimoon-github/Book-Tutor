from django.db import models
from django.contrib.postgres.fields import ArrayField
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
import hashlib

class Textbook(models.Model):
    """Main textbook model with metadata and processing status"""
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='textbooks/')
    upload_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_pages = models.PositiveIntegerField(default=0)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed')
        ],
        default='PENDING'
    )
    file_hash = models.CharField(max_length=64, unique=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['-upload_date']
    
    def save(self, *args, **kwargs):
        if self.pdf_file and not self.file_hash:
            # Generate hash for deduplication
            self.pdf_file.seek(0)
            file_hash = hashlib.sha256(self.pdf_file.read()).hexdigest()
            self.file_hash = file_hash
            self.pdf_file.seek(0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title or f"Textbook {self.id}"

class Chapter(models.Model):
    """Chapter organization within textbook"""
    textbook = models.ForeignKey(Textbook, related_name='chapters', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    start_page = models.PositiveIntegerField()
    end_page = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('textbook', 'number')
        ordering = ['number']
    
    def __str__(self):
        return f"Chapter {self.number}: {self.title}"

class TextbookSection(models.Model):
    """Structured content sections with type classification"""
    SECTION_TYPES = [
        ('RM', 'Reading Material'),
        ('EX', 'Exercise'),
        ('PP', 'Point to Ponder'),
        ('TN', 'Teacher Note'),
        ('PRE', 'Pre-Reading'),
        ('POST', 'Post-Reading'),
        ('IN', 'In-Text')
    ]
    
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='sections')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sections', null=True, blank=True)
    section_type = models.CharField(max_length=4, choices=SECTION_TYPES)
    title = models.CharField(max_length=255, blank=True)
    page_number = models.PositiveIntegerField()
    content = models.TextField()
    content_hash = models.CharField(max_length=64, blank=True)  # For deduplication
    position_on_page = models.JSONField(default=dict)  # Store x, y, width, height
    extracted_at = models.DateTimeField(auto_now_add=True)
    
    # Hierarchical structure
    parent_section = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    order_in_page = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['page_number', 'order_in_page']
        indexes = [
            models.Index(fields=['textbook', 'section_type']),
            models.Index(fields=['page_number']),
            models.Index(fields=['content_hash']),
        ]
    
    def save(self, *args, **kwargs):
        if self.content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_section_type_display()} - Page {self.page_number}"

class Question(models.Model):
    """Questions extracted from textbook sections"""
    QUESTION_TYPES = [
        ('PRE', 'Pre-Reading'),
        ('POST', 'Post-Reading'),
        ('IN', 'In-Text'),
        ('MCQ', 'Multiple Choice'),
        ('SA', 'Short Answer'),
        ('LA', 'Long Answer'),
        ('TF', 'True/False')
    ]
    
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='questions')
    section = models.ForeignKey(TextbookSection, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question_text = models.TextField()
    question_type = models.CharField(max_length=4, choices=QUESTION_TYPES)
    options = models.JSONField(null=True, blank=True)  # For MCQ options
    correct_answer = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    difficulty_level = models.CharField(
        max_length=10,
        choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')],
        default='MEDIUM'
    )
    page_number = models.PositiveIntegerField()
    order_in_section = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['page_number', 'order_in_section']
        indexes = [
            models.Index(fields=['textbook', 'question_type']),
            models.Index(fields=['page_number']),
        ]
    
    def __str__(self):
        return f"{self.get_question_type_display()}: {self.question_text[:50]}..."

class VectorIndex(models.Model):
    """Vector store index references for RAG integration"""
    textbook = models.OneToOneField(Textbook, on_delete=models.CASCADE, related_name='vector_index')
    index_file_path = models.CharField(max_length=500)
    embedding_model = models.CharField(max_length=100, default='text-embedding-ada-002')
    chunk_size = models.PositiveIntegerField(default=1000)
    chunk_overlap = models.PositiveIntegerField(default=200)
    total_chunks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Vector Index for {self.textbook.title}"

class ProcessingLog(models.Model):
    """Log processing activities and errors"""
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='processing_logs')
    stage = models.CharField(max_length=50)  # 'extraction', 'embedding', 'indexing'
    status = models.CharField(
        max_length=20,
        choices=[('SUCCESS', 'Success'), ('ERROR', 'Error'), ('WARNING', 'Warning')]
    )
    message = models.TextField()
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.stage} - {self.status} - {self.timestamp}"

# Legacy models for backward compatibility
class Book(models.Model):
    """Legacy model - kept for backward compatibility"""
    pdf = models.FileField(upload_to='pdfs/')
    content = models.TextField(blank=True)
    
    # Link to new model
    textbook = models.OneToOneField(Textbook, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.pdf.name

class Lesson(models.Model):
    """Legacy model - mapped to TextbookSection"""
    chapter = models.ForeignKey(Chapter, related_name='lessons', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    
    # Link to new model
    textbook_section = models.OneToOneField(TextbookSection, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('chapter', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Lesson {self.number}: {self.title}"
