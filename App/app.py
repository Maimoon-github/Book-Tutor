import streamlit as st
import requests
import base64
from src.data_loader import DataLoader
from src.agent import StreamlitTutorAgent

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Tutor",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styling ---
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* Sidebar styling */
    .st-emotion-cache-16txtl3 {
        padding-top: 1.5rem;
    }
    /* Chapter title in sidebar */
    .st-emotion-cache-16txtl3 a {
        font-size: 16px;
        border-radius: 0.5rem;
        margin-bottom: 5px;
    }
    h1 {
        font-size: 2.5em;
        font-weight: bold;
    }
    h3 {
        font-size: 1.8em;
        color: #2c3e50;
        border-bottom: 2px solid #2980b9;
        padding-bottom: 10px;
    }
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- Hugging Face API for Text-to-Speech ---
HF_API_TOKEN = "YOUR_HUGGINGFACE_API_TOKEN" # IMPORTANT: Replace with your actual token
TTS_API_URL = "https://api-inference.huggingface.co/models/hexgrad/Kokoro-82M"

def get_tts_audio(text: str):
    """Calls the Hugging Face API to get text-to-speech audio."""
    if not HF_API_TOKEN or HF_API_TOKEN == "YOUR_HUGGINGFACE_API_TOKEN":
        st.error("Hugging Face API token is not configured. Cannot generate audio.")
        return None

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": text}
    try:
        response = requests.post(TTS_API_URL, headers=headers, json=payload)
        if response.status_code == 200 and response.content:
            return response.content
        else:
            st.error(f"Failed to generate audio. Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while calling the TTS API: {e}")
        return None

def autoplay_audio(audio_bytes: bytes):
    """Encodes audio to base64 and uses HTML5 to autoplay it."""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio controls autoplay="true" style="display:none;">
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)


# --- Initialization ---
@st.cache_resource
def initialize_app():
    """Initializes the data loader and agent."""
    data_loader = DataLoader()
    agent = StreamlitTutorAgent(data_loader.get_all_data())
    return data_loader, agent

data_loader, agent = initialize_app()
chapter_titles = data_loader.get_chapter_titles()

# --- Session State Management ---
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = None
if 'view' not in st.session_state:
    st.session_state.view = None # Can be 'reading' or 'exercises'
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Sidebar Navigation ---
with st.sidebar:
    st.title("📖 Book Chapters")
    selected_chapter_title = st.radio(
        "Select a Chapter:",
        options=list(chapter_titles.values()),
        key="chapter_selector",
        label_visibility="collapsed"
    )

# Determine selected chapter number
chapter_num = next((num for num, title in chapter_titles.items() if title == selected_chapter_title), None)

# If selection changes, reset the view
if st.session_state.current_chapter != chapter_num:
    st.session_state.current_chapter = chapter_num
    st.session_state.view = None
    st.session_state.messages = [] # Clear chat history


# --- Main Panel ---
if chapter_num is not None:
    chapter_data = data_loader.get_chapter_data(chapter_num)

    st.title(f"Chapter {chapter_num}: {chapter_titles.get(chapter_num, '')}")

    # --- Student Learning Outcomes (SLOs) ---
    st.subheader("🎯 Student Learning Outcomes (SLOs)")
    st.info(chapter_data.get('outcomes', 'No SLOs found for this chapter.'))

    # --- View Selection Buttons ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Reading Material", use_container_width=True):
            st.session_state.view = 'reading'
    with col2:
        if st.button("View Exercises", use_container_width=True):
            st.session_state.view = 'exercises'

    # --- Display Content Based on View ---
    if st.session_state.view == 'reading':
        st.header("📚 Reading Material")
        reading_sections = chapter_data.get('reading', {})
        for section_title, section_content in reading_sections.items():
            with st.expander(f"**{section_title.replace('_', ' ').title()}**", expanded=True):
                st.markdown(section_content)

    elif st.session_state.view == 'exercises':
        st.header("✍️ Exercises")
        exercise_sections = chapter_data.get('exercises', {})
        for section_title, section_content in exercise_sections.items():
             with st.expander(f"**{section_title.replace('_', ' ').title()}**", expanded=True):
                st.markdown(section_content)

    # --- AI Tutor Agent ---
    st.header("🤖 AI Tutor Assistant")
    st.markdown("Ask me anything about the Student Learning Outcomes for this chapter!")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and st.button(f"🔊 Listen", key=f"tts_{message['content']}"):
                with st.spinner("Generating audio..."):
                    audio_content = get_tts_audio(message["content"])
                    if audio_content:
                        autoplay_audio(audio_content)

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # Stream response from agent
            response_stream = agent.get_response(chapter_num, prompt, st.session_state.messages)
            for chunk in response_stream:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            # Add a listen button for the new message
            if st.button(f"🔊 Listen", key=f"tts_{full_response}"):
                 with st.spinner("Generating audio..."):
                    audio_content = get_tts_audio(full_response)
                    if audio_content:
                        autoplay_audio(audio_content)


else:
    st.info("Select a chapter from the sidebar to get started.")

