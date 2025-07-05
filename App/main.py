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
from utils.pdf_parser import get_parsed_pdf_content
import queue
import threading
import time

# --- 1. Configuration and Initialization ---
st.set_page_config(page_title="Agentic AI Tutor", page_icon="🤖", layout="wide")
st.title("🤖 Agentic AI Tutor")
st.caption("A voice-driven, agentic AI tutor powered by your curriculum.")

# --- Load Models and Data ---
@st.cache_resource
def load_resources():
    try:
        asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")
        tts_pipeline = pipeline("text-to-speech", model="microsoft/speecht5_tts")
        vocoder = pipeline("text-to-speech", model="microsoft/speecht5_hifigan")
        reasoner_instance = Reasoner()
        embedding_url = "https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors/resolve/main/cmu_us_slt_arctic-wav-arctic_a0001.pt"
        speaker_embedding = torch.tensor(np.load(BytesIO(requests.get(embedding_url).content)))
        parsed_pdf = get_parsed_pdf_content()
        return asr_pipeline, tts_pipeline, vocoder, reasoner_instance, speaker_embedding, parsed_pdf
    except Exception as e:
        st.error(f"Fatal error during resource loading: {e}")
        return (None,) * 6

asr, tts, vocoder, reasoner, speaker_embedding, pdf_content = load_resources()

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me a question about the curriculum. Activate the microphone to speak."}]
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = queue.Queue()

# --- Audio Processing Class ---
class AudioRecorder(AudioProcessorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_queue = st.session_state.audio_buffer

    def recv(self, frame):
        # Using a thread-safe queue to handle audio frames
        self.audio_queue.put(frame.to_ndarray())
        return frame

# --- 2. UI Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Conversation")
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with col2:
    st.header("Curriculum")
    with st.expander("View Parsed Textbook Content", expanded=False):
        if pdf_content:
            st.text_area("PDF Content", pdf_content, height=400)
        else:
            st.warning("Could not load PDF content.")

# --- 3. Core Logic ---
webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioRecorder,
    media_stream_constraints={"audio": True, "video": False},
    send_interval=200, # ms
)

if webrtc_ctx.state.playing and not st.session_state.audio_buffer.empty():
    st.info("Voice detected, processing...", icon="🎤")

    all_frames = []
    while not st.session_state.audio_buffer.empty():
        all_frames.append(st.session_state.audio_buffer.get())

    if all_frames:
        audio_data = np.concatenate(all_frames, axis=0)

        # Write audio to a buffer and process
        buffer = BytesIO()
        sf.write(buffer, audio_data, 16000, format='WAV')
        buffer.seek(0)

        # Transcribe
        user_text = asr(buffer.read())["text"]

        if user_text:
            st.chat_message("user").write(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})

            with st.spinner("Thinking..."):
                agent_response = reasoner.process_query(user_text)

            st.chat_message("assistant").write(agent_response)
            st.session_state.messages.append({"role": "assistant", "content": agent_response})

            with st.spinner("Generating audio response..."):
                speech = tts(agent_response, forward_params={"speaker_embeddings": speaker_embedding})
                with st.spinner("Improving audio quality..."):
                     speech_with_vocoder = vocoder(speech['spectrogram'])

                output_audio_buffer = BytesIO()
                sf.write(output_audio_buffer, speech_with_vocoder["audio"], samplerate=16000, format='WAV')
                st.audio(output_audio_buffer, format='audio/wav', autoplay=True)

            # Clear the queue after processing
            with st.session_state.audio_buffer.mutex:
                st.session_state.audio_buffer.queue.clear()

            st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    if st.button("Clear Conversation History"):
        st.session_state.messages = [{"role": "assistant", "content": "History cleared. How can I help?"}]
        if os.path.exists("memory.json"):
            os.remove("memory.json")
        st.rerun()

    if st.button("Rebuild Vector Store"):
        with st.spinner("Rebuilding vector store from PDF... This may take a moment."):
            from utils.pdf_parser import get_vectorstore
            get_vectorstore(rebuild=True)
        st.success("Vector store rebuilt!")


# ```

# ### Summary of Changes and Required Actions

# 1.  **Rename `transformers.py`**: On your machine, please rename the `transformers.py` file to avoid import conflicts.
# 2.  **Updated `main.py`**: I have updated `main.py` to use `streamlit-webrtc`'s `webrtc_streamer`, which is a more stable way to handle audio input.
# 3.  **Check `requirements.txt`**: Ensure that `streamlit-webrtc` is listed in your `requirements.txt` file and that you have run `pip install -r requirements.txt` to install it.

# After making these changes, your application should run without the import and attribute errors. Let me know if you have any other questio