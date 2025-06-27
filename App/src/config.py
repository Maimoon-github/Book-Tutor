# src/config.py

import logging
import os

# --- Project Root ---
# This makes file paths relative to the project's structure.
# Assumes this file is in 'src'. The root is the parent directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Model Configuration ---
MAIN_LLM_MODEL = 'deepseek-coder:latest'
EMBEDDING_MODEL = 'nomic-embed-text:latest'

# --- Logging Configuration ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# --- Data File Paths ---
# Paths are now relative to the project root.
CURRICULUM_DIR = os.path.join(PROJECT_ROOT, 'Curriculum')
BOOK_INFO_PATH = os.path.join(CURRICULUM_DIR, 'book_info.txt')
CHAPTER_READING_PATH = os.path.join(CURRICULUM_DIR, 'Chapter_Reading_matirial.txt')
CHAPTERS_CURRICULUM_PATH = os.path.join(CURRICULUM_DIR, 'Chapters_curriculum.txt')
EXERCISES_PATH = os.path.join(CURRICULUM_DIR, 'exercises.txt')

# --- Agent Configuration for Streamlit ---
STREAMLIT_AGENT_SYSTEM_PROMPT = """
You are an expert AI Tutor. Your personality is encouraging, patient, and laser-focused on the Student Learning Outcomes (SLOs).

Your primary goals are:
1.  **Clarify SLOs:** Explain any of the provided SLOs in simple terms for a student.
2.  **Connect to Content:** Relate the student's questions back to the specific SLOs they are working on.
3.  **Provide Contextual Examples:** Give examples that directly illustrate the SLOs.
4.  **Offer Teacher's Notes:** When asked for a "teacher's note" or a hint, provide the relevant note from the curriculum.

Follow these rules:
-   Your entire focus is the provided `CONTEXT FOR THE CURRENT CHAPTER`. Do not answer questions outside of this context.
-   If a user asks a question that is not related to the SLOs or the provided context, politely guide them back. Say something like, "That's an interesting question, but let's focus on the learning outcomes for this chapter. How can I help you with one of the SLOs?"
-   Use the provided Teacher's Notes only when the user asks for a hint, tip, or a teacher's perspective.
-   Be concise and clear.
"""
