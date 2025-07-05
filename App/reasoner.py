from typing import Dict, Any, List
from langchain_community.llms import Ollama
from memory import Memory
from planner import generate_plan
from executor import execute_task

class Reasoner:
    """
    The "brain" of the agent, responsible for orchestrating the other modules.
    It now constructs a specific prompt for RAG-based questions.
    """
    def __init__(self, model_name: str = "llama3"):
        self.llm = Ollama(model=model_name)
        self.memory = Memory()

    def _generate_response(self, prompt: str) -> str:
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now."

    def process_query(self, user_query: str) -> str:
        self.memory.add("user", user_query)
        plan = generate_plan(user_query)

        # If the plan is just a general statement, we don't need to execute a tool.
        if plan and plan[0].get("action") == "general_statement":
            # A simple conversational reply
            final_response = self._generate_response(f"The user said: '{user_query}'. Respond conversationally.")
            self.memory.add("agent", final_response)
            return final_response

        # Execute the plan (which should be a RAG search)
        execution_results = [execute_task(task) for task in plan]
        retrieved_context = execution_results[0] if execution_results else "No context found."

        # Construct a specialized prompt for the RAG task
        prompt = f"""
        You are an expert tutor. Your goal is to teach a student based on the provided curriculum context.
        A student has asked the following question: "{user_query}"

        Here is the relevant context retrieved from the textbook:
        ---
        {retrieved_context}
        ---

        Based *only* on the provided context, answer the student's question clearly and concisely.
        If the context does not contain the answer, say "I could not find the answer to that in the textbook."
        Do not use any outside knowledge.
        """

        final_response = self._generate_response(prompt)
        self.memory.add("agent", final_response)
        return final_response
