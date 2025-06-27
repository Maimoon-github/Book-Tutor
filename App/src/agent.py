# src/agent.py

import logging
from .model_handler import OllamaClient
from .config import MAIN_LLM_MODEL, STREAMLIT_AGENT_SYSTEM_PROMPT
from typing import Dict, Any, Iterator, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamlitTutorAgent:
    """
    An AI Tutor agent specifically designed for the Streamlit application.
    It uses Student Learning Outcomes (SLOs) to drive its responses.
    """

    def __init__(self, all_curriculum_data: Dict[int, Any]):
        """
        Initializes the agent.
        Args:
            all_curriculum_data: A dictionary containing all loaded chapter data.
        """
        logger.info("Initializing StreamlitTutorAgent...")
        self.model_handler = OllamaClient()
        self.all_data = all_curriculum_data

    def _create_contextual_prompt(self, chapter_num: int, user_query: str, chat_history: List[Dict]) -> List[Dict]:
        """
        Creates the full prompt for the LLM, including system prompt,
        chapter context (SLOs, teacher's notes), and conversation history.
        """
        if chapter_num not in self.all_data:
            return [{"role": "system", "content": "Error: Invalid chapter selected."}, {"role": "user", "content": user_query}]

        chapter_data = self.all_data[chapter_num]
        slos = chapter_data.get('outcomes', 'No SLOs available.')
        # Extract teacher's note if available
        teacher_note = "No specific teacher's note available for this chapter."
        if 'reading' in chapter_data and 'teachers_note' in chapter_data['reading']:
            teacher_note = chapter_data['reading']['teachers_note']

        # The context provided to the LLM
        context = f"""
        CONTEXT FOR THE CURRENT CHAPTER ({chapter_data.get('title', '')}):
        ---
        **1. Student Learning Outcomes (SLOs):**
        {slos}

        **2. Teacher's Note (Use only when asked for a hint or teacher's perspective):**
        {teacher_note}
        ---
        """

        # Construct the final message list for the LLM
        # The system prompt sets the persona and rules
        messages = [{"role": "system", "content": STREAMLIT_AGENT_SYSTEM_PROMPT}]
        # We add the specific context as the first part of the user's message
        # This focuses the LLM on the most relevant information
        messages.append({"role": "user", "content": f"{context}\nNow, based on that context, please answer my question: {user_query}"})

        return messages


    def get_response(self, chapter_num: int, user_query: str, chat_history: List[Dict]) -> Iterator[str]:
        """
        Processes a user query based on the chapter's SLOs and returns a streamed response.

        Args:
            chapter_num: The currently selected chapter number.
            user_query: The user's question from the chat input.
            chat_history: The history of the conversation for context.

        Yields:
            A stream of response chunks from the LLM.
        """
        if not self.model_handler.client:
            yield "The AI model is not available right now. Please make sure Ollama is running and try again."
            return

        logger.info(f"Generating response for Chapter {chapter_num} with query: '{user_query}'")

        # Create the full, context-rich prompt for the LLM
        messages_for_llm = self._create_contextual_prompt(chapter_num, user_query, chat_history)

        # Get the streamed response
        response_stream = self.model_handler.get_stream_response(
            model=MAIN_LLM_MODEL,
            messages=messages_for_llm
        )

        yield from response_stream

