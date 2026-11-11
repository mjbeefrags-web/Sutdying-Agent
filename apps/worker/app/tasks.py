import logging
import smtplib
import ssl
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from uuid import UUID

from celery import Task
from celery.exceptions import CeleryError
from kombu.exceptions import OperationalError
from sqlalchemy import delete, select

from apps.api.app.core.config import get_settings
from apps.api.app.db.models import DocumentChunk, DocumentVersion, OutboxEvent, StudyDocument
from apps.api.app.db.session import SessionLocal
from apps.api.app.domains.documents.embeddings import EmbeddingUnavailable, embed_texts
from apps.api.app.domains.documents.processing import (
    DocumentProcessingError,
    chunk_pages,
    extract_pages,
)
from apps.api.app.domains.documents.storage import StorageUnavailable, get_object_storage
from apps.api.app.domains.identity.security import decrypt_outbox_token
from apps.worker.app.celery_app import celery_app

logger = logging.getLogger("study_platform.outbox")


@celery_app.task(name="system.ping")
def ping() -> str:
    return "pong"


def _send_email(recipient: str, purpose: str, token: str) -> None:
    settings = get_settings()
    link_path = "verify-email" if purpose == "verify_email" else "reset-password"
    subject = (
        "Verify your Study Platform email" if purpose == "verify_email" else "Reset your password"
    )
    action = "verify your email" if purpose == "verify_email" else "reset your password"
    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(
        f"Use this link to {action}:\n\n"
        f"{settings.web_origin}/{link_path}?token={token}\n\n"
        "If you did not request this, you can ignore this message."
    )
    context = ssl.create_default_context()
    if settings.smtp_use_tls:
        with smtplib.SMTP_SSL(
            settings.smtp_host, settings.smtp_port, timeout=10, context=context
        ) as smtp:
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_username:
                smtp.starttls(context=context)
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)


@celery_app.task(name="outbox.dispatch")
def dispatch_outbox() -> int:
    now = datetime.now(UTC)
    with SessionLocal.begin() as db:
        events = list(
            db.scalars(
                select(OutboxEvent)
                .where(
                    OutboxEvent.processed_at.is_(None),
                    OutboxEvent.available_at <= now,
                    OutboxEvent.event_type.in_(
                        ("email.verify_email", "email.reset_password", "document.process")
                    ),
                )
                .order_by(OutboxEvent.created_at)
                .with_for_update(skip_locked=True)
                .limit(10)
            )
        )
        event_ids = [(event.id, event.event_type) for event in events]
        for event in events:
            event.attempts += 1
            event.available_at = now + timedelta(seconds=30)

    delivered = 0
    for event_id, event_type in event_ids:
        if event_type == "document.process":
            delivered += int(_enqueue_document_event(event_id))
        else:
            delivered += int(_deliver_event(event_id))
    return delivered


def _enqueue_document_event(event_id: UUID) -> bool:
    with SessionLocal() as db:
        event = db.get(OutboxEvent, event_id)
        if event is None or event.processed_at is not None:
            return False
        try:
            version_id = UUID(str(event.payload["version_id"]))
        except (KeyError, ValueError) as exc:
            logger.error(
                "document_outbox_invalid",
                extra={"event_id": str(event_id), "error_type": type(exc).__name__},
            )
            _fail_outbox_event(event_id)
            return False

    try:
        process_document.delay(str(version_id))
    except (CeleryError, OperationalError) as exc:
        logger.warning(
            "document_dispatch_failed",
            extra={"event_id": str(event_id), "error_type": type(exc).__name__},
        )
        _retry_outbox_event(event_id)
        return False

    with SessionLocal.begin() as db:
        event = db.get(OutboxEvent, event_id)
        if event is not None and event.processed_at is None:
            event.processed_at = datetime.now(UTC)
            event.payload = {}
    return True


def _retry_outbox_event(event_id: UUID) -> None:
    with SessionLocal.begin() as db:
        event = db.get(OutboxEvent, event_id)
        if event is not None and event.processed_at is None:
            if event.attempts >= 10:
                event.event_type = "document.delivery_failed"
                event.processed_at = datetime.now(UTC)
                event.payload = {}
            else:
                event.available_at = datetime.now(UTC) + timedelta(
                    seconds=min(30 * 2 ** min(event.attempts, 9), 3600)
                )


def _fail_outbox_event(event_id: UUID) -> None:
    with SessionLocal.begin() as db:
        event = db.get(OutboxEvent, event_id)
        if event is not None and event.processed_at is None:
            event.event_type = "document.delivery_failed"
            event.processed_at = datetime.now(UTC)
            event.payload = {}


@celery_app.task(name="documents.process", bind=True)
def process_document(task: Task, version_id_value: str) -> None:
    version_id = UUID(version_id_value)
    task_id = task.request.id
    with SessionLocal.begin() as db:
        version = db.scalar(
            select(DocumentVersion).where(DocumentVersion.id == version_id).with_for_update()
        )
        if version is None or version.status in {"ready", "failed"}:
            return
        if version.processing_task_id and version.processing_task_id != task_id:
            return
        version.status = "extracting"
        version.processing_task_id = task_id
        version.error_code = None
        version.updated_at = datetime.now(UTC)
        object_key = version.object_key
        document_id = version.document_id

    try:
        pdf_bytes = get_object_storage().get_bytes(object_key)
        pages = extract_pages(pdf_bytes, get_settings().max_document_pages)
        chunks = chunk_pages(pages, get_settings().max_document_chunks)
        if not chunks:
            raise DocumentProcessingError("no_extractable_text", "The PDF contains no text.")

        with SessionLocal.begin() as db:
            version = db.get(DocumentVersion, version_id)
            if version is None:
                return
            if version.processing_task_id != task_id:
                return
            version.status = "embedding"
            version.page_count = len(pages)
            version.updated_at = datetime.now(UTC)

        vectors: list[list[float]] = []
        model_name = ""
        for offset in range(0, len(chunks), 64):
            batch = embed_texts([chunk.content for chunk in chunks[offset : offset + 64]])
            vectors.extend(batch.vectors)
            model_name = batch.model

        with SessionLocal.begin() as db:
            version = db.get(DocumentVersion, version_id)
            document = db.get(StudyDocument, document_id)
            if version is None or document is None or document.deleted_at is not None:
                return
            if version.processing_task_id != task_id:
                return
            db.execute(delete(DocumentChunk).where(DocumentChunk.version_id == version_id))
            db.add_all(
                [
                    DocumentChunk(
                        version_id=version_id,
                        ordinal=chunk.ordinal,
                        page_number=chunk.page_number,
                        content=chunk.content,
                        token_count=chunk.token_count,
                        embedding=vectors[index],
                    )
                    for index, chunk in enumerate(chunks)
                ]
            )
            version.status = "ready"
            version.embedding_model = model_name
            version.error_code = None
            version.processing_task_id = None
            version.processed_at = datetime.now(UTC)
            version.updated_at = datetime.now(UTC)
        logger.info(
            "document_processing_completed",
            extra={"document_id": str(document_id), "version_id": version_id_value},
        )
    except DocumentProcessingError as exc:
        _mark_document_failed(version_id, exc.code)
    except StorageUnavailable:
        _mark_document_failed(version_id, "storage_unavailable")
    except EmbeddingUnavailable:
        _mark_document_failed(version_id, "embedding_unavailable")


def _mark_document_failed(version_id: UUID, error_code: str) -> None:
    with SessionLocal.begin() as db:
        version = db.get(DocumentVersion, version_id)
        if version is not None and version.status not in {"ready", "failed"}:
            version.status = "failed"
            version.error_code = error_code
            version.processing_task_id = None
            version.processed_at = datetime.now(UTC)
            version.updated_at = datetime.now(UTC)
    logger.warning(
        "document_processing_failed",
        extra={"version_id": str(version_id), "error_code": error_code},
    )


def _deliver_event(event_id: UUID) -> bool:
    with SessionLocal() as db:
        event = db.get(OutboxEvent, event_id)
        if event is None or event.processed_at is not None:
            return False
        payload = dict(event.payload)
        attempt = event.attempts

    try:
        token = decrypt_outbox_token(payload["token_ciphertext"])
        _send_email(payload["email"], payload["purpose"], token)
    except (OSError, smtplib.SMTPException, KeyError, ValueError) as exc:
        logger.warning(
            "outbox_delivery_failed",
            extra={"event_id": str(event_id), "error_type": type(exc).__name__},
        )
        with SessionLocal.begin() as db:
            event = db.get(OutboxEvent, event_id)
            if event is not None and event.processed_at is None:
                event.available_at = datetime.now(UTC) + timedelta(
                    seconds=min(30 * 2 ** min(attempt, 9), 3600)
                )
                if attempt >= 10:
                    event.event_type = "email.delivery_failed"
                    event.processed_at = datetime.now(UTC)
                    event.payload = {}
        return False

    with SessionLocal.begin() as db:
        event = db.get(OutboxEvent, event_id)
        if event is not None and event.processed_at is None:
            event.processed_at = datetime.now(UTC)
            event.payload = {}
    return True
