from pydantic import BaseModel


class PipelineStartRequest(BaseModel):
    project_id: int


class ApprovalRequest(BaseModel):
    notes: str | None = None


class PipelineStatusResponse(BaseModel):
    workflow_id: str
    project_id: int
    status: str
    active_agent: str
    paused: bool
    waiting_for_input: bool
    approval_status: str


class PipelineHistoryResponse(BaseModel):
    workflow_id: str
    project_id: int
    status: str
    active_agent: str
    paused: bool
    waiting_for_input: bool
    approval_status: str
    retry_count: int
    event_count: int


class PipelineEventsResponse(BaseModel):
    workflow_id: str
    events: list[dict]
