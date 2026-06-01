from typing import Any, Literal, TypedDict


class ProjectState(TypedDict):
    """
    Shared orchestration state for the workflow graph.
    """

    project_id: int
    current_draft_id: int
    extracted_text: str

    active_agent: str
    pipeline_status: str

    retry_count: int

    paused: bool
    waiting_for_input: bool

    approval_status: Literal[
        "",
        "approved",
        "rejected",
    ]

    events: list[dict[str, Any]]
