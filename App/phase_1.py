# phase_1_pipeline.py
# This script fulfills the requirements for "Phase 1: Data Preparation & Knowledge Base Creation".
# It ingests curriculum files, parses them into detailed sections (SLOs, readings, exercises),
# extracts key terms, allows for metadata tagging, and populates a structured SQLite database.

import os
import json
import re
import sqlite3
import PyPDF2
import docx

# --- Configuration ---
# 1. Folder for original .pdf and .docx curriculum files.
CURRICULUM_SOURCE_FOLDER = 'curriculum_files'
# 2. Folder for intermediate raw .txt files.
TEXT_OUTPUT_FOLDER = 'extracted_text'
# 3. Path for the final SQLite database.
SQLITE_DB_PATH = 'knowledge_base.db'
# --- End of Configuration ---


# === STAGE 1: INGEST CURRICULUM FILES ===

def ingest_files(search_path):
    """
    Locates all PDF/DOCX files and records their filename and format.

    Args:
        search_path (str): The directory to search for curriculum files.

    Returns:
        list: A list of dictionaries, each containing info about a file.
    """
    discovered_files = []
    allowed_extensions = {'.pdf': 'PDF', '.docx': 'DOCX'}
    print("--- Stage 1: Ingesting Curriculum Files ---")
    if not os.path.exists(search_path):
        os.makedirs(search_path)
        print(f"Created directory: {search_path}")
        print("Please add your curriculum files to this folder and run the script again.")
        return []

    for root, _, files in os.walk(search_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_extensions:
                file_path = os.path.join(root, file)
                # Basic unit identifier from filename (can be customized)
                unit_identifier = os.path.splitext(file)[0]
                discovered_files.append({
                    'file_path': file_path,
                    'filename': file,
                    'format': allowed_extensions[ext],
                    'unit_identifier': unit_identifier,
                    'text_output_path': os.path.join(TEXT_OUTPUT_FOLDER, f"{unit_identifier}.txt")
                })
                print(f"  - Found: {file} (Format: {allowed_extensions[ext]})")

    if not discovered_files:
        print("No curriculum files found. Please add files to the source folder.")

    return discovered_files

def extract_raw_text(file_info):
    """
    Extracts raw text from a file and saves it to a .txt file.
    This step normalizes all documents into a single format for parsing.
    """
    text = ""
    file_path = file_info['file_path']
    try:
        if file_info['format'] == 'PDF':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n\n"
        elif file_info['format'] == 'DOCX':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])

        # Save the extracted text
        with open(file_info['text_output_path'], 'w', encoding='utf-8') as f:
            f.write(text)
        return text
    except Exception as e:
        print(f"  - ERROR: Could not extract text from {file_info['filename']}: {e}")
        return None

# === STAGE 2: PARSE & STRUCTURE CONTENT ===

def parse_and_structure_content(text, unit_identifier):
    """
    Parses raw text into logical sections based on predefined patterns.

    Args:
        text (str): The raw text content of a document.
        unit_identifier (str): The identifier for the book unit.

    Returns:
        dict: A structured record for the unit, containing parsed sections.
    """
    # Regex patterns to identify different section headers.
    # These will need to be adjusted based on the actual document format.
    patterns = {
        'chapter_title': r"^(Chapter\s*\d+|Unit\s*\d+)\s*[:\-\s]*(.*?)$",
        'slo': r"^(Student\s*Learning\s*Outcomes|Learning\s*Objectives)\s*[:\s]*$",
        'key_terms': r"^(Key\s*Terms|Vocabulary)\s*[:\s]*$",
        'exercises': r"^(Exercises|Practice\s*Problems|Activities)\s*[:\s]*$"
    }

    lines = text.split('\n')
    sections = []
    current_section = None
    current_content = []

    def save_current_section():
        """Helper to save the currently accumulating section."""
        if current_section and current_content:
            content_str = "\n".join(current_content).strip()
            if content_str:
                current_section['content'] = content_str
                # Also extract key terms from the content
                current_section['key_terms'] = extract_key_terms(content_str, current_section['type'])
                sections.append(current_section)

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped: continue

        matched_type = None
        for sec_type, pattern in patterns.items():
            match = re.match(pattern, line_stripped, re.IGNORECASE)
            if match:
                # A new section header is found. Save the previous one.
                save_current_section()

                # Start a new section
                current_section = {'type': sec_type, 'title': line_stripped}
                current_content = []
                # If it's a chapter title, capture the title content from the regex
                if sec_type == 'chapter_title':
                    current_section['title'] = match.group(2).strip() or match.group(1).strip()

                matched_type = sec_type
                break

        if not matched_type:
            # If the line is not a section header, add it to the current section's content.
            if current_section is None:
                # Content before any recognized header is treated as a reading passage.
                save_current_section()
                current_section = {'type': 'reading_passage', 'title': 'Introduction'}
                current_content = [line]
            else:
                current_content.append(line)

    # Save the very last section after the loop finishes
    save_current_section()

    return {
        'unit_identifier': unit_identifier,
        'sections': sections
    }

def extract_key_terms(content, section_type):
    """
    Extracts key terms from a block of content.
    This is a simple implementation that can be expanded with more advanced NLP.
    """
    # If the section is a "key_terms" section, we can treat each line as a term.
    if section_type == 'key_terms':
        # Assumes terms are separated by newlines, possibly with definitions.
        terms = [re.split(r'[:\-\s]+', line)[0].strip() for line in content.split('\n') if line.strip()]
        return list(filter(None, terms))

    # For other sections, this could use more advanced methods. For now, returns an empty list.
    return []


# === STAGE 3: TAG METADATA ===

def tag_metadata_manually(structured_record):
    """
    Prompts the user to add learning objectives to each section in a record.
    """
    print("\n" + "---" * 20)
    print(f"--- Stage 3: Tagging Metadata for Unit: {structured_record['unit_identifier']} ---")

    for section in structured_record['sections']:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Tagging Section: '{section['title']}' (Type: {section['type']})")
        print("Content Preview:")
        print(section['content'][:400] + "...")
        print("-" * 20)

        objectives = input("-> Enter Learning Objective(s) (comma-separated), or leave blank: ")

        # Add metadata to the section
        section['metadata'] = {
            'learning_objectives': [obj.strip() for obj in objectives.split(',') if obj.strip()]
        }
        print("Metadata added successfully.\n")

    return structured_record


# === STAGE 4: POPULATE THE KNOWLEDGE BASE ===

def create_knowledge_base(db_path):
    """
    Creates the SQLite database and the 'knowledge_base' table.
    """
    print("\n--- Stage 4: Populating the Knowledge Base ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # The table stores one record per book unit.
    # The structured content (sections, terms, metadata) is stored as a JSON string.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY,
        unit_identifier TEXT NOT NULL UNIQUE,
        source_filename TEXT,
        structured_content TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print(f"Knowledge base created or verified at: {db_path}")

def save_record_to_kb(db_path, tagged_record, source_filename):
    """
    Saves a single, fully processed record to the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Convert the structured content dictionary to a JSON string for storage.
    content_json = json.dumps(tagged_record, indent=4)

    # Use INSERT OR REPLACE to add new records or update existing ones.
    cursor.execute('''
    INSERT OR REPLACE INTO knowledge_base (unit_identifier, source_filename, structured_content)
    VALUES (?, ?, ?)
    ''', (
        tagged_record['unit_identifier'],
        source_filename,
        content_json
    ))

    conn.commit()
    conn.close()
    print(f"  - Saved record for unit '{tagged_record['unit_identifier']}' to the database.")

# === MAIN PIPELINE EXECUTION ===

def run_full_pipeline():
    """Executes the entire data preparation and knowledge base creation pipeline."""

    # --- Setup ---
    if not os.path.exists(TEXT_OUTPUT_FOLDER):
        os.makedirs(TEXT_OUTPUT_FOLDER)

    # --- STAGE 1 ---
    discovered_files = ingest_files(CURRICULUM_SOURCE_FOLDER)
    if not discovered_files:
        return

    # --- STAGE 4 (Setup) ---
    create_knowledge_base(SQLITE_DB_PATH)

    # --- Process Each File Through Stages 2, 3, and 4 ---
    for file_info in discovered_files:
        print(f"\nProcessing file: {file_info['filename']}")

        # --- STAGE 2 (Part 1: Text Extraction) ---
        print("  - Extracting raw text...")
        raw_text = extract_raw_text(file_info)
        if not raw_text:
            continue

        # --- STAGE 2 (Part 2: Parsing) ---
        print("  - Parsing and structuring content...")
        structured_record = parse_and_structure_content(raw_text, file_info['unit_identifier'])
        print(f"  - Parsed into {len(structured_record['sections'])} sections.")

        # --- STAGE 3 (Tagging) ---
        tagged_record = tag_metadata_manually(structured_record)

        # --- STAGE 4 (Population) ---
        save_record_to_kb(SQLITE_DB_PATH, tagged_record, file_info['filename'])

    print("\n--- Pipeline Finished Successfully! ---")
    print(f"Deliverable: Your knowledge base is ready at '{SQLITE_DB_PATH}'.")
    print("You can now use this database for semantic search and other AI tasks.")


if __name__ == "__main__":
    run_full_pipeline()
