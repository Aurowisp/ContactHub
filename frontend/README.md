# ContactHub frontend

Responsive React 18 + strict TypeScript + Vite + Ant Design client.

```powershell
npm install
npm run dev
npm run typecheck
npm run build
```

Routes are `/`, `/contacts`, `/favorites`, and `/import-export`. API code is centralized in `src/api`; shared models live in `src/types`. During development, Vite proxies `/api` to `http://localhost:8000`. In production Nginx serves the SPA and proxies that same path, so no CORS configuration is required.

The build output is `dist/`. Start the backend before using the development server.

