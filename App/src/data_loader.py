# src/data_loader.py

import re
import logging
from .config import (
    BOOK_INFO_PATH,
    CHAPTER_READING_PATH,
    CHAPTERS_CURRICULUM_PATH,
    EXERCISES_PATH,
    LOG_LEVEL,
    LOG_FORMAT
)
from typing import Dict, List

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading and parsing of all curriculum data from text files."""

    def __init__(self):
        """Initializes the DataLoader and loads all data."""
        self.all_data = {}
        self.chapter_titles = {}
        self._load_all_data()

    def _read_file(self, file_path: str) -> str:
        """Reads content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File not found at {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""

    def _parse_by_chapter(self, content: str) -> Dict[int, str]:
        """Parses content that is structured with 'Chapter X' headings."""
        pattern = r'(?i)chapter\s*#?\s*:?\s*(\d+)'
        parts = re.split(pattern, content)
        data = {}
        if len(parts) > 1:
            items = parts[1:]
            for i in range(0, len(items), 2):
                try:
                    chapter_num = int(items[i].strip())
                    chapter_content = items[i+1].strip()
                    data[chapter_num] = chapter_content
                except (ValueError, IndexError):
                    continue
        return data

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parses content within a single chapter into sections like
        'pre_reading', 'while_reading', 'post_reading', 'teacher_note'.
        """
        # Define the possible sections in the order they might appear
        section_keywords = [
            'pre-reading questions', 'while-reading questions',
            'post-reading questions', "teacher's note"
        ]

        content_lower = content.lower()
        sections = {}
        last_pos = 0

        # A regex to find the start of our sections
        pattern = r'(?i)(' + '|'.join(re.escape(key) for key in section_keywords) + r')'

        splits = list(re.finditer(pattern, content))

        # Add the main reading text before the first section
        first_section_start = splits[0].start() if splits else len(content)
        sections['main_reading'] = content[:first_section_start].strip()

        # Extract content for each section
        for i, match in enumerate(splits):
            section_name_raw = match.group(1).lower()
            section_name = section_name_raw.replace(' ', '_').replace("'", "")

            start_pos = match.end()
            end_pos = splits[i+1].start() if i + 1 < len(splits) else len(content)

            section_content = content[start_pos:end_pos].strip(': \n').strip()
            sections[section_name] = section_content

        return sections

    def _load_all_data(self):
        """Loads and processes all curriculum files."""
        # Load book info for chapter titles
        book_info_content = self._read_file(BOOK_INFO_PATH)
        for line in book_info_content.splitlines():
            match = re.match(r'Chapter (\d+): (.+)', line)
            if match:
                self.chapter_titles[int(match.group(1))] = match.group(2).strip()

        # Load and parse other curriculum files
        reading_content = self._read_file(CHAPTER_READING_PATH)
        curriculum_content = self._read_file(CHAPTERS_CURRICULUM_PATH)
        exercises_content = self._read_file(EXERCISES_PATH)

        readings_by_chapter = self._parse_by_chapter(reading_content)
        outcomes_by_chapter = self._parse_by_chapter(curriculum_content)
        exercises_raw_by_chapter = self._parse_by_chapter(exercises_content)

        all_chapter_nums = set(self.chapter_titles.keys()) | set(readings_by_chapter.keys())

        for num in sorted(list(all_chapter_nums)):
            # Parse sections within the reading material and exercises
            reading_sections = self._parse_sections(readings_by_chapter.get(num, ""))
            exercise_sections = self._parse_sections(exercises_raw_by_chapter.get(num, ""))

            self.all_data[num] = {
                'title': self.chapter_titles.get(num, f"Chapter {num}"),
                'reading': reading_sections,
                'outcomes': outcomes_by_chapter.get(num, "Not available."),
                'exercises': exercise_sections
            }
        logger.info(f"Loaded data for chapters: {list(self.all_data.keys())}")

    def get_chapter_titles(self) -> Dict[int, str]:
        return self.chapter_titles

    def get_chapter_data(self, chapter_num: int) -> Dict:
        return self.all_data.get(chapter_num, {})

    def get_all_data(self) -> Dict:
        return self.all_data

