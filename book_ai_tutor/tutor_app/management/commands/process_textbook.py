"""
Management command to process textbooks manually.
Useful for testing and debugging the extraction pipeline.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from tutor_app.models import Textbook
from tutor_app.tasks import process_textbook_upload
import os

class Command(BaseCommand):
    help = 'Process a textbook PDF for content extraction'

    def add_arguments(self, parser):
        parser.add_argument(
            'textbook_id',
            type=int,
            help='ID of the textbook to process'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocessing even if already completed'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually processing'
        )

    def handle(self, *args, **options):
        textbook_id = options['textbook_id']
        force = options['force']
        dry_run = options['dry_run']

        try:
            textbook = Textbook.objects.get(id=textbook_id)
        except Textbook.DoesNotExist:
            raise CommandError(f'Textbook with ID {textbook_id} does not exist')

        self.stdout.write(f'Textbook: {textbook.title}')
        self.stdout.write(f'Status: {textbook.processing_status}')
        self.stdout.write(f'PDF File: {textbook.pdf_file.name}')
        
        if not os.path.exists(textbook.pdf_file.path):
            raise CommandError(f'PDF file not found: {textbook.pdf_file.path}')

        if textbook.processing_status == 'COMPLETED' and not force:
            self.stdout.write(
                self.style.WARNING(
                    'Textbook already processed. Use --force to reprocess.'
                )
            )
            return

        if textbook.processing_status == 'PROCESSING':
            self.stdout.write(
                self.style.WARNING(
                    'Textbook is currently being processed. Use --force to override.'
                )
            )
            if not force:
                return

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    'DRY RUN: Would process textbook with the following settings:'
                )
            )
            self.stdout.write(f'  - PDF Path: {textbook.pdf_file.path}')
            self.stdout.write(f'  - File Size: {textbook.pdf_file.size} bytes')
            return

        self.stdout.write('Starting textbook processing...')
        
        try:
            result = process_textbook_upload(textbook_id)
            
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed textbook in {result["processing_time"]:.2f} seconds'
                    )
                )
                
                # Show results
                extraction_result = result.get('extraction_result', {})
                structuring_result = result.get('structuring_result', {})
                
                self.stdout.write('\nExtraction Results:')
                self.stdout.write(f'  - Total Pages: {extraction_result.get("total_pages", 0)}')
                self.stdout.write(f'  - Chapters Found: {len(extraction_result.get("chapters", []))}')
                self.stdout.write(f'  - Sections Found: {len(extraction_result.get("sections", []))}')
                self.stdout.write(f'  - Questions Found: {len(extraction_result.get("questions", []))}')
                
                self.stdout.write('\nStructuring Results:')
                self.stdout.write(f'  - Chapters Created: {structuring_result.get("chapters_count", 0)}')
                self.stdout.write(f'  - Sections Created: {structuring_result.get("sections_count", 0)}')
                self.stdout.write(f'  - Questions Created: {structuring_result.get("questions_count", 0)}')
                
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Processing failed: {result.get("error", "Unknown error")}'
                    )
                )
                
        except Exception as e:
            raise CommandError(f'Processing failed with exception: {str(e)}')