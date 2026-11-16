# ContactHub Render deployment preparation report

Report date: 2026-11-16  
Scope: local deployment adaptation and verification only  
Cloud status: not deployed

## Executive conclusion

ContactHub v1.0.1 is locally prepared for a Render deployment, and every executable local regression check passed. It is **not** yet a completed cloud deployment: no Render resources were created, no public URL exists, and public HTTPS, cross-device access, restart persistence, and end-to-end cloud behavior have not been tested.

The chosen reliable persistence design is SQLite at `/var/data/contacthub.db` on a 5 GB Render persistent disk. This requires a paid disk-capable backend plan. No paid resource was created and no cost was incurred during this work.

## Environment

| Component | Actual local value |
| --- | --- |
| OS | Windows / PowerShell |
| Python used for tests | 3.11.4 |
| Deployment Python pin | 3.11.11 |
| Node.js | 24.11.0 |
| Deployment Node pin | 22.11.0 |
| npm | 11.6.1 |
| Docker Compose | 2.40.2-desktop.1 |
| Local database under test | Independent temporary SQLite database |

The local runtime versions are compatible with the project, while `.python-version`, `.node-version`, and Blueprint environment values make the cloud build reproducible without changing application dependency versions.

## Deployment audit

Before adaptation, the backend already ran with FastAPI/Uvicorn and read `DATABASE_URL`, defaulting to local SQLite at `backend/data/contacthub.db`. The frontend used the relative `/api/v1` path through Vite or Nginx. There was no CORS middleware because the existing local/Docker topology was same-origin, and SQLite outside a Render disk would have been ephemeral.

The minimal deployment changes therefore were:

- retain the existing local API proxy behavior when no frontend environment variable is set;
- allow the static frontend build to use an explicit HTTPS backend origin;
- allow only configured production CORS origins, with safe local development defaults;
- verify database connectivity in the existing health endpoint;
- point production SQLite to a persistent-disk path through `DATABASE_URL`;
- describe both Render services, SPA routing, health checks, runtime pins, and disk in a Blueprint;
- document the initial two-service URL/CORS setup and public verification steps.

No contact model, API route, request/response schema, UI layout, Excel behavior, or business rule was intentionally changed.

## Files added

| File | Reason |
| --- | --- |
| `render.yaml` | Render Blueprint for the backend, static frontend, health check, SPA rewrite, environment variables, and persistent disk. |
| `backend/app/config.py` | Validates and normalizes trusted CORS origins. |
| `backend/tests/test_deployment.py` | Covers health success/failure, trusted/untrusted CORS, and invalid CORS configuration. |
| `backend/.python-version` | Pins the deployment Python version. |
| `frontend/src/api/client.test.ts` | Covers production API URL normalization and local fallback. |
| `frontend/src/vite-env.d.ts` | Supplies Vite environment typings. |
| `frontend/.node-version` | Pins the deployment Node.js version. |
| `docs/DEPLOY_RENDER.md` | Complete Render setup, persistence, verification, and troubleshooting guide. |
| `docs/RENDER_DEPLOYMENT_REPORT.md` | This evidence-based local acceptance record. |

## Files modified

| File | Reason |
| --- | --- |
| `backend/app/main.py` | Adds controlled CORS and makes `/health` verify the database without exposing internals. |
| `frontend/src/api/client.ts` | Reads and safely normalizes `VITE_API_BASE_URL` while preserving `/api/v1` locally. |
| `.env.example` | Documents production database, environment, CORS, and frontend URL variables. |
| `README.md` | Adds the deployment architecture/status and links without inventing public URLs. |
| `backend/README.md` | Documents CORS, health behavior, and persistent SQLite configuration. |
| `frontend/README.md` | Documents static-site API configuration. |
| `docs/API.md` | Corrects the health version and documents its database-aware 503 response. |

## Commands and actual results

| Command / check | Result |
| --- | --- |
| `python -m pytest -v` | Passed: 18/18 |
| `npm test` | Passed: 5 files, 25/25 tests |
| `npm run typecheck` | Passed |
| `npm run build` | Passed: 3,079 modules transformed |
| Clean `npm ci` using the repository lockfile | Passed in an isolated temporary directory: 309 packages installed |
| `python -m compileall -q app` | Passed |
| YAML parse plus Blueprint invariants | Passed |
| `docker compose config --quiet` | Passed |
| `npm run lint` | Not run: no lint script exists in `frontend/package.json` |

The production build emitted one non-blocking warning: its main JavaScript chunk is approximately 1.24 MB before gzip (396.64 kB gzip), above Vite's 500 kB warning threshold. Code splitting is a future performance improvement, not a deployment blocker.

### `npm ci` incident record

The first `npm ci` attempt in `frontend` could not delete `node_modules/@esbuild/win32-x64/esbuild.exe` because Windows reported it in use by Node/esbuild processes that predated this verification. Those processes were not terminated to avoid disrupting an existing local development session. A clean lockfile installation was then completed in a dedicated temporary directory, which was removed afterward. The original `node_modules` was restored with `npm install`; the SHA-256 of `package-lock.json` remained unchanged (`D76913501CF45F3509B6D5536B57EB00D639322BE87961DBB19BE8AE473BCA01`). The full frontend test, type-check, and build sequence passed after recovery.

## Regression coverage

The passing backend suite covers contact CRUD, validation and not-found responses, pagination, category and ordering, enhanced Notes/Label search, phone/email presence filters, multiple contact methods, cascade deletion, favorites and statistics, Excel export/template/import/error handling/formula safety, and an actual Excel round trip. Deployment tests additionally cover database-aware health and CORS policy.

The passing frontend suite covers dashboard navigation, URL/search filters, quick contact actions, safe website handling, and production API base URL construction. The successful TypeScript and Vite build checks cover the complete frontend compilation path.

## Render and public acceptance status

| Item | Actual result |
| --- | --- |
| Frontend URL | Not available; not deployed |
| Backend URL | Not available; not deployed |
| API Docs URL | Not available; not deployed |
| Health check over public HTTPS | Not tested |
| Cloud database | Planned SQLite on Render persistent disk; resource not created |
| Persistence after restart/redeploy | Not tested on Render |
| Public CRUD | Not tested |
| Public favorites | Not tested |
| Public multiple contact methods | Not tested |
| Public Excel import/export | Not tested |
| Public F07/F08/F09 regression | Locally automated checks passed; public checks not run |
| Browser console/network CORS | Not tested against Render |
| Mobile and different-network access | Not tested |
| Deployment screenshots | Not available |

## Git status

No Git command was executed, as explicitly requested. Consequently, this report does not claim a branch name, commit, pull request, merge, tag state, release state, or remote upload. All changes are local workspace changes only.

## Final answers

1. Has a real cloud-server deployment been completed? **No.**
2. Is there a public access URL? **No.**
3. Has a non-localhost endpoint been verified? **No.**
4. Have frontend and backend communicated successfully over the public internet? **No.**
5. Is the persistence design reliable? **Yes by design, using a paid persistent disk, but it is not verified until a real Render restart/redeploy test passes.**
6. Are deployment screenshots and public evidence available? **No.**
7. Is the code locally ready for the manual Render steps? **Yes; all local automated checks passed.**

The exact manual procedure and post-deployment acceptance checklist are in [DEPLOY_RENDER.md](DEPLOY_RENDER.md).
