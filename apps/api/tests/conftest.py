from collections.abc import Generator

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.app.core.config import get_settings
from apps.api.app.db import models  # noqa: F401
from apps.api.app.db.base import Base
from apps.api.app.db.session import get_db
from apps.api.app.main import app


@pytest.fixture
def db_factory() -> Generator[sessionmaker[Session], None, None]:
    get_settings().outbox_encryption_key = Fernet.generate_key().decode("ascii")
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db_factory: sessionmaker[Session], monkeypatch: pytest.MonkeyPatch) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        with db_factory() as session:
            yield session

    monkeypatch.setattr(
        "apps.api.app.domains.identity.router.enforce_rate_limit", lambda *args: None
    )
    monkeypatch.setattr(
        "apps.api.app.domains.courses.router.enforce_rate_limit", lambda *args: None
    )
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
