import re
import json
import os

def parse_text_file(file_path):
    """
    Parses a raw text file to identify chapters, sections, and key terms.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    unit_pattern = r"(Unit\s*\d+|Chapter\s*\d+)\s*[:\-\s]*(.*?)\n"
    chunks = []
    split_content = re.split(f'(?={unit_pattern})', content, flags=re.IGNORECASE)
    current_unit_name = "General"
    for unit_text in split_content:
        if not unit_text.strip():
            continue
        unit_match = re.search(unit_pattern, unit_text, re.IGNORECASE)
        if unit_match:
            unit_number = unit_match.group(1).strip()
            unit_title = unit_match.group(2).strip()
            current_unit_name = f"{unit_number}: {unit_title}"
            unit_content = unit_text[unit_match.end():]
        else:
            unit_content = unit_text
        chunk = {
            "unit_name": current_unit_name,
            "content": unit_content.strip(),
            "source_file": os.path.basename(file_path),
            "key_terms": [],
            "examples": []
        }
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    TEXT_FILE_PATH = 'path/to/your/extracted_text/sample_document.txt'  # <-- UPDATE THIS
    structured_data = parse_text_file(TEXT_FILE_PATH)
    print(json.dumps(structured_data, indent=2))
