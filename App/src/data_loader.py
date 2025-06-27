# src/data_loader.py

import re
import logging
from .config import (
    BOOK_INFO_PATH,
    CHAPTER_READING_PATH,
    CHAPTERS_CURRICULUM_PATH,
    EXERCISES_PATH
)
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    """
    An advanced data loader designed to parse the specific, complex structure
    of the curriculum text files.
    """

    def __init__(self):
        self.all_data: Dict[int, Dict] = {}
        self._load_all_data()

    def _read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"CRITICAL: File not found at {file_path}. The application cannot continue without this file.")
            return ""

    def _parse_master_file(self, content: str) -> Dict[int, str]:
        """Splits a file's entire content into a dictionary keyed by chapter number."""
        # This regex is designed to find "Chapter # X" or "Chapter X" at the start of a line.
        pattern = r'^(Chapter\s*#?\s*\d+.*)$'
        # re.MULTILINE allows '^' to match the start of each line.
        chapters = re.split(pattern, content, flags=re.MULTILINE)

        data: Dict[int, str] = {}
        if len(chapters) > 1:
            # The list is [prologue, chapter_1_header, chapter_1_content, chapter_2_header, ...]
            items = chapters[1:]
            for i in range(0, len(items), 2):
                header = items[i]
                chapter_content = items[i+1]
                # Extract chapter number from the header
                match = re.search(r'\d+', header)
                if match:
                    chapter_num = int(match.group(0))
                    # Combine header and content for full context
                    data[chapter_num] = (header + "\n" + chapter_content).strip()
        return data

    def _parse_chapter_sections(self, content: str) -> Dict[str, str]:
        """
        Parses the text of a single chapter into its constituent parts
        (e.g., Teacher's Note, Reading, Exercises).
        """
        if not content:
            return {}

        # Define the keywords that start each section, ordered by likely appearance.
        # This will be used to split the text. Case-insensitive.
        keywords = [
            "Teacher’s Note", "Pre-Reading", "While-Reading", "Post-Reading",
            "Reading:", "EXERCISE", "Point to Ponder", "Oral Communication",
            "Reading and Critical Analysis", "Language Check", "Writing Skills",
            "Students' Learning Outcomes"
        ]

        # Create a regex pattern that finds any of these keywords at the start of a line.
        pattern = r'^\s*(' + '|'.join(re.escape(key) for key in keywords) + r')'

        # Split the content by these keywords
        splits = re.split(pattern, content, flags=re.IGNORECASE | re.MULTILINE)

        sections: Dict[str, str] = {}
        # The first element is any text before the first keyword (like the chapter title)
        if splits[0].strip():
            sections['header'] = splits[0].strip()

        if len(splits) > 1:
            items = splits[1:]
            for i in range(0, len(items), 2):
                key = items[i].strip().title() # e.g., "Teacher’S Note" -> "Teacher'S Note"
                # Clean up the key name for consistency
                key = re.sub(r'[^a-zA-Z0-9\s]', '', key).replace(' ', '_')
                value = items[i+1].strip()
                sections[key] = value

        return sections

    def _load_all_data(self):
        """Loads all text files and orchestrates the parsing."""
        logger.info("Starting data loading process...")

        # Read all master files
        reading_material_content = self._read_file(CHAPTER_READING_PATH)
        curriculum_content = self._read_file(CHAPTERS_CURRICULUM_PATH)
        exercises_content = self._read_file(EXERCISES_PATH)

        # Split each master file into chapters
        readings_by_chapter = self._parse_master_file(reading_material_content)
        outcomes_by_chapter = self._parse_master_file(curriculum_content)
        exercises_by_chapter = self._parse_master_file(exercises_content)

        all_chapter_nums = set(readings_by_chapter.keys()) | set(outcomes_by_chapter.keys()) | set(exercises_by_chapter.keys())

        if not all_chapter_nums:
            logger.error("No chapters could be parsed from any file. Please check file formatting.")
            return

        for num in sorted(list(all_chapter_nums)):
            # For each chapter, parse its content into detailed sections
            reading_sections = self._parse_chapter_sections(readings_by_chapter.get(num, ""))
            outcome_sections = self._parse_chapter_sections(outcomes_by_chapter.get(num, ""))
            exercise_sections = self._parse_chapter_sections(exercises_by_chapter.get(num, ""))

            # Extract a clean title from the header, default to "Chapter X"
            title = reading_sections.get('header', f"Chapter {num}").split('\n')[0]

            self.all_data[num] = {
                'title': title,
                'reading_material': reading_sections,
                'learning_outcomes': outcome_sections,
                'exercises_and_notes': exercise_sections
            }

        logger.info(f"Successfully loaded and structured data for chapters: {list(self.all_data.keys())}")

    def get_chapter_titles(self) -> Dict[int, str]:
        return {num: data['title'] for num, data in self.all_data.items()}

    def get_chapter_data(self, chapter_num: int) -> Dict:
        return self.all_data.get(chapter_num, {})

    def get_all_data(self) -> Dict:
        return self.all_data
