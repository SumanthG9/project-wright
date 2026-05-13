from datetime import datetime

from pydantic import BaseModel


class DraftResponse(BaseModel):
    id: int
    project_id: int
    version: int
    file_path: str
    extracted_text: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class DraftListResponse(BaseModel):
    drafts: list[DraftResponse]
