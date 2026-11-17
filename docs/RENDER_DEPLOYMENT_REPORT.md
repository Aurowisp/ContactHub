# ContactHub Render Free + Supabase Free preparation report

Report date: 2026-11-17

Local branch: `v1.0.3`

Scope: local code adaptation and verification only

Cloud status: not deployed

## Conclusion

ContactHub is locally adapted for a zero-cost demo architecture using a Render Static Site, a Render Free FastAPI Web Service, and Supabase Free PostgreSQL. Existing local SQLite behavior and application APIs remain intact.

All executable local regression checks passed. A real PostgreSQL integration test was added but was **not run**, because no dedicated PostgreSQL test connection was provided. No Supabase project or Render service was created, so public HTTPS, public CORS, cloud CRUD, persistence after service restart, mobile access, and free-plan wake behavior remain unverified.

## Git status

- A local branch named `v1.0.3` was created from `v1.0.2` commit `502a428`.
- No commit was created.
- Nothing was pushed.
- No pull request or merge was created.
- Existing tags, releases, branches, and remote history were not modified.

## Database compatibility

### SQLite

- Default local URL remains `sqlite:///./data/contacthub.db`.
- SQLite-only `check_same_thread`, foreign-key PRAGMA, and directory creation remain SQLite-only.
- All SQLite/API/Excel regression tests passed.
- The ignored local database was not modified or uploaded. It currently contains 8 contacts and 27 contact methods; only counts were inspected.

### PostgreSQL

- Added pinned Psycopg 3 binary driver support.
- Bare `postgres://` and `postgresql://` URLs normalize to `postgresql+psycopg://`; already-correct URLs remain unchanged.
- Production startup rejects SQLite and unsupported database schemes.
- PostgreSQL uses pre-ping, a pool size of 3, overflow of 2, connection recycling, timeout, and a connection timeout suitable for a small single-instance backend.
- Existing SQLAlchemy model types, sequential integer primary keys, foreign key cascade, booleans, relationships, sorting/filtering, and timezone-aware timestamps require no model change. The `contact_methods.contact_id` foreign key is already indexed, which also supports efficient cascade deletion.
- The Supabase Session Pooler is compatible with the application's long-lived SQLAlchemy pool and prepared statements; the application pool is capped at five connections including overflow.
- `create_all()` explicitly imports all mapped models and remains idempotent. It is not presented as a schema migration tool.

### PostgreSQL integration status

An opt-in integration test covers connection/table creation, CRUD, favorites, multiple methods, foreign-key enforcement, cascade deletion, timestamps, Notes/Label search, category filtering, and Excel import/export. It requires a dedicated non-production database and a separate confirmation variable, creates a random schema, and refuses to use the same URL as `DATABASE_URL`.

Result: **NOT RUN** because no `POSTGRES_TEST_DATABASE_URL` was provided. This is not reported as a pass.

## Data migration and security

- `backend/scripts/migrate_database.py` copies data only to an empty target, preserves IDs, relationships, favorites, and timestamps, verifies counts, resets PostgreSQL sequences, and rolls back on failure.
- The migration script was unit-tested between isolated SQLite databases, including refusal to overwrite a non-empty target.
- No migration was run against the real local database or any cloud database.
- `backend/scripts/harden_supabase_data_api.sql` enables RLS and revokes `anon`/`authenticated` table and sequence access. The deployment guide recommends disabling the Data API entirely because ContactHub uses direct SQLAlchemy connections.
- No Supabase Auth, SDK, Storage, Edge Function, API key, `service_role`, or frontend database credential was introduced.

## Render Blueprint result

| Requirement | Actual local configuration |
| --- | --- |
| Backend compute | `plan: free` |
| Backend runtime | Python / Uvicorn / `$PORT` |
| Health check | `/health` |
| Frontend | `runtime: static` |
| Frontend build | `npm ci && npm run build` |
| Publish directory | `dist` |
| SPA rewrite | `/* -> /index.html` |
| Persistent disk | Absent |
| Render PostgreSQL | Absent |
| `DATABASE_URL` | `sync: false`; real value must be entered in Render |
| `CORS_ORIGINS` | `sync: false`; exact frontend origin required |
| `VITE_API_BASE_URL` | `sync: false`; backend origin required |

The Blueprint was parsed locally and assertions confirmed the free plan, absence of a disk/database resource, secret placeholder, static runtime, and rewrite rule.

## Files changed

| File | Change and reason | Business behavior impact |
| --- | --- | --- |
| `backend/app/database.py` | Dual SQLite/PostgreSQL URL handling, production guard, Psycopg pool settings, explicit model import | No API/UI change; database infrastructure only |
| `backend/requirements.txt` | Adds `psycopg[binary]==3.3.9` | PostgreSQL driver only |
| `backend/tests/test_database_config.py` | Tests URL normalization, production guard, pool configuration, Psycopg dialect | Tests only |
| `backend/tests/test_database_migration.py` | Tests exact migration and non-empty target protection | Tests only |
| `backend/tests/test_postgresql_integration.py` | Optional isolated PostgreSQL regression suite | Tests only; skipped without credentials |
| `backend/pytest.ini` | Registers PostgreSQL test marker | Tests only |
| `backend/scripts/migrate_database.py` | Manual opt-in SQLite/PostgreSQL copy tool | Never runs automatically |
| `backend/scripts/harden_supabase_data_api.sql` | Optional Data API/RLS hardening | Manual cloud security step |
| `render.yaml` | Changes backend to Free, removes disk/SQLite path, adds secret Supabase URL, renames frontend service | Deployment infrastructure only |
| `.env.example` | Documents development SQLite and pool variables without secrets | Configuration only |
| `.github/workflows/ci.yml` | Runs on `v1.0.*`, adds frontend tests, Blueprint check, optional PostgreSQL test | CI only |
| `README.md` | Describes free architecture, optional integration test, and documentation links | Documentation only |
| `backend/README.md` | Documents PostgreSQL, migration, and security | Documentation only |
| `frontend/README.md` | Clarifies production API origin handling | Documentation only |
| `docs/CODE_STYLE.md` | Defines backend, frontend, API, test, security, and review conventions | Documentation only |
| `docs/DEPLOY_RENDER.md` | Complete Supabase/Render setup, migration, backup, limitations, and acceptance guide | Documentation only |
| `docs/RENDER_DEPLOYMENT_REPORT.md` | This evidence-based report | Documentation only |

No contact schema, route, request/response model, UI component, Excel format, or completed F07/F08/F09 behavior was changed.

## Actual test results

Environment: Windows PowerShell, Python 3.11.4, Node.js 24.11.0, npm 11.6.1, Docker Compose 2.40.2.

| Test | Result |
| --- | --- |
| Backend `python -m pytest -v` | PASS: 27 passed, 1 PostgreSQL test skipped |
| Backend SQLite regression | PASS |
| Database configuration and migration tests | PASS |
| Backend PostgreSQL integration | NOT RUN: no dedicated test URL |
| Psycopg 3 import/dialect construction | PASS: 3.3.9 |
| Python compileall | PASS |
| Frontend clean lockfile install | PASS: 309 packages in isolated temporary directory |
| Frontend `npm test` | PASS: 5 files, 25 tests |
| Frontend `npm run typecheck` | PASS |
| Frontend `npm run build` | PASS: 3,079 modules transformed |
| Render Blueprint parse/invariants | PASS |
| Docker Compose configuration | PASS |
| `git diff --check` | PASS; only line-ending conversion warnings |
| GitHub Actions CI | NOT RUN: branch has not been pushed |
| Public Render/Supabase acceptance | NOT RUN: no cloud resources created |

The production build still reports a non-blocking large-chunk warning: the main JavaScript chunk is approximately 1.24 MB before gzip and 396.64 kB after gzip. No performance refactor was made because it is outside this deployment task.

`frontend/node_modules` was occupied by Node/esbuild processes that predated this test run. To avoid terminating the user's development session, `npm ci` was verified with the same lockfile in a temporary directory, which was removed afterward. Tests and the production build then passed in the real project directory.

## Free-plan and security risks

- Render Free spins down after inactivity and has cold-start delay, ephemeral local storage, and monthly usage limits.
- Supabase Free has database/egress quotas, may pause low-activity projects, and does not include automatic backups.
- External database traffic consumes bandwidth/egress quotas.
- ContactHub has no authentication. CORS is not access control; anyone reaching the public API may call CRUD endpoints. Only fictional demo records should be used.
- Manual off-site backups and tested restore procedures are required.
- Free plans are not suitable for workloads requiring stable latency, uptime SLA, or sensitive contact data.

## Public deployment acceptance

| Item | Actual result |
| --- | --- |
| Frontend URL | Not available |
| Backend URL | Not available |
| API docs URL | Not available |
| Supabase database | Not created by this task |
| Public health/CORS | Not tested |
| Public CRUD/favorites/multiple methods | Not tested |
| Public Excel workflow | Not tested |
| Persistence after Render restart | Not tested |
| Mobile/different-network access | Not tested |
| Screenshots/evidence | Not available |

## Final answers

1. Is the local code prepared for Render Free + Supabase Free? **Yes.**
2. Does local SQLite still work? **Yes; verified by automated tests.**
3. Is PostgreSQL supported in code? **Yes; configuration and driver construction are verified, but a real PostgreSQL integration run is still required.**
4. Does the Blueprint contain paid Render resources? **No.**
5. Has a real cloud deployment been completed? **No.**
6. Is cloud persistence proven? **No; it must be verified after deploying against Supabase.**
7. Were local contact records uploaded or changed? **No.**
8. Were changes committed or pushed? **No.**

Follow [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for the remaining manual Supabase and Render steps.
