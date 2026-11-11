from fastapi.testclient import TestClient

from apps.api.app.main import app
from apps.worker.app.tasks import ping

client = TestClient(app)


def test_liveness_does_not_depend_on_external_services() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_checks_required_dependencies(monkeypatch) -> None:
    class HealthyRedis:
        def ping(self) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr("apps.api.app.main.check_database", lambda: None)
    monkeypatch.setattr("apps.api.app.main.Redis.from_url", lambda *args, **kwargs: HealthyRedis())

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_reports_dependency_failure(monkeypatch) -> None:
    def database_unavailable() -> None:
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("apps.api.app.main.check_database", database_unavailable)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_worker_ping_task() -> None:
    assert ping.run() == "pong"
