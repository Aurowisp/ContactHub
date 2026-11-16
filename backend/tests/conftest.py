import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    def override_get_db():
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def contact_payload():
    return {
        "name": "Zhang San",
        "company": "ABC Technology",
        "job_title": "Engineer",
        "category": "Work",
        "notes": "Key customer",
        "is_favorite": True,
        "contact_methods": [
            {"type": "phone", "label": "Mobile", "value": "13800000000"},
            {"type": "phone", "label": "Work", "value": "05910000000"},
            {"type": "email", "label": "Work", "value": "zhang@company.com"},
            {"type": "email", "label": "Personal", "value": "zhang@gmail.com"},
            {"type": "social", "label": "WeChat", "value": "zhangsan123"},
            {"type": "address", "label": "Home", "value": "Fuzhou, China"},
        ],
    }

