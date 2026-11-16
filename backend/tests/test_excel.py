import io

from openpyxl import Workbook, load_workbook


XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def upload(client, content: bytes, name: str = "contacts.xlsx"):
    return client.post("/api/v1/contacts/import", files={"file": (name, content, XLSX)})


def workbook_bytes(rows, headers=None):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Contacts"
    worksheet.append(headers or [
        "Name", "Company", "Job Title", "Category", "Notes", "Favorite",
        "Phone 1 Label", "Phone 1 Value", "Email 1 Label", "Email 1 Value",
    ])
    for row in rows:
        worksheet.append(row)
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def test_export_valid_workbook_and_formula_safety(client):
    client.post("/api/v1/contacts", json={
        "name": "=DANGEROUS", "company": "+Formula", "is_favorite": True,
        "contact_methods": [
            {"type": "phone", "label": "Mobile", "value": "123"},
            {"type": "phone", "label": "Work", "value": "456"},
        ],
    })
    response = client.get("/api/v1/contacts/export")
    assert response.status_code == 200
    workbook = load_workbook(io.BytesIO(response.content), data_only=False)
    worksheet = workbook["Contacts"]
    headers = [cell.value for cell in worksheet[1]]
    assert "Phone 2 Value" in headers
    assert worksheet.max_row == 2
    assert worksheet["A2"].value == "'=DANGEROUS"
    assert worksheet.freeze_panes == "A2"
    assert client.delete("/api/v1/contacts/1").status_code == 204
    restored = upload(client, response.content)
    assert restored.json()["success"] == 1
    assert client.get("/api/v1/contacts").json()["items"][0]["name"] == "=DANGEROUS"


def test_template_download(client):
    response = client.get("/api/v1/contacts/import-template")
    assert response.status_code == 200
    workbook = load_workbook(io.BytesIO(response.content))
    assert workbook.sheetnames == ["Contacts", "Instructions"]
    headers = [cell.value for cell in workbook["Contacts"][1]]
    for method_type in ["Phone", "Email", "Social", "Address", "Website", "Other"]:
        assert f"{method_type} 1 Value" in headers


def test_import_valid_invalid_empty_and_unsupported(client):
    content = workbook_bytes([
        ["Alice", "ACME", "Dev", "Work", "", "Yes", "Mobile", "123", "Work", "a@x.com"],
        [None] * 10,
        ["", "ACME", "Dev", "Work", "", "No", "Mobile", "456", "", ""],
        ["Bob", "", "", "", "", "No", "", "789", "", ""],
    ])
    response = upload(client, content)
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 3
    assert result["success"] == 1
    assert result["skipped"] == 1
    assert len(result["errors"]) == 2
    alice = client.get("/api/v1/contacts", params={"keyword": "Alice"}).json()["items"][0]
    assert alice["is_favorite"] is True
    assert len(alice["contact_methods"]) == 2
    assert upload(client, b"bad", "bad.txt").status_code == 400
    assert upload(client, b"not xlsx").status_code == 400


def test_excel_round_trip_preserves_all_fields(client, contact_payload):
    original = client.post("/api/v1/contacts", json=contact_payload).json()
    exported = client.get("/api/v1/contacts/export").content
    assert client.delete(f"/api/v1/contacts/{original['id']}").status_code == 204
    imported = upload(client, exported)
    assert imported.status_code == 200
    assert imported.json()["success"] == 1
    restored = client.get("/api/v1/contacts").json()["items"][0]
    for field in ["name", "company", "job_title", "category", "notes", "is_favorite"]:
        assert restored[field] == original[field]
    original_methods = {(m["type"], m["label"], m["value"]) for m in original["contact_methods"]}
    restored_methods = {(m["type"], m["label"], m["value"]) for m in restored["contact_methods"]}
    assert restored_methods == original_methods
