from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Textbook, Chapter, TextbookSection, Question, 
    VectorIndex, ProcessingLog, Book, Lesson
)

@admin.register(Textbook)
class TextbookAdmin(admin.ModelAdmin):
    list_display = ['title', 'processing_status', 'total_pages', 'upload_date', 'file_size']
    list_filter = ['processing_status', 'upload_date']
    search_fields = ['title', 'file_hash']
    readonly_fields = ['file_hash', 'upload_date', 'last_updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'pdf_file', 'processing_status')
        }),
        ('Processing Details', {
            'fields': ('total_pages', 'version', 'file_hash'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('upload_date', 'last_updated'),
            'classes': ('collapse',)
        })
    )
    
    def file_size(self, obj):
        if obj.pdf_file:
            try:
                size = obj.pdf_file.size
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except:
                return "Unknown"
        return "No file"
    file_size.short_description = "File Size"

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['textbook', 'number', 'title', 'start_page', 'end_page', 'sections_count']
    list_filter = ['textbook']
    search_fields = ['title', 'textbook__title']
    ordering = ['textbook', 'number']
    
    def sections_count(self, obj):
        return obj.sections.count()
    sections_count.short_description = "Sections"

@admin.register(TextbookSection)
class TextbookSectionAdmin(admin.ModelAdmin):
    list_display = ['textbook', 'section_type', 'title_preview', 'page_number', 'chapter', 'extracted_at']
    list_filter = ['section_type', 'textbook', 'extracted_at']
    search_fields = ['title', 'content', 'textbook__title']
    readonly_fields = ['content_hash', 'extracted_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('textbook', 'chapter', 'section_type', 'title')
        }),
        ('Content', {
            'fields': ('page_number', 'content', 'order_in_page')
        }),
        ('Position & Metadata', {
            'fields': ('position_on_page', 'parent_section', 'content_hash', 'extracted_at'),
            'classes': ('collapse',)
        })
    )
    
    def title_preview(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_preview.short_description = "Title"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['textbook', 'question_type', 'question_preview', 'difficulty_level', 'page_number', 'section']
    list_filter = ['question_type', 'difficulty_level', 'textbook']
    search_fields = ['question_text', 'textbook__title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('textbook', 'section', 'question_type', 'difficulty_level')
        }),
        ('Question Content', {
            'fields': ('question_text', 'options', 'correct_answer', 'explanation')
        }),
        ('Position', {
            'fields': ('page_number', 'order_in_section'),
            'classes': ('collapse',)
        })
    )
    
    def question_preview(self, obj):
        return obj.question_text[:100] + "..." if len(obj.question_text) > 100 else obj.question_text
    question_preview.short_description = "Question"

@admin.register(VectorIndex)
class VectorIndexAdmin(admin.ModelAdmin):
    list_display = ['textbook', 'embedding_model', 'total_chunks', 'chunk_size', 'created_at']
    list_filter = ['embedding_model', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('textbook', 'embedding_model', 'chunk_size', 'chunk_overlap')
        }),
        ('Index Details', {
            'fields': ('index_file_path', 'total_chunks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = ['textbook', 'stage', 'status', 'message_preview', 'timestamp']
    list_filter = ['stage', 'status', 'timestamp']
    search_fields = ['message', 'textbook__title']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Log Entry', {
            'fields': ('textbook', 'stage', 'status', 'message')
        }),
        ('Details', {
            'fields': ('details', 'timestamp'),
            'classes': ('collapse',)
        })
    )
    
    def message_preview(self, obj):
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message
    message_preview.short_description = "Message"

# Legacy model admin (for backward compatibility)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['pdf', 'textbook_link', 'content_preview']
    search_fields = ['pdf', 'content']
    
    def textbook_link(self, obj):
        if obj.textbook:
            url = reverse('admin:tutor_app_textbook_change', args=[obj.textbook.id])
            return format_html('<a href="{}">{}</a>', url, obj.textbook.title)
        return "No linked textbook"
    textbook_link.short_description = "Linked Textbook"
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content Preview"

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'number', 'title', 'textbook_section_link']
    list_filter = ['chapter__textbook']
    search_fields = ['title', 'content']
    
    def textbook_section_link(self, obj):
        if obj.textbook_section:
            url = reverse('admin:tutor_app_textbooksection_change', args=[obj.textbook_section.id])
            return format_html('<a href="{}">{}</a>', url, "View Section")
        return "No linked section"
    textbook_section_link.short_description = "Linked Section"

# Custom admin site configuration
admin.site.site_header = "Book AI Tutor Administration"
admin.site.site_title = "Book AI Tutor Admin"
admin.site.index_title = "Welcome to Book AI Tutor Administration"
