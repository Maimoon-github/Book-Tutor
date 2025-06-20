# Troubleshooting Guide

## Common Issues and Solutions

### 1. Django-Q Compatibility Issues

**Problem**: `NotImplementedError: ugettext() is deleted`

**Solution**: This has been fixed in the updated requirements.txt. We now use `django-q2` instead of the old `django-q` package.

```bash
# Uninstall old packages
pip uninstall django-q django-q-registry

# Install updated requirements
pip install -r requirements.txt
```

### 2. Django Setup Script Issues

**Problem**: `ModuleNotFoundError: No module named 'book_ai_tutor.settings'` when running `setup.py`

**Solution**: Use the simplified setup script instead:
```bash
# Use the quick setup script (recommended)
python quick_setup.py

# Or run setup manually:
cd book_ai_tutor
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 3. Missing Dependencies

**Problem**: Import errors for PyMuPDF, Redis, or other packages

**Solution**: 
```bash
# Install all dependencies
pip install -r requirements.txt

# For PyMuPDF issues on some systems:
pip install --upgrade PyMuPDF

# For Redis connection issues (if using Redis):
sudo apt-get install redis-server
redis-server
```

### 4. Database Migration Issues

**Problem**: Migration errors or database schema issues

**Solution**:
```bash
# Reset migrations (development only)
rm book_ai_tutor/tutor_app/migrations/0*.py
python book_ai_tutor/manage.py makemigrations tutor_app
python book_ai_tutor/manage.py migrate

# Or start fresh with a new database
rm book_ai_tutor/db.sqlite3
python book_ai_tutor/manage.py migrate
```

### 5. Background Tasks Not Working

**Problem**: PDF processing seems stuck or not starting

**Solutions**:

**Option A: Use Database Queue (Recommended for Development)**
- The system is configured to use database queuing by default
- Tasks will run synchronously if Django-Q worker is not running
- No additional setup required

**Option B: Use Redis Queue (Production)**
```bash
# Install and start Redis
sudo apt-get install redis-server
redis-server

# Update settings.py to use Redis
# Uncomment the Redis configuration in Q_CLUSTER settings

# Start Django-Q worker
python manage.py qcluster
```

### 6. File Upload Issues

**Problem**: PDF upload fails or times out

**Solutions**:
```bash
# Check file permissions
chmod 755 book_ai_tutor/media/
chmod 755 book_ai_tutor/media/textbooks/

# Check file size limits in settings.py
# Current limit: 100MB per file, 500 pages max

# For large files, increase timeout in settings:
# Q_CLUSTER['timeout'] = 7200  # 2 hours
```

### 7. PyMuPDF Installation Issues

**Problem**: `fitz` module not found or compilation errors

**Solutions**:
```bash
# On Ubuntu/Debian:
sudo apt-get install python3-dev
pip install --upgrade PyMuPDF

# On macOS:
brew install mupdf-tools
pip install --upgrade PyMuPDF

# Alternative: Use conda
conda install -c conda-forge pymupdf
```

### 8. Static Files Not Loading

**Problem**: CSS/JS files not loading in templates

**Solution**:
```bash
# Collect static files
python manage.py collectstatic

# For development, ensure DEBUG=True in settings.py
# For production, configure proper static file serving
```

### 9. Permission Errors

**Problem**: Permission denied errors when processing files

**Solution**:
```bash
# Fix media directory permissions
chmod -R 755 book_ai_tutor/media/
chmod -R 755 book_ai_tutor/logs/

# Ensure Django can write to these directories
chown -R $USER:$USER book_ai_tutor/media/
chown -R $USER:$USER book_ai_tutor/logs/
```

### 10. Memory Issues with Large PDFs

**Problem**: Out of memory errors during PDF processing

**Solutions**:
```bash
# Reduce chunk size in settings.py:
TEXTBOOK_PROCESSING = {
    'CHUNK_SIZE': 500,  # Reduce from 1000
    'MAX_PAGES': 200,   # Reduce from 500
}

# Process files in smaller batches
# Consider using pagination for large textbooks
```

### 11. API Response Time Issues

**Problem**: API responses taking longer than 3 seconds

**Solutions**:
```bash
# Check database indexes
python manage.py dbshell
# Run: EXPLAIN QUERY PLAN SELECT * FROM tutor_app_textbooksection WHERE textbook_id = 1;

# Optimize queries by:
# 1. Using select_related() and prefetch_related()
# 2. Adding database indexes
# 3. Implementing caching
# 4. Reducing page size in API responses
```

## Development Tips

### Quick Setup
```bash
# Use the quick setup script (recommended)
python quick_setup.py

# Or use the full setup script
python setup.py

# Or manual setup:
pip install -r requirements.txt
cd book_ai_tutor
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Testing PDF Processing
```bash
# Test with a specific textbook
python manage.py process_textbook 1 --dry-run

# Force reprocessing
python manage.py process_textbook 1 --force

# Check processing logs
python manage.py shell
>>> from tutor_app.models import ProcessingLog
>>> ProcessingLog.objects.filter(textbook_id=1).order_by('-timestamp')
```

### Debugging API Issues
```bash
# Test API endpoints directly
curl "http://localhost:8000/api/textbooks/"
curl "http://localhost:8000/api/textbooks/1/content/"
curl "http://localhost:8000/api/search/?q=test"

# Check Django logs
tail -f book_ai_tutor/logs/django.log
```

### Performance Monitoring
```bash
# Monitor Django-Q tasks
python manage.py qmonitor

# Check database performance
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

## Getting Help

1. **Check Logs**: Always check `book_ai_tutor/logs/django.log` for detailed error messages
2. **Admin Interface**: Use `/admin/` to inspect data and processing logs
3. **Django Shell**: Use `python manage.py shell` for debugging
4. **API Testing**: Test API endpoints with curl or Postman
5. **GitHub Issues**: Report bugs with full error logs and system information

## System Requirements

- **Python**: 3.8+
- **Django**: 5.2+
- **Memory**: 4GB+ recommended for large PDF processing
- **Storage**: Sufficient space for PDF files and extracted content
- **OS**: Linux, macOS, or Windows with WSL