from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.state import ProjectState
from backend.models.draft import Draft


async def get_latest_project_draft(
    project_id: int,
    db: AsyncSession,
) -> Draft | None:
    result = await db.execute(
        select(Draft)
        .where(Draft.project_id == project_id)
        .order_by(Draft.version.desc())
    )

    return result.scalars().first()


async def load_project_context(
    project_id: int,
    db: AsyncSession,
) -> ProjectState:

    draft = await get_latest_project_draft(
        project_id=project_id,
        db=db,
    )

    if draft is None:
        raise ValueError("No draft available for processing")

    if not draft.extracted_text or not draft.extracted_text.strip():
        raise ValueError("Draft contains no extracted text")

    return {
        "project_id": project_id,
        "current_draft_id": draft.id,
        "extracted_text": draft.extracted_text,
        "idc_output": {},
        "active_agent": "",
        "pipeline_status": "pending",
        "retry_count": 0,
        "paused": False,
        "waiting_for_input": False,
        "approval_status": "",
        "events": [],
    }
