from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import json
import time
import logging

from .forms import BookUploadForm
from .models import (
    Book, Textbook, Chapter, TextbookSection, Question, 
    ProcessingLog, VectorIndex
)
from .tasks import queue_textbook_processing, get_processing_status

logger = logging.getLogger(__name__)

# Legacy views for backward compatibility
def upload_book(request):
    """Legacy upload view - redirects to new textbook upload"""
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create new Textbook instance
            textbook = Textbook.objects.create(
                title=request.FILES['pdf'].name,
                pdf_file=request.FILES['pdf']
            )
            
            # Create legacy Book instance for compatibility
            book = form.save(commit=False)
            book.textbook = textbook
            book.save()
            
            # Queue processing
            queue_textbook_processing(textbook.id)
            
            return redirect('textbook_detail', pk=textbook.pk)
    else:
        form = BookUploadForm()
    return render(request, 'upload.html', {'form': form})

def book_detail(request, pk):
    """Legacy book detail view"""
    book = get_object_or_404(Book, pk=pk)
    if book.textbook:
        return redirect('textbook_detail', pk=book.textbook.pk)
    return render(request, 'detail.html', {'book': book})

# New structured content views

class TextbookUploadView(View):
    """Handle textbook PDF uploads with structured processing"""
    
    def get(self, request):
        """Show upload form"""
        form = BookUploadForm()
        return render(request, 'textbook_upload.html', {'form': form})
    
    def post(self, request):
        """Process textbook upload"""
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract title from filename or form
            pdf_file = request.FILES['pdf']
            title = request.POST.get('title') or pdf_file.name.replace('.pdf', '')
            
            # Create textbook instance
            textbook = Textbook.objects.create(
                title=title,
                pdf_file=pdf_file
            )
            
            # Queue background processing
            task_id = queue_textbook_processing(textbook.id)
            
            return JsonResponse({
                'status': 'success',
                'textbook_id': textbook.id,
                'task_id': task_id,
                'message': 'Textbook uploaded successfully. Processing started.'
            })
        
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)

class TextbookDetailView(View):
    """Display textbook with structured content"""
    
    def get(self, request, pk):
        """Show textbook detail page"""
        textbook = get_object_or_404(Textbook, pk=pk)
        
        # Get processing status
        status_info = get_processing_status(textbook.id)
        
        # Get content statistics
        stats = {
            'chapters': Chapter.objects.filter(textbook=textbook).count(),
            'sections': TextbookSection.objects.filter(textbook=textbook).count(),
            'questions': Question.objects.filter(textbook=textbook).count(),
            'reading_materials': TextbookSection.objects.filter(
                textbook=textbook, section_type='RM'
            ).count(),
            'exercises': TextbookSection.objects.filter(
                textbook=textbook, section_type='EX'
            ).count(),
        }
        
        context = {
            'textbook': textbook,
            'status_info': status_info,
            'stats': stats
        }
        
        return render(request, 'textbook_detail.html', context)

# API Views for structured content

@require_http_methods(["GET"])
def api_textbook_list(request):
    """API endpoint to list textbooks with metadata"""
    textbooks = Textbook.objects.annotate(
        sections_count=Count('sections'),
        questions_count=Count('questions'),
        chapters_count=Count('chapters')
    ).order_by('-upload_date')
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = min(int(request.GET.get('per_page', 10)), 50)
    
    paginator = Paginator(textbooks, per_page)
    page_obj = paginator.get_page(page)
    
    data = {
        'textbooks': [
            {
                'id': textbook.id,
                'title': textbook.title,
                'upload_date': textbook.upload_date.isoformat(),
                'processing_status': textbook.processing_status,
                'total_pages': textbook.total_pages,
                'sections_count': textbook.sections_count,
                'questions_count': textbook.questions_count,
                'chapters_count': textbook.chapters_count
            }
            for textbook in page_obj
        ],
        'pagination': {
            'page': page_obj.number,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_textbook_content(request, textbook_id):
    """API endpoint to get structured textbook content"""
    start_time = time.time()
    
    try:
        textbook = Textbook.objects.get(id=textbook_id)
    except Textbook.DoesNotExist:
        return JsonResponse({'error': 'Textbook not found'}, status=404)
    
    # Get query parameters
    section_type = request.GET.get('section_type')
    page_number = request.GET.get('page_number')
    chapter_id = request.GET.get('chapter_id')
    include_questions = request.GET.get('include_questions', 'false').lower() == 'true'
    
    # Build query
    sections_query = TextbookSection.objects.filter(textbook=textbook)
    
    if section_type:
        sections_query = sections_query.filter(section_type=section_type)
    if page_number:
        sections_query = sections_query.filter(page_number=int(page_number))
    if chapter_id:
        sections_query = sections_query.filter(chapter_id=int(chapter_id))
    
    # Prefetch related data
    if include_questions:
        sections_query = sections_query.prefetch_related('questions')
    
    sections = sections_query.order_by('page_number', 'order_in_page')
    
    # Pagination for large results
    page = request.GET.get('page', 1)
    per_page = min(int(request.GET.get('per_page', 20)), 100)
    
    paginator = Paginator(sections, per_page)
    page_obj = paginator.get_page(page)
    
    # Format response
    sections_data = []
    for section in page_obj:
        section_data = {
            'section_id': section.id,
            'content_type': section.section_type,
            'title': section.title,
            'page': section.page_number,
            'body': section.content,
            'position_on_page': section.position_on_page,
            'extracted_at': section.extracted_at.isoformat(),
            'chapter': {
                'id': section.chapter.id,
                'number': section.chapter.number,
                'title': section.chapter.title
            } if section.chapter else None
        }
        
        if include_questions:
            section_data['related_questions'] = [
                {
                    'id': q.id,
                    'question_text': q.question_text,
                    'question_type': q.question_type,
                    'options': q.options,
                    'difficulty_level': q.difficulty_level
                }
                for q in section.questions.all()
            ]
        else:
            section_data['related_questions'] = [q.id for q in section.questions.all()]
        
        sections_data.append(section_data)
    
    response_time = time.time() - start_time
    
    data = {
        'textbook_id': textbook_id,
        'textbook_title': textbook.title,
        'sections': sections_data,
        'pagination': {
            'page': page_obj.number,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        },
        'metadata': {
            'response_time': response_time,
            'filters_applied': {
                'section_type': section_type,
                'page_number': page_number,
                'chapter_id': chapter_id,
                'include_questions': include_questions
            }
        }
    }
    
    # Check response time requirement (max 3 seconds)
    if response_time > 3.0:
        logger.warning(f"API response time exceeded 3s: {response_time:.2f}s for textbook {textbook_id}")
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_textbook_chapters(request, textbook_id):
    """API endpoint to get textbook chapters"""
    try:
        textbook = Textbook.objects.get(id=textbook_id)
    except Textbook.DoesNotExist:
        return JsonResponse({'error': 'Textbook not found'}, status=404)
    
    chapters = Chapter.objects.filter(textbook=textbook).annotate(
        sections_count=Count('sections'),
        questions_count=Count('sections__questions')
    ).order_by('number')
    
    data = {
        'textbook_id': textbook_id,
        'chapters': [
            {
                'id': chapter.id,
                'number': chapter.number,
                'title': chapter.title,
                'start_page': chapter.start_page,
                'end_page': chapter.end_page,
                'sections_count': chapter.sections_count,
                'questions_count': chapter.questions_count
            }
            for chapter in chapters
        ]
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_textbook_questions(request, textbook_id):
    """API endpoint to get textbook questions"""
    try:
        textbook = Textbook.objects.get(id=textbook_id)
    except Textbook.DoesNotExist:
        return JsonResponse({'error': 'Textbook not found'}, status=404)
    
    # Query parameters
    question_type = request.GET.get('question_type')
    difficulty = request.GET.get('difficulty')
    page_number = request.GET.get('page_number')
    
    questions_query = Question.objects.filter(textbook=textbook)
    
    if question_type:
        questions_query = questions_query.filter(question_type=question_type)
    if difficulty:
        questions_query = questions_query.filter(difficulty_level=difficulty)
    if page_number:
        questions_query = questions_query.filter(page_number=int(page_number))
    
    questions = questions_query.select_related('section').order_by('page_number', 'order_in_section')
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = min(int(request.GET.get('per_page', 20)), 100)
    
    paginator = Paginator(questions, per_page)
    page_obj = paginator.get_page(page)
    
    data = {
        'textbook_id': textbook_id,
        'questions': [
            {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'options': question.options,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'difficulty_level': question.difficulty_level,
                'page_number': question.page_number,
                'section': {
                    'id': question.section.id,
                    'title': question.section.title,
                    'section_type': question.section.section_type
                } if question.section else None
            }
            for question in page_obj
        ],
        'pagination': {
            'page': page_obj.number,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_processing_status(request, textbook_id):
    """API endpoint to check processing status"""
    status_info = get_processing_status(textbook_id)
    return JsonResponse(status_info)

@csrf_exempt
@require_http_methods(["POST"])
def api_reprocess_textbook(request, textbook_id):
    """API endpoint to reprocess a textbook"""
    try:
        textbook = Textbook.objects.get(id=textbook_id)
        
        if textbook.processing_status == 'PROCESSING':
            return JsonResponse({
                'error': 'Textbook is already being processed'
            }, status=400)
        
        # Queue reprocessing
        task_id = queue_textbook_processing(textbook_id)
        
        return JsonResponse({
            'status': 'success',
            'task_id': task_id,
            'message': 'Reprocessing started'
        })
        
    except Textbook.DoesNotExist:
        return JsonResponse({'error': 'Textbook not found'}, status=404)

# Search and filter views

@require_http_methods(["GET"])
def api_search_content(request):
    """API endpoint to search across textbook content"""
    query = request.GET.get('q', '').strip()
    textbook_id = request.GET.get('textbook_id')
    content_types = request.GET.getlist('content_type')
    
    if not query:
        return JsonResponse({'error': 'Search query required'}, status=400)
    
    # Build search query
    search_query = Q(content__icontains=query) | Q(title__icontains=query)
    
    sections_query = TextbookSection.objects.filter(search_query)
    
    if textbook_id:
        sections_query = sections_query.filter(textbook_id=int(textbook_id))
    
    if content_types:
        sections_query = sections_query.filter(section_type__in=content_types)
    
    sections = sections_query.select_related('textbook', 'chapter').order_by('-extracted_at')[:50]
    
    results = [
        {
            'id': section.id,
            'textbook_id': section.textbook.id,
            'textbook_title': section.textbook.title,
            'section_type': section.section_type,
            'title': section.title,
            'content_preview': section.content[:200] + '...' if len(section.content) > 200 else section.content,
            'page_number': section.page_number,
            'chapter': {
                'id': section.chapter.id,
                'title': section.chapter.title
            } if section.chapter else None
        }
        for section in sections
    ]
    
    return JsonResponse({
        'query': query,
        'results_count': len(results),
        'results': results
    })
