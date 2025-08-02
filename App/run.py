import os
import sys
from dotenv import load_dotenv
import streamlit as st
import logging

# Add the parent directory to path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(parent_dir, "book_tutor.log"))
    ]
)

# Import application modules
from src.app import main

if __name__ == "__main__":
    try:
        # Check if Ollama model is specified
        if not os.environ.get("OLLAMA_MODEL"):
            st.error("""
            Ollama model not specified in environment variables!
            Please create a .env file in the App directory with your model configuration:
            ```
            OLLAMA_MODEL=deepseek-r1:1.5b
            OLLAMA_BASE_URL=http://localhost:11434
            ```
            """)
            st.stop()
            
        # Check if Ollama service is running
        import requests
        try:
            response = requests.get(os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
        except requests.exceptions.ConnectionError:
            st.error("""
            Cannot connect to Ollama service! 
            Please make sure Ollama is running and accessible at the configured URL.
            
            You can start Ollama using the command: ollama serve
            """)
            st.stop()

        # Launch the application
        main()
    except Exception as e:
        logging.error(f"Application error: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")
