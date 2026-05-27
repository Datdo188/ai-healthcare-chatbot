import os
import shutil
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def sanitize_filename(filename: str) -> str:
    base_name = os.path.basename(filename or "").strip()

    if not base_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename."
        )

    safe_name = "".join(
        char if char.isalnum() or char in ("-", "_", ".") else "_"
        for char in base_name
    )

    safe_name = safe_name.strip("._")

    if not safe_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename."
        )

    return safe_name


def get_file_size_bytes(file: UploadFile) -> int:
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    return size


def validate_document(file: UploadFile) -> str:
    safe_filename = sanitize_filename(file.filename or "")
    _, extension = os.path.splitext(safe_filename.lower())

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are allowed."
        )

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file_size = get_file_size_bytes(file)

    if file_size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File is too large. Maximum allowed size is "
                f"{settings.MAX_UPLOAD_SIZE_MB} MB."
            )
        )

    return safe_filename


def generate_unique_filename(original_filename: str) -> str:
    safe_filename = sanitize_filename(original_filename)
    name, extension = os.path.splitext(safe_filename)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid4().hex[:8]

    return f"{timestamp}_{unique_id}_{name}{extension}"


def save_uploaded_document(file: UploadFile) -> dict:
    safe_original_filename = validate_document(file)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_filename = generate_unique_filename(safe_original_filename)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "original_filename": safe_original_filename,
        "saved_filename": unique_filename,
        "path": file_path
    }


def delete_document_file(file_path: str) -> bool:
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return True

    return False