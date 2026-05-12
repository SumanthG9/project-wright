from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DraftResponse(BaseModel):
    id: int
    project_id: int
    version: int
    file_path: str
    extracted_text: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
