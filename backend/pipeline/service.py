from uuid import uuid4

from backend.agents.graph import resume_graph, run_graph
from backend.agents.state import ProjectState

# Temporary in-memory workflow registry
# Phase 3 only.
# Later replaced by database persistence.
WORKFLOWS: dict[str, ProjectState] = {}


async def start_pipeline(
    project_id: int,
    draft_id: int,
) -> tuple[str, ProjectState]:

    workflow_id = str(uuid4())

    state: ProjectState = {
        "project_id": project_id,
        "current_draft_id": draft_id,
        "extracted_text": "",
        "active_agent": "",
        "pipeline_status": "pending",
        "retry_count": 0,
        "paused": False,
        "waiting_for_input": False,
        "approval_status": "",
        "events": [],
    }

    result = await run_graph(state)

    WORKFLOWS[workflow_id] = result

    return workflow_id, result


async def approve_pipeline(workflow_id: str) -> ProjectState:

    state = WORKFLOWS.get(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    result = await resume_graph(
        state,
        approval="approved",
    )

    WORKFLOWS[workflow_id] = result

    return result


async def reject_pipeline(workflow_id: str) -> ProjectState:

    state = WORKFLOWS.get(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    result = await resume_graph(
        state,
        approval="rejected",
    )

    WORKFLOWS[workflow_id] = result

    return result


def get_pipeline_status(workflow_id: str) -> ProjectState:

    state = WORKFLOWS.get(workflow_id)

    if state is None:
        raise ValueError("Workflow not found")

    return state
