import hmac
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.core.config import get_settings
from apps.api.app.core.errors import AppError
from apps.api.app.core.origin import require_same_origin
from apps.api.app.db.models import AuthSession, User
from apps.api.app.db.session import get_db
from apps.api.app.domains.identity.security import hash_secret, normalize_db_datetime

DbSession = Annotated[Session, Depends(get_db)]


def get_current_session(
    request: Request,
    db: DbSession,
) -> AuthSession:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise AppError(
            401,
            "unauthenticated",
            "Sign in to continue.",
            headers={"WWW-Authenticate": "Session"},
        )
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hash_secret(token),
            AuthSession.revoked_at.is_(None),
        )
    )
    if session is None or normalize_db_datetime(session.expires_at) <= datetime.now(UTC):
        raise AppError(
            401,
            "unauthenticated",
            "Sign in to continue.",
            headers={"WWW-Authenticate": "Session"},
        )
    return session


def get_current_user(
    db: DbSession, auth_session: Annotated[AuthSession, Depends(get_current_session)]
) -> User:
    user = db.get(User, auth_session.user_id)
    if user is None or user.disabled_at is not None or user.email_verified_at is None:
        raise AppError(401, "unauthenticated", "Sign in to continue.")
    return user


def require_csrf(
    request: Request,
    auth_session: Annotated[AuthSession, Depends(get_current_session)],
    csrf_header: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    require_same_origin(request)
    csrf_cookie = request.cookies.get(get_settings().csrf_cookie_name)
    if (
        not csrf_cookie
        or not csrf_header
        or not hmac.compare_digest(csrf_cookie, csrf_header)
        or not hmac.compare_digest(hash_secret(csrf_header), auth_session.csrf_token_hash)
    ):
        raise AppError(403, "csrf_validation_failed", "The request could not be verified.")


def set_session_cookies(response: Response, token: str, csrf_token: str, max_age: int) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.session_cookie_name,
        token,
        max_age=max_age,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        max_age=max_age,
        httponly=False,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )


def clear_session_cookies(response: Response) -> None:
    settings = get_settings()
    for name in (settings.session_cookie_name, settings.csrf_cookie_name):
        response.delete_cookie(
            name,
            path="/",
            secure=settings.secure_cookies,
            httponly=name == settings.session_cookie_name,
            samesite="lax",
        )
