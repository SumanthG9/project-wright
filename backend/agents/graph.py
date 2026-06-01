from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from backend.agents.checkpoint import get_checkpointer
from backend.agents.events import (
    APPROVAL_RECEIVED,
    APPROVAL_REJECTED,
    PIPELINE_COMPLETED,
    WAITING_FOR_APPROVAL,
    WORKFLOW_PAUSED,
    WORKFLOW_RESUMED,
    create_event,
)
from backend.agents.idc import idc_node
from backend.agents.state import ProjectState


async def placeholder_node(state: ProjectState) -> ProjectState:
    """
    Simulated orchestration node.
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

    return state


async def hitl_node(state: ProjectState) -> ProjectState:
    """
    Simulated HITL checkpoint.
    """

    state["paused"] = True
    state["waiting_for_input"] = True
    state["pipeline_status"] = "paused"

    state["events"].append(
        create_event(
            event=WORKFLOW_PAUSED,
            project_id=state["project_id"],
            agent="hitl",
            status="paused",
        )
    )

    state["events"].append(
        create_event(
            event=WAITING_FOR_APPROVAL,
            project_id=state["project_id"],
            agent="hitl",
            status="waiting",
        )
    )

    return state


async def finalize_node(state: ProjectState) -> ProjectState:
    """
    Final orchestration node.
    """

    state["pipeline_status"] = "completed"

    if state.get("approval_status") == "approved":
        state["events"].append(
            create_event(
                event=APPROVAL_RECEIVED,
                project_id=state["project_id"],
                agent="hitl",
                status="approved",
            )
        )
    else:
        state["events"].append(
            create_event(
                event=APPROVAL_REJECTED,
                project_id=state["project_id"],
                agent="hitl",
                status="rejected",
            )
        )

    state["events"].append(
        create_event(
            event=WORKFLOW_RESUMED,
            project_id=state["project_id"],
            agent="hitl",
            status="running",
        )
    )

    state["events"].append(
        create_event(
            event=PIPELINE_COMPLETED,
            project_id=state["project_id"],
            agent="system",
            status="completed",
        )
    )

    return state


def route_after_hitl(state: ProjectState):
    """
    Conditional routing after HITL checkpoint.
    """

    if state.get("approval_status") in ("approved", "rejected"):
        return "finalize"

    return END


async def run_graph(state: ProjectState) -> ProjectState:
    """
    Executes workflow until the HITL pause point.
    """

    builder = StateGraph(ProjectState)

    # Nodes
    builder.add_node("idc", idc_node)
    builder.add_node("hitl", hitl_node)
    builder.add_node("finalize", finalize_node)

    # Flow
    builder.add_edge(START, "idc")
    builder.add_edge("idc", "hitl")

    builder.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {
            "finalize": "finalize",
            END: END,
        },
    )

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    async with get_checkpointer() as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)

        result = await graph.ainvoke(
            state,
            config=config,
        )

    return result


async def resume_graph(
    state: ProjectState,
    approval: str = "approved",
) -> ProjectState:
    """
    Resume workflow from paused HITL state.
    """

    state["paused"] = False
    state["waiting_for_input"] = False
    state["approval_status"] = approval

    builder = StateGraph(ProjectState)

    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "finalize")
    builder.add_edge("finalize", END)

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    async with get_checkpointer() as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)

        result = await graph.ainvoke(
            state,
            config=config,
        )

    return result
