from pathlib import Path
from uuid import uuid4

import fitz
from docx import Document
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.models.draft import Draft

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


def validate_upload_file(file: UploadFile, file_bytes: bytes) -> None:
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .docx and .pdf files are allowed",
        )

    max_size = settings.max_upload_size_mb * 1024 * 1024

    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit",
        )


async def get_next_draft_version(
    db: AsyncSession,
    project_id: int,
) -> int:
    result = await db.execute(
        select(func.max(Draft.version)).where(Draft.project_id == project_id)
    )

    max_version = result.scalar()

    return (max_version or 0) + 1


def save_upload_file(
    file_bytes: bytes,
    original_filename: str,
    project_id: int,
    version: int,
) -> str:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(original_filename).suffix.lower()

    filename = f"project_{project_id}_v{version}_{uuid4().hex}{extension}"

    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return str(file_path)


def extract_docx_text(file_path: str) -> str:
    try:
        document = Document(file_path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"DOCX extraction failed: {str(e)}",
        )


def extract_pdf_text(file_path: str) -> str:
    try:
        pdf = fitz.open(file_path)

        pages = []

        for page in pdf:
            text = page.get_text().strip()

            if text:
                pages.append(text)

        pdf.close()

        return "\n\n".join(pages)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF extraction failed: {str(e)}",
        )


def extract_text_from_file(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".docx":
        return extract_docx_text(file_path)

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type",
    )


async def get_latest_draft(
    db: AsyncSession,
    project_id: int,
) -> Draft | None:
    result = await db.execute(
        select(Draft)
        .where(Draft.project_id == project_id)
        .order_by(Draft.version.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()
