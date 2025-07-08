from typing import Tuple, Optional, Dict, Any
from langchain_community.llms import Ollama
from memory import Memory
from control_flow import ControlFlow

class Reasoner:
    """
    The 'brain' of the agent. It decides the user's intent and routes
    the query to the appropriate handler in the ControlFlow module.
    """
    def __init__(self, model_name: str = "deepseek-coder:1.3b"):
        self.llm = Ollama(model=model_name)
        self.memory = Memory()
        self.control_flow = ControlFlow(self.llm)

    def _decide_intent(self, user_query: str, conversation_history: list) -> str:
        """
        Uses the LLM to classify the user's intent.
        """
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        prompt = f"""
        You are a router for an AI tutor. Based on the user's latest query and the conversation history, classify the user's intent into one of the following categories: 'question', 'exercise_request', 'exercise_answer', 'simple_reply'.

        - 'question': The user is asking for information, an explanation, or a definition (e.g., "What is photosynthesis?", "Explain the main causes of World War 1.").
        - 'exercise_request': The user explicitly asks for a test, quiz, or exercise (e.g., "Give me an exercise," "Test my knowledge.").
        - 'exercise_answer': The user is providing an answer to a question you just asked as part of an exercise.
        - 'simple_reply': The user is making a simple conversational statement (e.g., "Hello", "Thanks", "That makes sense").

        Conversation History:
        {history_str}

        User's Latest Query: "{user_query}"

        Intent:
        """
        try:
            response = self.llm.invoke(prompt).strip().lower()
            # Basic parsing to extract the keyword
            if 'exercise_answer' in response:
                return 'exercise_answer'
            if 'exercise_request' in response:
                return 'exercise_request'
            if 'question' in response:
                return 'question'
            return 'simple_reply' # Default
        except Exception as e:
            print(f"Error during intent decision: {e}")
            return 'simple_reply'

    def process_query(self, user_query: str, rag_retriever, current_exercise: Optional[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Processes a user's query based on the system diagram.
        1. Adds user query to memory.
        2. Decides user intent.
        3. Routes to the correct control flow function.
        4. Adds agent response to memory.
        5. Returns the response text and any active exercise object.
        """
        self.memory.add("user", user_query)

        # If there's an active exercise, the intent is likely an answer to it.
        if current_exercise:
            intent = 'exercise_answer'
        else:
            intent = self._decide_intent(user_query, self.memory.retrieve(last_k=5))

        print(f"Decided Intent: {intent}")

        response_text = ""
        exercise_obj_out = None

        if intent == 'exercise_request':
            response_text, exercise_obj_out = self.control_flow.handle_exercise_request()
        elif intent == 'exercise_answer':
            response_text = self.control_flow.handle_exercise_answer(user_query, current_exercise)
            exercise_obj_out = None # The exercise is now complete
        elif intent == 'question':
            if not rag_retriever:
                response_text = "The knowledge base is not ready. Please upload files in the 'Vector DB Management' tab first."
            else:
                response_text = self.control_flow.handle_rag_question(user_query, rag_retriever)
        else: # simple_reply
            response_text = self.control_flow.handle_simple_reply(user_query)

        self.memory.add("agent", response_text)
        return response_text, exercise_obj_out

