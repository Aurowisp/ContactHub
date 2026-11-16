# ContactHub API v1

Base path: `/api/v1`. JSON errors use `{ "detail": "message" }`; request validation errors return HTTP 422.

## Contacts

### `GET /contacts`

Query parameters: `keyword` (searches name, company, title, notes, method labels, and method values), `favorite` (boolean), `category`, `has_phone` (boolean), `has_email` (boolean), `skip` (default 0), and `limit` (1–100, default 20). Presence filters support both `true` and `false` and can be combined with the other filters. Returns `{ items, total, skip, limit }`, ordered by name then ID.

### `GET /contacts/{id}`

Returns a complete contact including `contact_methods`, timestamps, and favorite status. Returns 404 if absent.

### `POST /contacts`

Creates a contact; returns HTTP 201 and the stored record.

```json
{
  "name": "Zhang San",
  "company": "ABC Technology",
  "job_title": "Engineer",
  "category": "Work",
  "notes": "Example",
  "is_favorite": true,
  "contact_methods": [
    { "type": "phone", "label": "Mobile", "value": "13800000000" },
    { "type": "email", "label": "Work", "value": "zhang@example.com" }
  ]
}
```

`name`, method `label`, and method `value` cannot be blank. Method type is one of `phone`, `email`, `social`, `address`, `website`, or `other`.

### `PUT /contacts/{id}`

Accepts the complete shape above. Existing method IDs are updated, omitted methods are deleted, and new methods without IDs are created. Returns the synchronized record or 404.

### `DELETE /contacts/{id}`

Deletes the contact and its methods. Returns 204 or 404.

### `PATCH /contacts/{id}/favorite`

Body: `{ "is_favorite": true }`. Returns the updated contact or 404.

## Statistics

### `GET /stats`

Returns real database totals:

```json
{
  "total_contacts": 12,
  "favorite_contacts": 3,
  "contacts_with_phone": 9,
  "contacts_with_email": 8,
  "recently_added": []
}
```

## Excel

### `GET /contacts/export`

Returns the complete address book as an XLSX attachment.

### `GET /contacts/import-template`

Returns `contacts_template.xlsx` with Contacts and Instructions worksheets.

### `POST /contacts/import`

Multipart field: `file` (`.xlsx`, maximum 10 MB). Returns:

```json
{
  "total": 10,
  "success": 8,
  "skipped": 1,
  "errors": [{ "row": 5, "reason": "Missing contact name" }]
}
```

Invalid file structure returns 400 and oversized content returns 413.

## System

`GET /health` is outside the versioned prefix. It verifies database connectivity and returns `{ "status": "ok", "version": "1.0.1" }`; a database failure returns HTTP 503 with `{ "status": "error" }`.

