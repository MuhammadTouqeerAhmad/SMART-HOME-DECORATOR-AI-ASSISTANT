from src.agent import graph

def generate_design(initial_state: dict) -> dict:
    """
    Execute the existing LangGraph design workflow.
    """
    result = graph.invoke(initial_state)

    return result