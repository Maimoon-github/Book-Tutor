# Quick Start Guide

## Option 1: Automated Setup (Recommended)

```bash
# Clone or navigate to the project directory
cd Book-Tutor

# Run the quick setup script
python quick_setup.py

# Start the development server
cd book_ai_tutor
python manage.py runserver
```

## Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
cd book_ai_tutor
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Option 3: Background Tasks (Optional)

For processing large PDFs, start the background worker in a separate terminal:

```bash
cd book_ai_tutor
python manage.py qcluster
```

## Access the Application

1. **Upload Interface**: http://127.0.0.1:8000/textbook/upload/
2. **Admin Interface**: http://127.0.0.1:8000/admin/
3. **API Documentation**: See IMPLEMENTATION.md

## Troubleshooting

If you encounter any issues:

1. Check TROUBLESHOOTING.md for common problems
2. Ensure you have Python 3.8+ installed
3. Make sure all dependencies are installed correctly
4. Check the logs in `book_ai_tutor/logs/django.log`

## Next Steps

1. Upload a PDF textbook
2. Monitor processing status
3. Explore the extracted content via API
4. Check the admin interface for detailed data

For detailed documentation, see:
- IMPLEMENTATION.md - Complete technical documentation
- TROUBLESHOOTING.md - Common issues and solutions
- README.md - Project overview and architecture