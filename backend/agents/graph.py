from langgraph.graph import END, START, StateGraph

from backend.agents.events import create_event
from backend.agents.publisher import publish_event
from backend.agents.state import ProjectState


async def placeholder_node(state: ProjectState) -> ProjectState:
    """
    Minimal orchestration node used to validate:
    - state mutation
    - event emission
    - Redis pub/sub integration
    """

    started_event = create_event(
        event="placeholder_agent_started",
        project_id=state["project_id"],
        agent="placeholder",
        status="running",
    )

    state["events"].append(started_event)

    await publish_event(
        project_id=state["project_id"],
        event=started_event,
    )

    state["active_agent"] = "placeholder"

    completed_event = create_event(
        event="placeholder_agent_completed",
        project_id=state["project_id"],
        agent="placeholder",
        status="completed",
    )

    state["events"].append(completed_event)

    await publish_event(
        project_id=state["project_id"],
        event=completed_event,
    )

    state["pipeline_status"] = "completed"

    pipeline_event = create_event(
        event="pipeline_completed",
        project_id=state["project_id"],
        agent="system",
        status="completed",
    )

    state["events"].append(pipeline_event)

    await publish_event(
        project_id=state["project_id"],
        event=pipeline_event,
    )

    return state


graph_builder = StateGraph(ProjectState)

graph_builder.add_node(
    "placeholder",
    placeholder_node,
)

graph_builder.add_edge(
    START,
    "placeholder",
)

graph_builder.add_edge(
    "placeholder",
    END,
)

graph = graph_builder.compile()
