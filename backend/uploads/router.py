from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.draft import Draft
from backend.models.project import Project
from backend.models.user import User
from backend.uploads.schemas import DraftResponse
from backend.uploads.service import save_upload_file, validate_upload_file

router = APIRouter(tags=["Uploads"])


@router.post(
    "/{project_id}",
    response_model=DraftResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_draft(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a draft file for a project.
    """

    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Validate uploaded file
    await validate_upload_file(file)

    # Temporary versioning strategy (Week 4 Day 3 improves this)
    version_result = await db.execute(
        select(func.count(Draft.id)).where(Draft.project_id == project_id)
    )

    version = version_result.scalar_one() + 1

    # Save file to disk
    saved_file_path = await save_upload_file(
        file=file,
        project_id=project_id,
        version=version,
    )

    draft = Draft(
        project_id=project_id,
        version=version,
        file_path=saved_file_path,
        extracted_text="",
    )

    db.add(draft)

    await db.commit()
    await db.refresh(draft)

    return draft
