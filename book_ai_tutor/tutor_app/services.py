import os
import re
import PyPDF2
from PIL import Image
import io
import tempfile
import fitz  # PyMuPDF
import numpy as np
from collections import defaultdict

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import Document, Chapter, Section, Content


class PDFContentExtractor:
    """
    Service class for extracting structured content from PDF documents
    """
    
    def __init__(self, document):
        self.document = document
        self.pdf_path = document.pdf_file.path
        
    def extract_all_content(self):
        """Extract all content from the document"""
        try:
            # Process the PDF using PyMuPDF (fitz)
            doc = fitz.open(self.pdf_path)
            
            # Extract document structure (TOC/bookmarks)
            toc = doc.get_toc()
            
            # If no TOC, create a default chapter structure
            if not toc:
                main_chapter = self._create_default_chapter()
                self._process_pages_without_toc(doc, main_chapter)
            else:
                # Process document with TOC structure
                self._process_structured_document(doc, toc)
            
            return {
                "status": "success",
                "message": "Content extracted successfully",
                "pages_processed": len(doc)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error extracting content: {str(e)}"
            }
    
    def _create_default_chapter(self):
        """Create a default chapter for the document"""
        return Chapter.objects.create(
            document=self.document,
            number=1,
            title="Main Content"
        )
    
    def _process_pages_without_toc(self, doc, chapter):
        """Process pages when no TOC is available"""
        for page_num, page in enumerate(doc):
            # Extract text
            text = page.get_text()
            if text.strip():
                Content.objects.create(
                    chapter=chapter,
                    content_type='text',
                    text_content=text,
                    page_number=page_num + 1,
                    position_order=1
                )
            
            # Extract images
            self._extract_images_from_page(page, chapter, page_num)
    
    def _process_structured_document(self, doc, toc):
        """Process document with TOC structure"""
        # Map of level -> current chapter/section
        current = {
            1: None,  # Chapter
            2: None,  # Section
        }
        
        chapters = []
        sections = []
        
        # First pass: Create chapter/section structure
        for i, (level, title, page) in enumerate(toc):
            if level == 1:
                # Create new chapter
                chapter = Chapter.objects.create(
                    document=self.document,
                    title=title,
                    number=len(chapters) + 1
                )
                chapters.append(chapter)
                current[1] = chapter
                current[2] = None
            elif level == 2 and current[1]:
                # Create new section under current chapter
                section = Section.objects.create(
                    chapter=current[1],
                    title=title,
                    number=len(sections) + 1
                )
                sections.append(section)
                current[2] = section
        
        # If no chapters were created, create a default one
        if not chapters:
            chapters.append(self._create_default_chapter())
            current[1] = chapters[0]
        
        # Second pass: Assign content to the appropriate chapters/sections
        page_ranges = []
        for i, (level, title, page) in enumerate(toc):
            start_page = page - 1  # 0-based indexing
            
            # Find the end page (next entry's page - 1 or last page)
            end_page = None
            if i < len(toc) - 1:
                end_page = toc[i+1][2] - 2  # -1 for 0-based indexing, -1 to not overlap
            else:
                end_page = len(doc) - 1
            
            page_ranges.append((level, title, start_page, end_page))
        
        # Process content for each page range
        for level, title, start_page, end_page in page_ranges:
            # Find the appropriate chapter/section
            target_chapter = None
            target_section = None
            
            for chap in chapters:
                if chap.title == title:
                    target_chapter = chap
                    break
            
            if not target_chapter and level == 2:
                for sect in sections:
                    if sect.title == title:
                        target_section = sect
                        target_chapter = sect.chapter
                        break
            
            if not target_chapter:
                target_chapter = chapters[0]  # Default to first chapter
            
            # Process pages in range
            for page_num in range(start_page, end_page + 1):
                if page_num < len(doc):
                    page = doc[page_num]
                    text = page.get_text()
                    
                    if text.strip():
                        if target_section:
                            Content.objects.create(
                                section=target_section,
                                content_type='text',
                                text_content=text,
                                page_number=page_num + 1,
                                position_order=1
                            )
                        else:
                            Content.objects.create(
                                chapter=target_chapter,
                                content_type='text',
                                text_content=text,
                                page_number=page_num + 1,
                                position_order=1
                            )
                    
                    # Extract images
                    parent = target_section if target_section else target_chapter
                    is_section = target_section is not None
                    self._extract_images_from_page(page, parent, page_num, is_section)
    
    def _extract_images_from_page(self, page, parent, page_num, is_section=False):
        """Extract images from a page and save them to the database"""
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = self.document.pdf_file.name.split('/')[-1].split('.')[0]
                image_filename = f"{base_image}_p{page_num+1}_img{img_index+1}.png"
                
                # Extract image
                image_bytes = page.extract_image(xref)
                if image_bytes:
                    image_data = image_bytes["image"]
                    
                    # Save the image to media storage
                    image_path = f"content_images/{image_filename}"
                    image_file = ContentFile(image_data)
                    saved_path = default_storage.save(image_path, image_file)
                    
                    # Create content entry
                    content_args = {
                        'content_type': 'image',
                        'text_content': f"Image from page {page_num+1}",
                        'image': saved_path,
                        'page_number': page_num + 1,
                        'position_order': img_index + 2  # +2 because text is position 1
                    }
                    
                    if is_section:
                        content_args['section'] = parent
                    else:
                        content_args['chapter'] = parent
                    
                    Content.objects.create(**content_args)
        except Exception as e:
            # Log error but continue processing
            print(f"Error extracting images from page {page_num}: {e}")
    
    def detect_tables(self, doc):
        """
        Placeholder for table detection function.
        Would use libraries like camelot-py or tabula-py in a production environment
        """
        # This is a stub - actual implementation would require additional libraries
        pass
