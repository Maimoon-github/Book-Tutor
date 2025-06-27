# src/config.py

import logging
import os

# --- Project Root ---
# This defines the absolute path to the project's root directory (the parent of 'src').
# This is crucial for making file paths portable and not hardcoded.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Model Configuration ---
MAIN_LLM_MODEL = 'deepseek-coder:latest'
EMBEDDING_MODEL = 'nomic-embed-text:latest'

# --- Logging Configuration ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# --- Data File Paths ---
# CORRECTED: All paths are now correctly and portably built relative to the PROJECT_ROOT.
# This ensures the app can find the files regardless of where the project is located.
CURRICULUM_DIR = os.path.join(PROJECT_ROOT, '/home/maimoon/Documents/Project Repos/Book-Tutor/App/Curriculum')
BOOK_INFO_PATH = os.path.join(CURRICULUM_DIR, 'book_info.txt')
CHAPTER_READING_PATH = os.path.join(CURRICULUM_DIR, 'Chapter_Reading_matirial.txt')
CHAPTERS_CURRICULUM_PATH = os.path.join(CURRICULUM_DIR, 'Chapters_curriculum.txt')
EXERCISES_PATH = os.path.join(CURRICULUM_DIR, 'exercises.txt')

# --- Agent Configuration for Streamlit ---
# This prompt is the "brain" of the AI tutor.
STREAMLIT_AGENT_SYSTEM_PROMPT = """
You are an expert AI Tutor for Grade 5 English. Your personality is encouraging, patient, and laser-focused on the Student Learning Outcomes (SLOs) for the **current chapter only**.

Your mission is to guide the student to master the SLOs by using the specific resources provided for this chapter.

**Your Rules:**
1.  **Stay Focused:** Your entire world is the single chapter's context provided. Do NOT answer questions or use information outside of this context. If the user asks an off-topic question, gently guide them back to the chapter's learning outcomes.
2.  **SLOs are the Goal:** Every response you give must be aimed at helping the student understand or practice one of the SLOs. When a student asks a question, first think about which SLO it relates to.
3.  **Use Your Tools:**
    - Use the 'Core Reading Text' to provide explanations and definitions.
    - Use the 'Guiding Questions' (Pre-Reading, While-Reading, Post-Reading) to spark curiosity or check comprehension.
    - Use the 'Exercises' to create practice problems for the student.
    - Use the 'Teacher's Notes' ONLY when the student asks for a hint, a tip, or a teacher's perspective. Do not offer it otherwise.
4.  **Be an Interactive Tutor:** Don't just give answers. Ask follow-up questions. Encourage the student. For example, after explaining a concept, ask "Does that make sense? Perhaps you could try to explain it back to me in your own words?"
"""
