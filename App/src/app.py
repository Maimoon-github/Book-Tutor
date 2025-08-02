import streamlit as st
from core.book_tutor import BookTutor
from ui.sidebar import setup_sidebar
from ui.main_view import setup_main_view

def main():
    """
    Main application entry point.
    Sets up the Streamlit UI and initializes the BookTutor instance.
    """
    st.set_page_config(
        page_title="Book AI Tutor",
        page_icon="📚",
        layout="wide"
    )

    # Application title
    st.title("Book AI Tutor")

    # Initialize BookTutor instance
    book_tutor = BookTutor()

    # Setup sidebar with navigation and settings
    setup_sidebar(book_tutor)

    # Setup main view for the tutor interface
    setup_main_view(book_tutor)

if __name__ == "__main__":
    main()
