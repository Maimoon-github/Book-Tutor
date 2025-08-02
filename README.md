# Book AI Tutor

An intelligent AI-powered educational agent that serves as an interactive learning companion for students.

## Overview

The Book AI Tutor is designed to:

1. **Guide Structured Learning**: Provides systematic support through pre-reading, during-reading, and post-reading phases.
2. **Deliver Targeted Assessments**: Offers chapter-specific exercises and assessments aligned with curriculum goals.
3. **Encourage Critical Thinking**: Incorporates "points to ponder" to deepen student engagement.
4. **Self-Improve Through Teacher Tips**: Utilizes embedded instructional strategies to refine teaching methods.
5. **Maintain Curriculum Alignment**: Ensures all activities directly support curriculum objectives.

## Project Structure

- `App/`: Main application code
  - `src/`: Source code
    - `agents/`: Specialized AI agents
    - `tools/`: Tools used by the agents
    - `core/`: Core functionality
    - `curriculum/`: Curriculum management
    - `ui/`: User interface components
  - `requirements.txt`: Dependencies
- `Curriculum/`: Curriculum content files
- `docs/`: Documentation

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Book-Tutor.git
   cd Book-Tutor
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r App/requirements.txt
   ```

4. **Install and set up Ollama**:
   Install Ollama from the [official website](https://ollama.ai/download) and pull the required model:
   ```bash
   ollama pull deepseek-r1:1.5b
   ```

5. **Set up environment variables**:
   Create a `.env` file in the `App` directory with the following content:
   ```
   OLLAMA_MODEL=deepseek-r1:1.5b
   OLLAMA_BASE_URL=http://localhost:11434
   TEMPERATURE=0.7
   TOP_P=0.9
   MAX_TOKENS=2048
   ```

6. **Start the Ollama server** (in a separate terminal):
   ```bash
   ollama serve
   ```

7. **Check your Ollama setup** (optional):
   ```bash
   cd Book-Tutor/App
   python check_ollama.py --test
   ```

8. **Run the application**:
   ```bash
   cd App/src
   streamlit run app.py
   ```

## Usage

1. Select a chapter from the sidebar.
2. Progress through the learning phases:
   - Pre-Reading: Prepare for the chapter with vocabulary and introductory questions.
   - During-Reading: Engage with the text with interactive features.
   - Post-Reading: Consolidate learning with summaries and discussion questions.
   - Assessment: Test your understanding with various question types.
   - Critical Thinking: Deepen your engagement with reflection questions and scenarios.

## Features

- **Adaptive Learning**: Content adjusts based on student performance.
- **Interactive Reading**: Contextual definitions, comprehension checks, and annotations.
- **Progress Tracking**: Monitor mastery and identify learning gaps.
- **Curriculum Alignment**: All activities mapped to specific learning outcomes.
- **Self-Improvement**: The system refines teaching approaches based on effectiveness data.

## Acknowledgments

- This project is based on the Grade-5 English book "This Way English" according to the Single National Curriculum 2020.
