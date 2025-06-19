from django.db import models
import uuid
from django.utils import timezone

class Document(models.Model):
    """Model for storing PDF document metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='documents/')
    upload_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Chapter(models.Model):
    """Model for storing chapters from a document"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    number = models.IntegerField()
    
    class Meta:
        ordering = ['number']
        
    def __str__(self):
        return f"{self.document.title} - Chapter {self.number}: {self.title}"

class Section(models.Model):
    """Model for storing sections within chapters"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    number = models.IntegerField()
    
    class Meta:
        ordering = ['number']
        
    def __str__(self):
        return f"{self.chapter.document.title} - Chapter {self.chapter.number} - Section {self.number}: {self.title}"

class Content(models.Model):
    """Model for storing actual content from the PDF"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='contents', null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='direct_contents', null=True, blank=True)
    content_type = models.CharField(max_length=50, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('table', 'Table'),
        ('code', 'Code Block'),
        ('formula', 'Mathematical Formula')
    ])
    text_content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='content_images/', blank=True, null=True)
    page_number = models.IntegerField()
    position_order = models.IntegerField()  # For ordering content within a section
    
    class Meta:
        ordering = ['page_number', 'position_order']
        
    def __str__(self):
        parent = self.section if self.section else self.chapter
        parent_name = f"Section {self.section.number}" if self.section else f"Chapter {self.chapter.number}"
        return f"{parent.title} - {self.content_type} content at page {self.page_number}"
