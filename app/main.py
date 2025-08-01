import streamlit as st
import numpy as np
import base64
from io import BytesIO
import queue
import os
import tempfile

# --- Core App Imports ---
try:
    from transformers import pipeline
    from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
except ImportError as e:
    st.error(f"A required library is missing: {e}. Please run 'pip install -r requirements.txt'")
    st.stop()

# --- Local Module Imports (all .py files in the same directory) ---
# This is the section that causes the error if files are not in the same directory.
try:
    from reasoner import Reasoner
    from file_processor import process_uploaded_files, get_ollama_models
except ModuleNotFoundError:
    st.error("CRITICAL ERROR: Could not find local Python modules (e.g., 'reasoner.py', 'file_processor.py'). Please ensure all .py files are in the same directory as main.py.")
    # Add a diagnostic to help the user
    st.info(f"Current Working Directory: {os.getcwd()}")
    st.code("Files in this directory:\n" + "\n".join(os.listdir('.')))
    st.stop()


# --- 1. Top-Level Configuration and Initialization ---
st.set_page_config(page_title="Agentic AI Tutor", page_icon="🤖", layout="wide")

# --- Initialize session_state keys to prevent errors on first run ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! Configure your tutor in the sidebar, then upload curriculum files to begin."}]
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = queue.Queue()
if "rag_retriever" not in st.session_state:
    st.session_state.rag_retriever = None
if "current_exercise" not in st.session_state:
    st.session_state.current_exercise = None
if "tutor_subject" not in st.session_state:
    st.session_state.tutor_subject = "8th Grade History"
if "tutor_instructions" not in st.session_state:
    st.session_state.tutor_instructions = "You are a friendly and encouraging tutor who uses the Socratic method."
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "llama3"
if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = "nomic-embed-text"


# --- 2. Load Models and App Components ---
@st.cache_resource
def load_asr_model():
    """Loads the Automatic Speech Recognition (ASR) model."""
    try:
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        os.makedirs(cache_dir, exist_ok=True)
        return pipeline("automatic-speech-recognition", model="openai/whisper-base.en", cache_dir=cache_dir)
    except Exception as e:
        st.error(f"Could not load ASR model: {e}. Please check internet connection and transformers library.")
        return None

asr = load_asr_model()

class AudioRecorder(AudioProcessorBase):
    """Processes audio frames from the browser, placing them in a queue."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_queue = st.session_state.audio_buffer

    def recv(self, frame):
        self.audio_queue.put(frame.to_ndarray())
        return frame

def get_pdf_display(uploaded_file: BytesIO) -> str:
    """Generates an HTML iframe to display a PDF."""
    base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
    return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'

def handle_user_query(user_text: str, reasoner_instance: Reasoner):
    """Processes a user's query and updates the chat."""
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text, exercise_obj = reasoner_instance.process_query(
                user_text,
                st.session_state.rag_retriever,
                st.session_state.current_exercise
            )
            st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

    if exercise_obj:
        st.session_state.current_exercise = exercise_obj
    elif "correct" in response_text.lower() or "incorrect" in response_text.lower():
         st.session_state.current_exercise = None

# --- 3. Main App UI ---
st.title("🤖 Agentic AI Tutor")
st.caption("A personalized learning assistant powered by your curriculum.")

with st.sidebar:
    st.header("⚙️ Configuration")
    st.subheader("Tutor Persona")
    st.session_state.tutor_subject = st.text_input("Tutor Subject / Grade Level", st.session_state.tutor_subject)
    st.session_state.tutor_instructions = st.text_area("Custom Instructions", st.session_state.tutor_instructions, height=150)

    st.subheader("Ollama Models")
    try:
        available_models = get_ollama_models()
        if available_models:
            llm_index = available_models.index(st.session_state.llm_model) if st.session_state.llm_model in available_models else 0
            embedding_index = available_models.index(st.session_state.embedding_model) if st.session_state.embedding_model in available_models else 0
            st.session_state.llm_model = st.selectbox("LLM Model (for Reasoning)", available_models, index=llm_index)
            st.session_state.embedding_model = st.selectbox("Embedding Model (for RAG)", available_models, index=embedding_index)
        else:
            st.warning("No Ollama models found. Please ensure Ollama is running and you have pulled models (e.g., 'ollama pull llama3').")

    except Exception as e:
        st.error(f"Could not connect to Ollama. Please ensure it is running. Error: {e}")

reasoner = Reasoner(
    llm_model=st.session_state.llm_model,
    tutor_subject=st.session_state.tutor_subject,
    tutor_instructions=st.session_state.tutor_instructions
)

tab_tutor, tab_viewer, tab_db = st.tabs(["AI Tutor", "Textbook Viewer", "Vector DB Management"])

with tab_tutor:
    st.header("Conversation")
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    st.divider()
    if st.session_state.rag_retriever:
        if asr:
            st.subheader("Voice Input")
            st.info("Click 'Start' to enable your microphone. The system will process your voice when you pause.")
            webrtc_ctx = webrtc_streamer(
                key="audio-recorder",
                mode=WebRtcMode.SENDONLY,
                audio_processor_factory=AudioRecorder,
                media_stream_constraints={"audio": True, "video": False},
            )
            if webrtc_ctx.state.playing and not st.session_state.audio_buffer.empty():
                with st.spinner("Voice detected, transcribing..."):
                    all_frames = []
                    while not st.session_state.audio_buffer.empty():
                        all_frames.append(st.session_state.audio_buffer.get())
                    if all_frames:
                        audio_data = np.concatenate(all_frames, axis=0)
                        user_text_from_voice = asr(audio_data.flatten())["text"]
                        if user_text_from_voice.strip():
                            handle_user_query(user_text_from_voice, reasoner)
                            st.rerun()
        if prompt := st.chat_input("Or, type your question here..."):
            handle_user_query(prompt, reasoner)
            st.rerun()
    else:
        st.warning("Please upload and process your curriculum in the 'Vector DB Management' tab to activate the tutor.")

with tab_viewer:
    st.header("Textbook PDF Viewer")
    st.info("Upload a single PDF file from your curriculum to preview it here.")
    book_file = st.file_uploader("Upload a PDF to preview", type=["pdf"], key="book_viewer_uploader")
    if book_file:
        st.markdown(get_pdf_display(book_file), unsafe_allow_html=True)

with tab_db:
    st.header("Curriculum Manager & Vector Database")
    st.info("Upload your curriculum files (PDF, TXT, MD) here. These files will form the knowledge base for the AI Tutor.")
    uploaded_files = st.file_uploader(
        "Upload curriculum files", type=["pdf", "txt", "md"], accept_multiple_files=True, key="vector_db_uploader"
    )
    if st.button("Process Files and Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Processing files, creating embeddings, and building vector store... This may take a moment."):
                try:
                    vectorstore = process_uploaded_files(uploaded_files, st.session_state.embedding_model)
                    st.session_state.rag_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                    st.success("Knowledge base is ready! You can now ask questions in the 'AI Tutor' tab.")
                except ValueError as ve:
                     st.error(f"Processing Error: {ve}")
                except Exception as e:
                    if "model" in str(e) and "not found" in str(e):
                        st.error(f"Ollama Model Not Found: The embedding model '{st.session_state.embedding_model}' is not available. Please run 'ollama pull {st.session_state.embedding_model}' in your terminal and try again.")
                    else:
                        st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please upload at least one curriculum file.")
