from backend.agents.state import ProjectState

WORKFLOWS: dict[str, ProjectState] = {}


def register_workflow(
    workflow_id: str,
    state: ProjectState,
) -> None:
    WORKFLOWS[workflow_id] = state


def get_workflow(
    workflow_id: str,
) -> ProjectState | None:
    return WORKFLOWS.get(workflow_id)


def update_workflow(
    workflow_id: str,
    state: ProjectState,
) -> None:
    WORKFLOWS[workflow_id] = state
