from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.draft import Draft
from backend.models.project import Project
from backend.models.user import User
from backend.uploads.schemas import DraftResponse
from backend.uploads.service import (
    extract_text_from_file,
    generate_upload_path,
    save_upload_file,
    validate_upload_file,
)

router = APIRouter(tags=["Uploads"])


@router.post(
    "/{project_id}",
    response_model=DraftResponse,
    status_code=201,
)
async def upload_draft(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )

    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    content = await validate_upload_file(file)

    version_result = await db.execute(
        select(func.count(Draft.id)).where(Draft.project_id == project_id)
    )

    version_count = version_result.scalar() or 0
    next_version = version_count + 1

    upload_path = generate_upload_path(
        project_id=project_id,
        version=next_version,
        original_filename=file.filename,
    )

    saved_path = await save_upload_file(content, upload_path)

    extracted_text = extract_text_from_file(saved_path)

    draft = Draft(
        project_id=project_id,
        version=next_version,
        file_path=saved_path,
        extracted_text=extracted_text,
    )

    db.add(draft)

    await db.commit()
    await db.refresh(draft)

    return draft
