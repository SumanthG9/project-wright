from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.graph import resume_graph, run_graph
from backend.agents.state import ProjectState
from backend.pipeline.data_loader import load_project_context
from backend.pipeline.registry import get_workflow, register_workflow, update_workflow


async def start_pipeline(
    project_id: int,
    db: AsyncSession,
) -> tuple[str, ProjectState]:

    workflow_id = str(uuid4())

    state = await load_project_context(
        project_id=project_id,
        db=db,
    )

    result = await run_graph(state)

    register_workflow(
        workflow_id,
        result,
    )

    return workflow_id, result


async def approve_pipeline(
    workflow_id: str,
) -> ProjectState:

    state = get_workflow(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    result = await resume_graph(
        state,
        approval="approved",
    )

    update_workflow(
        workflow_id,
        result,
    )

    return result


async def reject_pipeline(
    workflow_id: str,
) -> ProjectState:

    state = get_workflow(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    result = await resume_graph(
        state,
        approval="rejected",
    )

    update_workflow(
        workflow_id,
        result,
    )

    return result


async def resume_pipeline(
    workflow_id: str,
) -> ProjectState:

    state = get_workflow(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    state["paused"] = False
    state["waiting_for_input"] = False
    state["pipeline_status"] = "running"

    update_workflow(
        workflow_id,
        state,
    )

    return state


def get_pipeline_status(
    workflow_id: str,
) -> ProjectState:

    state = get_workflow(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    return state


def get_pipeline_history(
    workflow_id: str,
) -> ProjectState:

    state = get_workflow(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    return state


def get_pipeline_events(
    workflow_id: str,
) -> list[dict]:

    state = get_workflow(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    return state["events"]
