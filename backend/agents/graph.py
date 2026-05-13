from langgraph.graph import END, START, StateGraph

from backend.agents.events import create_event
from backend.agents.state import ProjectState


def placeholder_node(state: ProjectState) -> ProjectState:
    """
    Minimal placeholder orchestration node.

    No AI logic yet.
    Only validates LangGraph execution flow.
    """

    event = create_event(
        event="agent_started",
        project_id=state["project_id"],
        agent="placeholder",
        status="running",
    )

    state["active_agent"] = "placeholder"
    state["pipeline_status"] = "running"

    state["events"].append(event)

    completion_event = create_event(
        event="agent_completed",
        project_id=state["project_id"],
        agent="placeholder",
        status="completed",
    )

    state["events"].append(completion_event)

    state["pipeline_status"] = "completed"

    return state


def build_graph():
    """
    Build minimal Project Wright orchestration graph.
    """

    graph_builder = StateGraph(ProjectState)

    graph_builder.add_node("placeholder", placeholder_node)

    graph_builder.add_edge(START, "placeholder")
    graph_builder.add_edge("placeholder", END)

    return graph_builder.compile()
