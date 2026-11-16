# ContactHub on Render

This guide describes how to deploy ContactHub as two Render services:

```text
Browser
  -> Render Static Site (React/Vite)
  -> Render Web Service (FastAPI)
  -> SQLite database on a Render persistent disk
```

The repository is deployment-ready, but it does not claim that a public deployment already exists. Record the actual URLs assigned by Render after deployment; do not substitute guessed URLs.

## Current deployment status

| Item | Status / URL |
| --- | --- |
| Frontend | Not deployed; URL pending |
| Backend API | Not deployed; URL pending |
| API documentation | Not deployed; URL pending |

## Important cost and persistence decision

ContactHub uses SQLite. A reliable Render deployment therefore needs a persistent disk mounted on the backend service. Render does not support persistent disks on free web services, so `render.yaml` selects the smallest paid web-service plan currently represented by the Blueprint plan ID `0.5c-512mb` and attaches a 5 GB disk.

Creating or editing `render.yaml` does not create a service or incur a charge. Review the current price in the Render dashboard before creating the Blueprint. If a strictly free demo is required, do not deploy this configuration as-is: an ephemeral SQLite file can be lost on restart or redeploy, and Render's free PostgreSQL offering has its own expiration limits. Migrating to PostgreSQL would require an intentional application and dependency change and is outside this deployment adaptation.

Official references:

- [Render Blueprint specification](https://render.com/docs/blueprint-spec)
- [Persistent disks](https://render.com/docs/disks)
- [Free instance limitations](https://render.com/docs/free)
- [Monorepo support](https://render.com/docs/monorepo-support)
- [Static-site rewrites](https://render.com/docs/redirects-rewrites)

## Prerequisites

- A copy of the repository in a Git provider supported by Render.
- A Render account with permission to create a paid web service and persistent disk.
- The current application tests and builds passing locally.
- A decision on the deployment region. The supplied Blueprint uses `singapore`; change it before initial service creation if another region is required. Render does not allow changing a service's region in place after creation.

## Environment variables

### Backend (`contacthub-api`)

| Variable | Required value | Purpose |
| --- | --- | --- |
| `PYTHON_VERSION` | `3.11.11` | Pins the Python runtime used by the service. |
| `ENVIRONMENT` | `production` | Disables development-only default CORS origins. |
| `DATABASE_URL` | `sqlite:////var/data/contacthub.db` | Stores SQLite on the mounted persistent disk. |
| `CORS_ORIGINS` | Actual frontend origin, for example `https://<actual-frontend-host>` | Allows the separate frontend to call the API. Use comma-separated origins if needed; do not use `*`. |

`CORS_ORIGINS` must contain origins only, without paths. A trailing slash is accepted and normalized. Production starts with no allowed cross-origin caller when this variable is empty, which is safer than an open wildcard.

### Frontend (`contacthub-web`)

| Variable | Required value | Purpose |
| --- | --- | --- |
| `NODE_VERSION` | `22.11.0` | Pins the Node.js build runtime. |
| `VITE_API_BASE_URL` | Actual backend origin, for example `https://<actual-backend-host>` | Builds the browser client with the public API location. |

`VITE_API_BASE_URL` can be either the backend origin or the full URL ending in `/api/v1`; the frontend normalizes both forms. Vite variables are embedded at build time, so changing this value requires a new static-site build.

## Recommended deployment with `render.yaml`

The root-level [render.yaml](../render.yaml) defines both services, their build/start commands, the health check, SPA rewrite, security headers, and the persistent disk. The two public URLs cannot be known until Render creates the services, so two environment values are marked `sync: false`.

1. In the Render dashboard, choose **New > Blueprint** and connect the repository.
2. Review the proposed resources carefully. Confirm the region, paid backend plan, and 5 GB disk before applying.
3. When prompted for `VITE_API_BASE_URL` and `CORS_ORIGINS`, temporary placeholder origins may be needed for initial creation. Do not leave placeholders in the completed deployment.
4. Apply the Blueprint and wait for both services to receive their real Render URLs.
5. Set frontend `VITE_API_BASE_URL` to the actual backend origin, then redeploy the static site.
6. Set backend `CORS_ORIGINS` to the actual frontend origin, then redeploy the backend.
7. Run the verification checklist below and record the real URLs in project documentation.

Because the two services need each other's generated URL, the final environment-variable update and redeploy are expected on first setup.

## Manual dashboard setup

Use this route if you prefer not to create a Blueprint.

### 1. Create the backend web service

Configure these values:

| Setting | Value |
| --- | --- |
| Service type | Web Service |
| Runtime | Python |
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/health` |
| Instance | Paid plan that supports a persistent disk |
| Disk mount path | `/var/data` |
| Disk size | 5 GB |

Add the backend environment variables listed above. `CORS_ORIGINS` can be added after the frontend has its real URL. Deploy, then save the backend origin shown in the dashboard.

### 2. Create the frontend static site

Configure these values:

| Setting | Value |
| --- | --- |
| Service type | Static Site |
| Root directory | `frontend` |
| Build command | `npm ci && npm run build` |
| Publish directory | `dist` |
| Rewrite | `/*` to `/index.html` |

Set `VITE_API_BASE_URL` to the real backend origin. Deploy and save the frontend origin shown in the dashboard.

### 3. Complete CORS configuration

Set backend `CORS_ORIGINS` to the real frontend origin and redeploy the backend. If both a Render domain and a custom domain are used, separate them with commas:

```text
https://actual-site.onrender.com,https://contacts.example.com
```

## Verification checklist

Do not mark the deployment complete until every relevant check passes against the public services.

1. Open `https://<actual-backend-host>/health`; expect HTTP 200 and `{"status":"ok","version":"1.0.1"}`.
2. Open `https://<actual-backend-host>/docs`; confirm the OpenAPI page loads.
3. Open the frontend and refresh each route: `/`, `/contacts`, `/favorites`, and `/import-export`.
4. In browser developer tools, confirm API requests target the real HTTPS backend, not `localhost`, and there are no CORS or mixed-content errors.
5. Create a contact with multiple phones, emails, and social accounts; edit it and toggle favorite status.
6. Verify search, category filtering, favorite filtering, deletion, dashboard statistics, and empty/error states.
7. Export Excel, import it into a clean test deployment if available, and verify field preservation and row-error reporting.
8. Restart or redeploy only the backend service and confirm previously created data still exists. This is the critical persistent-disk check.
9. Confirm HTTPS works for both services and no secrets or database paths are exposed in browser responses.

## Local preparation test result

Last local verification: 2026-11-16 on Windows, before any cloud deployment.

| Check | Actual result |
| --- | --- |
| Backend `python -m pytest -v` | 18 passed |
| Frontend `npm test` | 5 files, 25 tests passed |
| Frontend `npm run typecheck` | Passed |
| Frontend `npm run build` | Passed; one non-blocking large-chunk warning |
| Clean lockfile install | `npm ci` passed in an isolated temporary directory using the repository lockfile |
| `render.yaml` parse and invariant checks | Passed |
| `docker compose config --quiet` | Passed |
| Public HTTPS, CORS, CRUD, Excel, restart persistence, and mobile access | Not tested because no Render services were created |

These results establish local deployment readiness only. They are not evidence of a completed cloud deployment. See [RENDER_DEPLOYMENT_REPORT.md](RENDER_DEPLOYMENT_REPORT.md) for the complete acceptance record.

## Backup and recovery

- Use the application's Excel export regularly as a portable address-book backup.
- Consider Render disk snapshots or another platform backup mechanism appropriate to the account plan.
- A persistent disk protects data across service restarts and deploys, but it is not a substitute for an independent backup.
- Before any database migration, export contacts and take a disk-level backup.

## Troubleshooting

### Browser reports a CORS error

Check that `CORS_ORIGINS` exactly matches the frontend's scheme and hostname. Do not include `/contacts` or another path. After changing it, redeploy the backend.

### Requests still target `localhost` or the static-site domain

Set `VITE_API_BASE_URL` to the real backend origin and trigger a new frontend build. This value is compiled into the static assets.

### Refreshing a frontend route returns 404

Verify the static-site rewrite is `/*` to `/index.html`. It is already present in `render.yaml`.

### Data disappears after a redeploy

Verify the backend is on a disk-capable paid plan, the disk is mounted at `/var/data`, and `DATABASE_URL` is exactly `sqlite:////var/data/contacthub.db`. Data written elsewhere on the service filesystem is ephemeral.

### Health check returns 503

The process is running but cannot execute a database query. Inspect backend logs, the disk mount, directory permissions, and `DATABASE_URL`.

### Excel upload fails

Confirm the file is a real `.xlsx`, is no larger than 10 MB, and matches the documented columns in [Excel-Format.md](Excel-Format.md). Review the returned row-level errors before retrying.

