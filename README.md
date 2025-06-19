# Book AI Tutor

A Django backend for processing, storing, and previewing structured content from PDFs.

## Features

- Upload PDF documents
- Extract text and images from PDFs
- Detect and preserve document structure (chapters, sections)
- Store content in a structured database
- Preview content with a clean, responsive UI
- RESTful API for integration with other applications

## Requirements

- Python 3.8+
- Django 5.2+
- Additional Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Book-Tutor
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
cd book_ai_tutor
python manage.py migrate
```

5. Create a superuser for the admin interface:

```bash
python manage.py createsuperuser
```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

The application will be available at http://localhost:8000/

- Admin interface: http://localhost:8000/admin/
- API endpoints: http://localhost:8000/api/

## Usage

### Using the API

1. **Upload a PDF document**:

```
POST /api/documents/
```

Form data:
- `title`: Document title
- `author` (optional): Author name
- `description` (optional): Document description
- `pdf_file`: The PDF file to upload

2. **Extract content from a PDF**:

```
POST /api/documents/{document_id}/extract-content/
```

3. **Get document content**:

```
GET /api/documents/{document_id}/
```

4. **Preview document**:

For API response:
```
GET /api/documents/{document_id}/preview/
```

For HTML preview:
```
GET /api/documents/{document_id}/preview/?format=html
```

### Using the Sample Script

A sample script is provided to demonstrate the API usage:

```bash
python upload_and_extract.py path/to/your.pdf
```

## Project Structure

- `tutor_app/models.py`: Database models for storing document structure and content
- `tutor_app/views.py`: API views and logic
- `tutor_app/services.py`: PDF content extraction services
- `tutor_app/serializers.py`: API serializers
- `tutor_app/templates/`: HTML templates for content preview

## Advanced Content Extraction

The system uses PyMuPDF (fitz) and PyPDF2 to extract content from PDFs:

- Text extraction with structure preservation
- Image extraction and storage
- Table of contents parsing for document structure
- Page and section organization