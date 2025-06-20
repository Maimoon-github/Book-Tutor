#!/usr/bin/env python3
"""
Setup script for Book AI Tutor
Handles installation and initial configuration
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Book AI Tutor...")
    
    # Check if we're in the right directory
    if not os.path.exists('book_ai_tutor/manage.py'):
        print("❌ Please run this script from the Book-Tutor root directory")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Configure Django environment before setup
    script_path = os.path.dirname(os.path.abspath(__file__))
    django_project_path = os.path.join(script_path, 'book_ai_tutor')
    
    # Add the Django project directory to Python path
    sys.path.insert(0, django_project_path)
    
    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_ai_tutor.settings')
    
    # Change to Django project directory
    os.chdir('book_ai_tutor')
    
    # Set up Django
    try:
        django.setup()
        print("✅ Django environment configured successfully")
    except Exception as e:
        print(f"❌ Error during Django setup: {e}")
        print("💡 Try running the setup manually:")
        print("   cd book_ai_tutor")
        print("   python manage.py migrate")
        sys.exit(1)
    
    # Create migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        print("❌ Failed to create migrations")
        sys.exit(1)
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        print("❌ Failed to run migrations")
        sys.exit(1)
    
    # Create superuser (optional)
    print("\n🔐 Create a superuser account for admin access")
    create_superuser = input("Do you want to create a superuser now? (y/n): ").lower().strip()
    
    if create_superuser == 'y':
        try:
            subprocess.run("python manage.py createsuperuser", shell=True, check=True)
            print("✅ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Superuser creation skipped or failed")
    
    # Create necessary directories
    directories = ['media', 'media/textbooks', 'logs', 'staticfiles']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the development server:")
    print("   cd book_ai_tutor")
    print("   python manage.py runserver")
    print("\n2. (Optional) Start background task worker in another terminal:")
    print("   cd book_ai_tutor")
    print("   python manage.py qcluster")
    print("\n3. Open your browser and go to:")
    print("   http://127.0.0.1:8000/textbook/upload/")
    print("\n4. Admin interface (if you created a superuser):")
    print("   http://127.0.0.1:8000/admin/")
    
    print("\n📚 For more information, see IMPLEMENTATION.md")

if __name__ == "__main__":
    main()