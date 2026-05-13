from pydantic import BaseModel


class PipelineStartRequest(BaseModel):
    project_id: int
    draft_id: int


class PipelineResponse(BaseModel):
    project_id: int
    status: str
    active_agent: str
