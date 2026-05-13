from typing import Any, TypedDict


class ProjectState(TypedDict):
    """
    Shared orchestration state for the workflow graph.

    Every future agent mutates this same object.
    """

    project_id: int
    current_draft_id: int
    extracted_text: str

    active_agent: str
    pipeline_status: str

    retry_count: int

    events: list[dict[str, Any]]
