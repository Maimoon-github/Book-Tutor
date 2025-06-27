# src/data_loader.py

import os
import re
import logging
from . import config
from typing import Dict, List, Set, Any

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    An advanced, dynamic data loader that discovers and parses complex,
    multi-section chapter files (`chapter_*.txt`).
    """

    def __init__(self):
        self.all_data: Dict[int, Dict[str, Any]] = {}
        self._discover_and_load_chapters()

    def _discover_and_load_chapters(self):
        """Scans the curriculum directory, finds all chapters, and loads them."""
        logger.info(f"Scanning for chapters in: {config.CURRICULUM_PATH}")
        if not os.path.isdir(config.CURRICULUM_PATH):
            logger.critical(f"Curriculum directory not found: {config.CURRICULUM_PATH}")
            return

        chapter_pattern = re.compile(r'chapter_(\d+)\.txt')
        found_chapters: Set[int] = {
            int(match.group(1))
            for filename in os.listdir(config.CURRICULUM_PATH)
            if (match := chapter_pattern.match(filename))
        }

        if not found_chapters:
            logger.error(f"No chapter files found in '{config.CURRICULUM_PATH}'. Ensure files are named 'chapter_1.txt', 'chapter_2.txt', etc.")
            return

        logger.info(f"Discovered chapters: {sorted(list(found_chapters))}")
        for chapter_num in sorted(list(found_chapters)):
            self.all_data[chapter_num] = self._load_and_parse_chapter(chapter_num)

    def _load_and_parse_chapter(self, chapter_num: int) -> Dict[str, Any]:
        """Loads and performs a deep parse on a single chapter file."""
        file_path = os.path.join(config.CURRICULUM_PATH, f'chapter_{chapter_num}.txt')
        chapter_content: Dict[str, Any] = {'title': f"Chapter {chapter_num}", 'warnings': []}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            parsed_data = self._parse_sections(content)
            chapter_content.update(parsed_data)

            # Use the first line of the file as the chapter title if available
            if content.strip():
                first_line = content.strip().split('\n')[0]
                if not first_line.lower().startswith('chapter'):
                    chapter_content['title'] = first_line

        except FileNotFoundError:
            warning_msg = f"File not found for Chapter {chapter_num}: `chapter_{chapter_num}.txt`."
            logger.warning(warning_msg)
            chapter_content['warnings'].append(warning_msg)

        return chapter_content

    def _parse_sections(self, content: str) -> Dict[str, Any]:
        """
        Parses a chapter's full text into a structured dictionary based on headers.
        """
        if not content: return {}

        # Define all possible section headers, case-insensitive
        headers = [
            "Student Learning Outcomes", "PRE-READING", "WHILE-READING",
            "POST-READING", "TEACHER’S NOTE", "Exercises", "POINTS TO PONDER"
        ]

        # Create a robust regex pattern to find these headers at the start of a line
        pattern = re.compile(r'^\s*(' + '|'.join(re.escape(h) for h in headers) + r')\s*$', re.IGNORECASE | re.MULTILINE)

        sections: Dict[str, Any] = {}
        last_pos = 0
        last_key = 'main_content_header' # The very first part of the text

        for match in pattern.finditer(content):
            # The text between the last header and this one belongs to the last key
            section_text = content[last_pos:match.start()].strip()
            if last_key != 'main_content_header': # Don't save empty headers
                 self._assign_section(sections, last_key, section_text)

            # The new key is the header we just found
            last_key = match.group(1).upper().replace(' ', '_')
            last_pos = match.end()

        # Add the final section of content (after the last header)
        final_text = content[last_pos:].strip()
        self._assign_section(sections, last_key, final_text)

        # Special handling for Exercises, which have their own subsections
        if 'EXERCISES' in sections and isinstance(sections['EXERCISES'], str):
            sections['EXERCISES'] = self._parse_exercise_subsections(sections['EXERCISES'])

        return sections

    def _assign_section(self, sections_dict: Dict, key: str, text: str):
        """Helper to assign text to the right key, handling 'WHILE-READING' lists."""
        if not text: return

        # WHILE-READING can appear multiple times, so we store it as a list
        if 'WHILE-READING' in key:
            if 'WHILE-READING' not in sections_dict:
                sections_dict['WHILE-READING'] = []
            sections_dict['WHILE-READING'].append(text)
        else:
            sections_dict[key] = text

    def _parse_exercise_subsections(self, exercise_content: str) -> Dict[str, str]:
        """Parses the content of the 'Exercises' block into its A, B, C, D parts."""
        pattern = re.compile(r'^\s*([A-Z])\s+([A-Za-z\s]+)$', re.MULTILINE)
        return self._parse_generic_subsections(exercise_content, pattern)

    def _parse_generic_subsections(self, content: str, pattern: re.Pattern) -> Dict[str, str]:
        """A generic parser for content with sub-headers."""
        subsections: Dict[str, str] = {}
        last_pos = 0
        last_key = "Introduction"

        for match in pattern.finditer(content):
            subsections[last_key] = content[last_pos:match.start()].strip()
            last_key = f"{match.group(1)} {match.group(2).strip()}"
            last_pos = match.end()

        subsections[last_key] = content[last_pos:].strip()
        return {k: v for k, v in subsections.items() if v}

    def get_all_data(self) -> Dict:
        return self.all_data

    def get_chapter_titles(self) -> Dict[int, str]:
        return {num: data.get('title', f"Chapter {num}") for num, data in self.all_data.items()}

    def get_chapter_data(self, chapter_num: int) -> Dict:
        return self.all_data.get(chapter_num, {})

