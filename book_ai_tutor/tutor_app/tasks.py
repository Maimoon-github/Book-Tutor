"""
Background tasks for PDF processing and content extraction.
Uses Django-Q for async processing of large textbooks.
"""

import os
import time
from django.conf import settings
from django.utils import timezone
try:
    from django_q.tasks import async_task
    from django_q.models import Task
    DJANGO_Q_AVAILABLE = True
except ImportError:
    DJANGO_Q_AVAILABLE = False
    # Fallback for when Django-Q is not available
    def async_task(func_name, *args, **kwargs):
        # Import and run the function synchronously
        module_name, function_name = func_name.rsplit('.', 1)
        module = __import__(module_name, fromlist=[function_name])
        func = getattr(module, function_name)
        return func(*args)
import logging

from .models import Textbook, Chapter, TextbookSection, Question, ProcessingLog, VectorIndex
from .services.pdf_extractor import PDFContentExtractor, ContentDeduplicator

logger = logging.getLogger(__name__)

def process_textbook_upload(textbook_id: int) -> dict:
    """
    Main task for processing uploaded textbook PDF.
    Orchestrates extraction, structuring, and indexing.
    
    Args:
        textbook_id: ID of the Textbook model instance
        
    Returns:
        Processing result dictionary
    """
    start_time = time.time()
    
    try:
        textbook = Textbook.objects.get(id=textbook_id)
        textbook.processing_status = 'PROCESSING'
        textbook.save()
        
        # Log processing start
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='extraction',
            status='SUCCESS',
            message='Started PDF processing',
            details={'start_time': timezone.now().isoformat()}
        )
        
        # Step 1: Extract content from PDF
        extraction_result = extract_pdf_content(textbook)
        
        # Step 2: Structure and save content
        structuring_result = structure_extracted_content(textbook, extraction_result)
        
        # Step 3: Create vector embeddings (if enabled)
        if getattr(settings, 'ENABLE_VECTOR_INDEXING', False):
            indexing_result = create_vector_index(textbook)
        else:
            indexing_result = {'status': 'skipped', 'message': 'Vector indexing disabled'}
        
        # Update textbook status
        textbook.processing_status = 'COMPLETED'
        textbook.total_pages = extraction_result.get('total_pages', 0)
        textbook.save()
        
        processing_time = time.time() - start_time
        
        # Log successful completion
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='completion',
            status='SUCCESS',
            message='Textbook processing completed successfully',
            details={
                'processing_time': processing_time,
                'total_pages': textbook.total_pages,
                'sections_created': structuring_result.get('sections_count', 0),
                'questions_created': structuring_result.get('questions_count', 0),
                'chapters_created': structuring_result.get('chapters_count', 0)
            }
        )
        
        return {
            'status': 'success',
            'textbook_id': textbook_id,
            'processing_time': processing_time,
            'extraction_result': extraction_result,
            'structuring_result': structuring_result,
            'indexing_result': indexing_result
        }
        
    except Exception as e:
        logger.error(f"Error processing textbook {textbook_id}: {str(e)}")
        
        # Update textbook status to failed
        try:
            textbook = Textbook.objects.get(id=textbook_id)
            textbook.processing_status = 'FAILED'
            textbook.save()
            
            # Log error
            ProcessingLog.objects.create(
                textbook=textbook,
                stage='error',
                status='ERROR',
                message=f'Processing failed: {str(e)}',
                details={
                    'error_type': type(e).__name__,
                    'processing_time': time.time() - start_time
                }
            )
        except:
            pass  # Don't fail if we can't log the error
        
        return {
            'status': 'error',
            'textbook_id': textbook_id,
            'error': str(e),
            'processing_time': time.time() - start_time
        }

def extract_pdf_content(textbook: Textbook) -> dict:
    """
    Extract structured content from PDF using PyMuPDF.
    
    Args:
        textbook: Textbook model instance
        
    Returns:
        Extraction result dictionary
    """
    try:
        extractor = PDFContentExtractor(max_pages=500)
        pdf_path = textbook.pdf_file.path
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract content
        extraction_result = extractor.extract_content(pdf_path)
        
        # Log extraction success
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='extraction',
            status='SUCCESS',
            message='PDF content extraction completed',
            details={
                'total_pages': extraction_result.get('total_pages', 0),
                'sections_found': len(extraction_result.get('sections', [])),
                'questions_found': len(extraction_result.get('questions', [])),
                'chapters_found': len(extraction_result.get('chapters', []))
            }
        )
        
        return extraction_result
        
    except Exception as e:
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='extraction',
            status='ERROR',
            message=f'PDF extraction failed: {str(e)}',
            details={'error_type': type(e).__name__}
        )
        raise

def structure_extracted_content(textbook: Textbook, extraction_result: dict) -> dict:
    """
    Structure extracted content into database models.
    
    Args:
        textbook: Textbook model instance
        extraction_result: Result from PDF extraction
        
    Returns:
        Structuring result dictionary
    """
    try:
        deduplicator = ContentDeduplicator()
        
        # Create chapters
        chapters_created = 0
        chapter_map = {}  # Map page numbers to chapters
        
        for chapter_data in extraction_result.get('chapters', []):
            chapter, created = Chapter.objects.get_or_create(
                textbook=textbook,
                number=chapter_data['number'],
                defaults={
                    'title': chapter_data['title'],
                    'start_page': chapter_data['start_page'],
                    'end_page': chapter_data.get('end_page', chapter_data['start_page'])
                }
            )
            if created:
                chapters_created += 1
            
            # Map pages to chapters (rough mapping)
            for page in range(chapter_data['start_page'], chapter_data.get('end_page', chapter_data['start_page']) + 1):
                chapter_map[page] = chapter
        
        # Create sections
        sections_created = 0
        for section_data in extraction_result.get('sections', []):
            # Skip duplicates
            if deduplicator.is_duplicate(section_data['content']):
                continue
            
            # Find associated chapter
            page_num = section_data['page_number']
            chapter = chapter_map.get(page_num)
            
            section = TextbookSection.objects.create(
                textbook=textbook,
                chapter=chapter,
                section_type=section_data['section_type'],
                title=section_data.get('title', ''),
                page_number=page_num,
                content=section_data['content'],
                position_on_page=section_data.get('position_on_page', {}),
                order_in_page=sections_created  # Simple ordering
            )
            sections_created += 1
        
        # Create questions
        questions_created = 0
        for question_data in extraction_result.get('questions', []):
            # Find associated section (if any)
            page_num = question_data['page_number']
            section = TextbookSection.objects.filter(
                textbook=textbook,
                page_number=page_num,
                section_type='EX'  # Associate with exercise sections
            ).first()
            
            question = Question.objects.create(
                textbook=textbook,
                section=section,
                question_text=question_data['question_text'],
                question_type=question_data.get('question_type', 'SA'),
                options=question_data.get('options'),
                page_number=page_num,
                order_in_section=questions_created
            )
            questions_created += 1
        
        # Update chapter end pages based on content
        for chapter in Chapter.objects.filter(textbook=textbook):
            last_section = TextbookSection.objects.filter(
                textbook=textbook,
                chapter=chapter
            ).order_by('-page_number').first()
            
            if last_section:
                chapter.end_page = last_section.page_number
                chapter.save()
        
        result = {
            'chapters_count': chapters_created,
            'sections_count': sections_created,
            'questions_count': questions_created
        }
        
        # Log structuring success
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='structuring',
            status='SUCCESS',
            message='Content structuring completed',
            details=result
        )
        
        return result
        
    except Exception as e:
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='structuring',
            status='ERROR',
            message=f'Content structuring failed: {str(e)}',
            details={'error_type': type(e).__name__}
        )
        raise

def create_vector_index(textbook: Textbook) -> dict:
    """
    Create vector embeddings for RAG integration.
    This is a placeholder for future RAG implementation.
    
    Args:
        textbook: Textbook model instance
        
    Returns:
        Indexing result dictionary
    """
    try:
        # Placeholder for vector indexing
        # In full implementation, this would:
        # 1. Chunk the content appropriately
        # 2. Generate embeddings using OpenAI or local model
        # 3. Store in FAISS/Chroma vector store
        # 4. Create VectorIndex record
        
        # For now, just create a placeholder record
        vector_index, created = VectorIndex.objects.get_or_create(
            textbook=textbook,
            defaults={
                'index_file_path': f'vector_stores/textbook_{textbook.id}.faiss',
                'embedding_model': 'text-embedding-ada-002',
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'total_chunks': 0
            }
        )
        
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='indexing',
            status='SUCCESS',
            message='Vector index placeholder created',
            details={'vector_index_id': vector_index.id}
        )
        
        return {
            'status': 'placeholder_created',
            'vector_index_id': vector_index.id,
            'message': 'Vector indexing placeholder - implement with RAG module'
        }
        
    except Exception as e:
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='indexing',
            status='ERROR',
            message=f'Vector indexing failed: {str(e)}',
            details={'error_type': type(e).__name__}
        )
        raise

# Utility functions for task management

def queue_textbook_processing(textbook_id: int) -> str:
    """
    Queue textbook processing task.
    
    Args:
        textbook_id: ID of textbook to process
        
    Returns:
        Task ID
    """
    task_id = async_task(
        'tutor_app.tasks.process_textbook_upload',
        textbook_id,
        task_name=f'process_textbook_{textbook_id}',
        timeout=3600,  # 1 hour timeout
        retry=1
    )
    
    logger.info(f"Queued textbook processing task {task_id} for textbook {textbook_id}")
    return task_id

def get_processing_status(textbook_id: int) -> dict:
    """
    Get processing status for a textbook.
    
    Args:
        textbook_id: ID of textbook
        
    Returns:
        Status dictionary
    """
    try:
        textbook = Textbook.objects.get(id=textbook_id)
        
        # Get latest processing logs
        logs = ProcessingLog.objects.filter(textbook=textbook).order_by('-timestamp')[:5]
        
        # Check for running tasks (only if Django-Q is available)
        has_running_task = False
        if DJANGO_Q_AVAILABLE:
            running_tasks = Task.objects.filter(
                name=f'process_textbook_{textbook_id}',
                stopped__isnull=True
            )
            has_running_task = running_tasks.exists()
        
        return {
            'textbook_id': textbook_id,
            'status': textbook.processing_status,
            'total_pages': textbook.total_pages,
            'has_running_task': has_running_task,
            'recent_logs': [
                {
                    'stage': log.stage,
                    'status': log.status,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat()
                }
                for log in logs
            ]
        }
        
    except Textbook.DoesNotExist:
        return {
            'textbook_id': textbook_id,
            'status': 'NOT_FOUND',
            'error': 'Textbook not found'
        }

def cleanup_failed_processing(textbook_id: int) -> dict:
    """
    Clean up after failed processing.
    
    Args:
        textbook_id: ID of textbook
        
    Returns:
        Cleanup result
    """
    try:
        textbook = Textbook.objects.get(id=textbook_id)
        
        # Remove partial data
        TextbookSection.objects.filter(textbook=textbook).delete()
        Question.objects.filter(textbook=textbook).delete()
        Chapter.objects.filter(textbook=textbook).delete()
        
        # Reset status
        textbook.processing_status = 'PENDING'
        textbook.total_pages = 0
        textbook.save()
        
        ProcessingLog.objects.create(
            textbook=textbook,
            stage='cleanup',
            status='SUCCESS',
            message='Cleaned up failed processing data'
        )
        
        return {'status': 'success', 'message': 'Cleanup completed'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}