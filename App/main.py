import streamlit as st
from transformers import pipeline
import numpy as np
import soundfile as sf
from io import BytesIO
from reasoner import Reasoner
import os
import requests
import torch

# --- 1. Configuration and Initialization ---

st.set_page_config(
    page_title="Agentic AI Tutor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agentic AI Tutor")
st.caption("A voice-driven, agentic AI tutor powered by local models.")

@st.cache_resource
def load_models():
    """
    Load and cache the ASR, TTS, and Reasoner models to avoid reloading on every run.
    This also includes the vocoder needed for the TTS model.
    """
    try:
        asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")
        tts_pipeline = pipeline("text-to-speech", model="microsoft/speecht5_tts")
        vocoder = pipeline("text-to-speech", model="microsoft/speecht5_hifigan")
        reasoner_instance = Reasoner()

        # Download and cache the speaker embedding
        embedding_url = "https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors/resolve/main/cmu_us_slt_arctic-wav-arctic_a0001.pt"
        speaker_embedding = torch.tensor(np.load(BytesIO(requests.get(embedding_url).content)))

        return asr_pipeline, tts_pipeline, vocoder, reasoner_instance, speaker_embedding
    except Exception as e:
        st.error(f"Error loading models: {e}. Please ensure you have a running Ollama instance and all dependencies are installed.")
        return None, None, None, None, None

asr, tts, vocoder, reasoner, speaker_embedding = load_models()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you learn today? Speak into the microphone below."}]

# --- 2. UI and Chat Display ---

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- 3. Core Logic: Audio Processing and Agent Interaction ---

audio_bytes = st.audio_recorder(
    text="Click the microphone to speak...",
    icon="🎤",
    pause_threshold=2.0,
    sample_rate=16000
)

if audio_bytes and all([asr, tts, vocoder, reasoner, speaker_embedding is not None]):
    st.info("Processing your voice...", icon="⏳")

    try:
        # Step A: Transcribe Audio to Text
        audio_buffer = BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(audio_buffer)
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        user_text = asr({"sampling_rate": sample_rate, "raw": audio_data})["text"]

        if user_text:
            st.chat_message("user").write(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})

            # Step B: Process Text with the Reasoner
            with st.spinner("Thinking..."):
                agent_response = reasoner.process_query(user_text)

            # Step C: Display Agent Response
            st.chat_message("assistant").write(agent_response)
            st.session_state.messages.append({"role": "assistant", "content": agent_response})

            # Step D: Convert Agent Response to Speech
            with st.spinner("Generating audio response..."):
                speech = tts(agent_response, forward_params={"speaker_embeddings": speaker_embedding})
                speech_with_vocoder = vocoder(speech['spectrogram'])

                output_audio_buffer = BytesIO()
                sf.write(output_audio_buffer, speech_with_vocoder["audio"], samplerate=16000, format='WAV')
                output_audio_buffer.seek(0)
                st.audio(output_audio_buffer, format='audio/wav')

                st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- 4. Sidebar Information ---
with st.sidebar:
    st.header("About")
    st.markdown(
        "This is a demonstration of an **agentic AI tutor** that uses "
        "local language models (via Ollama) and speech recognition to create an "
        "interactive learning experience."
    )
    st.header("How It Works")
    st.markdown(
        """
        1.  **Speech-to-Text**: Your voice is captured and transcribed using `openai/whisper`.
        2.  **Planning**: The agent creates a plan to address your query.
        3.  **Execution**: It executes the plan, which may involve fetching web content.
        4.  **Reasoning**: A local LLM (like Llama 3) reasons over the results to form an answer.
        5.  **Text-to-Speech**: The final answer is converted back to audio.
        """
    )
    if st.button("Clear Conversation History"):
        st.session_state.messages = [{"role": "assistant", "content": "History cleared. How can I help you now?"}]
        if os.path.exists("memory.json"):
            try:
                os.remove("memory.json")
            except OSError as e:
                st.error(f"Error removing memory file: {e}")
        st.rerun()

