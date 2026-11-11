from functools import lru_cache

from cryptography.fernet import Fernet
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Study Platform API"
    database_url: str = "postgresql+psycopg://study:study@localhost:5432/study"
    redis_url: str = "redis://localhost:6379/0"
    web_origin: str = "http://localhost:3000"
    session_ttl_days: int = 30
    email_verification_hours: int = 24
    password_reset_minutes: int = 30
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = False
    smtp_from_email: str = "study-platform@localhost"
    outbox_encryption_key: str = ""
    storage_endpoint_url: str = "http://localhost:9000"
    storage_access_key: str = "study-local"
    storage_secret_key: str = "local-development-secret-change-me"
    storage_bucket: str = "study-documents"
    storage_region: str = "us-east-1"
    storage_auto_create_bucket: bool = True
    max_document_upload_bytes: int = 25 * 1024 * 1024
    max_document_pages: int = 250
    max_document_chunks: int = 500
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @field_validator("outbox_encryption_key")
    @classmethod
    def validate_outbox_encryption_key(cls, value: str) -> str:
        if value:
            try:
                Fernet(value.encode("ascii"))
            except (UnicodeEncodeError, ValueError) as exc:
                raise ValueError("OUTBOX_ENCRYPTION_KEY must be a valid Fernet key.") from exc
        return value

    @model_validator(mode="after")
    def production_requires_secure_configuration(self) -> "Settings":
        if self.app_env.lower() in {"production", "staging"}:
            if not self.web_origin.startswith("https://"):
                raise ValueError("WEB_ORIGIN must use HTTPS outside development.")
            if not self.smtp_use_tls and not self.smtp_username:
                raise ValueError(
                    "Production email delivery must use TLS or authenticated STARTTLS."
                )
            if not self.outbox_encryption_key:
                raise ValueError("OUTBOX_ENCRYPTION_KEY is required outside development.")
            if not self.storage_endpoint_url.startswith("https://"):
                raise ValueError("STORAGE_ENDPOINT_URL must use HTTPS outside development.")
            if self.storage_secret_key == "local-development-secret-change-me":
                raise ValueError("A non-development STORAGE_SECRET_KEY is required.")
            if self.storage_auto_create_bucket:
                raise ValueError("STORAGE_AUTO_CREATE_BUCKET must be disabled outside development.")
            if "study:study@" in self.database_url:
                raise ValueError(
                    "The development database credentials are not allowed in production."
                )
        return self

    @model_validator(mode="after")
    def validate_embedding_schema(self) -> "Settings":
        if self.openai_embedding_dimensions != 1536:
            raise ValueError(
                "OPENAI_EMBEDDING_DIMENSIONS must match the current pgvector schema (1536)."
            )
        return self

    @property
    def session_cookie_name(self) -> str:
        if self.app_env.lower() in {"production", "staging"}:
            return "__Host-study_session"
        return "study_session"

    @property
    def csrf_cookie_name(self) -> str:
        if self.app_env.lower() in {"production", "staging"}:
            return "__Host-study_csrf"
        return "study_csrf"

    @property
    def secure_cookies(self) -> bool:
        return self.app_env.lower() in {"production", "staging"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
