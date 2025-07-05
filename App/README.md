# Agentic AI Tutor

This project is a voice-driven, agentic AI tutor that uses Retrieval-Augmented Generation (RAG) to provide a conversational learning experience. The agent can understand spoken language, retrieve information from a textbook, and guide students toward their learning objectives.

## Project Structure

.
├── main.py
├── fetcher.py
├── planner.py
├── executor.py
├── memory.py
├── reasoner.py
├── requirements.txt
├── utils
│   └── init.py
└── README.md

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    streamlit run main.py
    ```

## Usage

Once the application is running, you can interact with the AI tutor using your voice. The tutor will respond to your questions, provide explanations, and guide you through the learning material.
