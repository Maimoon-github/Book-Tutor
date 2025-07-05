import json
from typing import Dict, Any, List

from langchain.llms import Ollama
from memory import Memory
from planner import generate_plan
from executor import execute_task

class Reasoner:
    """
    The "brain" of the agent, responsible for orchestrating the other modules.
    """
    def __init__(self, model_name: str = "llama3"):
        """
        Initializes the Reasoner.

        Args:
            model_name: The name of the Ollama model to use.
        """
        self.llm = Ollama(model=model_name)
        self.memory = Memory()

    def _generate_response(self, prompt: str) -> str:
        """
        Generates a response from the LLM based on a prompt.

        Args:
            prompt: The input prompt for the LLM.

        Returns:
            The raw string response from the LLM.
        """
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now."

    def process_query(self, user_query: str) -> str:
        """
        Processes a user's query and returns the agent's response.

        This method orchestrates the plan-execute-reason loop.

        Args:
            user_query: The query from the user.

        Returns:
            The agent's final response as a string.
        """
        # 1. Add user query to memory
        self.memory.add("user", user_query)

        # 2. Generate a plan based on the user query
        plan = generate_plan(user_query)
        print(f"Generated Plan: {plan}")

        # 3. Execute the plan
        execution_results = []
        context_for_next_step = {}
        for task in plan:
            # Pass results from previous steps if needed
            if "content" in task["parameters"] and "last_result" in context_for_next_step:
                 task["parameters"]["content"] = context_for_next_step.get("last_result")

            result = execute_task(task)
            execution_results.append(result)
            context_for_next_step["last_result"] = result

        print(f"Execution Results: {execution_results}")

        # 4. Reason over the results and generate a final response
        # We'll build a prompt that includes the conversation history and execution results
        conversation_history = self.memory.retrieve(last_k=5)

        prompt = "You are an AI assistant. Based on the following conversation history and the results of the actions you just took, provide a helpful and concise response to the user.\n\n"
        prompt += "## Conversation History:\n"
        for entry in conversation_history:
            prompt += f"{entry['role']}: {entry['content']}\n"

        prompt += "\n## Action Results:\n"
        for i, result in enumerate(execution_results):
            prompt += f"Result of action {i+1}: {str(result)[:1000]}\n" # Truncate long results

        prompt += "\n## Your Final Response:\n"

        final_response = self._generate_response(prompt)

        # 5. Add agent's final response to memory
        self.memory.add("agent", final_response)

        return final_response


if __name__ == '__main__':
    # Example usage:
    reasoner = Reasoner()

    # --- Test Case 1: A simple question ---
    print("--- Running Test Case 1: Simple Question ---")
    query1 = "What is LangChain?"
    response1 = reasoner.process_query(query1)
    print(f"\nUser Query: {query1}")
    print(f"Agent Response: {response1}")

    print("\n" + "="*20 + "\n")

    # --- Test Case 2: A research task (will use placeholder from executor) ---
    print("--- Running Test Case 2: Research Task ---")
    query2 = "Can you research the main features of Python from https://www.python.org/about/"
    response2 = reasoner.process_query(query2)
    print(f"\nUser Query: {query2}")
    print(f"Agent Response: {response2}")
