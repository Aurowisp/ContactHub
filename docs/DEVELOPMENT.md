# Development and verification

## Commands

Backend: `cd backend; python -m pytest -q`

Frontend: `cd frontend; npm run typecheck; npm run build`

Local services: run `python -m uvicorn app.main:app --reload` from `backend`, then `npm run dev` from `frontend`.

## Manual browser checklist

1. Open Dashboard and confirm all four totals and recent contacts match API data.
2. Create a contact with two phones, two emails, a social account, address, website, notes, category, and favorite enabled.
3. Open its detail drawer and confirm every method is present.
4. Edit the contact: update one method, remove another, add another of the same type, and save.
5. Search by a method value; filter by category and favorite status; change page size.
6. Toggle the star, refresh, and confirm persistence; verify the Favorites route updates.
7. Cancel an edit and confirm no data changes. Confirm deletion prompts before cascading.
8. Export Excel and inspect that the contact uses one row with distinct numbered columns.
9. Delete the contact, import the export, and confirm the import result and restored fields.
10. Download the template. Try a bad extension, >10 MB file, missing name, and half-complete method pair.
11. Repeat key views at mobile width and confirm the drawer navigation and scrollable table work.

Automated browser tooling was not added to the lightweight stack; the API suite covers integration behavior, and this checklist covers browser-specific presentation and download behavior.

## Deployment review

Run `docker compose config` and `docker compose up --build -d`. Verify `/health`, `/api/v1/stats`, SPA refresh on `/favorites`, upload limit, and volume persistence after `docker compose down` followed by `up`. Do not use `down -v` if data must be retained.

