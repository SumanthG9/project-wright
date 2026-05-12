from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    title: str
    type: Literal["original", "fanfiction"]
    genre: str
    audience: str


class ProjectUpdate(BaseModel):
    title: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    type: str
    genre: str
    audience: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
