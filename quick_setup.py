#!/usr/bin/env python3
"""
Quick Setup Script for Book AI Tutor
Simplified version that avoids Django import issues
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    print("🚀 Quick Setup for Book AI Tutor...")
    
    # Check if we're in the right directory
    if not os.path.exists('book_ai_tutor/manage.py'):
        print("❌ Please run this script from the Book-Tutor root directory")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        print("💡 Try installing manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Change to Django project directory for all subsequent commands
    django_dir = os.path.join(os.getcwd(), 'book_ai_tutor')
    
    # Create migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations", cwd=django_dir):
        print("❌ Failed to create migrations")
        print("💡 Try running manually: cd book_ai_tutor && python manage.py makemigrations")
        sys.exit(1)
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations", cwd=django_dir):
        print("❌ Failed to run migrations")
        print("💡 Try running manually: cd book_ai_tutor && python manage.py migrate")
        sys.exit(1)
    
    # Create necessary directories
    directories = [
        'book_ai_tutor/media',
        'book_ai_tutor/media/textbooks', 
        'book_ai_tutor/logs', 
        'book_ai_tutor/staticfiles'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create superuser (optional)
    print("\n🔐 Create a superuser account for admin access")
    create_superuser = input("Do you want to create a superuser now? (y/n): ").lower().strip()
    
    if create_superuser == 'y':
        print("📝 Creating superuser...")
        try:
            subprocess.run("python manage.py createsuperuser", shell=True, check=True, cwd=django_dir)
            print("✅ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Superuser creation skipped or failed")
        except KeyboardInterrupt:
            print("\n⚠️ Superuser creation cancelled")
    
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
    print("🔧 For troubleshooting, see TROUBLESHOOTING.md")

if __name__ == "__main__":
    main()