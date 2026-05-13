from typing import TypedDict


class ProjectState(TypedDict):
    project_id: int
    current_draft_id: int
    extracted_text: str

    active_agent: str
    pipeline_status: str

    retry_count: int

    events: list[dict]
