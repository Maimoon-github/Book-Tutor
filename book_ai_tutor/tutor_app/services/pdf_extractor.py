"""
PDF Content Extraction Service using PyMuPDF (fitz)
Extracts structured content from educational textbooks with precise positioning.
"""

import fitz  # PyMuPDF
import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentBlock:
    """Represents a content block with position and type information"""
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    page_num: int
    block_type: str
    confidence: float = 0.0
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PDFContentExtractor:
    """
    Extracts structured content from PDF textbooks using PyMuPDF.
    Identifies different content types based on formatting and patterns.
    """
    
    # Pattern matching for different content types
    PATTERNS = {
        'exercise': [
            r'^Exercise\s+\d+\.?\d*',
            r'^Activity\s+\d+\.?\d*',
            r'^Practice\s+\d+\.?\d*',
            r'^\d+\.\s*[A-Z]',  # Numbered questions
        ],
        'point_to_ponder': [
            r'^Points?\s+to\s+Ponder',
            r'^Think\s+About',
            r'^Reflect\s+on',
            r'^Consider\s+this',
        ],
        'teacher_note': [
            r'^Teacher\'?s?\s+Note',
            r'^Instructor\s+Note',
            r'^Teaching\s+Tip',
            r'^\[Teacher\]',
            r'^\(Teacher\)',
        ],
        'pre_reading': [
            r'^Pre-?Reading',
            r'^Before\s+Reading',
            r'^Warm-?up',
        ],
        'post_reading': [
            r'^Post-?Reading',
            r'^After\s+Reading',
            r'^Follow-?up',
        ],
        'chapter_title': [
            r'^Chapter\s+\d+',
            r'^Unit\s+\d+',
            r'^Lesson\s+\d+',
        ]
    }
    
    def __init__(self, max_pages: int = 500):
        self.max_pages = max_pages
        
    def extract_content(self, pdf_path: str) -> Dict:
        """
        Main extraction method that processes the entire PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content organized by type and page
        """
        try:
            doc = fitz.open(pdf_path)
            
            if len(doc) > self.max_pages:
                raise ValueError(f"PDF has {len(doc)} pages, exceeds limit of {self.max_pages}")
            
            extraction_result = {
                'total_pages': len(doc),
                'chapters': [],
                'sections': [],
                'questions': [],
                'metadata': {
                    'extraction_date': None,
                    'processing_time': 0,
                    'errors': []
                }
            }
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_content = self._extract_page_content(page, page_num + 1)
                
                # Organize content by type
                for content_block in page_content:
                    if content_block.block_type == 'chapter':
                        extraction_result['chapters'].append(self._format_chapter(content_block))
                    elif content_block.block_type in ['RM', 'EX', 'PP', 'TN', 'PRE', 'POST']:
                        extraction_result['sections'].append(self._format_section(content_block))
                    elif content_block.block_type in ['question']:
                        extraction_result['questions'].append(self._format_question(content_block))
            
            doc.close()
            return extraction_result
            
        except Exception as e:
            logger.error(f"Error extracting content from {pdf_path}: {str(e)}")
            raise
    
    def _extract_page_content(self, page: fitz.Page, page_num: int) -> List[ContentBlock]:
        """
        Extract content blocks from a single page with position information.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-indexed)
            
        Returns:
            List of ContentBlock objects
        """
        content_blocks = []
        
        # Get text blocks with position information
        blocks = page.get_text("dict")
        
        for block in blocks.get("blocks", []):
            if "lines" not in block:
                continue
                
            # Extract text and position
            block_text = ""
            bbox = block.get("bbox", (0, 0, 0, 0))
            
            for line in block["lines"]:
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
                block_text += "\n"
            
            block_text = block_text.strip()
            if not block_text:
                continue
            
            # Classify content type
            content_type = self._classify_content_type(block_text, bbox, page_num)
            
            # Calculate confidence based on formatting and patterns
            confidence = self._calculate_confidence(block_text, content_type, block)
            
            content_block = ContentBlock(
                text=block_text,
                bbox=bbox,
                page_num=page_num,
                block_type=content_type,
                confidence=confidence,
                metadata={
                    'font_info': self._extract_font_info(block),
                    'position_info': self._analyze_position(bbox, page.rect)
                }
            )
            
            content_blocks.append(content_block)
        
        return content_blocks
    
    def _classify_content_type(self, text: str, bbox: Tuple, page_num: int) -> str:
        """
        Classify content type based on text patterns and formatting.
        
        Args:
            text: Text content
            bbox: Bounding box coordinates
            page_num: Page number
            
        Returns:
            Content type code
        """
        text_lower = text.lower().strip()
        
        # Check for specific patterns
        for content_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return self._map_content_type(content_type)
        
        # Heuristic classification based on position and formatting
        if self._is_header_position(bbox):
            if any(word in text_lower for word in ['chapter', 'unit', 'lesson']):
                return 'chapter'
            return 'RM'  # Reading Material header
        
        if self._is_sidebar_position(bbox):
            return 'TN'  # Likely teacher note
        
        if self._contains_question_indicators(text):
            return 'question'
        
        # Default to reading material
        return 'RM'
    
    def _map_content_type(self, pattern_type: str) -> str:
        """Map pattern types to model field values"""
        mapping = {
            'exercise': 'EX',
            'point_to_ponder': 'PP',
            'teacher_note': 'TN',
            'pre_reading': 'PRE',
            'post_reading': 'POST',
            'chapter_title': 'chapter'
        }
        return mapping.get(pattern_type, 'RM')
    
    def _calculate_confidence(self, text: str, content_type: str, block: Dict) -> float:
        """Calculate confidence score for content classification"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for pattern matches
        for patterns in self.PATTERNS.values():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence += 0.3
                    break
        
        # Font-based confidence adjustments
        font_info = self._extract_font_info(block)
        if font_info.get('is_bold', False):
            confidence += 0.1
        if font_info.get('font_size', 0) > 14:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_font_info(self, block: Dict) -> Dict:
        """Extract font information from text block"""
        font_info = {
            'font_size': 0,
            'font_name': '',
            'is_bold': False,
            'is_italic': False
        }
        
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font_info['font_size'] = max(font_info['font_size'], span.get('size', 0))
                font_info['font_name'] = span.get('font', '')
                flags = span.get('flags', 0)
                font_info['is_bold'] = font_info['is_bold'] or bool(flags & 2**4)
                font_info['is_italic'] = font_info['is_italic'] or bool(flags & 2**1)
        
        return font_info
    
    def _analyze_position(self, bbox: Tuple, page_rect: fitz.Rect) -> Dict:
        """Analyze position relative to page"""
        x0, y0, x1, y1 = bbox
        page_width = page_rect.width
        page_height = page_rect.height
        
        return {
            'relative_x': x0 / page_width,
            'relative_y': y0 / page_height,
            'width_ratio': (x1 - x0) / page_width,
            'height_ratio': (y1 - y0) / page_height,
            'is_header': y0 < page_height * 0.15,
            'is_footer': y1 > page_height * 0.85,
            'is_sidebar': x0 > page_width * 0.7 or x1 < page_width * 0.3
        }
    
    def _is_header_position(self, bbox: Tuple) -> bool:
        """Check if position indicates header content"""
        _, y0, _, _ = bbox
        return y0 < 100  # Top 100 points of page
    
    def _is_sidebar_position(self, bbox: Tuple) -> bool:
        """Check if position indicates sidebar content"""
        x0, _, x1, _ = bbox
        return x0 > 400 or x1 < 200  # Rough sidebar detection
    
    def _contains_question_indicators(self, text: str) -> bool:
        """Check if text contains question indicators"""
        question_indicators = [
            r'\?',  # Question mark
            r'^\d+\.',  # Numbered list
            r'^[a-z]\)',  # Lettered options
            r'What|How|Why|When|Where|Which|Who',  # Question words
        ]
        
        for indicator in question_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                return True
        return False
    
    def _format_chapter(self, content_block: ContentBlock) -> Dict:
        """Format chapter information"""
        # Extract chapter number and title
        text = content_block.text
        chapter_match = re.search(r'Chapter\s+(\d+)(?:\s*[:\-]\s*(.+))?', text, re.IGNORECASE)
        
        if chapter_match:
            number = int(chapter_match.group(1))
            title = chapter_match.group(2) or f"Chapter {number}"
        else:
            number = content_block.page_num
            title = text[:100]  # First 100 chars as title
        
        return {
            'number': number,
            'title': title.strip(),
            'start_page': content_block.page_num,
            'end_page': content_block.page_num,  # Will be updated during processing
            'position': content_block.bbox
        }
    
    def _format_section(self, content_block: ContentBlock) -> Dict:
        """Format section information"""
        return {
            'section_type': content_block.block_type,
            'title': self._extract_section_title(content_block.text),
            'page_number': content_block.page_num,
            'content': content_block.text,
            'position_on_page': {
                'x': content_block.bbox[0],
                'y': content_block.bbox[1],
                'width': content_block.bbox[2] - content_block.bbox[0],
                'height': content_block.bbox[3] - content_block.bbox[1]
            },
            'confidence': content_block.confidence,
            'metadata': content_block.metadata
        }
    
    def _format_question(self, content_block: ContentBlock) -> Dict:
        """Format question information"""
        question_text = content_block.text
        
        # Detect question type
        question_type = self._detect_question_type(question_text)
        
        # Extract options for MCQ
        options = None
        if question_type == 'MCQ':
            options = self._extract_mcq_options(question_text)
        
        return {
            'question_text': question_text,
            'question_type': question_type,
            'options': options,
            'page_number': content_block.page_num,
            'position': content_block.bbox,
            'confidence': content_block.confidence
        }
    
    def _extract_section_title(self, text: str) -> str:
        """Extract title from section text"""
        lines = text.split('\n')
        if lines:
            # First line is usually the title
            title = lines[0].strip()
            # Remove common prefixes
            title = re.sub(r'^(Exercise|Activity|Practice)\s+\d+\.?\d*\s*[:\-]?\s*', '', title, flags=re.IGNORECASE)
            return title[:255]  # Limit to model field length
        return ""
    
    def _detect_question_type(self, text: str) -> str:
        """Detect question type from text content"""
        text_lower = text.lower()
        
        # Check for multiple choice indicators
        if re.search(r'[a-d]\)', text) or 'choose' in text_lower:
            return 'MCQ'
        
        # Check for true/false
        if 'true' in text_lower and 'false' in text_lower:
            return 'TF'
        
        # Check for short answer indicators
        if len(text.split()) < 50:
            return 'SA'
        
        return 'LA'  # Default to long answer
    
    def _extract_mcq_options(self, text: str) -> List[str]:
        """Extract multiple choice options from text"""
        options = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for a), b), c), d) pattern
            match = re.match(r'^[a-d]\)\s*(.+)', line.strip(), re.IGNORECASE)
            if match:
                options.append(match.group(1).strip())
        
        return options if options else None

class ContentDeduplicator:
    """Remove duplicate content during extraction"""
    
    def __init__(self):
        self.seen_hashes = set()
    
    def is_duplicate(self, content: str) -> bool:
        """Check if content is duplicate based on hash"""
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        if content_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(content_hash)
        return False
    
    def reset(self):
        """Reset the deduplicator for new document"""
        self.seen_hashes.clear()