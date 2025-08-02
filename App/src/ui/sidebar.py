import streamlit as st
from typing import Dict, Any

def setup_sidebar(book_tutor):
    """
    Set up the sidebar with navigation and settings.

    Args:
        book_tutor: BookTutor instance
    """
    with st.sidebar:
        st.header("Navigation")

        # Chapter selection
        chapter_options = {
            1: "Chapter 1: Kindness of the Holy Rasool",
            2: "Chapter 2",
            3: "Chapter 3"
        }
        selected_chapter = st.selectbox(
            "Select a chapter:",
            options=list(chapter_options.keys()),
            format_func=lambda x: chapter_options[x]
        )

        # Learning phase selection
        learning_phases = ["Pre-Reading", "During-Reading", "Post-Reading", "Assessment", "Critical Thinking"]
        selected_phase = st.radio("Learning Phase:", learning_phases)

        # Store the selections in session state
        st.session_state.selected_chapter = selected_chapter
        st.session_state.selected_phase = selected_phase.lower().replace("-", "_")

        st.divider()

        # Settings section
        st.header("Settings")

        # Difficulty setting for assessments
        if selected_phase == "Assessment":
            difficulty_options = ["Easy", "Medium", "Hard"]
            selected_difficulty = st.select_slider(
                "Difficulty level:",
                options=difficulty_options,
                value="Medium"
            )
            st.session_state.difficulty = selected_difficulty.lower()

        # Question type selection for assessments
        if selected_phase == "Assessment":
            question_types = ["Multiple Choice", "Short Answer", "True/False"]
            selected_types = st.multiselect(
                "Question types:",
                options=question_types,
                default=["Multiple Choice"]
            )
            st.session_state.question_types = [q_type.lower().replace(" ", "_") for q_type in selected_types]

        # Student information (placeholder for future implementation)
        st.divider()
        if st.button("Reset Progress"):
            # This would reset the student's progress tracking
            st.success("Progress reset successfully!")

        # Display current progress summary
        st.divider()
        st.header("Progress Summary")

        # This would be replaced with actual progress data
        chapter_progress = {
            1: 75,  # percentage
            2: 30,
            3: 0
        }

        for chapter, progress in chapter_progress.items():
            st.progress(progress / 100, text=f"Chapter {chapter}: {progress}%")

        st.caption("Progress based on completed activities and assessments.")
