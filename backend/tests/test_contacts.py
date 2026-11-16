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


def test_enhanced_search_fields_case_partial_and_combinations(client):
    first = client.post("/api/v1/contacts", json={
        "name": "Alice Zhang",
        "company": "Future Robotics",
        "job_title": "Research Engineer",
        "category": "Work",
        "notes": "Robotics project teammate",
        "is_favorite": True,
        "contact_methods": [
            {"type": "phone", "label": "Mobile", "value": "13800000000"},
            {"type": "phone", "label": "Work", "value": "05910000001"},
            {"type": "email", "label": "University", "value": "alice@fzu.edu.cn"},
            {"type": "social", "label": "WeChat", "value": "alice_robotics"},
            {"type": "other", "label": "Work", "value": "robotics-workspace"},
        ],
    })
    assert first.status_code == 201
    second = client.post("/api/v1/contacts", json={
        "name": "Bob Chen",
        "company": "Example Studio",
        "job_title": "Designer",
        "category": "Friends",
        "notes": "Lowercase hiking group",
        "is_favorite": False,
        "contact_methods": [
            {"type": "phone", "label": "mobile backup", "value": "13800000002"},
        ],
    })
    assert second.status_code == 201

    cases = {
        "Alice": "Alice Zhang",
        "future robotics": "Alice Zhang",
        "RESEARCH ENGINEER": "Alice Zhang",
        "robotics project": "Alice Zhang",
        "fzu.edu": "Alice Zhang",
        "University": "Alice Zhang",
        "WECHAT": "Alice Zhang",
        "HIKING": "Bob Chen",
        "mobile backup": "Bob Chen",
    }
    for keyword, expected_name in cases.items():
        result = client.get("/api/v1/contacts", params={"keyword": keyword}).json()
        assert result["total"] == 1, keyword
        assert result["items"][0]["name"] == expected_name

    missing = client.get("/api/v1/contacts", params={"keyword": "not-present"}).json()
    assert missing["total"] == 0
    assert missing["items"] == []

    favorite = client.get(
        "/api/v1/contacts", params={"keyword": "mobile", "favorite": True}
    ).json()
    assert favorite["total"] == 1
    assert favorite["items"][0]["name"] == "Alice Zhang"

    category = client.get(
        "/api/v1/contacts", params={"keyword": "mobile", "category": "friends"}
    ).json()
    assert category["total"] == 1
    assert category["items"][0]["name"] == "Bob Chen"

    multiple_matches = client.get(
        "/api/v1/contacts", params={"keyword": "mobile"}
    ).json()
    assert multiple_matches["total"] == 2
    assert [item["name"] for item in multiple_matches["items"]] == [
        "Alice Zhang", "Bob Chen"
    ]

    same_contact_multiple_methods = client.get(
        "/api/v1/contacts", params={"keyword": "work"}
    ).json()
    assert same_contact_multiple_methods["total"] == 1
    assert len(same_contact_multiple_methods["items"]) == 1
    assert same_contact_multiple_methods["items"][0]["name"] == "Alice Zhang"

    whitespace = client.get("/api/v1/contacts", params={"keyword": "   "}).json()
    assert whitespace["total"] == 2


def test_phone_email_presence_filters_combinations_total_and_pagination(client):
    contacts = [
        ("Both Alpha", "Work", [
            {"type": "phone", "label": "Mobile", "value": "111"},
            {"type": "email", "label": "Work", "value": "alpha@example.com"},
        ]),
        ("Both Beta", "Family", [
            {"type": "phone", "label": "Home", "value": "222"},
            {"type": "email", "label": "Personal", "value": "beta@example.com"},
        ]),
        ("Phone Only", "Work", [
            {"type": "phone", "label": "Mobile", "value": "333"},
        ]),
        ("Email Only", "Work", [
            {"type": "email", "label": "Work", "value": "email@example.com"},
        ]),
        ("No Methods", "Work", []),
    ]
    for name, category, methods in contacts:
        response = client.post("/api/v1/contacts", json={
            "name": name, "category": category, "contact_methods": methods,
        })
        assert response.status_code == 201

    phone = client.get("/api/v1/contacts", params={"has_phone": True}).json()
    assert phone["total"] == 3
    assert {item["name"] for item in phone["items"]} == {
        "Both Alpha", "Both Beta", "Phone Only"
    }

    no_phone = client.get("/api/v1/contacts", params={"has_phone": False}).json()
    assert no_phone["total"] == 2
    assert {item["name"] for item in no_phone["items"]} == {"Email Only", "No Methods"}

    email = client.get("/api/v1/contacts", params={"has_email": True}).json()
    assert email["total"] == 3
    assert {item["name"] for item in email["items"]} == {
        "Both Alpha", "Both Beta", "Email Only"
    }

    no_email = client.get("/api/v1/contacts", params={"has_email": False}).json()
    assert no_email["total"] == 2
    assert {item["name"] for item in no_email["items"]} == {"No Methods", "Phone Only"}

    both = client.get("/api/v1/contacts", params={
        "has_phone": True, "has_email": True,
    }).json()
    assert both["total"] == 2
    assert [item["name"] for item in both["items"]] == ["Both Alpha", "Both Beta"]

    keyword = client.get("/api/v1/contacts", params={
        "has_phone": True, "keyword": "alpha",
    }).json()
    assert keyword["total"] == 1
    assert keyword["items"][0]["name"] == "Both Alpha"

    category = client.get("/api/v1/contacts", params={
        "has_email": True, "category": "work",
    }).json()
    assert category["total"] == 2
    assert {item["name"] for item in category["items"]} == {"Both Alpha", "Email Only"}

    page = client.get("/api/v1/contacts", params={
        "has_phone": True, "skip": 1, "limit": 1,
    }).json()
    assert page["total"] == 3
    assert len(page["items"]) == 1
    assert page["skip"] == 1
    assert page["limit"] == 1

