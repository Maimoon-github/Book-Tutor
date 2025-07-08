import streamlit as st
from transformers import pipeline
import numpy as np
import soundfile as sf
from io import BytesIO
from reasoner import Reasoner
import os
import tempfile
import queue
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
from gtts import gTTS

# Corrected import path
from core.file_processor import process_uploaded_files

# --- Document Loaders for Viewer ---
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

# --- 1. Top-Level Configuration and Initialization ---
st.set_page_config(page_title="Agentic AI Tutor", page_icon="🤖", layout="wide")

# Initialize session_state keys
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! Please upload and process your curriculum files in the 'Vector DB Management' tab to begin."}]
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = queue.Queue()
if "rag_retriever" not in st.session_state:
    st.session_state.rag_retriever = None
if "current_exercise" not in st.session_state:
    st.session_state.current_exercise = None

# --- 2. Load Models (run only once) ---
@st.cache_resource
def load_models():
    """
    Loads the necessary models for the application.
    - Automatic Speech Recognition (ASR) to convert voice to text.
    - Reasoner for processing queries.
    """
    try:
        asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
        reasoner_instance = Reasoner()
        return asr_pipeline, reasoner_instance
    except Exception as e:
        st.error(f"A model failed to load: {e}. Please check your internet connection and library versions.")
        return None, None

asr, reasoner = load_models()

# --- 3. Audio Processing & Helper Functions ---
class AudioRecorder(AudioProcessorBase):
    """
    A class to process audio frames from the user's microphone in real-time.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_queue = st.session_state.audio_buffer

    def recv(self, frame):
        """
        This method is called for each audio frame received from the browser.
        """
        self.audio_queue.put(frame.to_ndarray())
        return frame

def get_text_from_file(uploaded_file):
    """
    Extracts text content from an uploaded file for the viewer.
    """
    text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        if uploaded_file.name.lower().endswith(".pdf"):
            loader = PyPDFLoader(tmp_path)
        elif uploaded_file.name.lower().endswith(".md"):
            loader = UnstructuredMarkdownLoader(tmp_path)
        elif uploaded_file.name.lower().endswith(".txt"):
            loader = TextLoader(tmp_path)
        else:
            return "Unsupported file format. Please upload PDF, TXT, or MD."

        documents = loader.load()
        text = "\n\n".join([doc.page_content for doc in documents])

    except Exception as e:
        text = f"Error reading file: {e}"
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
    return text

def text_to_speech(text: str) -> BytesIO:
    """
    Converts a text string to an in-memory audio file using gTTS.
    """
    audio_fp = BytesIO()
    try:
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
    except Exception as e:
        st.error(f"Failed to generate audio: {e}")
    return audio_fp

def handle_user_query(user_text: str):
    """
    Central function to process a user's query, whether from voice or text.
    """
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.spinner("Thinking..."):
        # The reasoner now returns both a text response and potentially an exercise object
        response_text, exercise_obj = reasoner.process_query(
            user_text,
            st.session_state.rag_retriever,
            st.session_state.current_exercise
        )

    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # If the reasoner returned an exercise, store it in the session state
    if exercise_obj:
        st.session_state.current_exercise = exercise_obj
    # If the response indicates the exercise is finished, clear it
    elif "correct" in response_text.lower() or "incorrect" in response_text.lower():
         st.session_state.current_exercise = None


    # Generate and play audio response
    audio_fp = text_to_speech(response_text)
    if audio_fp.getbuffer().nbytes > 0:
        st.audio(audio_fp, format='audio/mp3', start_time=0)

    st.rerun()

# --- 4. Main App UI ---
st.title("🤖 Agentic AI Tutor")
st.caption("Your personal AI tutor, powered by your own curriculum and a voice interface.")

tab_tutor, tab_viewer, tab_db = st.tabs(["AI Tutor", "Textbook Viewer", "Vector DB Management"])

# --- Tab 1: AI Tutor ---
with tab_tutor:
    st.header("Conversation")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.rag_retriever:
        st.subheader("Voice Input")
        st.info("Click 'Start' to enable your microphone, then speak your question.")
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
                    # The sample rate for streamlit-webrtc is typically 16000
                    user_text_from_voice = asr(audio_data.flatten(), sampling_rate=16000)["text"]
                    if user_text_from_voice.strip():
                        handle_user_query(user_text_from_voice)

        if prompt := st.chat_input("Or, type your question here..."):
            handle_user_query(prompt)
    else:
        st.warning("Please upload and process your curriculum in the 'Vector DB Management' tab to activate the tutor.")

# --- Tab 2: Textbook Viewer ---
with tab_viewer:
    st.header("Textbook Viewer")
    st.info("Upload a single textbook file (PDF, TXT, or MD) to read its content.")
    book_file = st.file_uploader("Upload a book to preview", type=["pdf", "txt", "md"], key="book_viewer_uploader")
    if book_file:
        with st.spinner(f"Extracting text from {book_file.name}..."):
            book_text = get_text_from_file(book_file)
            st.text_area("Book Content", book_text, height=600)

# --- Tab 3: Vector DB Management ---
with tab_db:
    st.header("Curriculum Manager & Vector Database")
    st.info("Upload your curriculum files here. These files will form the knowledge base for the AI Tutor.")
    uploaded_files = st.file_uploader(
        "Upload curriculum files (PDF, TXT, MD)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key="vector_db_uploader"
    )
    if st.button("Process Files and Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Processing files, creating embeddings, and building vector store... This may take a moment."):
                try:
                    vectorstore = process_uploaded_files(uploaded_files)
                    st.session_state.rag_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                    st.success("Knowledge base is ready! You can now ask questions in the 'AI Tutor' tab.")
                except Exception as e:
                    st.error(f"Failed to process files: {e}")
        else:
            st.warning("Please upload at least one curriculum file.")
