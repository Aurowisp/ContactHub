# ContactHub backend

FastAPI application using Python 3.11+, SQLAlchemy 2, Pydantic 2, SQLite/PostgreSQL, Psycopg 3, and OpenPyXL.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

`DATABASE_URL` defaults to `sqlite:///./data/contacthub.db`. SQLite foreign keys are enabled on every connection. Bare `postgres://` and `postgresql://` URLs are normalized to `postgresql+psycopg://` for Psycopg 3. When `ENVIRONMENT=production`, startup refuses SQLite so a Render Free restart cannot silently lose the address book. PostgreSQL uses a small configurable pool with pre-ping and connection recycling.

A contact owns its methods through `delete-orphan` and database-level cascade rules. Writes commit atomically; Excel rows use nested transactions and independent commits so a bad row cannot corrupt a valid one.

All business endpoints are under `/api/v1`; `/health` and generated `/docs` are also available. Errors use FastAPI's JSON `detail` convention, validation returns 422, missing records return 404, invalid workbooks return 400, oversized uploads return 413, and internal database details are hidden.

For a split frontend/backend deployment, set `ENVIRONMENT=production`, use the Supabase Session Pooler URL in `DATABASE_URL`, and provide `CORS_ORIGINS` as a comma-separated list of exact trusted HTTP(S) origins. Wildcards and non-HTTP origins are rejected. `/health` verifies that a database query succeeds and returns 503 when the database is unavailable. See [DEPLOY_RENDER.md](../docs/DEPLOY_RENDER.md).

Optional PostgreSQL integration tests require both `POSTGRES_TEST_DATABASE_URL` and `POSTGRES_TEST_CONFIRM_ISOLATED=1`. They create and remove only a unique schema inside a dedicated test project and explicitly refuse to use the same URL as `DATABASE_URL`. Never point them at production.

Local records can be copied to an empty PostgreSQL database with `scripts/migrate_database.py`; it preserves IDs, relationships, favorite state, and timestamps and refuses non-empty targets. It never runs automatically. `scripts/harden_supabase_data_api.sql` enables RLS and removes direct `anon`/`authenticated` access for projects where the Supabase Data API remains enabled.

Run the isolated suite with `python -m pytest -q`. Format details are in [Excel-Format.md](../docs/Excel-Format.md), and routes are in [API.md](../docs/API.md).

