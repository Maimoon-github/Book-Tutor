import re
from typing import Dict, Any
from fetcher import fetch_and_parse

def execute_task(task: Dict[str, Any]) -> Any:
    """
    Executes a single task from a plan.

    Args:
        task: A dictionary containing the action to perform and its parameters.

    Returns:
        The result of the executed task.
    """
    action = task.get("action")
    parameters = task.get("parameters", {})
    result = None

    print(f"Executing task: {action} with parameters: {parameters}")

    if action == "fetch_content":
        query = parameters.get("query", "")
        # A simple regex to find a URL in the query string.
        # A more robust solution would use a dedicated search tool.
        url_match = re.search(r'https?://[^\s]+', query)
        if url_match:
            url = url_match.group(0)
            print(f"Found URL: {url}")
            result = fetch_and_parse(url)
        else:
            # Placeholder for a future search implementation
            result = f"Could not find a URL in the query: '{query}'. In the future, I would use a search engine here."

    elif action == "reason_about_content":
        # This will later involve the LLM to analyze the fetched content.
        # For now, it's a placeholder.
        content = parameters.get("content", "") # This would be passed from the previous step's result
        result = f"Placeholder for reasoning about content. Content length: {len(content)}"
        print(result)

    elif action == "answer_question":
        # This will be handled by the RAG pipeline.
        question = parameters.get("question", "")
        result = f"Placeholder for answering question: '{question}'"
        print(result)

    elif action == "general_query":
        # This will be a general-purpose LLM call.
        text = parameters.get("text", "")
        result = f"Placeholder for handling general query: '{text}'"
        print(result)

    else:
        print(f"Unknown action: {action}")
        result = f"Error: Unknown action '{action}'"

    return result

if __name__ == '__main__':
    # Example usage:
    from planner import generate_plan

    # --- Test Case 1: Research Task ---
    print("--- Running Test Case 1: Research Task ---")
    research_goal = "Research https://www.python.org/"
    research_plan = generate_plan(research_goal)

    # We'll simulate the flow of passing results between steps
    context = {}
    for step in research_plan:
        if "content" in step["parameters"]:
             step["parameters"]["content"] = context.get("last_result")

        task_result = execute_task(step)
        context["last_result"] = task_result
        print(f"Task result: {str(task_result)[:100]}...")

    print("\n" + "="*20 + "\n")

    # --- Test Case 2: Question Answering Task ---
    print("--- Running Test Case 2: Question Answering Task ---")
    qa_goal = "What is Python?"
    qa_plan = generate_plan(qa_goal)
    for step in qa_plan:
        execute_task(step)

