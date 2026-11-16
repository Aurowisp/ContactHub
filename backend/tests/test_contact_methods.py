from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models.contact import ContactMethod


def test_multiple_methods_and_cascade_delete(client, contact_payload):
    created = client.post("/api/v1/contacts", json=contact_payload).json()
    types = [method["type"] for method in created["contact_methods"]]
    assert types.count("phone") == 2
    assert types.count("email") == 2
    assert types.count("social") == 1
    assert types.count("address") == 1
    assert client.delete(f"/api/v1/contacts/{created['id']}").status_code == 204
    assert client.get("/api/v1/contacts", params={"keyword": "zhang@gmail.com"}).json()["total"] == 0


def test_empty_method_fields_rejected(client):
    response = client.post("/api/v1/contacts", json={
        "name": "Alice",
        "contact_methods": [{"type": "phone", "label": " ", "value": "123"}],
    })
    assert response.status_code == 422

