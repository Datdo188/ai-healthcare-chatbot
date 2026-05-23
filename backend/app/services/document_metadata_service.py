from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import UploadedDocument, User


def create_document_metadata(
    db: Session,
    user: User,
    original_filename: str,
    saved_filename: str,
    path: str,
    status_value: str = "uploaded"
) -> UploadedDocument:
    document = UploadedDocument(
        user_id=user.id,
        original_filename=original_filename,
        saved_filename=saved_filename,
        path=path,
        status=status_value
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def list_user_documents(
    db: Session,
    user: User
) -> list[UploadedDocument]:
    return (
        db.query(UploadedDocument)
        .filter(UploadedDocument.user_id == user.id)
        .order_by(UploadedDocument.created_at.desc())
        .all()
    )


def get_user_document_by_saved_filename(
    db: Session,
    user: User,
    saved_filename: str
) -> UploadedDocument:
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.user_id == user.id,
            UploadedDocument.saved_filename == saved_filename
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or you do not have access to it."
        )

    return document


def update_document_status(
    db: Session,
    document: UploadedDocument,
    status_value: str
) -> UploadedDocument:
    document.status = status_value

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def delete_document_metadata(
    db: Session,
    document: UploadedDocument
) -> None:
    db.delete(document)
    db.commit()