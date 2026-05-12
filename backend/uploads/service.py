from pathlib import Path
from uuid import uuid4

import docx
import fitz
from fastapi import HTTPException, UploadFile

from backend.core.config import settings

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


async def validate_upload_file(
    file: UploadFile,
) -> bytes:
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .docx and .pdf files are allowed.",
        )

    content = await file.read()

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit.",
        )

    return content


def generate_upload_path(
    project_id: int,
    version: int,
    original_filename: str,
) -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(original_filename).suffix.lower()

    filename = f"project_{project_id}_v{version}_{uuid4().hex}{extension}"

    return upload_dir / filename


async def save_upload_file(
    content: bytes,
    destination: Path,
) -> str:
    with open(destination, "wb") as buffer:
        buffer.write(content)

    return str(destination)


def extract_docx_text(file_path: str) -> str:
    try:
        document = docx.Document(file_path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DOCX extraction failed: {str(e)}",
        )


def extract_pdf_text(file_path: str) -> str:
    try:
        document = fitz.open(file_path)

        extracted_pages = []

        for page in document:
            text = page.get_text().strip()

            if text:
                extracted_pages.append(text)

        document.close()

        return "\n\n".join(extracted_pages)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {str(e)}",
        )


def extract_text_from_file(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".docx":
        return extract_docx_text(file_path)

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type for extraction.",
    )
