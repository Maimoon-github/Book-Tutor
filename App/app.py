import streamlit as st
import base64
import io
import soundfile as sf
import torch
from src.data_loader import DataLoader
from src.agent import StreamlitTutorAgent

# --- Kokoro TTS Integration ---
# This setup is now more robust and provides clearer instructions.
try:
    from kokoro import KPipeline
except ImportError:
    st.error("Kokoro TTS library not found. Please run: pip install kokoro>=0.9.2")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Tutor", page_icon="📖", layout="wide", initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
<style>
    .main .block-container { padding: 2rem; }
    h1 { font-size: 2.5em; font-weight: bold; }
    h3 { font-size: 1.8em; color: #2c3e50; border-bottom: 2px solid #2980b9; padding-bottom: 10px; }
    .stButton>button { border-radius: 0.5rem; font-weight: bold; padding: 0.5rem 1rem; }
</style>
""", unsafe_allow_html=True)


# --- Initialization (Cached for performance) ---
@st.cache_resource
def initialize_app():
    """Loads all necessary resources once."""
    data_loader = DataLoader()
    agent = StreamlitTutorAgent(data_loader.get_all_data())
    tts_pipeline = None
    try:
        tts_pipeline = KPipeline(lang_code='a')
    except Exception as e:
        st.warning(f"Could not initialize Kokoro TTS: {e}. Audio features will be disabled.")
    return data_loader, agent, tts_pipeline

data_loader, agent, tts_pipeline = initialize_app()
chapter_titles = data_loader.get_chapter_titles()


# --- Functions ---
def get_kokoro_audio(text: str):
    """Generates audio using the cached Kokoro pipeline."""
    if not tts_pipeline: return None
    try:
        generator = tts_pipeline(text, voice='af_heart')
        full_audio = torch.cat([audio_chunk for _, _, audio_chunk in generator]).numpy()
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, 24000, format='WAV')
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        st.error(f"Kokoro audio generation failed: {e}")
        return None

def autoplay_audio(audio_bytes: bytes):
    """Embeds HTML5 audio player to autoplay sound."""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f'<audio controls autoplay="true" style="display:none;"><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>'
    st.markdown(md, unsafe_allow_html=True)


# --- Session State ---
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = None
if 'view' not in st.session_state:
    st.session_state.view = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Sidebar ---
with st.sidebar:
    st.title("📖 Book Chapters")
    if not chapter_titles:
        st.error("No chapters found. Check your `Curriculum` directory and file contents.")
        st.stop()

    # Set a default chapter if none is selected
    if st.session_state.current_chapter is None:
        st.session_state.current_chapter = list(chapter_titles.keys())[0]

    selected_chapter_num = st.radio(
        "Select a Chapter:",
        options=list(chapter_titles.keys()),
        format_func=lambda num: f"Chapter {num}: {chapter_titles[num]}",
        key="chapter_selector",
        index=list(chapter_titles.keys()).index(st.session_state.current_chapter)
    )

    if st.session_state.current_chapter != selected_chapter_num:
        st.session_state.current_chapter = selected_chapter_num
        st.session_state.view = None
        st.session_state.messages = []
        st.experimental_rerun()


# --- Main Panel ---
chapter_num = st.session_state.current_chapter
chapter_data = data_loader.get_chapter_data(chapter_num)

st.title(f"Chapter {chapter_num}: {chapter_titles.get(chapter_num, '')}")

st.subheader("🎯 Student Learning Outcomes (SLOs)")
st.info(chapter_data.get('outcomes', 'No SLOs found for this chapter.'))

col1, col2 = st.columns(2)
if col1.button("View Reading Material", use_container_width=True):
    st.session_state.view = 'reading'
    st.experimental_rerun()  # FIXED: Force UI to update

if col2.button("View Exercises", use_container_width=True):
    st.session_state.view = 'exercises'
    st.experimental_rerun()  # FIXED: Force UI to update

# Display content based on button clicks
if st.session_state.view == 'reading':
    st.header("📚 Reading Material")
    for title, content in chapter_data.get('reading', {}).items():
        with st.expander(f"**{title.replace('_', ' ').title()}**", expanded=True):
            st.markdown(content)

elif st.session_state.view == 'exercises':
    st.header("✍️ Exercises")
    for title, content in chapter_data.get('exercises', {}).items():
         with st.expander(f"**{title.replace('_', ' ').title()}**", expanded=True):
            st.markdown(content)

# AI Tutor Chat
st.header("🤖 AI Tutor Assistant")
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and tts_pipeline:
            if st.button("🔊 Listen", key=f"tts_{i}"):
                with st.spinner("Generating audio..."):
                    audio = get_kokoro_audio(message["content"])
                    if audio: autoplay_audio(audio)

if prompt := st.chat_input("Ask about the learning outcomes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        response_stream = agent.get_response(chapter_num, st.session_state.messages)
        for chunk in response_stream:
            full_response += chunk
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.experimental_rerun()


