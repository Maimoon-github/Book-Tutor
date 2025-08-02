import os
import gradio as gr
import re

# Path to the curriculum folder
CURRICULUM_DIR = os.path.join(os.path.dirname(__file__), '..', 'Curriculum')
# List all chapter text files matching pattern chapter_*.txt
chapter_files = [f for f in os.listdir(CURRICULUM_DIR) if f.startswith('chapter_') and f.endswith('.txt')]
# Sort files by chapter number
chapter_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
# Map display names to file names
chapter_names = [f"Chapter {int(f.split('_')[1].split('.')[0])}" for f in chapter_files]
chapter_map = dict(zip(chapter_names, chapter_files))

# Define main headers in each chapter file
MAIN_SECTIONS = [
    "Student Learning Outcomes",
    "Reading Material",
    "Exercise Material"
]

# Define reading sub-sections
READING_SUBSECTIONS = [
    "Pre-reading Questions",
    "While-reading Questions",
    "Post-reading Questions"
]

def parse_reading_section(text):
    """Parse the Reading Material section into main content and sub-sections."""
    result = {"main": "", "Pre-reading Questions": "", "While-reading Questions": "", "Post-reading Questions": ""}
    if not text:
        return result

    # Split the reading section by the sub-section headers
    pattern = "(" + "|".join(map(re.escape, READING_SUBSECTIONS)) + ")"
    parts = re.split(pattern, text)
    # The text before the first sub-header is the main reading content
    result["main"] = parts[0].strip() if parts[0].strip() else ""
    # Process the sub-section header-content pairs
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i].strip()
            content = parts[i+1].strip()
            result[header] = content
    return result

def parse_chapter_content(content):
    """Parse chapter content into main sections (Student Learning Outcomes, Reading Material, Exercise Material).
    The Reading Material section is further parsed into its sub-sections.
    """
    sections = {}
    pattern = "(" + "|".join(map(re.escape, MAIN_SECTIONS)) + ")"
    parts = re.split(pattern, content)

    # If there is any introduction content before the first header, save it as "Introduction"
    if parts[0].strip():
        sections["Introduction"] = parts[0].strip()

    # Process headers: each header is followed by its content
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i].strip()
            section_content = parts[i+1].strip()
            sections[header] = section_content

    # If Reading Material is defined, further parse its sub-sections
    if "Reading Material" in sections:
        reading_parts = parse_reading_section(sections["Reading Material"])
        sections["Reading Material"] = reading_parts["main"]
        sections.update({
            "Pre-reading Questions": reading_parts["Pre-reading Questions"],
            "While-reading Questions": reading_parts["While-reading Questions"],
            "Post-reading Questions": reading_parts["Post-reading Questions"]
        })

    return sections

def load_chapter(chapter_name):
    """Read and return the parsed content of the selected chapter."""
    file_name = chapter_map.get(chapter_name)
    file_path = os.path.join(CURRICULUM_DIR, file_name)
    with open(file_path, 'r') as f:
        content = f.read()
    return parse_chapter_content(content)

# Build Gradio interface
def build_interface():
    with gr.Blocks(title="Book Tutor Curriculum") as iface:
        gr.Markdown("# Book Tutor Curriculum")
        gr.Markdown("Select a chapter to view its content.")

        chapter_dropdown = gr.Dropdown(choices=chapter_names, label="Select Chapter")

        # Student Learning Outcomes at the top
        with gr.Column():
            gr.Markdown("### Student Learning Outcomes")
            learning_outcomes = gr.Textbox(label="", interactive=False)

        # Create tabs for Reading Material and Exercise Material
        with gr.Tabs():
            # Reading Material tab
            with gr.TabItem("Reading Material"):
                reading_content = gr.Textbox(label="Main Reading Content", interactive=False)
                with gr.Accordion("Pre-reading Questions", open=False):
                    pre_reading = gr.Textbox(interactive=False)
                with gr.Accordion("While-reading Questions", open=False):
                    while_reading = gr.Textbox(interactive=False)
                with gr.Accordion("Post-reading Questions", open=False):
                    post_reading = gr.Textbox(interactive=False)

            # Exercise Material tab
            with gr.TabItem("Exercise Material"):
                exercise_content = gr.Textbox(label="Exercises", interactive=False)

        def update_display(chapter_name):
            sections = load_chapter(chapter_name)

            outcomes = sections.get("Student Learning Outcomes", "No learning outcomes available")
            reading = sections.get("Reading Material", "No reading material available")
            pre_q = sections.get("Pre-reading Questions", "No pre-reading questions available")
            while_q = sections.get("While-reading Questions", "No while-reading questions available")
            post_q = sections.get("Post-reading Questions", "No post-reading questions available")
            exercises = sections.get("Exercise Material", "No exercise materials available")

            return [outcomes, reading, pre_q, while_q, post_q, exercises]

        chapter_dropdown.change(
            fn=update_display,
            inputs=[chapter_dropdown],
            outputs=[learning_outcomes, reading_content, pre_reading, while_reading, post_reading, exercise_content]
        )

    return iface

if __name__ == "__main__":
    interface = build_interface()
    interface.launch()
