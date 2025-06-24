import os
import PyPDF2
import docx

def find_curriculum_files(search_path):
    """
    Finds all PDF and DOCX files in a directory and its subdirectories.
    """
    document_files = []
    allowed_extensions = ('.pdf', '.docx')
    for root, _, files in os.walk(search_path):
        for file in files:
            if file.lower().endswith(allowed_extensions):
                document_files.append(os.path.join(root, file))
    return document_files

def verify_slo_presence(file_path):
    """
    Checks if "Student Learning Outcomes" is mentioned in a document.
    """
    text = ""
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        elif file_path.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    return "student learning outcomes" in text.lower()

if __name__ == "__main__":
    CURRICULUM_FOLDER = input('ENTER YOUR PDF :  -->    ')  # <-- UPDATE THIS
    all_files = find_curriculum_files(CURRICULUM_FOLDER)
    print("--- Curriculum File Inspection ---")
    if not all_files:
        print(f"No documents found in '{CURRICULUM_FOLDER}'. Please check the path.")
    else:
        for file_path in all_files:
            has_slos = verify_slo_presence(file_path)
            print(f"File: {file_path} | Contains SLOs: {has_slos}")
