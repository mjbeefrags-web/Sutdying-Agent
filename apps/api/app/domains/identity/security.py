import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from pwdlib import PasswordHash

from apps.api.app.core.config import get_settings

password_hash = PasswordHash.recommended()
_dummy_password_hash = password_hash.hash(secrets.token_urlsafe(32))


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def new_secret() -> str:
    return secrets.token_urlsafe(32)


def verify_password(plain: str, hashed: str | None) -> bool:
    return password_hash.verify(plain, hashed or _dummy_password_hash)


def utc_now() -> datetime:
    return datetime.now(UTC)


def normalize_db_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def session_expiry() -> datetime:
    return utc_now() + timedelta(days=get_settings().session_ttl_days)


def encrypt_outbox_token(token: str) -> str:
    key = get_settings().outbox_encryption_key
    if not key:
        raise ValueError("OUTBOX_ENCRYPTION_KEY is required to queue account email.")
    return Fernet(key.encode("ascii")).encrypt(token.encode("utf-8")).decode("ascii")


def decrypt_outbox_token(token_ciphertext: str) -> str:
    key = get_settings().outbox_encryption_key
    if not key:
        raise ValueError("OUTBOX_ENCRYPTION_KEY is required to deliver account email.")
    try:
        return Fernet(key.encode("ascii")).decrypt(token_ciphertext.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("The outbox token could not be decrypted.") from exc
