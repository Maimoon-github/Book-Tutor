from typing import List, Dict, Any

def generate_plan(goal: str) -> List[Dict[str, Any]]:
    """
    Generates a sequence of steps to achieve a given goal.

    For this initial version, the planner is rule-based. It checks for
    keywords in the goal to decide which plan to execute.

    Args:
        goal: The high-level goal.

    Returns:
        A list of dictionaries, where each dictionary represents a sub-task.
    """
    plan = []
    normalized_goal = goal.lower()

    # Rule 1: If the goal is to research a topic, fetch content from a URL.
    # A more advanced version would use a search engine to find the URL.
    if "research" in normalized_goal or "look up" in normalized_goal:
        # For now, we'll assume the goal contains a URL.
        # A future version could use a search tool to find a relevant URL.
        # This is a placeholder for a more sophisticated implementation.
        plan.append({
            "action": "fetch_content",
            "parameters": {"query": goal} # The 'goal' is passed as a query to be handled later
        })
        plan.append({
            "action": "reason_about_content",
            "parameters": {}
        })

    # Rule 2: If the goal is to answer a direct question.
    elif "?" in normalized_goal:
        plan.append({
            "action": "answer_question",
            "parameters": {"question": goal}
        })

    # Default plan: If no specific rule matches, treat it as a general query.
    else:
        plan.append({
            "action": "general_query",
            "parameters": {"text": goal}
        })

    return plan

if __name__ == '__main__':
    # Example usage:
    test_goal_1 = "Research the history of Python programming."
    plan_1 = generate_plan(test_goal_1)
    print(f"Plan for '{test_goal_1}':")
    for step in plan_1:
        print(f"- {step}")

    print("-" * 20)

    test_goal_2 = "What is the capital of France?"
    plan_2 = generate_plan(test_goal_2)
    print(f"Plan for '{test_goal_2}':")
    for step in plan_2:
        print(f"- {step}")
