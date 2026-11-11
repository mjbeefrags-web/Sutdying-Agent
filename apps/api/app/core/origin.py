from fastapi import Request

from apps.api.app.core.config import get_settings
from apps.api.app.core.errors import AppError


def require_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is not None and origin.rstrip("/") != get_settings().web_origin.rstrip("/"):
        raise AppError(403, "invalid_origin", "This request origin is not allowed.")
