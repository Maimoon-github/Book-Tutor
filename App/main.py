import streamlit as st
from transformers import pipeline
import numpy as np
import soundfile as sf
from io import BytesIO
from reasoner import Reasoner
import os
import requests
import torch
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
from core.file_processor import process_uploaded_files
import queue

# --- 1. Top-Level Configuration and Initialization ---
st.set_page_config(page_title="Agentic AI Tutor", page_icon="🤖", layout="wide")

# Initialize session_state keys at the very top to prevent errors
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! Please upload your curriculum files to begin."}]
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = queue.Queue()
if "rag_retriever" not in st.session_state:
    st.session_state.rag_retriever = None

# --- Load Models (run only once) ---
@st.cache_resource
def load_models():
    try:
        asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")
        tts_pipeline = pipeline("text-to-speech", model="microsoft/speecht5_tts")
        reasoner_instance = Reasoner()
        embedding_url = "https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors/resolve/main/cmu_us_slt_arctic-wav-arctic_a0001.pt"
        # FIX: Use torch.load and set weights_only=False for PyTorch 2.6+ compatibility
        speaker_embedding = torch.load(BytesIO(requests.get(embedding_url).content), weights_only=False)
        return asr_pipeline, tts_pipeline, reasoner_instance, speaker_embedding
    except Exception as e:
        st.error(f"A model failed to load: {e}. Please check your internet connection and library versions.")
        return None, None, None, None

asr, tts, reasoner, speaker_embedding = load_models()

# --- Audio Processing Class (Corrected) ---
class AudioRecorder(AudioProcessorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_queue = st.session_state.audio_buffer

    def recv(self, frame):
        # This method is called for each audio frame. We put it in a queue.
        self.audio_queue.put(frame.to_ndarray())
        return frame

# --- Main App UI ---
st.title("🤖 Agentic AI Tutor")
st.caption("A voice-driven, agentic AI tutor powered by your own curriculum.")

# --- UI Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Conversation")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with col2:
    st.header("Curriculum Manager")
    uploaded_files = st.file_uploader(
        "Upload your curriculum files (PDF, TXT, MD)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if st.button("Process Files and Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Processing files and building vector store..."):
                try:
                    vectorstore = process_uploaded_files(uploaded_files)
                    st.session_state.rag_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                    st.success("Knowledge base is ready! You can now ask questions.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to process files: {e}")
        else:
            st.warning("Please upload at least one file.")

# --- Audio Input and Core Logic ---
if st.session_state.rag_retriever:
    st.header("Voice Input")
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioRecorder,
        media_stream_constraints={"audio": True, "video": False},
    )

    # FIX: Process the queue, don't call a non-existent method
    if webrtc_ctx.state.playing and not st.session_state.audio_buffer.empty():
        st.info("Voice detected, processing...", icon="🎤")

        all_frames = []
        while not st.session_state.audio_buffer.empty():
            all_frames.append(st.session_state.audio_buffer.get())

        if all_frames:
            audio_data = np.concatenate(all_frames, axis=0)
            buffer = BytesIO()
            sf.write(buffer, audio_data, 16000, format='WAV')
            buffer.seek(0)

            user_text = asr(buffer.read())["text"]

            if user_text:
                st.chat_message("user").write(user_text)
                st.session_state.messages.append({"role": "user", "content": user_text})

                with st.spinner("Thinking..."):
                    agent_response = reasoner.process_query(user_text, st.session_state.rag_retriever)

                st.chat_message("assistant").write(agent_response)
                st.session_state.messages.append({"role": "assistant", "content": agent_response})

                with st.spinner("Generating audio response..."):
                    speech = tts(agent_response, forward_params={"speaker_embeddings": speaker_embedding})
                    st.audio(speech["audio"], sample_rate=speech["sampling_rate"], autoplay=True)

                st.rerun()
else:
    st.info("Please upload and process your curriculum files to activate the tutor.")
