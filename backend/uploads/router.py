from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.draft import Draft
from backend.models.project import Project
from backend.models.user import User
from backend.uploads.schemas import DraftListResponse, DraftResponse
from backend.uploads.service import (
    delete_uploaded_file,
    extract_text_from_file,
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
) -> DraftResponse:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    file_bytes = await file.read()

    validate_upload_file(file, len(file_bytes))

    version_result = await db.execute(
        select(func.max(Draft.version)).where(Draft.project_id == project_id)
    )

    max_version = version_result.scalar()

    next_version = (max_version or 0) + 1

    saved_path = save_upload_file(
        file_bytes=file_bytes,
        project_id=project_id,
        version=next_version,
        original_filename=file.filename,
    )

    try:
        extracted_text = extract_text_from_file(saved_path)

        if not extracted_text.strip():
            delete_uploaded_file(saved_path)

            raise HTTPException(
                status_code=400,
                detail="Document contains no extractable text",
            )

    except Exception:
        delete_uploaded_file(saved_path)
        raise

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


@router.get(
    "/{project_id}/drafts",
    response_model=DraftListResponse,
)
async def list_project_drafts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DraftListResponse:
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
            detail="Project not found",
        )

    drafts_result = await db.execute(
        select(Draft)
        .where(Draft.project_id == project_id)
        .order_by(Draft.version.desc())
    )

    drafts = drafts_result.scalars().all()

    return DraftListResponse(drafts=drafts)


@router.get(
    "/{project_id}/latest",
    response_model=DraftResponse,
)
async def get_latest_draft(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DraftResponse:
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
            detail="Project not found",
        )

    draft_result = await db.execute(
        select(Draft)
        .where(Draft.project_id == project_id)
        .order_by(Draft.version.desc())
        .limit(1)
    )

    latest_draft = draft_result.scalar_one_or_none()

    if not latest_draft:
        raise HTTPException(
            status_code=404,
            detail="No drafts found for this project",
        )

    return latest_draft
