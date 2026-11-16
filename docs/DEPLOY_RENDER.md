# ContactHub: Render Free + Supabase Free

This guide deploys ContactHub without a paid Render disk:

```text
GitHub branch
  -> Render Static Site (React/Vite, free)
  -> Render Web Service (FastAPI, free)
  -> Supabase PostgreSQL (free)
```

Local development and Docker continue to use SQLite. The cloud backend uses PostgreSQL, so Render's ephemeral filesystem never stores the address book.

## Current status

| Item | Status / URL |
| --- | --- |
| Local branch | `v1.0.3` |
| Frontend | Not deployed; actual URL pending |
| Backend | Not deployed; actual URL pending |
| API docs | Not deployed; actual URL pending |
| Supabase project | Not created by this task |

No public URL is claimed until the services are actually created and tested.

## Why this architecture

Render Free web services use an ephemeral filesystem, cannot attach persistent disks, and spin down after 15 minutes without inbound traffic. SQLite on that filesystem would be lost after a restart, redeploy, or spin-down. The Blueprint therefore uses `plan: free`, has no `disk` section, and stores durable data in Supabase PostgreSQL.

For a persistent backend on a network where IPv4 compatibility is needed, Supabase recommends the shared Session Pooler. Copy its host, port, and username from the Dashboard; do not construct them from a project name or region.

Official references:

- [Render Free limitations](https://render.com/docs/free)
- [Render Blueprint specification](https://render.com/docs/blueprint-spec)
- [Supabase database connection methods](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase connection pooling and limits](https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits)
- [Supabase Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Supabase database backups](https://supabase.com/docs/guides/platform/backups)
- [Supabase pricing and current quotas](https://supabase.com/pricing)
- [Securing the Supabase Data API](https://supabase.com/docs/guides/api/securing-your-api)

## 1. Create the Supabase Free project

1. Create a new Free project in the [Supabase Dashboard](https://supabase.com/dashboard/). Use demo data only; ContactHub currently has no login or per-user authorization.
2. Save the generated database password in a password manager. Never place it in frontend variables, documentation, Git, screenshots, or chat logs.
3. In the project, open **Connect** and choose **Session pooler**.
4. Copy the entire connection string. On Free projects, Session Pooler port `5432` is IPv4-compatible. Its username is normally shaped like `postgres.<project-ref>`; use the exact Dashboard value.
5. Replace the password placeholder. Percent-encode reserved password characters such as `@`, `:`, `/`, `?`, `#`, and `%` before placing them in a URL.
6. Preserve the Dashboard's connection options and require TLS. A typical shape is:

   ```text
   postgresql://postgres.<project-ref>:<encoded-password>@<dashboard-pooler-host>:5432/postgres?sslmode=require
   ```

The backend converts the bare scheme to `postgresql+psycopg://` automatically. A URL already using `postgresql+psycopg://` is left unchanged.

### Data API security

ContactHub does not use Supabase Auth, JavaScript SDK, REST, or GraphQL. The safest configuration is to disable the Data API in **Project Settings / Integrations / Data API**. If the Data API must remain enabled, after the first backend startup creates the tables, run [harden_supabase_data_api.sql](../backend/scripts/harden_supabase_data_api.sql) in the SQL editor. It enables RLS and revokes table/sequence access from `anon` and `authenticated`; it creates no public policies.

The FastAPI server connects directly with database credentials. Never expose the PostgreSQL URL or a `service_role`/secret key to the browser.

## 2. Review the Blueprint

The root [render.yaml](../render.yaml) defines:

- `contacthub-api`: Python Web Service, `plan: free`, root `backend`, `/health` check;
- `contacthub-frontend`: Static Site, root `frontend`, `dist` output;
- no Render database and no persistent disk;
- SPA rewrite `/* -> /index.html`;
- `sync: false` for secrets and URLs that must be entered in the Dashboard.

Before creating services, confirm the backend contains `plan: free` and no `disk` block.

## 3. Backend environment variables

| Variable | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.11.11` |
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | Actual Supabase Session Pooler connection string; secret |
| `CORS_ORIGINS` | Actual Render frontend origin only |
| `DB_POOL_SIZE` | `3` |
| `DB_MAX_OVERFLOW` | `2` |
| `DB_POOL_RECYCLE` | Optional; default `300` seconds |
| `DB_POOL_TIMEOUT` | Optional; default `30` seconds |

Production startup deliberately fails if `DATABASE_URL` is missing or points to SQLite. `CORS_ORIGINS` accepts comma-separated exact HTTP(S) origins and rejects `*`.

## 4. Frontend environment variables

| Variable | Value |
| --- | --- |
| `NODE_VERSION` | `22.11.0` |
| `VITE_API_BASE_URL` | Actual backend origin, such as `https://<actual-backend-host>` |

Do not add `/api/v1`; the client adds it. This value is compiled into the static assets, so every change requires a new frontend build.

## 5. Deploy with Render Blueprint

1. Push the reviewed branch only after explicitly approving Git commit/push operations.
2. In Render choose **New > Blueprint**, connect the repository, and select the deployment branch.
3. Enter the real Supabase `DATABASE_URL` when prompted. It is marked `sync: false` and is not stored in the repository.
4. Because Render has not assigned the two service URLs yet, use temporary valid placeholder origins for `CORS_ORIGINS` and `VITE_API_BASE_URL` during initial creation, for example `https://placeholder.invalid`.
5. Confirm the backend plan is **Free** and that no disk or Render PostgreSQL resource is proposed.
6. Apply the Blueprint and record the actual backend and frontend HTTPS origins.
7. In the frontend environment, replace `VITE_API_BASE_URL` with the real backend origin and trigger a new static-site build.
8. In the backend environment, replace `CORS_ORIGINS` with the real frontend origin and redeploy the backend.
9. Run the public verification checklist below.

For an existing Blueprint, Render ignores newly added `sync: false` values during sync; add or update them manually in each service's Environment page.

## 6. Table initialization

FastAPI calls `Base.metadata.create_all()` at startup. It creates missing `contacts` and `contact_methods` tables and indexes, and repeated startup is safe. It does not modify existing columns and is not a general migration system.

After first startup:

1. Open `/health`; expect HTTP 200.
2. Confirm both tables exist in Supabase.
3. Disable the Data API or run the supplied hardening SQL.
4. Do not add `anon` policies merely to make the backend work; direct SQLAlchemy access does not need Data API grants.

## 7. Optional local SQLite data migration

The repository may contain an ignored local SQLite database. It is never uploaded automatically. Export Excel first as a human-readable backup, then use the migration script only with a new or empty target database.

From `backend` in PowerShell:

```powershell
$env:MIGRATION_SOURCE_DATABASE_URL="sqlite:///./data/contacthub.db"
$env:MIGRATION_TARGET_DATABASE_URL="<actual-supabase-session-pooler-url>"
python scripts/migrate_database.py --confirm-empty-target
Remove-Item Env:MIGRATION_SOURCE_DATABASE_URL
Remove-Item Env:MIGRATION_TARGET_DATABASE_URL
```

The script:

- refuses a non-empty target;
- preserves contact and method IDs, relationships, favorites, and timestamps;
- copies inside one target transaction and rolls back on failure;
- verifies source/target record counts;
- resets PostgreSQL ID sequences after explicit-ID insertion;
- never deletes or edits the source database.

To restore exact database records to a new local SQLite file, reverse the URLs and choose a path that does not already contain records:

```powershell
$env:MIGRATION_SOURCE_DATABASE_URL="<actual-supabase-session-pooler-url>"
$env:MIGRATION_TARGET_DATABASE_URL="sqlite:///./data/contacthub-restored.db"
python scripts/migrate_database.py --confirm-empty-target
```

Do not commit either database file or any exported personal data.

## 8. PostgreSQL integration tests

Use a separate Supabase project or another dedicated PostgreSQL test database. Never use the production URL.

```powershell
cd backend
$env:POSTGRES_TEST_DATABASE_URL="<dedicated-test-session-pooler-url>"
$env:POSTGRES_TEST_CONFIRM_ISOLATED="1"
python -m pytest -m postgres -v
```

The test creates a randomly named schema, checks table creation, CRUD, favorites, multiple methods, constraints, cascade delete, timestamps, search, category filters, and Excel import/export, then removes only that schema. It refuses to run if the test URL equals `DATABASE_URL`.

Without these variables, the test is reported as skipped rather than falsely passed.

## 9. Public verification checklist

1. Backend `/health` returns HTTP 200 and does not expose a database URL.
2. Backend `/docs` loads over HTTPS.
3. Frontend routes `/`, `/contacts`, `/favorites`, and `/import-export` survive direct refresh.
4. Browser Network shows the real HTTPS backend, never `localhost`, and no CORS/mixed-content errors.
5. Create, read, edit, delete, search, category-filter, favorite, and unfavorite a demo contact.
6. Test multiple phones, emails, social accounts, custom labels, and quick actions.
7. Verify Dashboard totals and card navigation.
8. Download the Excel template, import valid/invalid rows, export, and compare data.
9. Let the Render backend spin down or manually redeploy it; confirm Supabase records remain.
10. Test from another browser/device/network and capture real evidence only.

## 10. Backups and recovery

Supabase Free does not provide automatic database backups. Make regular off-site logical backups and test restores. The current official workflow uses Supabase CLI `db dump` for roles, schema, and data, or PostgreSQL `pg_dump`/`psql`; follow [Supabase's current backup/restore guide](https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore) when executing it.

Minimum practice:

- keep periodic application Excel exports for contact-level recovery;
- keep encrypted logical PostgreSQL dumps outside the repository;
- never commit dumps, `.env`, database passwords, or real contact records;
- test restoration into a separate project before relying on a backup;
- export and back up before running migrations or destructive SQL;
- use the provided migration script only with an empty destination.

## 11. Free-plan limits and privacy risk

As reviewed on 2026-11-17, Render Free web services spin down after 15 minutes without traffic and can take about a minute to wake. A workspace receives 750 Free instance hours per month; build minutes and bandwidth have separate included limits. The filesystem is ephemeral and the plan provides no production SLA.

Supabase Free currently includes 500 MB database size and 5 GB egress per project, can pause low-activity projects after about seven days, and has no automatic backups. Limits can change; verify the official pricing and documentation before deployment.

ContactHub has no authentication. Anyone who can reach the public FastAPI URL can potentially call CRUD endpoints directly. CORS restricts browser origins but is not authentication. Use fictional demo contacts only; do not expose private address books until real authentication and authorization are designed as a separate feature.

## Troubleshooting

### Backend fails immediately in production

Check that `DATABASE_URL` is set to PostgreSQL, not SQLite. The failure is intentional protection against ephemeral production storage.

### Database connection times out

Copy the Session Pooler URL again from Supabase **Connect**. Confirm port `5432`, the pooler-specific username, an encoded password, and TLS options. Do not guess the host.

### Health returns 503 after inactivity

Supabase may be paused or waking, or credentials may be invalid. Review both Render and Supabase logs without posting connection strings.

### Browser reports CORS errors

Set `CORS_ORIGINS` to the exact frontend scheme and hostname with no path, then redeploy the backend. CORS does not secure direct API access.

### Frontend still calls the wrong host

Update `VITE_API_BASE_URL` to the backend origin and rebuild the static site. Do not append `/api/v1`.

### Frontend route refresh returns 404

Confirm the Blueprint rewrite is `/*` to `/index.html`.
