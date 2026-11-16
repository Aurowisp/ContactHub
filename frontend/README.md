# ContactHub frontend

Responsive React 18 + strict TypeScript + Vite + Ant Design client.

```powershell
npm install
npm run dev
npm run typecheck
npm run build
```

Routes are `/`, `/contacts`, `/favorites`, and `/import-export`. API code is centralized in `src/api`; shared models live in `src/types`. During development, Vite proxies `/api` to `http://localhost:8000`. In the Docker production topology, Nginx proxies that same path, so no CORS configuration is required.

For a separately hosted static frontend such as Render, set `VITE_API_BASE_URL` to the public backend origin before building, for example `https://<actual-backend-host>`. Do not hard-code or guess a service URL. The client appends `/api/v1` when needed. See [DEPLOY_RENDER.md](../docs/DEPLOY_RENDER.md).

The build output is `dist/`. Start the backend before using the development server.

