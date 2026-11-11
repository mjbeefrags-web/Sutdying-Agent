from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from apps.api.app.core.config import Settings, get_settings
from apps.api.app.db.models import EmailToken, Membership, Organization, OutboxEvent
from apps.api.app.domains.identity.security import decrypt_outbox_token, hash_secret

ORIGIN = "http://localhost:3000"
PASSWORD = "correct horse battery staple"


def register(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/v1/auth/register",
        headers={"Origin": ORIGIN},
        json={"email": email, "password": PASSWORD, "display_name": "Student"},
    )
    assert response.status_code == 202
    return response.json()["message"]


def latest_outbox(db_factory: sessionmaker[Session], purpose: str) -> tuple[str, str]:
    with db_factory() as db:
        event = db.scalar(
            select(OutboxEvent)
            .where(OutboxEvent.event_type == f"email.{purpose}")
            .order_by(OutboxEvent.created_at.desc())
        )
        assert event is not None
        return str(event.payload["email"]), decrypt_outbox_token(
            str(event.payload["token_ciphertext"])
        )


def verify(client: TestClient, token: str) -> None:
    response = client.post(
        "/api/v1/auth/email/verify",
        headers={"Origin": ORIGIN},
        json={"token": token},
    )
    assert response.status_code == 200


def login(client: TestClient, email: str, password: str = PASSWORD) -> None:
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert client.cookies.get(get_settings().csrf_cookie_name)
    session_cookie = response.cookies.get(get_settings().session_cookie_name)
    assert session_cookie
    assert get_settings().secure_cookies is False


def csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get(get_settings().csrf_cookie_name)
    assert token
    return {"Origin": ORIGIN, "X-CSRF-Token": token}


def test_registration_verification_login_profile_and_csrf(
    client: TestClient, db_factory: sessionmaker[Session]
) -> None:
    message = register(client, "Student@Example.com")
    assert "verification link" in message
    email, verify_token = latest_outbox(db_factory, "verify_email")
    assert email == "student@example.com"

    duplicate = client.post(
        "/api/v1/auth/register",
        headers={"Origin": ORIGIN},
        json={"email": "student@example.com", "password": PASSWORD, "display_name": "Other"},
    )
    assert duplicate.status_code == 202
    assert duplicate.json()["message"] == message
    with db_factory() as db:
        assert db.scalar(select(OutboxEvent).where(OutboxEvent.event_type == "email.verify_email"))

    unverified_login = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": email, "password": PASSWORD},
    )
    assert unverified_login.status_code == 401
    verify(client, verify_token)
    login(client, email)

    current = client.get("/api/v1/auth/session")
    assert current.status_code == 200
    assert current.json()["email_verified"] is True
    assert current.headers["x-request-id"]

    without_csrf = client.patch(
        "/api/v1/account/profile",
        headers={"Origin": ORIGIN},
        json={"display_name": "New Name"},
    )
    assert without_csrf.status_code == 403
    changed = client.patch(
        "/api/v1/account/profile",
        headers=csrf_headers(client),
        json={"display_name": "New Name", "locale": "en-GB"},
    )
    assert changed.status_code == 200
    assert changed.json()["display_name"] == "New Name"
    assert changed.json()["locale"] == "en-GB"


def test_tenant_scoped_course_access_and_archiving(
    client: TestClient, db_factory: sessionmaker[Session]
) -> None:
    register(client, "owner@example.com")
    _, owner_token = latest_outbox(db_factory, "verify_email")
    verify(client, owner_token)
    login(client, "owner@example.com")

    with db_factory() as db:
        organization = db.scalar(select(Organization))
        assert organization is not None
        organization_id = organization.id
        assert db.scalar(select(Membership).where(Membership.organization_id == organization_id))

    created = client.post(
        f"/api/v1/organizations/{organization_id}/courses",
        headers=csrf_headers(client),
        json={"name": "Molecular Biology", "description": "Lecture notes"},
    )
    assert created.status_code == 201
    course_id = created.json()["id"]
    assert created.json()["organization_id"] == str(organization_id)
    assert len(client.get(f"/api/v1/organizations/{organization_id}/courses").json()) == 1

    register(client, "other@example.com")
    _, other_token = latest_outbox(db_factory, "verify_email")
    verify(client, other_token)
    other_client = TestClient(client.app)
    login(other_client, "other@example.com")
    foreign_course = other_client.get(f"/api/v1/courses/{course_id}")
    foreign_org = other_client.get(f"/api/v1/organizations/{organization_id}/courses")
    assert foreign_course.status_code == 404
    assert foreign_org.status_code == 404

    archived = client.delete(
        f"/api/v1/courses/{course_id}",
        headers=csrf_headers(client),
    )
    assert archived.status_code == 204
    assert client.get(f"/api/v1/courses/{course_id}").status_code == 200
    assert client.get(f"/api/v1/organizations/{organization_id}/courses").json() == []


def test_password_reset_revokes_active_sessions(
    client: TestClient, db_factory: sessionmaker[Session]
) -> None:
    register(client, "reset@example.com")
    _, verify_token = latest_outbox(db_factory, "verify_email")
    verify(client, verify_token)
    login(client, "reset@example.com")

    request_reset = client.post(
        "/api/v1/auth/password-reset/request",
        headers={"Origin": ORIGIN},
        json={"email": "reset@example.com"},
    )
    assert request_reset.status_code == 202
    _, reset_token = latest_outbox(db_factory, "reset_password")
    reset = client.post(
        "/api/v1/auth/password-reset/confirm",
        headers={"Origin": ORIGIN},
        json={"token": reset_token, "new_password": "even stronger passphrase"},
    )
    assert reset.status_code == 200
    assert client.get("/api/v1/auth/session").status_code == 401

    old_password = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "reset@example.com", "password": PASSWORD},
    )
    assert old_password.status_code == 401
    login(client, "reset@example.com", "even stronger passphrase")

    reused = client.post(
        "/api/v1/auth/password-reset/confirm",
        headers={"Origin": ORIGIN},
        json={"token": reset_token, "new_password": "another valid passphrase"},
    )
    assert reused.status_code == 400


def test_logout_revokes_session_and_clears_cookies(
    client: TestClient, db_factory: sessionmaker[Session]
) -> None:
    register(client, "logout@example.com")
    _, verify_token = latest_outbox(db_factory, "verify_email")
    verify(client, verify_token)
    login(client, "logout@example.com")

    response = client.post("/api/v1/auth/logout", headers=csrf_headers(client))
    assert response.status_code == 204
    assert client.get("/api/v1/auth/session").status_code == 401
    assert client.cookies.get(get_settings().session_cookie_name) is None


def test_expired_email_verification_token_is_rejected(
    client: TestClient, db_factory: sessionmaker[Session]
) -> None:
    register(client, "expired@example.com")
    _, token = latest_outbox(db_factory, "verify_email")
    with db_factory() as db:
        db.execute(
            update(EmailToken)
            .where(EmailToken.token_hash == hash_secret(token))
            .values(expires_at=datetime.now(UTC) - timedelta(minutes=1))
        )
        db.commit()

    response = client.post(
        "/api/v1/auth/email/verify",
        headers={"Origin": ORIGIN},
        json={"token": token},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_or_expired_token"


def test_registration_reports_unavailable_email_configuration(
    client: TestClient, db_factory: sessionmaker[Session]
) -> None:
    get_settings().outbox_encryption_key = ""
    response = client.post(
        "/api/v1/auth/register",
        headers={"Origin": ORIGIN},
        json={
            "email": "configuration@example.com",
            "password": PASSWORD,
            "display_name": "Student",
        },
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "email_delivery_unavailable"
    with db_factory() as db:
        assert db.scalar(select(OutboxEvent)) is None


def test_invalid_outbox_encryption_key_is_rejected() -> None:
    with pytest.raises(ValidationError, match="valid Fernet key"):
        Settings(outbox_encryption_key="not-a-valid-key")


def test_wrong_origin_rejected_for_auth_mutations(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        headers={"Origin": "https://attacker.example"},
        json={"email": "victim@example.com", "password": PASSWORD, "display_name": "Victim"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "invalid_origin"
