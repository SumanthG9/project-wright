import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from backend.core.config import settings

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


async def validate_upload_file(file: UploadFile) -> None:
    """
    Validate uploaded file type and size.
    """

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .docx and .pdf files are allowed",
        )

    contents = await file.read()
    file_size = len(contents)

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit",
        )

    # Reset cursor after reading
    await file.seek(0)


async def save_upload_file(
    file: UploadFile,
    project_id: int,
    version: int,
) -> str:
    """
    Save uploaded file to disk and return file path.
    """

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename).suffix.lower()

    unique_filename = f"project_{project_id}_v{version}_{uuid4().hex}{extension}"

    file_path = upload_dir / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)
