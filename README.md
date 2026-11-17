# ContactHub v1.0.1

ContactHub is a full-stack address book built for an Extreme Programming course assignment. It manages contacts, persistent favorites, and any number of typed contact methods, and provides lossless Excel import/export with row-level validation feedback.

## Features

- Complete contact CRUD with search, category/favorite filters, deterministic pagination, and detail views.
- Search across notes and contact-method labels, plus phone/email presence filters.
- Clickable dashboard statistics and contact-detail copy/call/email/open shortcuts.
- Persistent favorites with a dedicated Favorites route.
- Multiple phone, email, social, address, website, and custom methods per contact.
- Real `.xlsx` export with one contact per row and dynamically sized method columns.
- Additive `.xlsx` import, detailed row errors, size/type validation, and a downloadable template.
- Live dashboard statistics and recently added contacts.
- Responsive React/Ant Design interface with loading, empty, error, confirmation, and validation states.
- SQLite foreign keys, cascade deletion, transactions, API validation, and isolated automated tests.
- Production Docker topology with Nginx, FastAPI, and a persistent SQLite volume.

## Architecture and stack

```text
Browser -> React 18 + TypeScript + Ant Design
        -> /api/v1 through Vite proxy or Nginx
        -> FastAPI + Pydantic 2 + SQLAlchemy 2
        -> SQLite locally or PostgreSQL in cloud / OpenPyXL
```

The frontend never accesses SQLite directly. All mutations and statistics use the REST API as their source of truth.

## Project layout

```text
frontend/            React/Vite application
backend/app/         FastAPI models, schemas, services, and routes
backend/tests/       Isolated API and Excel tests
docs/                API, Excel, development, XP, and test documentation
docker/nginx.conf    Static hosting and API reverse proxy
.github/workflows/   Backend/frontend continuous integration
Dockerfile           Backend and web build targets
docker-compose.yml   Persistent production topology
```

## Local development

Requirements: Python 3.11+, Node.js 20+ (22 recommended), and npm.

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

The database is created at `backend/data/contacthub.db`. OpenAPI is available at `http://localhost:8000/docs`; health is at `http://localhost:8000/health`.

### Frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to FastAPI at port 8000.

## Testing

```powershell
cd backend
python -m pytest -q

# Optional: requires a dedicated non-production PostgreSQL project
$env:POSTGRES_TEST_DATABASE_URL="<test-session-pooler-url>"
$env:POSTGRES_TEST_CONFIRM_ISOLATED="1"
python -m pytest -m postgres -v

cd ..\frontend
npm run typecheck
npm run build
```

Tests use a separate temporary SQLite database and never touch application data. The suite includes contact/favorite/method behavior, invalid files and rows, Excel formula safety, and an actual export-clean-import field comparison.

## Excel workflow

Use **Import / Export** in the sidebar. Export always includes the full database, not the current page. Download the template before preparing a manual import. Repeated imports are additive and can create duplicate contacts. See [Excel format](docs/Excel-Format.md).

## Docker deployment

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Open `http://localhost` (or the server's public hostname). `contacthub_data` persists SQLite through container recreation. For a public server, point DNS to the host, allow ports 80/443 in the firewall, and terminate TLS with a certificate-aware edge proxy. Public deployment is not claimed by this repository alone.

## Render cloud deployment

The repository includes a zero-cost deployment design: a Render Static Site, a Render Free FastAPI Web Service, and a Supabase Free PostgreSQL database. Local development and Docker continue to use SQLite.

| Endpoint | Current status |
| --- | --- |
| Online demo | Not deployed |
| Backend API | Not deployed |
| API documentation | Not deployed |

See [Render deployment guide](docs/DEPLOY_RENDER.md) for Supabase setup, Session Pooler configuration, environment variables, backups, migration, and public verification. The [deployment preparation report](docs/RENDER_DEPLOYMENT_REPORT.md) separates verified local behavior from tests that require a real PostgreSQL project or public deployment. Free plans have cold starts, quotas, pausing, and backup limitations and are intended for demos rather than production SLA workloads.

## API and documentation

- [API reference](docs/API.md)
- [Excel format](docs/Excel-Format.md)
- [Development and manual verification](docs/DEVELOPMENT.md)
- [Code style guide](docs/CODE_STYLE.md)
- [Render deployment](docs/DEPLOY_RENDER.md)
- [Render deployment preparation report](docs/RENDER_DEPLOYMENT_REPORT.md)
- [XP process and user stories](docs/XP.md)
- [Release notes](RELEASE_NOTES.md)
- Backend details: [backend/README.md](backend/README.md)
- Frontend details: [frontend/README.md](frontend/README.md)

## Screenshots

Capture the real running application for submission and place images in `docs/screenshots/`. Recommended views: Dashboard, Contacts, dynamic contact form, Favorites, Import result, and exported workbook. No fabricated screenshots are included.

## Development history

The planned XP milestones are CRUD (0.1), favorites (0.2), multiple methods (0.3), Excel interchange (0.4), integrated UI/testing (0.5), deployment-ready 1.0.0, and the focused contact enhancements in 1.0.1. See [XP.md](docs/XP.md) for stories and acceptance criteria.
