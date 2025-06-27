# app.py

import streamlit as st
import base64
import io
import soundfile as sf
import torch
from src.data_loader import DataLoader
from src.agent import StreamlitTutorAgent

# --- Page & State Setup ---
st.set_page_config(page_title="Agentic AI Tutor", layout="wide")

# --- Styling ---
st.markdown("""
<style>
    .main .block-container { padding: 1rem 2rem; }
    h1, h2, h3 { font-weight: bold; }
    h1 { font-size: 2.2em; color: #2c3e50; }
    h2 { font-size: 1.6em; color: #2980b9; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 2rem; }
    h3 { font-size: 1.3em; color: #34495e; }
    .st-emotion-cache-16txtl3 a { font-size: 16px !important; }
    .stAudio { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
@st.cache_resource
def initialize_app():
    """Loads and caches all necessary resources for the app."""
    data_loader = DataLoader()
    if not data_loader.get_all_data():
        st.error("FATAL: No curriculum data loaded. Check `Curriculum` folder and file names (e.g., `chapter_1.txt`).")
        st.stop()
    agent = StreamlitTutorAgent(data_loader.get_all_data())
    tts_pipeline = None
    try:
        from kokoro import KPipeline
        tts_pipeline = KPipeline(lang_code='a')
    except Exception as e:
        st.warning(f"Could not init Kokoro TTS: {e}. Audio features disabled.")
    return data_loader, agent, tts_pipeline

data_loader, agent, tts_pipeline = initialize_app()
chapter_titles = data_loader.get_chapter_titles()

# --- TTS & Audio Functions ---
def get_audio_bytes(text: str):
    if not tts_pipeline: return None
    try:
        generator = tts_pipeline(text, voice='af_heart')
        audio_chunks = [chunk for _, _, chunk in generator if chunk is not None]
        if not audio_chunks: return None
        full_audio = torch.cat(audio_chunks).numpy()
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, 24000, format='WAV')
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        st.error(f"Audio generation failed: {e}")
        return None

def play_agent_voice(text: str, autoplay: bool = False):
    """Generates, displays, and optionally autoplays the agent's voice."""
    audio_bytes = get_audio_bytes(text)
    if audio_bytes:
        st.audio(audio_bytes, format='audio/wav', autoplay=autoplay)

# --- Agent Interaction Logic ---
def trigger_agent_action(action_type: str, details: dict = None, autoplay: bool = False):
    """Calls the agent, gets a text response, and plays it as audio."""
    with st.spinner(f"Agent is thinking..."):
        response_stream = agent.generate_agent_action(st.session_state.current_chapter, action_type, details)
        full_response = "".join(response_stream)

        if full_response:
            st.info("Agent's thought (for debugging): " + full_response)
            play_agent_voice(full_response, autoplay=autoplay)
        else:
            st.error("Agent failed to generate a response.")

# --- Session State ---
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = list(chapter_titles.keys())[0] if chapter_titles else None
    st.session_state.did_welcome = False # Track if welcome prompt has been played

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("📖 Book Chapters")
    selected_chapter = st.radio(
        "Select a Chapter:", options=chapter_titles.keys(),
        format_func=lambda num: f"Chapter {num}: {chapter_titles[num]}",
        key="chapter_selector"
    )
    if st.session_state.current_chapter != selected_chapter:
        st.session_state.current_chapter = selected_chapter
        st.session_state.did_welcome = False # Reset welcome prompt for new chapter
        st.rerun()

# --- Main UI ---
chapter_num = st.session_state.current_chapter
if chapter_num is None:
    st.error("No chapter selected or available.")
    st.stop()

chapter_data = data_loader.get_chapter_data(chapter_num)
st.title(chapter_data.get('title', f"Chapter {chapter_num}"))

# Display file loading warnings
for warning in chapter_data.get('warnings', []):
    st.warning(f"⚠️ {warning}")

# --- Agent Welcome Prompt ---
st.header("🎤 Agent Prompt")
agent_prompt_area = st.container(border=True)
with agent_prompt_area:
    if not st.session_state.did_welcome:
        trigger_agent_action("PRE_READING_PROMPT", autoplay=True)
        st.session_state.did_welcome = True
    else:
        st.write("Ask a question below or work on the exercises.")

# --- Curriculum Display ---
st.header("📚 Chapter Content")
with st.expander("🎯 Student Learning Outcomes", expanded=True):
    st.markdown(chapter_data.get('STUDENT_LEARNING_OUTCOMES', "Not available."))

with st.expander("👓 Pre-, While-, and Post-Reading", expanded=False):
    st.subheader("Pre-Reading Questions")
    st.markdown(chapter_data.get('PRE-READING', "Not available."))
    st.subheader("While-Reading Prompts")
    for i, prompt in enumerate(chapter_data.get('WHILE-READING', ["Not available."])):
        st.markdown(f"- {prompt}")
    st.subheader("Post-Reading Questions")
    st.markdown(chapter_data.get('POST-READING', "Not available."))

with st.expander("✍️ Exercises", expanded=False):
    exercises = chapter_data.get('EXERCISES', {})
    if not exercises:
        st.write("No exercises found for this chapter.")
    else:
        for title, content in exercises.items():
            st.subheader(title)
            st.markdown(content)
            # Simple interaction model for exercises
            st.text_input("Your Answer", key=f"ex_answer_{chapter_num}_{title}")
            if st.button("Get a Hint", key=f"ex_hint_{chapter_num}_{title}"):
                 with agent_prompt_area:
                     trigger_agent_action("EXERCISE_HINT", details={'exercise_text': content})

# --- General Q&A Input ---
st.header("💬 Ask a Question")
user_query = st.text_input("Type your question about the chapter here:")
if st.button("Ask Agent"):
    if user_query:
        with agent_prompt_area:
             trigger_agent_action("GENERAL_QUESTION", details={'user_query': user_query})
    else:
        st.warning("Please enter a question.")
