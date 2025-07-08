import json
from typing import Dict, Any, Tuple, Optional
from langchain_community.llms import Ollama

class ControlFlow:
    """
    This module executes the specific tasks decided by the Reasoner,
    such as handling a RAG search or managing an exercise.
    """
    def __init__(self, llm_instance: Ollama):
        self.llm = llm_instance
        self.exercise_pool = self._load_exercises()

    def _load_exercises(self) -> list:
        """Loads exercises from a local JSON file."""
        try:
            with open("exercises.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return a default exercise if the file is missing or corrupt
            return [{"id": "default-001", "question": "What is 2 + 2?", "answer": "4"}]

    def handle_rag_question(self, user_query: str, rag_retriever) -> str:
        """
        Performs a RAG search and uses an LLM to generate an answer based on context.
        """
        try:
            # 1. Retrieve relevant documents from the vector DB
            docs = rag_retriever.get_relevant_documents(user_query)
            retrieved_context = "\n\n---\n\n".join([doc.page_content for doc in docs])

            if not retrieved_context:
                return "I could not find any relevant information in the provided documents to answer your question."

            # 2. Generate an answer using the context
            prompt = f"""
            You are an expert tutor. Your goal is to teach a student based on the provided curriculum context.
            A student has asked the following question: "{user_query}"

            Here is the relevant context retrieved from the textbook:
            ---
            {retrieved_context}
            ---

            Based *only* on the provided context, answer the student's question clearly and concisely.
            If the context does not contain the answer, state that you could not find the answer in the textbook.
            Do not use any outside knowledge.
            """
            return self.llm.invoke(prompt)

        except Exception as e:
            print(f"Error during RAG search: {e}")
            return "Sorry, I encountered an error while searching the knowledge base."

    def handle_exercise_request(self) -> Tuple[str, Dict[str, Any]]:
        """
        Fetches a new exercise and prepares it for the user.
        """
        # For simplicity, we'll just grab the first exercise.
        # A real system might track progress and select exercises dynamically.
        exercise = self.exercise_pool[0]
        response_text = f"Of course! Let's test your knowledge. Here is your question:\n\n**{exercise['question']}**"
        return response_text, exercise

    def handle_exercise_answer(self, user_answer: str, exercise: Dict[str, Any]) -> str:
        """
        Validates the user's answer to an exercise.
        """
        if not exercise:
            return "There is no active exercise. If you'd like one, just ask!"

        # Simple exact match validation. A more advanced system would use an LLM.
        if user_answer.strip().lower() == exercise['answer'].strip().lower():
            return "That's correct! Well done."
        else:
            return f"That's not quite right. The correct answer is: **{exercise['answer']}**"

    def handle_simple_reply(self, user_query: str) -> str:
        """
        Generates a simple conversational response.
        """
        prompt = f"The user said: '{user_query}'. Respond conversationally in a friendly and brief manner."
        return self.llm.invoke(prompt)

