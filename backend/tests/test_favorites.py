def test_favorite_persistence_filter_and_stats(client):
    first = client.post("/api/v1/contacts", json={
        "name": "Alice", "contact_methods": [{"type": "phone", "label": "Mobile", "value": "1"}]
    }).json()
    client.post("/api/v1/contacts", json={
        "name": "Bob", "is_favorite": True,
        "contact_methods": [{"type": "email", "label": "Work", "value": "b@example.com"}]
    })
    marked = client.patch(f"/api/v1/contacts/{first['id']}/favorite", json={"is_favorite": True})
    assert marked.status_code == 200
    assert marked.json()["is_favorite"] is True
    favorites = client.get("/api/v1/contacts", params={"favorite": True}).json()
    assert favorites["total"] == 2
    unmarked = client.patch(f"/api/v1/contacts/{first['id']}/favorite", json={"is_favorite": False})
    assert unmarked.json()["is_favorite"] is False
    assert client.get(f"/api/v1/contacts/{first['id']}").json()["is_favorite"] is False
    stats = client.get("/api/v1/stats").json()
    assert stats["total_contacts"] == 2
    assert stats["favorite_contacts"] == 1
    assert stats["contacts_with_phone"] == 1
    assert stats["contacts_with_email"] == 1
    assert len(stats["recently_added"]) == 2

