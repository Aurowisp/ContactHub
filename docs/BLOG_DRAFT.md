# ContactHub 1.0.0 — course blog draft

## Problem and user value

ContactHub replaces fixed phone/email fields with a true one-to-many contact model. Users can bookmark important contacts and safely move the entire address book through a documented Excel format.

## XP approach

Development progressed in small, testable increments: CRUD, favorites, multiple contact methods, Excel interchange, then the integrated UI. Automated tests shaped the critical behavior, especially method synchronization, partial import failure, and export/import equality. Refactoring kept HTTP routes thin and moved reusable logic into services.

## Engineering highlights

- FastAPI, Pydantic 2, SQLAlchemy 2, and SQLite with enforced foreign keys.
- React, strict TypeScript, Vite, and Ant Design responsive interface.
- Dynamic Excel columns preserve arbitrary method counts while keeping one contact per row.
- Formula-like user text is escaped on export and restored on import.
- Docker Compose serves the SPA through Nginx and persists SQLite in a named volume.
- GitHub Actions independently verifies backend tests and the frontend production build.

## Evidence to add before publishing

Insert real screenshots of the Dashboard, Contacts table, dynamic edit form, Favorites page, import results, and exported workbook. Add the final GitHub repository, pull request, release URL, public deployment URL if actually deployed, and a short demo video link. Include the final test output rather than estimated results.

## Reflection

The most important design choice was treating contact methods as rows instead of comma-separated text or fixed columns. The hardest interchange constraint was simultaneously preserving unlimited methods, one contact per row, separate information fields, and re-importability. Dynamic numbered column pairs satisfy those constraints without exposing database IDs.
