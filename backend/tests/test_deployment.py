import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_cors_origins
from app.database import get_db
from app.main import app


def test_health_checks_database_without_exposing_configuration(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.1"}
    assert "database_url" not in response.text.lower()


def test_health_reports_database_failure(client):
    class UnavailableDatabase:
        def execute(self, _statement):
            raise SQLAlchemyError("database unavailable")

    def unavailable_db():
        yield UnavailableDatabase()

    working_override = app.dependency_overrides[get_db]
    app.dependency_overrides[get_db] = unavailable_db
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides[get_db] = working_override

    assert response.status_code == 503
    assert response.json() == {"status": "error"}


def test_local_cors_preflight_allows_known_frontend(client):
    response = client.options(
        "/api/v1/contacts",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_untrusted_cors_origin_is_not_allowed(client):
    response = client.options(
        "/api/v1/contacts",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers


def test_production_cors_requires_explicit_origins(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert get_cors_origins() == []

    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://contacthub-web.onrender.com, https://contacts.example.com/",
    )
    assert get_cors_origins() == [
        "https://contacthub-web.onrender.com",
        "https://contacts.example.com",
    ]


def test_cors_rejects_wildcards_and_non_http_origins(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(ValueError, match="wildcards are not allowed"):
        get_cors_origins()

    monkeypatch.setenv("CORS_ORIGINS", "javascript:alert(1)")
    with pytest.raises(ValueError, match=r"http\(s\) origins"):
        get_cors_origins()
