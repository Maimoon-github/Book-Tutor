import os
import PyPDF2
import docx

def extract_text_from_file(file_path):
    """
    Extracts all text content from a PDF or DOCX file.
    """
    text = ""
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + " "
        elif file_path.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Could not extract text from {file_path}: {e}")
    return text

def find_curriculum_files(search_path):
    document_files = []
    allowed_extensions = ('.pdf', '.docx')
    for root, _, files in os.walk(search_path):
        for file in files:
            if file.lower().endswith(allowed_extensions):
                document_files.append(os.path.join(root, file))
    return document_files

if __name__ == "__main__":
    SOURCE_FOLDER = 'path/to/your/curriculum/files'  # <-- UPDATE THIS
    OUTPUT_FOLDER = 'path/to/your/extracted_text'    # <-- UPDATE THIS
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    all_curriculum_files = find_curriculum_files(SOURCE_FOLDER)
    print("--- Starting Text Extraction ---")
    for file_path in all_curriculum_files:
        print(f"Processing: {file_path}")
        content = extract_text_from_file(file_path)
        if content:
            base_filename = os.path.basename(file_path)
            output_filename = os.path.splitext(base_filename)[0] + '.txt'
            output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  -> Saved to: {output_filepath}")
    print("--- Text Extraction Complete ---")
