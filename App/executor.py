import re
from typing import Dict, Any
from fetcher import fetch_and_parse
# Updated import to use the new robust document parser
from utils.document_parser import get_vectorstore

# Initialize the RAG retriever from our vector store
try:
    vectorstore = get_vectorstore()
    rag_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
except Exception as e:
    print(f"Failed to initialize RAG retriever: {e}")
    rag_retriever = None

def execute_task(task: Dict[str, Any]) -> Any:
    """
    Executes a single task from a plan.
    """
    action = task.get("action")
    parameters = task.get("parameters", {})
    result = None

    print(f"Executing task: {action} with parameters: {parameters}")

    if action == "rag_search":
        if not rag_retriever:
            return "Error: RAG system is not available."

        question = parameters.get("question", "")
        if not question:
            return "Error: No question provided for RAG search."

        try:
            docs = rag_retriever.get_relevant_documents(question)
            result = "\n\n---\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            result = f"Error during RAG search: {e}"

    elif action == "fetch_content":
        query = parameters.get("query", "")
        url_match = re.search(r'https?://[^\s]+', query)
        if url_match:
            url = url_match.group(0)
            result = fetch_and_parse(url)
        else:
            result = f"Could not find a URL in the query: '{query}'."

    else:
        result = f"Error: Unknown action '{action}'"

    return result
