# src/data_loader.py

import re
import logging
# FIXED: Import the entire config module instead of individual variables.
# This is a more robust pattern that avoids many common import errors.
from . import config
from typing import Dict, List

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
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
            logger.error(f"CRITICAL: File not found at {file_path}. Please ensure the file exists and the path in 'config.py' is correct.")
            return ""

    def _parse_master_file(self, content: str) -> Dict[int, str]:
        """Splits a file's content into a dictionary keyed by chapter number."""
        pattern = r'^(Chapter\s*#?\s*\d+.*)$'
        chapters = re.split(pattern, content, flags=re.MULTILINE)
        data: Dict[int, str] = {}
        if len(chapters) > 1:
            items = chapters[1:]
            for i in range(0, len(items), 2):
                header, chapter_content = items[i], items[i+1]
                match = re.search(r'\d+', header)
                if match:
                    chapter_num = int(match.group(0))
                    data[chapter_num] = (header + "\n" + chapter_content).strip()
        return data

    def _parse_chapter_sections(self, content: str) -> Dict[str, str]:
        """Parses a single chapter's text into its constituent parts."""
        if not content: return {}
        keywords = [
            "Teacher’s Note", "Pre-Reading", "While-Reading", "Post-Reading",
            "Reading:", "EXERCISE", "Point to Ponder", "Oral Communication",
            "Reading and Critical Analysis", "Language Check", "Writing Skills",
            "Students' Learning Outcomes"
        ]
        pattern = r'^\s*(' + '|'.join(re.escape(key) for key in keywords) + r')'
        splits = re.split(pattern, content, flags=re.IGNORECASE | re.MULTILINE)

        sections: Dict[str, str] = {'header': splits[0].strip()}
        if len(splits) > 1:
            items = splits[1:]
            for i in range(0, len(items), 2):
                key = re.sub(r'[^a-zA-Z0-9\s]', '', items[i].strip().title()).replace(' ', '_')
                sections[key] = items[i+1].strip()
        return sections

    def _load_all_data(self):
        """Loads all text files and orchestrates the parsing."""
        logger.info("Starting data loading process...")

        # FIXED: Access path variables through the imported 'config' module.
        reading_material = self._read_file(config.CHAPTER_READING_PATH)
        curriculum = self._read_file(config.CHAPTERS_CURRICULUM_PATH)
        exercises = self._read_file(config.EXERCISES_PATH)

        readings_by_chapter = self._parse_master_file(reading_material)
        outcomes_by_chapter = self._parse_master_file(curriculum)
        exercises_by_chapter = self._parse_master_file(exercises)

        all_chapter_nums = set(readings_by_chapter.keys()) | set(outcomes_by_chapter.keys()) | set(exercises_by_chapter.keys())

        if not all_chapter_nums:
            logger.error("No chapters could be parsed. Check that your text files contain 'Chapter X' headings.")
            return

        for num in sorted(list(all_chapter_nums)):
            reading_sections = self._parse_chapter_sections(readings_by_chapter.get(num, ""))
            outcome_sections = self._parse_chapter_sections(outcomes_by_chapter.get(num, ""))
            exercise_sections = self._parse_chapter_sections(exercises_by_chapter.get(num, ""))

            title = reading_sections.get('header', f"Chapter {num}").split('\n')[0]

            self.all_data[num] = {
                'title': title,
                'reading_material': reading_sections,
                'learning_outcomes': outcome_sections,
                'exercises_and_notes': exercise_sections
            }

        logger.info(f"Successfully structured data for chapters: {list(self.all_data.keys())}")

    def get_chapter_titles(self) -> Dict[int, str]:
        return {num: data['title'] for num, data in self.all_data.items()}

    def get_chapter_data(self, chapter_num: int) -> Dict:
        return self.all_data.get(chapter_num, {})

    def get_all_data(self) -> Dict:
        return self.all_data
