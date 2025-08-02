import os
import json
import re
from typing import Dict, Any, List

class CurriculumLoader:
    """
    Utility class for loading and processing curriculum content from files.
    """

    def __init__(self, curriculum_dir):
        """
        Initialize the CurriculumLoader.

        Args:
            curriculum_dir: Directory containing curriculum files
        """
        self.curriculum_dir = curriculum_dir

    def load_curriculum_structure(self):
        """
        Load the overall curriculum structure with chapters and their metadata.

        Returns:
            Dict with curriculum structure
        """
        # Load the chapters curriculum file to get learning outcomes
        chapters_curriculum_path = os.path.join(self.curriculum_dir, "Chapters_curriculum.txt")
        curriculum_data = self._parse_chapters_curriculum(chapters_curriculum_path)

        # Load book information
        book_info_path = os.path.join(self.curriculum_dir, "book_info.txt")
        book_info = self._load_book_info(book_info_path)

        # Find all chapter files
        chapter_files = {}
        for filename in os.listdir(self.curriculum_dir):
            if filename.startswith("chapter_") and filename.endswith(".txt"):
                chapter_number = int(filename.split("_")[1].split(".")[0])
                chapter_files[chapter_number] = os.path.join(self.curriculum_dir, filename)

        # Create curriculum structure
        curriculum = {
            "book_info": book_info,
            "chapters": {}
        }

        # Add chapters with their metadata
        for chapter_number, file_path in chapter_files.items():
            chapter_title = self._extract_chapter_title(file_path)
            curriculum["chapters"][chapter_number] = {
                "id": chapter_number,
                "title": chapter_title,
                "content_path": file_path,
                "learning_outcomes": curriculum_data.get(chapter_number, {}).get("learning_outcomes", [])
            }

        return curriculum

    def load_chapter_content(self, chapter_id):
        """
        Load the content for a specific chapter.

        Args:
            chapter_id: ID of the chapter to load

        Returns:
            Dict with chapter content structured into sections
        """
        curriculum = self.load_curriculum_structure()

        if chapter_id not in curriculum["chapters"]:
            raise ValueError(f"Chapter {chapter_id} not found in curriculum")

        chapter_info = curriculum["chapters"][chapter_id]
        content_path = chapter_info["content_path"]

        with open(content_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Parse the chapter content into sections
        sections = self._parse_chapter_content(raw_content)

        return {
            "id": chapter_id,
            "title": chapter_info["title"],
            "learning_outcomes": chapter_info["learning_outcomes"],
            "sections": sections
        }

    def _parse_chapters_curriculum(self, file_path):
        """
        Parse the chapters curriculum file to extract learning outcomes.

        Args:
            file_path: Path to the chapters curriculum file

        Returns:
            Dict with chapter learning outcomes
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by chapter
            chapters_data = {}
            chapter_blocks = content.split("Chapter ")

            for block in chapter_blocks:
                if not block.strip():
                    continue

                # Extract chapter number
                match = re.match(r"(\d+)\s+curriculum:", block)
                if match:
                    chapter_number = int(match.group(1))

                    # Extract learning outcomes
                    outcomes = []
                    if "Students' Learning Outcomes" in block:
                        outcomes_section = block.split("Students' Learning Outcomes")[1].split("\n\n")[0]
                        for line in outcomes_section.split("\n"):
                            if "•" in line:
                                outcome = line.split("•")[1].strip()
                                if outcome:
                                    outcomes.append(outcome)

                    chapters_data[chapter_number] = {
                        "learning_outcomes": outcomes
                    }

            return chapters_data

        except Exception as e:
            print(f"Error parsing chapters curriculum: {str(e)}")
            return {}

    def _load_book_info(self, file_path):
        """
        Load book information from the book_info.txt file.

        Args:
            file_path: Path to the book info file

        Returns:
            Dict with book information
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract basic book information
            lines = content.strip().split("\n")
            book_info = {
                "grade": lines[0] if len(lines) > 0 else "Unknown",
                "title": " ".join(lines[1:3]) if len(lines) > 2 else "Unknown",
                "curriculum": lines[3] if len(lines) > 3 else "Unknown"
            }

            return book_info

        except Exception as e:
            print(f"Error loading book info: {str(e)}")
            return {
                "grade": "Unknown",
                "title": "Unknown",
                "curriculum": "Unknown"
            }

    def _extract_chapter_title(self, file_path):
        """
        Extract the title of a chapter from its file.

        Args:
            file_path: Path to the chapter file

        Returns:
            Chapter title as a string
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()

            # Check if the first line contains the chapter title
            if first_line.startswith("Chapter "):
                return first_line.split(": ")[1] if ":" in first_line else first_line
            else:
                return f"Chapter {os.path.basename(file_path).split('_')[1].split('.')[0]}"

        except Exception as e:
            print(f"Error extracting chapter title: {str(e)}")
            return f"Chapter {os.path.basename(file_path).split('_')[1].split('.')[0]}"

    def _parse_chapter_content(self, raw_content):
        """
        Parse the raw chapter content into structured sections.

        Args:
            raw_content: Raw text content of the chapter

        Returns:
            List of section dictionaries
        """
        sections = []

        # Identify main sections
        pre_reading_match = re.search(r"PRE-READING(.*?)WHILE-READING", raw_content, re.DOTALL)
        while_reading_match = re.search(r"WHILE-READING(.*?)POST-READING", raw_content, re.DOTALL)
        post_reading_match = re.search(r"POST-READING(.*?)TEACHER'S NOTE", raw_content, re.DOTALL)
        exercises_match = re.search(r"Exercises(.*?)$", raw_content, re.DOTALL)

        # Extract pre-reading content
        if pre_reading_match:
            pre_reading_content = pre_reading_match.group(1).strip()
            sections.append({
                "type": "pre-reading",
                "content": pre_reading_content,
                "items": self._extract_numbered_items(pre_reading_content)
            })

        # Extract while-reading content
        if while_reading_match:
            while_reading_content = while_reading_match.group(1).strip()
            sections.append({
                "type": "while-reading",
                "content": while_reading_content,
                "paragraphs": self._split_paragraphs(while_reading_content)
            })

        # Extract post-reading content
        if post_reading_match:
            post_reading_content = post_reading_match.group(1).strip()
            sections.append({
                "type": "post-reading",
                "content": post_reading_content,
                "items": self._extract_numbered_items(post_reading_content)
            })

        # Extract exercises
        if exercises_match:
            exercises_content = exercises_match.group(1).strip()
            sections.append({
                "type": "exercises",
                "content": exercises_content,
                "subsections": self._extract_exercise_subsections(exercises_content)
            })

        return sections

    def _extract_numbered_items(self, content):
        """
        Extract numbered items from content.

        Args:
            content: The content to extract items from

        Returns:
            List of items
        """
        items = []

        # Look for roman numerals (i, ii, iii) or other numbering patterns
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if re.match(r"^[ivxIVX]+\)", line) or re.match(r"^[ivxIVX]+\.", line):
                items.append(line)
            elif re.match(r"^\d+\.", line) or re.match(r"^\d+\)", line):
                items.append(line)

        return items

    def _split_paragraphs(self, content):
        """
        Split content into paragraphs.

        Args:
            content: The content to split

        Returns:
            List of paragraphs
        """
        # Split by double newlines or other paragraph separators
        raw_paragraphs = re.split(r"\n\s*\n", content)

        # Clean up each paragraph
        paragraphs = []
        for para in raw_paragraphs:
            cleaned = para.strip()
            if cleaned:
                paragraphs.append(cleaned)

        return paragraphs

    def _extract_exercise_subsections(self, content):
        """
        Extract subsections from exercises.

        Args:
            content: The exercise content

        Returns:
            Dict of subsections
        """
        subsections = {}

        # Look for exercise section headers (e.g., "A Oral Communication")
        section_matches = re.finditer(r"([A-Z])\s+([\w\s]+)\n", content)

        last_pos = 0
        for match in section_matches:
            section_letter = match.group(1)
            section_name = match.group(2).strip()
            start_pos = match.start()

            # If this isn't the first section, extract the content of the previous section
            if last_pos > 0:
                prev_section_content = content[last_pos:start_pos].strip()
                prev_section_letter = content[last_pos:last_pos+1]
                prev_section_name = re.search(r"([A-Z])\s+([\w\s]+)\n", content[last_pos-2:last_pos+30])
                if prev_section_name:
                    prev_section_name = prev_section_name.group(2).strip()
                    subsections[f"{prev_section_letter} {prev_section_name}"] = prev_section_content

            last_pos = start_pos

        # Extract the content of the last section
        if last_pos > 0:
            last_section_content = content[last_pos:].strip()
            last_section_letter = content[last_pos:last_pos+1]
            last_section_name = re.search(r"([A-Z])\s+([\w\s]+)\n", content[last_pos-2:last_pos+30])
            if last_section_name:
                last_section_name = last_section_name.group(2).strip()
                subsections[f"{last_section_letter} {last_section_name}"] = last_section_content

        return subsections
