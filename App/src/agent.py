# src/agent.py

# import logging
# from .model_handler import OllamaClient
# from .config import MAIN_LLM_MODEL, STREAMLIT_AGENT_SYSTEM_PROMPT
# from typing import Dict, Any, Iterator, List

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class StreamlitTutorAgent:
#     """
#     An AI Tutor agent specifically designed for the Streamlit application.
#     It uses Student Learning Outcomes (SLOs) to drive its responses.
#     """

#     def __init__(self, all_curriculum_data: Dict[int, Any]):
#         """
#         Initializes the agent.
#         Args:
#             all_curriculum_data: A dictionary containing all loaded chapter data.
#         """
#         logger.info("Initializing StreamlitTutorAgent...")
#         self.model_handler = OllamaClient()
#         self.all_data = all_curriculum_data

#     def _create_contextual_prompt(self, chapter_num: int, user_query: str, chat_history: List[Dict]) -> List[Dict]:
#         """
#         Creates the full prompt for the LLM, including system prompt,
#         chapter context (SLOs, teacher's notes), and conversation history.
#         """
#         if chapter_num not in self.all_data:
#             return [{"role": "system", "content": "Error: Invalid chapter selected."}, {"role": "user", "content": user_query}]

#         chapter_data = self.all_data[chapter_num]
#         slos = chapter_data.get('outcomes', 'No SLOs available.')
#         # Extract teacher's note if available
#         teacher_note = "No specific teacher's note available for this chapter."
#         if 'reading' in chapter_data and 'teachers_note' in chapter_data['reading']:
#             teacher_note = chapter_data['reading']['teachers_note']

#         # The context provided to the LLM
#         context = f"""
#         CONTEXT FOR THE CURRENT CHAPTER ({chapter_data.get('title', '')}):
#         ---
#         **1. Student Learning Outcomes (SLOs):**
#         {slos}

#         **2. Teacher's Note (Use only when asked for a hint or teacher's perspective):**
#         {teacher_note}
#         ---
#         """

#         # Construct the final message list for the LLM
#         # The system prompt sets the persona and rules
#         messages = [{"role": "system", "content": STREAMLIT_AGENT_SYSTEM_PROMPT}]
#         # We add the specific context as the first part of the user's message
#         # This focuses the LLM on the most relevant information
#         messages.append({"role": "user", "content": f"{context}\nNow, based on that context, please answer my question: {user_query}"})

#         return messages


#     def get_response(self, chapter_num: int, user_query: str, chat_history: List[Dict]) -> Iterator[str]:
#         """
#         Processes a user query based on the chapter's SLOs and returns a streamed response.

#         Args:
#             chapter_num: The currently selected chapter number.
#             user_query: The user's question from the chat input.
#             chat_history: The history of the conversation for context.

#         Yields:
#             A stream of response chunks from the LLM.
#         """
#         if not self.model_handler.client:
#             yield "The AI model is not available right now. Please make sure Ollama is running and try again."
#             return

#         logger.info(f"Generating response for Chapter {chapter_num} with query: '{user_query}'")

#         # Create the full, context-rich prompt for the LLM
#         messages_for_llm = self._create_contextual_prompt(chapter_num, user_query, chat_history)

#         # Get the streamed response
#         response_stream = self.model_handler.get_stream_response(
#             model=MAIN_LLM_MODEL,
#             messages=messages_for_llm
#         )

#         yield from response_stream



# src/agent.py

import logging
from .model_handler import OllamaClient
from .config import MAIN_LLM_MODEL, STREAMLIT_AGENT_SYSTEM_PROMPT
from typing import Dict, Any, Iterator, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamlitTutorAgent:
    """
    An AI Tutor agent for Streamlit that uses a more advanced reasoning process
    by analyzing conversation history and SLOs to provide better responses.
    """

    def __init__(self, all_curriculum_data: Dict[int, Any]):
        """Initializes the agent with all curriculum data."""
        logger.info("Initializing StreamlitTutorAgent...")
        self.model_handler = OllamaClient()
        self.all_data = all_curriculum_data

    def _create_thoughtful_prompt(self, chapter_num: int, chat_history: List[Dict]) -> List[Dict]:
        """
        Creates a sophisticated prompt for the LLM that encourages critical thinking.
        It combines the system prompt, chapter context (SLOs), and the recent
        conversation history to guide the LLM's reasoning process.
        """
        if chapter_num not in self.all_data:
            return [{"role": "system", "content": "Error: Chapter data not found."},
                    {"role": "user", "content": chat_history[-1]['content']}]

        chapter_data = self.all_data[chapter_num]
        slos = chapter_data.get('outcomes', 'No SLOs available.')
        teacher_note = chapter_data.get('reading', {}).get('teachers_note', 'Not available.')

        # Construct the context block
        context = f"""
        ### CONTEXT FOR {chapter_data.get('title', '').upper()}
        - **Student Learning Outcomes (SLOs):** {slos}
        - **Teacher's Note (for hints):** {teacher_note}
        """

        # Construct a summarized history to give the LLM conversational context
        history_summary = "\n".join(
            [f"- {msg['role'].capitalize()}: {msg['content'][:200]}" for msg in chat_history[-5:]] # last 5 messages
        )

        # The user's most recent question
        latest_query = chat_history[-1]['content']

        # This detailed prompt guides the LLM to "think" before answering.
        final_prompt = f"""
        {context}

        ### CONVERSATION HISTORY
        {history_summary}

        ### INSTRUCTIONS
        You are an expert AI Tutor. Your student has just asked the following question: "{latest_query}"

        1.  **Analyze the Request:** First, silently analyze the student's question in relation to the SLOs and the conversation history. Is the student asking for clarification, an example, or testing their understanding?
        2.  **Formulate a Response:** Based on your analysis, generate a helpful, encouraging, and clear response.
        3.  **Adhere to Rules:** Ensure your response is directly related to the provided context and SLOs. If the question is off-topic, gently guide the student back to the learning objectives.

        **Your Response:**
        """

        # Final message list for the LLM
        messages = [
            {"role": "system", "content": STREAMLIT_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": final_prompt}
        ]

        return messages

    def get_response(self, chapter_num: int, chat_history: List[Dict]) -> Iterator[str]:
        """
        Processes a user query by generating a thoughtful prompt and streaming the response.
        """
        if not self.model_handler.client:
            yield "The AI model is not available. Please ensure Ollama is running and restart."
            return

        if not chat_history:
            yield "I can't respond to an empty message. What would you like to know?"
            return

        logger.info(f"Generating thoughtful response for Chapter {chapter_num}.")

        messages_for_llm = self._create_thoughtful_prompt(chapter_num, chat_history)

        yield from self.model_handler.get_stream_response(
            model=MAIN_LLM_MODEL,
            messages=messages_for_llm
        )
