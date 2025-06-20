# Book AI Tutor - Structured Content Extraction Implementation

## Overview

This implementation provides a comprehensive backend system for extracting structured content from PDF textbooks, storing it in a relational database, and serving it through RESTful API endpoints. The system is designed specifically for educational textbooks containing reading materials, exercises, questions, and teacher notes.

## Architecture

### Core Components

1. **Models** (`models.py`)
   - `Textbook`: Main textbook entity with processing status and metadata
   - `Chapter`: Chapter organization within textbooks
   - `TextbookSection`: Structured content sections with type classification
   - `Question`: Extracted questions with type and difficulty classification
   - `VectorIndex`: Vector store references for future RAG integration
   - `ProcessingLog`: Comprehensive logging of processing activities

2. **PDF Extraction Service** (`services/pdf_extractor.py`)
   - Uses PyMuPDF (fitz) for precise text positioning and extraction
   - Pattern-based content type classification
   - Hierarchical content structure preservation
   - Content deduplication and confidence scoring

3. **Background Processing** (`tasks.py`)
   - Django-Q integration for async PDF processing
   - Multi-stage processing pipeline (extraction → structuring → indexing)
   - Comprehensive error handling and logging
   - Processing status tracking and recovery

4. **API Endpoints** (`views.py`)
   - RESTful API for content retrieval with filtering and pagination
   - Sub-3-second response time optimization
   - Search functionality across content types
   - Processing status monitoring

## Features Implemented

### ✅ Content Extraction
- **PDF Processing**: PyMuPDF-based extraction with position awareness
- **Content Classification**: Automatic detection of:
  - Reading Materials (RM)
  - Exercises (EX)
  - Points to Ponder (PP)
  - Teacher Notes (TN)
  - Pre/Post Reading activities
- **Question Detection**: Automatic identification and classification of:
  - Multiple Choice Questions (MCQ)
  - Short Answer (SA)
  - Long Answer (LA)
  - True/False (TF)
- **Hierarchical Structure**: Chapter → Section → Question relationships

### ✅ Data Storage
- **PostgreSQL Ready**: Models designed for PostgreSQL with pgvector support
- **Content Deduplication**: Hash-based duplicate detection during ingestion
- **Page-level Versioning**: Support for textbook updates and reprocessing
- **Metadata Preservation**: Font information, positioning, confidence scores

### ✅ API Interface
- **Content Retrieval**: `/api/textbooks/{id}/content/` with filtering
- **Chapter Navigation**: `/api/textbooks/{id}/chapters/`
- **Question Access**: `/api/textbooks/{id}/questions/` with type filtering
- **Search Functionality**: `/api/search/` across all content types
- **Processing Status**: Real-time processing status monitoring

### ✅ User Experience
- **Progressive Loading**: Paginated content delivery
- **Visual Distinction**: Clear separation of student vs teacher content
- **Consistent Labeling**: Standardized section type labels
- **Real-time Updates**: Processing status updates via WebSocket-ready architecture

## API Endpoints

### Content Retrieval
```http
GET /api/textbooks/{textbook_id}/content/
```
**Parameters:**
- `section_type`: Filter by content type (RM, EX, PP, TN, etc.)
- `page_number`: Filter by specific page
- `chapter_id`: Filter by chapter
- `include_questions`: Include related questions in response
- `page`: Pagination page number
- `per_page`: Items per page (max 100)

**Response Format:**
```json
{
  "textbook_id": 123,
  "sections": [
    {
      "section_id": 456,
      "content_type": "RM",
      "title": "Introduction to Algebra",
      "page": 45,
      "body": "Content text...",
      "position_on_page": {"x": 50, "y": 100, "width": 400, "height": 200},
      "related_questions": [789, 790],
      "chapter": {
        "id": 12,
        "number": 3,
        "title": "Mathematical Foundations"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_count": 95
  }
}
```

### Question Access
```http
GET /api/textbooks/{textbook_id}/questions/
```
**Parameters:**
- `question_type`: Filter by question type (MCQ, SA, LA, TF)
- `difficulty`: Filter by difficulty level (EASY, MEDIUM, HARD)
- `page_number`: Filter by page

### Search
```http
GET /api/search/?q=algebra&content_type=RM&textbook_id=123
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Start Django-Q Worker (Optional for Development)
```bash
# In a separate terminal (optional - tasks can run synchronously without this)
python manage.py qcluster
```

### 4. Run Development Server
```bash
python manage.py runserver
```

**Note**: The system is configured to use the database for task queuing in development mode. For production, uncomment the Redis configuration in `settings.py` and set up Redis.

## Usage

### 1. Upload Textbook
- Navigate to `/textbook/upload/`
- Select PDF file (max 500 pages, 100MB)
- Processing starts automatically in background

### 2. Monitor Processing
- View processing status at `/textbook/{id}/`
- Check logs in Django admin or via API

### 3. Access Content
- Use API endpoints to retrieve structured content
- Filter by content type, chapter, or page
- Search across all content

### 4. Manual Processing (for testing)
```bash
# Process specific textbook
python manage.py process_textbook 1

# Dry run to see what would be processed
python manage.py process_textbook 1 --dry-run

# Force reprocessing
python manage.py process_textbook 1 --force
```

## Performance Optimizations

### Database Indexing
- Composite indexes on `(textbook, section_type)`
- Page number indexing for fast page-based queries
- Content hash indexing for deduplication

### API Response Time
- Prefetch related objects to minimize database queries
- Pagination to limit response size
- Response time monitoring with warnings for >3s responses

### Background Processing
- Async processing for files >20 pages
- Chunked processing to prevent memory issues
- Comprehensive error handling and recovery

## Content Classification Patterns

The system uses regex patterns to identify different content types:

### Exercises
- `^Exercise\s+\d+\.?\d*`
- `^Activity\s+\d+\.?\d*`
- `^Practice\s+\d+\.?\d*`

### Points to Ponder
- `^Points?\s+to\s+Ponder`
- `^Think\s+About`
- `^Reflect\s+on`

### Teacher Notes
- `^Teacher\'?s?\s+Note`
- `^Instructor\s+Note`
- `^\[Teacher\]`

### Questions
- Multiple choice indicators: `[a-d]\)`, "choose"
- True/false indicators: "true" and "false" keywords
- Question words: "What", "How", "Why", etc.

## Error Handling

### Processing Errors
- Comprehensive logging to `ProcessingLog` model
- Automatic status updates (PENDING → PROCESSING → COMPLETED/FAILED)
- Cleanup utilities for failed processing

### API Errors
- Proper HTTP status codes
- Detailed error messages
- Rate limiting to prevent abuse

## Future Enhancements

### RAG Integration Ready
- `VectorIndex` model prepared for vector store integration
- Chunk metadata preserved for embedding
- LangChain/LangGraph integration points identified

### Advanced Features
- Content compression for large textbooks
- Multi-language support
- Advanced question type detection
- Automated difficulty assessment

## Testing

### Unit Tests
```bash
python manage.py test tutor_app
```

### Manual Testing
1. Upload sample PDF textbook
2. Monitor processing in admin interface
3. Test API endpoints with different filters
4. Verify content classification accuracy

## Monitoring & Logging

### Processing Logs
- All processing stages logged to database
- File-based logging for debugging
- Processing time tracking

### Performance Monitoring
- API response time tracking
- Background task monitoring via Django-Q admin
- Database query optimization monitoring

## Security Considerations

### File Upload Security
- File type validation (PDF only)
- File size limits (100MB)
- Virus scanning ready (implement with ClamAV)

### API Security
- Rate limiting implemented
- CSRF protection for state-changing operations
- Input sanitization for search queries

### Data Privacy
- Content hash-based deduplication
- Secure file storage
- Processing logs with sensitive data filtering

## Deployment Notes

### Production Settings
- Set `DEBUG = False`
- Configure proper database (PostgreSQL recommended)
- Set up Redis for production use
- Configure proper logging
- Set up monitoring (Sentry, etc.)

### Scaling Considerations
- Multiple Django-Q workers for high throughput
- Database connection pooling
- CDN for static files
- Load balancing for API endpoints

This implementation provides a solid foundation for educational content extraction and can be extended with AI tutoring capabilities as outlined in the main README.md.