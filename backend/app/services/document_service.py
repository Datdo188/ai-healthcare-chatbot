import os
import shutil
from datetime import datetime
from uuid import uuid4

from fastapi import UploadFile, HTTPException, status

UPLOAD_DIR = "data/medical_docs"

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def sanitize_filename(filename: str) -> str:
    """
    Remove unsafe path characters from uploaded filename.
    """

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


def validate_document(file: UploadFile) -> str:
    safe_filename = sanitize_filename(file.filename or "")
    _, extension = os.path.splitext(safe_filename.lower())

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are allowed."
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
    """
    Delete physical document file if it exists.
    Returns True if deleted, False if file was already missing.
    """

    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return True

    return False