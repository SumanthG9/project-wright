from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from backend.agents.checkpoint import get_checkpointer
from backend.agents.events import create_event
from backend.agents.state import ProjectState


async def placeholder_node(state: ProjectState) -> ProjectState:
    """
    Minimal orchestration node used to validate:
    - state mutation
    - checkpoint persistence
    - resumable execution
    """

    started_event = create_event(
        event="placeholder_agent_started",
        project_id=state["project_id"],
        agent="placeholder",
        status="running",
    )

    state["events"].append(started_event)

    state["active_agent"] = "placeholder"
    state["pipeline_status"] = "running"

    completed_event = create_event(
        event="placeholder_agent_completed",
        project_id=state["project_id"],
        agent="placeholder",
        status="completed",
    )

    state["events"].append(completed_event)

    state["pipeline_status"] = "completed"

    pipeline_completed_event = create_event(
        event="pipeline_completed",
        project_id=state["project_id"],
        agent="system",
        status="completed",
    )

    state["events"].append(pipeline_completed_event)

    return state


async def run_graph(state: ProjectState) -> ProjectState:
    """
    Executes the orchestration graph with durable checkpointing.
    """

    builder = StateGraph(ProjectState)

    builder.add_node("placeholder", placeholder_node)

    builder.add_edge(START, "placeholder")
    builder.add_edge("placeholder", END)

    config = {"configurable": {"thread_id": str(uuid4())}}

    async with get_checkpointer() as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)

        result = await graph.ainvoke(
            state,
            config=config,
        )

    return result
