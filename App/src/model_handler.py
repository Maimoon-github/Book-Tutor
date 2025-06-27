# src/model_handler.py

import ollama
import logging
from .config import LOG_LEVEL, LOG_FORMAT
from typing import List, Dict, Iterator

# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class OllamaClient:
    """A client for interacting with a local Ollama server."""

    def __init__(self, host: str = 'http://localhost:11434'):
        """Initializes the OllamaClient."""
        self.client = None
        try:
            self.client = ollama.Client(host=host)
            self.client.list()
            logger.info(f"Ollama client connected to {host} successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama at {host}. Ensure Ollama is running. Error: {e}")
            self.client = None

    def get_stream_response(self, model: str, messages: List[Dict[str, str]]) -> Iterator[str]:
        """
        Gets a streaming response from the Ollama model.

        Args:
            model: The name of the Ollama model to use.
            messages: A list of message dictionaries for the chat.

        Yields:
            A stream of response chunks from the model.
        """
        if not self.client:
            error_message = "Ollama client is not available. Please restart the application."
            logger.error(error_message)
            yield error_message
            return

        try:
            logger.debug(f"Sending request to model '{model}' with {len(messages)} messages.")
            stream = self.client.chat(model=model, messages=messages, stream=True)
            for chunk in stream:
                if 'content' in chunk.get('message', {}):
                    yield chunk['message']['content']
        except Exception as e:
            error_message = f"An error occurred with Ollama. Is it running? Error: {e}"
            logger.error(error_message)
            yield error_message

