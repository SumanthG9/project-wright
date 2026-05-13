from pathlib import Path
from uuid import uuid4

import fitz
from docx import Document
from fastapi import HTTPException, UploadFile

from backend.core.config import settings

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


def validate_upload_file(file: UploadFile, file_size: int) -> None:
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .docx and .pdf files are allowed",
        )

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit",
        )


def save_upload_file(
    *,
    file_bytes: bytes,
    project_id: int,
    version: int,
    original_filename: str,
) -> str:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(original_filename).suffix.lower()

    unique_filename = f"project_{project_id}_v{version}_{uuid4().hex}{extension}"

    file_path = upload_dir / unique_filename

    file_path.write_bytes(file_bytes)

    return str(file_path)


def delete_uploaded_file(file_path: str) -> None:
    path = Path(file_path)

    if path.exists():
        path.unlink()


def extract_docx_text(file_path: str) -> str:
    try:
        document = Document(file_path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"DOCX extraction failed: {str(exc)}",
        ) from exc


def extract_pdf_text(file_path: str) -> str:
    try:
        document = fitz.open(file_path)

        pages = []

        for page in document:
            text = page.get_text().strip()

            if text:
                pages.append(text)

        return "\n\n".join(pages)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"PDF extraction failed: {str(exc)}",
        ) from exc


def extract_text_from_file(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".docx":
        return extract_docx_text(file_path)

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type",
    )
