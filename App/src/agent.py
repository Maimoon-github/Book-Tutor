# src/agent.py

import logging
from . import config
from .model_handler import OllamaClient
from typing import Dict, Any, Iterator, List

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class StreamlitTutorAgent:
    """
    An advanced, state-aware AI agent designed for proactive, voice-first tutoring.
    """

    def __init__(self, all_curriculum_data: Dict[int, Any]):
        self.model_handler = OllamaClient()
        self.all_data = all_curriculum_data
        logger.info("Agentic Tutor initialized with structured curriculum data.")

    def _get_chapter_context(self, chapter_num: int) -> str:
        """Builds a comprehensive context string for a given chapter."""
        if chapter_num not in self.all_data:
            return "<Error>Context not available.</Error>"

        chapter_data = self.all_data[chapter_num]
        slos = chapter_data.get('STUDENT_LEARNING_OUTCOMES', 'Not specified.')
        reading = chapter_data.get('WHILE-READING', ['Not specified.'])[0] # Get the main text
        teacher_note = chapter_data.get("TEACHER’S_NOTE", "Not specified.")

        return f"""
<CONTEXT>
    <CHAPTER_TITLE>{chapter_data.get('title', '')}</CHAPTER_TITLE>
    <SLOS>{slos}</SLOS>
    <READING_TEXT>{reading}</READING_TEXT>
    <TEACHER_NOTE>{teacher_note}</TEACHER_NOTE>
</CONTEXT>
"""

    def generate_agent_action(self, chapter_num: int, action_type: str, details: Dict = None) -> Iterator[str]:
        """
        The main entry point for all agent actions. It crafts a specific prompt
        based on the requested action (e.g., pre-reading, hint, etc.).
        """
        if not self.model_handler.client:
            yield "AI model is not available. Please ensure Ollama is running."
            return

        context = self._get_chapter_context(chapter_num)
        chapter_data = self.all_data.get(chapter_num, {})

        prompt = f"{context}\n\n<TASK>"

        if action_type == "PRE_READING_PROMPT":
            pre_reading_q = chapter_data.get("PRE-READING", "Let's get started with this chapter!")
            prompt += f"Your task is to act as a friendly tutor. Welcome the student to the chapter and ask the following pre-reading questions in an engaging, conversational way. Your response should be audio-first, so keep it natural.\n<QUESTIONS>{pre_reading_q}</QUESTIONS>"

        elif action_type == "EXERCISE_HINT":
            if not details or 'exercise_text' not in details:
                yield "Cannot generate hint without the exercise text."
                return
            exercise = details['exercise_text']
            prompt += f"A student is working on an exercise and asked for a hint. DO NOT give the answer. Your task is to provide a helpful, encouraging hint that guides them to the right answer themselves.\n<EXERCISE>{exercise}</EXERCISE>"

        elif action_type == "GENERAL_QUESTION":
            if not details or 'user_query' not in details:
                 yield "Cannot answer without a question."
                 return
            query = details['user_query']
            prompt += f"A student has the following question. Based on all the provided chapter context (SLOs, reading text, etc.), provide a clear and helpful answer. Keep it concise and focused.\n<QUESTION>{query}</QUESTION>"

        else:
            yield f"Unknown action type: {action_type}"
            return

        prompt += "\n</TASK>"

        messages_for_llm = [
            {"role": "system", "content": config.STREAMLIT_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        yield from self.model_handler.get_stream_response(
            model=config.MAIN_LLM_MODEL,
            messages=messages_for_llm
        )
