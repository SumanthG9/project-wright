from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("original", "fanfiction", name="project_type"), nullable=False
    )
    genre: Mapped[str | None] = mapped_column(String(100))
    audience: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="projects")
    drafts: Mapped[list["Draft"]] = relationship(back_populates="project")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="project")
    hitl_checkpoints: Mapped[list["HitlCheckpoint"]] = relationship(
        back_populates="project"
    )
