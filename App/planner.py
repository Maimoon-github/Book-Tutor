from typing import List, Dict, Any

def generate_plan(goal: str) -> List[Dict[str, Any]]:
    """
    Generates a plan to achieve a given goal.
    The plan is now focused on using the RAG pipeline for questions.
    """
    plan = []
    normalized_goal = goal.lower().strip()

    # The primary goal is to answer questions using the curriculum.
    # We will default to a RAG search for any input that looks like a question.
    if "?" in normalized_goal or any(word in normalized_goal for word in ["what is", "explain", "who", "where", "when", "why", "how"]):
        plan.append({
            "action": "rag_search",
            "parameters": {"question": goal}
        })
    # If it's not a question, we can have other actions, but for now, we'll
    # treat it as a general statement that doesn't require a tool.
    else:
        plan.append({
            "action": "general_statement",
            "parameters": {"text": goal}
        })


    return plan
