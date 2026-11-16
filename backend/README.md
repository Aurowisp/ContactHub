# ContactHub backend

FastAPI application using Python 3.11+, SQLAlchemy 2, Pydantic 2, SQLite, and OpenPyXL.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

`DATABASE_URL` defaults to `sqlite:///./data/contacthub.db`. SQLite foreign keys are enabled on every connection. A contact owns its methods through `delete-orphan` and database-level cascade rules. Writes commit atomically; Excel rows use nested transactions and independent commits so a bad row cannot corrupt a valid one.

All business endpoints are under `/api/v1`; `/health` and generated `/docs` are also available. Errors use FastAPI's JSON `detail` convention, validation returns 422, missing records return 404, invalid workbooks return 400, oversized uploads return 413, and internal database details are hidden.

Run the isolated suite with `python -m pytest -q`. Format details are in [Excel-Format.md](../docs/Excel-Format.md), and routes are in [API.md](../docs/API.md).

