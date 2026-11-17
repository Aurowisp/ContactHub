# ContactHub Code Style Guide

This document defines the conventions for new and modified ContactHub code. Preserve existing behavior, public APIs, data meaning, and UI conventions. Do not reformat unrelated files while implementing a focused change.

The repository currently has no configured Black, Ruff, ESLint, or Prettier command. The rules below are therefore enforced through review, TypeScript strict mode, automated tests, and production builds. Do not claim a formatter or lint check passed unless that tool is actually added and run.

## 1. General principles

- Prefer the smallest change that completely solves the problem.
- Keep business logic independent from HTTP and UI concerns.
- Reuse existing services, schemas, components, and helpers before adding abstractions.
- Use UTF-8, spaces instead of tabs, and a final newline.
- Remove trailing whitespace and keep `git diff --check` clean.
- Choose clear names over abbreviations. Comments should explain why, not restate what the code does.
- Do not leave commented-out code, debugging output, temporary credentials, or generated artifacts in source files.
- Avoid bulk dependency upgrades and unrelated refactoring in feature or deployment changes.

## 2. Project boundaries

### Backend

```text
backend/app/api/routes/   HTTP routing, dependency injection, status codes
backend/app/schemas/      Pydantic request and response contracts
backend/app/models/       SQLAlchemy persistence models and relationships
backend/app/services/     Business rules and database operations
backend/app/database.py   Engine, sessions, database configuration
backend/tests/            API, service, database, and integration tests
backend/scripts/          Explicitly invoked maintenance tools
```

Routes should remain thin: validate through schemas, call a service, translate known domain errors into HTTP responses, and return the result. Do not duplicate queries or business rules inside route functions.

### Frontend

```text
frontend/src/api/         Axios client and API functions
frontend/src/components/  Reusable UI components
frontend/src/pages/       Route-level screens and orchestration
frontend/src/types/       Shared TypeScript domain types
frontend/src/utils/       Pure reusable helpers
```

Components must not access the database or construct backend connection details. All server communication goes through `src/api`.

## 3. Python style

### Formatting and naming

- Target Python 3.11 or newer.
- Use four spaces for indentation and follow PEP 8 where it does not conflict with established project style.
- Aim for lines no longer than 100 characters. Wrap function calls, collections, and boolean expressions with parentheses.
- Use `snake_case` for functions, variables, modules, and fixture names.
- Use `PascalCase` for classes, Pydantic models, and exceptions.
- Use `UPPER_SNAKE_CASE` for true module constants.
- Prefix private implementation helpers with `_`.

### Imports

Separate imports into these groups with one blank line:

1. Python standard library.
2. Third-party packages.
3. Local `app` imports.

Prefer explicit imports. Do not use wildcard imports. Avoid circular imports; when a deferred import is required for SQLAlchemy model registration, add a short explanation.

### Types and functions

- Add type hints to new public functions and non-obvious helpers.
- Prefer modern syntax such as `str | None`, `list[str]`, and `dict[str, Any]`.
- Use `None` for an absent optional value rather than an empty string unless the API contract requires otherwise.
- Keep functions focused. Extract a helper when it gives a concept a useful name or removes real duplication.
- Do not catch `Exception` unless operating at a deliberate boundary such as per-row Excel error reporting or transaction cleanup. Preserve the original cause with `raise ... from exc` when translating exceptions.

### FastAPI and Pydantic

- Keep all business endpoints under `/api/v1`; system endpoints such as `/health` remain outside the versioned prefix.
- Define request validation in Pydantic schemas instead of duplicating it in routes and services.
- Use explicit `response_model` and appropriate HTTP status codes.
- Return user-safe error messages through FastAPI's `detail` convention. Never expose database URLs, passwords, file-system paths, SQL statements, or raw internal exceptions.
- Use domain exceptions such as `ContactNotFoundError` in the service layer and translate them in the route layer.
- Use `async def` only when the function awaits asynchronous work. The synchronous SQLAlchemy session should remain in normal `def` functions.

### SQLAlchemy and database portability

- Obtain sessions through `Depends(get_db)` in routes. Do not create engines or global sessions in route or service modules.
- Keep transaction ownership clear. A service that performs a mutation is responsible for commit/rollback behavior.
- Use SQLAlchemy expressions instead of string-built SQL. If raw SQL is necessary, use bound parameters and fixed identifiers.
- Preserve SQLite and PostgreSQL compatibility. Guard dialect-specific behavior explicitly.
- Keep SQLite-only settings, such as `check_same_thread` and foreign-key PRAGMA, isolated to SQLite.
- Use timezone-aware UTC datetimes for stored timestamps.
- Index foreign keys and frequently filtered columns when justified by actual query patterns.
- Keep transactions short and never perform network calls while holding a database transaction.
- Production database credentials must come from environment variables. Never hard-code or log them.
- `Base.metadata.create_all()` may initialize missing tables, but it must not be described as a replacement for schema migrations.

## 4. TypeScript and React style

### Formatting and naming

- Keep TypeScript strict mode enabled. Do not weaken `tsconfig` checks to make code compile.
- Use two spaces for indentation, single quotes, semicolons, and trailing commas in multiline structures.
- Use `camelCase` for variables, functions, hooks, and props.
- Use `PascalCase` for React components and named object types.
- Use descriptive names for module-level configuration. Reserve `UPPER_SNAKE_CASE` for universal constants that are not domain objects.
- Use `.tsx` only for files containing JSX; use `.ts` for API, types, and pure helpers.

### Types

- Avoid `any`. Use `unknown` at untrusted boundaries and narrow it with type guards.
- Reuse domain types from `src/types` instead of creating slightly different local copies.
- Use `import type` for type-only imports.
- Model optional and nullable API fields accurately; do not silently convert `null` into a different business meaning.
- Keep backend field names unchanged in API types, including established `snake_case` JSON fields.

### Components and hooks

- Keep route-level data loading and navigation in pages; keep reusable presentation and interaction in components.
- Define clear prop types and name event callbacks `onSave`, `onCancel`, `onDelete`, and similar `on...` forms.
- Keep render logic declarative. Move reusable transformations and security-sensitive URL handling into tested helpers.
- Include every referenced value in hook dependency arrays. Do not suppress hook dependencies to hide stale-state bugs.
- Avoid duplicating server state in multiple components. Refresh from the API after successful mutations when the current architecture expects the server as source of truth.
- Use existing Ant Design components and project CSS classes rather than introducing a second component or styling system.

### API and error handling

- Use the shared Axios client in `src/api/client.ts`.
- Keep the `/api/v1` prefix centralized. `VITE_API_BASE_URL` contains the backend origin, not database credentials.
- Never expose `DATABASE_URL`, Supabase database passwords, secret keys, or `service_role` values in `VITE_` variables.
- Convert unknown request failures with the shared error helper and display actionable, non-sensitive messages.
- Always handle loading, empty, success, and failure states for user-visible requests.

### Accessibility and browser safety

- Interactive non-button elements must support keyboard activation and an appropriate role. Prefer real buttons and links when possible.
- Give icon-only controls an accessible label.
- Preserve visible confirmation for destructive actions.
- Validate external URLs before rendering clickable links. Block dangerous schemes such as `javascript:`.
- Do not rely on CORS as authentication or authorization.

## 5. CSS conventions

- Use descriptive kebab-case class names such as `.contact-form` and `.method-row`.
- Reuse existing design tokens, spacing, breakpoints, and Ant Design behavior.
- Keep responsive behavior intact; test both narrow and desktop layouts after layout changes.
- Avoid `!important` unless overriding third-party styles is unavoidable and documented.
- Do not add inline styles for values that belong in reusable CSS.

## 6. API conventions

- Preserve the public base path `/api/v1` and existing request/response shapes.
- Use plural resource names and REST semantics:
  - `GET` for reads;
  - `POST` for creation/import actions;
  - `PUT` for complete contact updates;
  - `PATCH` for focused state changes such as favorite status;
  - `DELETE` for deletion.
- Use 201 for successful creation, 204 for successful deletion without a body, 404 for missing records, 422 for schema validation, and specific 4xx responses for invalid files or limits.
- Pagination responses retain `items`, `total`, `skip`, and `limit`.
- Do not change API behavior solely to simplify frontend code.

## 7. Testing conventions

### Backend

- Name test files `test_*.py` and test functions `test_<behavior>`.
- Use the isolated temporary SQLite fixture for ordinary API tests. Tests must never touch `backend/data/contacthub.db`.
- Test externally visible behavior: status codes, response bodies, persisted state, constraints, and error handling.
- Add regression tests before or with bug fixes.
- Keep PostgreSQL integration tests marked `postgres`, opt-in, and restricted to a dedicated non-production database. Never point destructive tests at `DATABASE_URL`.
- Database migration tests must verify rollback or overwrite protection as well as successful copying.
- Excel changes require real workbook tests, invalid-file/row tests, and a round-trip field comparison.

### Frontend

- Place Vitest files next to the implementation as `*.test.ts` or `*.test.tsx`.
- Prefer user-observable queries and interactions over assertions on component internals.
- Mock the API boundary, not React or Ant Design implementation details.
- Cover URL/query synchronization, loading, empty, success, error, keyboard, and destructive-confirmation behavior when affected.
- API base URL changes require tests for local fallback, deployed origins, and prefix normalization.

### Test data

- Use fictional contacts and obviously non-production credentials.
- Never copy real contact names, phone numbers, emails, database dumps, or secrets into fixtures.
- Keep tests deterministic; do not depend on execution order or an external network unless explicitly marked as integration tests.

## 8. Security and configuration

- Secrets belong in ignored local environment files or deployment dashboards, never source code.
- `.env.example` contains placeholders and safe defaults only.
- Browser-visible `VITE_` variables are public by design and must never contain secrets.
- Validate trusted origins and reject wildcard production CORS.
- Sanitize spreadsheet output against formula injection and validate upload type and size.
- Public deployment currently has no user authentication. Use demo data only and document this limitation rather than treating CORS as protection.
- Maintenance scripts must be explicit, safe by default, transactional where possible, and refuse ambiguous or destructive targets.

## 9. Documentation style

- Use Markdown with short descriptive headings and fenced code blocks that specify the language.
- Keep commands accurate for the stated shell and working directory.
- Mark placeholders with angle brackets, for example `<actual-backend-host>`; never invent successful public URLs.
- Separate verified results from instructions and future work.
- Update related README, API, deployment, and test documentation when behavior or configuration changes.
- Link to current primary documentation for time-sensitive platform limits.

## 10. Pre-review checklist

Run the checks relevant to the change from the repository root:

```powershell
cd backend
python -m pytest -v
python -m compileall -q app scripts tests

cd ..\frontend
npm test
npm run typecheck
npm run build

cd ..
docker compose config --quiet
git diff --check
```

For database/deployment changes, also validate `render.yaml` and run the PostgreSQL integration suite only with an explicitly confirmed isolated test database.

There is currently no `npm run lint` script. Do not add an undocumented lint step or report lint as passing until a formatter/linter configuration is intentionally introduced and applied without unrelated code churn.

Before requesting review, confirm:

- tests and builds relevant to the change pass;
- no existing test was deleted or weakened;
- no generated build output, local database, `.env`, backup, or personal data is included;
- public API and UI behavior remain compatible unless the change explicitly requires otherwise;
- documentation and actual configuration agree;
- known limitations and unexecuted integration tests are reported honestly.
