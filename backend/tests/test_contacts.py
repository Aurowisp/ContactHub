def test_contact_crud_and_search(client, contact_payload):
    created = client.post("/api/v1/contacts", json=contact_payload)
    assert created.status_code == 201
    contact = created.json()
    contact_id = contact["id"]
    assert contact["name"] == "Zhang San"
    assert len(contact["contact_methods"]) == 6

    fetched = client.get(f"/api/v1/contacts/{contact_id}")
    assert fetched.status_code == 200
    assert fetched.json() == contact

    by_method = client.get("/api/v1/contacts", params={"keyword": "gmail"}).json()
    assert by_method["total"] == 1
    assert len(by_method["items"]) == 1

    update = {**contact_payload, "name": "Zhang Updated"}
    update["contact_methods"] = [contact["contact_methods"][0], {
        "type": "website", "label": "Portfolio", "value": "https://example.com"
    }]
    updated = client.put(f"/api/v1/contacts/{contact_id}", json=update)
    assert updated.status_code == 200
    assert updated.json()["name"] == "Zhang Updated"
    assert [item["type"] for item in updated.json()["contact_methods"]] == ["phone", "website"]

    assert client.delete(f"/api/v1/contacts/{contact_id}").status_code == 204
    assert client.get(f"/api/v1/contacts/{contact_id}").status_code == 404


def test_validation_and_not_found(client):
    invalid = client.post("/api/v1/contacts", json={"name": "  ", "contact_methods": []})
    assert invalid.status_code == 422
    bad_method = client.post("/api/v1/contacts", json={
        "name": "Test", "contact_methods": [{"type": "fax", "label": "Work", "value": "1"}]
    })
    assert bad_method.status_code == 422
    assert client.get("/api/v1/contacts/999").status_code == 404
    assert client.delete("/api/v1/contacts/999").status_code == 404


def test_pagination_category_and_ordering(client):
    for name, category in [("Charlie", "Work"), ("Alice", "Family"), ("Bob", "Work")]:
        assert client.post("/api/v1/contacts", json={"name": name, "category": category}).status_code == 201
    page = client.get("/api/v1/contacts", params={"category": "work", "limit": 1}).json()
    assert page["total"] == 2
    assert page["items"][0]["name"] == "Bob"

