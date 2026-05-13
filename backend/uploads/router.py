from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.draft import Draft
from backend.models.project import Project
from backend.models.user import User
from backend.uploads.schemas import DraftListResponse, DraftResponse
from backend.uploads.service import (
    extract_text_from_file,
    get_latest_draft,
    get_next_draft_version,
    save_upload_file,
    validate_upload_file,
)

router = APIRouter(tags=["uploads"])


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

    file_bytes = await file.read()

    validate_upload_file(file, file_bytes)

    version = await get_next_draft_version(db, project_id)

    file_path = save_upload_file(
        file_bytes=file_bytes,
        original_filename=file.filename,
        project_id=project_id,
        version=version,
    )

    extracted_text = extract_text_from_file(file_path)

    draft = Draft(
        project_id=project_id,
        version=version,
        file_path=file_path,
        extracted_text=extracted_text,
    )

    db.add(draft)

    await db.commit()
    await db.refresh(draft)

    return draft


@router.get(
    "/{project_id}/drafts",
    response_model=DraftListResponse,
)
async def list_project_drafts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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

    result = await db.execute(
        select(Draft)
        .where(Draft.project_id == project_id)
        .order_by(Draft.version.desc())
    )

    drafts = result.scalars().all()

    return DraftListResponse(drafts=drafts)


@router.get(
    "/{project_id}/latest",
    response_model=DraftResponse,
)
async def get_latest_project_draft(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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

    latest_draft = await get_latest_draft(db, project_id)

    if not latest_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No drafts found",
        )

    return latest_draft
