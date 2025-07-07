import re
from typing import Dict, Any

# fetch_and_parse is no longer used in the main RAG workflow but kept for potential future use
from fetcher import fetch_and_parse

def execute_task(task: Dict[str, Any], rag_retriever) -> Any:
    """
    Executes a single task from a plan using the provided RAG retriever.
    """
    action = task.get("action")
    parameters = task.get("parameters", {})
    result = None

    print(f"Executing task: {action} with parameters: {parameters}")

    if action == "rag_search":
        if not rag_retriever:
            return "Error: RAG system has not been initialized. Please upload files first."

        question = parameters.get("question", "")
        if not question:
            return "Error: No question provided for RAG search."

        try:
            docs = rag_retriever.get_relevant_documents(question)
            result = "\n\n---\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            result = f"Error during RAG search: {e}"

    else:
        result = f"Error: Unknown action '{action}'"

    return result
