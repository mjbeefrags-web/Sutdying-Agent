import hashlib
import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from apps.api.app.core.config import get_settings
from apps.api.app.core.errors import AppError
from apps.api.app.core.rate_limit import enforce_rate_limit
from apps.api.app.db.models import (
    AuditEvent,
    Course,
    DocumentVersion,
    Membership,
    OutboxEvent,
    StudyDocument,
    User,
)
from apps.api.app.db.session import get_db
from apps.api.app.domains.documents.schemas import DocumentRead
from apps.api.app.domains.documents.storage import (
    ObjectStorage,
    StorageUnavailable,
    get_object_storage,
)
from apps.api.app.domains.identity.dependencies import get_current_user, require_csrf

logger = logging.getLogger("study_platform.documents")
router = APIRouter(tags=["documents"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
Csrf = Annotated[None, Depends(require_csrf)]


def _course_for_user(db: Session, course_id: UUID, user_id: UUID) -> Course:
    course = db.scalar(
        select(Course)
        .join(Membership, Membership.organization_id == Course.organization_id)
        .where(Course.id == course_id, Membership.user_id == user_id)
    )
    if course is None:
        raise AppError(404, "not_found", "The requested resource was not found.")
    return course


def _document_for_user(db: Session, document_id: UUID, user_id: UUID) -> StudyDocument:
    document = db.scalar(
        select(StudyDocument)
        .join(Course, Course.id == StudyDocument.course_id)
        .join(Membership, Membership.organization_id == Course.organization_id)
        .where(
            StudyDocument.id == document_id,
            StudyDocument.deleted_at.is_(None),
            Membership.user_id == user_id,
        )
        .options(selectinload(StudyDocument.versions))
    )
    if document is None:
        raise AppError(404, "not_found", "The requested resource was not found.")
    return document


def _document_read(document: StudyDocument) -> DocumentRead:
    version = max(document.versions, key=lambda record: record.version, default=None)
    if version is None:
        raise AppError(500, "document_version_missing", "The document is unavailable.")
    return DocumentRead(
        id=document.id,
        course_id=document.course_id,
        title=document.title,
        filename=version.original_filename,
        version=version.version,
        status=version.status,
        error_code=version.error_code,
        size_bytes=version.size_bytes,
        page_count=version.page_count,
        created_at=document.created_at,
        updated_at=version.updated_at,
    )


def _audit_document(db: Session, request: Request, document: StudyDocument, user: User) -> None:
    db.add(
        AuditEvent(
            actor_user_id=user.id,
            organization_id=document.course.organization_id,
            action="document.deleted",
            resource_type="document",
            resource_id=str(document.id),
            request_id=getattr(request.state, "request_id", ""),
            metadata_json={},
        )
    )


def _safe_filename(filename: str | None) -> str:
    normalized = (filename or "").replace("\\", "/").strip()
    safe_name = Path(normalized).name
    if not safe_name or safe_name in {".", ".."} or Path(safe_name).suffix.casefold() != ".pdf":
        raise AppError(415, "unsupported_document_type", "Only PDF documents are supported.")
    if len(safe_name) > 255:
        raise AppError(422, "filename_too_long", "The filename must be 255 characters or less.")
    return safe_name


@router.get("/courses/{course_id}/documents", response_model=list[DocumentRead])
def list_documents(course_id: UUID, db: DbSession, user: CurrentUser) -> list[DocumentRead]:
    _course_for_user(db, course_id, user.id)
    documents = list(
        db.scalars(
            select(StudyDocument)
            .where(StudyDocument.course_id == course_id, StudyDocument.deleted_at.is_(None))
            .options(selectinload(StudyDocument.versions))
            .order_by(StudyDocument.created_at.desc(), StudyDocument.id)
        )
    )
    return [_document_read(document) for document in documents]


@router.post(
    "/courses/{course_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def upload_document(
    course_id: UUID,
    request: Request,
    db: DbSession,
    user: CurrentUser,
    _csrf: Csrf,
    file: Annotated[UploadFile, File()],
) -> DocumentRead:
    settings = get_settings()
    course = _course_for_user(db, course_id, user.id)
    enforce_rate_limit("documents:upload", str(user.id), 20, 60 * 60)
    filename = _safe_filename(file.filename)
    request_length = request.headers.get("content-length")
    if request_length is not None:
        try:
            if int(request_length) > settings.max_document_upload_bytes + 1_000_000:
                raise AppError(413, "document_too_large", "The PDF exceeds the upload size limit.")
        except ValueError as exc:
            raise AppError(400, "invalid_content_length", "The upload request is invalid.") from exc
    if file.size is not None and file.size > settings.max_document_upload_bytes:
        raise AppError(413, "document_too_large", "The PDF exceeds the upload size limit.")

    checksum = hashlib.sha256()
    size_bytes = 0
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
            temp_path = Path(temporary.name)
            while block := file.file.read(1024 * 1024):
                size_bytes += len(block)
                if size_bytes > settings.max_document_upload_bytes:
                    raise AppError(
                        413, "document_too_large", "The PDF exceeds the upload size limit."
                    )
                if size_bytes <= 5 and not b"%PDF-".startswith(block[:5]):
                    raise AppError(415, "invalid_pdf_signature", "The uploaded file is not a PDF.")
                checksum.update(block)
                temporary.write(block)
        if size_bytes == 0:
            raise AppError(422, "empty_document", "The uploaded PDF is empty.")
        with temp_path.open("rb") as uploaded:
            if uploaded.read(5) != b"%PDF-":
                raise AppError(415, "invalid_pdf_signature", "The uploaded file is not a PDF.")

        checksum_hex = checksum.hexdigest()
        duplicate = db.scalar(
            select(StudyDocument.id).where(
                StudyDocument.course_id == course_id,
                StudyDocument.checksum_sha256 == checksum_hex,
                StudyDocument.deleted_at.is_(None),
            )
        )
        if duplicate is not None:
            raise AppError(409, "duplicate_document", "This PDF is already in the course.")
        db.rollback()

        document_id = uuid4()
        version_id = uuid4()
        object_key = f"documents/{course_id.hex}/{document_id.hex}/{version_id.hex}.pdf"
        storage = get_object_storage()
        try:
            storage.put_file(object_key, temp_path, size_bytes)
        except StorageUnavailable as exc:
            raise AppError(503, "document_storage_unavailable", str(exc)) from exc

        version = DocumentVersion(
            id=version_id,
            version=1,
            original_filename=filename,
            content_type="application/pdf",
            size_bytes=size_bytes,
            checksum_sha256=checksum_hex,
            object_key=object_key,
            status="queued",
        )
        document = StudyDocument(
            id=document_id,
            course_id=course_id,
            uploaded_by_user_id=user.id,
            title=Path(filename).stem,
            checksum_sha256=checksum_hex,
            versions=[version],
        )
        document.course = course
        db.add(document)
        db.add(
            OutboxEvent(
                event_type="document.process",
                aggregate_id=str(version_id),
                schema_version=1,
                payload={"version_id": str(version_id)},
            )
        )
        db.commit()
        db.refresh(document)
        db.refresh(version)
        return _document_read(document)
    except IntegrityError as exc:
        db.rollback()
        if "object_key" in locals():
            _delete_orphan(get_object_storage(), object_key)
        duplicate = db.scalar(
            select(StudyDocument.id).where(
                StudyDocument.course_id == course_id,
                StudyDocument.checksum_sha256 == checksum.hexdigest(),
                StudyDocument.deleted_at.is_(None),
            )
        )
        if duplicate is not None:
            raise AppError(409, "duplicate_document", "This PDF is already in the course.") from exc
        raise AppError(503, "document_save_failed", "The document could not be saved.") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        if "object_key" in locals():
            _delete_orphan(get_object_storage(), object_key)
        raise AppError(503, "document_save_failed", "The document could not be saved.") from exc
    finally:
        file.file.close()
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _delete_orphan(storage: ObjectStorage, object_key: str) -> None:
    try:
        storage.delete(object_key)
    except StorageUnavailable:
        logger.exception("orphaned_document_object", extra={"object_key": object_key})


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document(document_id: UUID, db: DbSession, user: CurrentUser) -> DocumentRead:
    return _document_read(_document_for_user(db, document_id, user.id))


@router.post("/documents/{document_id}/retry", response_model=DocumentRead, status_code=202)
def retry_document(
    document_id: UUID,
    request: Request,
    db: DbSession,
    user: CurrentUser,
    _csrf: Csrf,
) -> DocumentRead:
    document = _document_for_user(db, document_id, user.id)
    version = max(document.versions, key=lambda record: record.version, default=None)
    if version is None:
        raise AppError(500, "document_version_missing", "The document is unavailable.")
    if version.status != "failed":
        raise AppError(409, "document_not_retryable", "Only failed processing can be retried.")
    version.status = "queued"
    version.error_code = None
    version.processing_task_id = None
    version.processed_at = None
    version.updated_at = datetime.now(UTC)
    db.add(
        OutboxEvent(
            event_type="document.process",
            aggregate_id=str(version.id),
            schema_version=1,
            payload={"version_id": str(version.id)},
        )
    )
    db.commit()
    db.refresh(version)
    return _document_read(document)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    request: Request,
    db: DbSession,
    user: CurrentUser,
    _csrf: Csrf,
) -> Response:
    document = _document_for_user(db, document_id, user.id)
    object_keys = [version.object_key for version in document.versions]
    db.rollback()
    storage = get_object_storage()
    for object_key in object_keys:
        try:
            storage.delete(object_key)
        except StorageUnavailable as exc:
            raise AppError(503, "document_storage_unavailable", str(exc)) from exc
    document = _document_for_user(db, document_id, user.id)
    _audit_document(db, request, document, user)
    db.delete(document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
