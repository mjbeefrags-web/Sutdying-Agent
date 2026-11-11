import logging
from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.app.core.config import get_settings
from apps.api.app.core.errors import AppError
from apps.api.app.core.origin import require_same_origin
from apps.api.app.core.rate_limit import enforce_rate_limit
from apps.api.app.db.models import (
    AuditEvent,
    AuthSession,
    EmailToken,
    Membership,
    Organization,
    OutboxEvent,
    Profile,
    User,
    utc_now,
)
from apps.api.app.db.session import get_db
from apps.api.app.domains.identity.dependencies import (
    clear_session_cookies,
    get_current_session,
    get_current_user,
    require_csrf,
    set_session_cookies,
)
from apps.api.app.domains.identity.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    ProfilePatch,
    RegisterRequest,
    TokenRequest,
    UserRead,
)
from apps.api.app.domains.identity.security import (
    encrypt_outbox_token,
    hash_secret,
    new_secret,
    password_hash,
    session_expiry,
    verify_password,
)
from apps.api.app.domains.identity.security import (
    utc_now as auth_utc_now,
)

logger = logging.getLogger("study_platform.identity")
router = APIRouter(tags=["identity"])
DbSession = Annotated[Session, Depends(get_db)]

GENERIC_REGISTRATION_MESSAGE = "If the address can be registered, check for a verification link."
GENERIC_RESET_MESSAGE = "If an account exists for that address, a reset link will be sent."


def _client_id(request: Request) -> str:
    return request.client.host if request.client is not None else "unknown"


def _audit(
    db: Session,
    request: Request,
    action: str,
    resource_type: str,
    resource_id: UUID | str | None,
    actor_user_id: UUID | None = None,
    organization_id: UUID | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            request_id=getattr(request.state, "request_id", ""),
            metadata_json={},
        )
    )


def _queue_email_token(db: Session, user: User, purpose: str) -> None:
    now = auth_utc_now()
    db.execute(
        update(EmailToken)
        .where(
            EmailToken.user_id == user.id,
            EmailToken.purpose == purpose,
            EmailToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    token = new_secret()
    try:
        token_ciphertext = encrypt_outbox_token(token)
    except ValueError as exc:
        raise AppError(
            503,
            "email_delivery_unavailable",
            "Account email delivery is temporarily unavailable.",
        ) from exc
    settings = get_settings()
    ttl = (
        timedelta(hours=settings.email_verification_hours)
        if purpose == "verify_email"
        else timedelta(minutes=settings.password_reset_minutes)
    )
    db.add(
        EmailToken(
            user_id=user.id,
            purpose=purpose,
            token_hash=hash_secret(token),
            expires_at=now + ttl,
        )
    )
    db.add(
        OutboxEvent(
            event_type=f"email.{purpose}",
            aggregate_id=str(user.id),
            schema_version=1,
            payload={
                "email": user.email,
                "purpose": purpose,
                "token_ciphertext": token_ciphertext,
            },
        )
    )


def _user_read(user: User) -> UserRead:
    if user.profile is None:
        raise AppError(500, "profile_missing", "The account profile is unavailable.")
    return UserRead(
        id=str(user.id),
        email=user.email,
        email_verified=user.email_verified_at is not None,
        display_name=user.profile.display_name,
        locale=user.profile.locale,
    )


@router.post("/auth/register", status_code=status.HTTP_202_ACCEPTED)
def register(payload: RegisterRequest, request: Request, db: DbSession) -> dict[str, str]:
    require_same_origin(request)
    client_id = _client_id(request)
    enforce_rate_limit("auth:register:ip", client_id, 50, 24 * 60 * 60)
    email = str(payload.email).strip().casefold()
    enforce_rate_limit("auth:register:email", email, 5, 60 * 60)

    existing = db.scalar(select(User.id).where(User.email == email))
    if existing is not None:
        return {"message": GENERIC_REGISTRATION_MESSAGE}

    display_name = payload.display_name.strip()
    if not display_name:
        raise AppError(422, "invalid_display_name", "Display name cannot be empty.")
    user = User(email=email, password_hash=password_hash.hash(payload.password))
    profile = Profile(display_name=display_name, locale="en")
    organization = Organization(name="Personal Study Space")
    try:
        db.add(user)
        db.flush()
        profile.user_id = user.id
        organization.owner_user_id = user.id
        db.add_all([profile, organization])
        db.flush()
        db.add(Membership(organization_id=organization.id, user_id=user.id, role="owner"))
        _queue_email_token(db, user, "verify_email")
        _audit(db, request, "account.registered", "user", user.id, user.id, organization.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            return {"message": GENERIC_REGISTRATION_MESSAGE}
        raise
    return {"message": GENERIC_REGISTRATION_MESSAGE}


@router.post("/auth/email/verify")
def verify_email(payload: TokenRequest, request: Request, db: DbSession) -> dict[str, str]:
    require_same_origin(request)
    now = auth_utc_now()
    token = db.scalar(
        select(EmailToken)
        .where(
            EmailToken.token_hash == hash_secret(payload.token),
            EmailToken.purpose == "verify_email",
            EmailToken.used_at.is_(None),
            EmailToken.expires_at > now,
        )
        .with_for_update()
    )
    if token is None:
        raise AppError(
            400, "invalid_or_expired_token", "The verification link is invalid or expired."
        )
    user = db.get(User, token.user_id)
    if user is None:
        raise AppError(
            400, "invalid_or_expired_token", "The verification link is invalid or expired."
        )
    token.used_at = now
    user.email_verified_at = now
    _audit(db, request, "account.email_verified", "user", user.id, user.id)
    db.commit()
    return {"message": "Your email is verified. You can now sign in."}


@router.post("/auth/email/resend", status_code=status.HTTP_202_ACCEPTED)
def resend_verification(
    payload: PasswordResetRequest, request: Request, db: DbSession
) -> dict[str, str]:
    require_same_origin(request)
    email = str(payload.email).strip().casefold()
    enforce_rate_limit("auth:verify:ip", _client_id(request), 50, 60 * 60)
    enforce_rate_limit("auth:verify:email", email, 3, 60 * 60)
    user = db.scalar(select(User).where(User.email == email))
    if user is not None and user.email_verified_at is None and user.disabled_at is None:
        _queue_email_token(db, user, "verify_email")
        db.commit()
    return {"message": GENERIC_REGISTRATION_MESSAGE}


@router.post("/auth/login")
def login(payload: LoginRequest, request: Request, response: Response, db: DbSession) -> UserRead:
    require_same_origin(request)
    email = str(payload.email).strip().casefold()
    enforce_rate_limit("auth:login:ip", _client_id(request), 100, 15 * 60)
    enforce_rate_limit("auth:login:email", email, 10, 15 * 60)
    user = db.scalar(select(User).where(User.email == email))
    password_valid = verify_password(payload.password, user.password_hash if user else None)
    if (
        user is None
        or not password_valid
        or user.disabled_at is not None
        or user.email_verified_at is None
    ):
        raise AppError(
            401,
            "invalid_credentials",
            "Email or password is incorrect, or the account is not verified.",
            headers={"WWW-Authenticate": "Session"},
        )

    raw_token = new_secret()
    csrf_token = new_secret()
    expires_at = session_expiry()
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_secret(raw_token),
            csrf_token_hash=hash_secret(csrf_token),
            expires_at=expires_at,
        )
    )
    _audit(db, request, "session.created", "auth_session", None, user.id)
    db.commit()
    set_session_cookies(
        response,
        raw_token,
        csrf_token,
        int((expires_at - auth_utc_now()).total_seconds()),
    )
    return _user_read(user)


@router.get("/auth/session")
def session_info(
    user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return _user_read(user)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: DbSession,
    auth_session: Annotated[object, Depends(get_current_session)],
    _csrf: Annotated[None, Depends(require_csrf)],
) -> Response:
    auth_session.revoked_at = auth_utc_now()
    _audit(db, request, "session.revoked", "auth_session", auth_session.id, auth_session.user_id)
    db.commit()
    clear_session_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/auth/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
    payload: PasswordResetRequest, request: Request, db: DbSession
) -> dict[str, str]:
    require_same_origin(request)
    email = str(payload.email).strip().casefold()
    enforce_rate_limit("auth:password_reset:ip", _client_id(request), 50, 60 * 60)
    enforce_rate_limit("auth:password_reset:email", email, 3, 60 * 60)
    user = db.scalar(select(User).where(User.email == email, User.disabled_at.is_(None)))
    if user is not None:
        _queue_email_token(db, user, "reset_password")
        db.commit()
    return {"message": GENERIC_RESET_MESSAGE}


@router.post("/auth/password-reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirm, request: Request, db: DbSession
) -> dict[str, str]:
    require_same_origin(request)
    now = auth_utc_now()
    token = db.scalar(
        select(EmailToken)
        .where(
            EmailToken.token_hash == hash_secret(payload.token),
            EmailToken.purpose == "reset_password",
            EmailToken.used_at.is_(None),
            EmailToken.expires_at > now,
        )
        .with_for_update()
    )
    if token is None:
        raise AppError(400, "invalid_or_expired_token", "The reset link is invalid or expired.")
    user = db.get(User, token.user_id)
    if user is None or user.disabled_at is not None:
        raise AppError(400, "invalid_or_expired_token", "The reset link is invalid or expired.")
    token.used_at = now
    user.password_hash = password_hash.hash(payload.new_password)
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    _audit(db, request, "account.password_reset", "user", user.id, user.id)
    db.commit()
    return {"message": "Password updated. Sign in with your new password."}


@router.get("/account/profile")
def get_profile(user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return _user_read(user)


@router.patch("/account/profile")
def update_profile(
    payload: ProfilePatch,
    request: Request,
    db: DbSession,
    user: Annotated[User, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(require_csrf)],
) -> UserRead:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise AppError(422, "empty_update", "Provide at least one profile field.")
    if any(value is None for value in changes.values()):
        raise AppError(422, "invalid_update", "Profile fields cannot be cleared.")
    if "display_name" in changes:
        user.profile.display_name = changes["display_name"].strip()
        if not user.profile.display_name:
            raise AppError(422, "invalid_display_name", "Display name cannot be empty.")
    if "locale" in changes:
        user.profile.locale = changes["locale"]
    user.profile.updated_at = utc_now()
    _audit(db, request, "profile.updated", "profile", user.id, user.id)
    db.commit()
    db.refresh(user)
    return _user_read(user)
