# backend/projects/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    type: Literal["original", "fanfiction"]  # "original" or "fanfiction"
    genre: str
    audience: str


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    audience: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    type: str
    genre: str
    audience: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
