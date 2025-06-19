from django.contrib import admin
from .models import Document, Chapter, Section, Content

class ContentInline(admin.TabularInline):
    model = Content
    extra = 0
    
class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    
class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'upload_date')
    search_fields = ('title', 'author', 'description')
    inlines = [ChapterInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('document', 'number', 'title')
    list_filter = ('document',)
    search_fields = ('title', 'document__title')
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'number', 'title')
    list_filter = ('chapter__document', 'chapter')
    search_fields = ('title', 'chapter__title')
    inlines = [ContentInline]

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('get_parent', 'content_type', 'page_number', 'position_order')
    list_filter = ('content_type',)
    
    def get_parent(self, obj):
        return obj.section if obj.section else obj.chapter
    get_parent.short_description = 'Parent'
