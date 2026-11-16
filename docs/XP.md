# Extreme Programming record

## User stories

- As a user, I can create, view, find, edit, and delete a contact so my address book remains accurate.
- As a user, I can bookmark and unbookmark contacts and see a favorite-only list so important people remain easy to reach.
- As a user, I can add any number of labeled methods of the same or different types so no communication detail is lost.
- As a user, I can import valid Excel rows while seeing precise errors for invalid rows so bulk entry is safe.
- As a user, I can export every contact in a re-importable workbook so I can back up or move my data.

## Small releases

| Milestone | Increment |
|---|---|
| 0.1 | Database, validation, contact CRUD, search, pagination |
| 0.2 | Persistent favorite API, filters, statistics |
| 0.3 | One-to-many typed methods and synchronization |
| 0.4 | Dynamic Excel export/import/template and round-trip tests |
| 0.5 | Responsive dashboard, directory, favorites, dynamic form, data tools |
| 1.0.0 | CI, Docker/Nginx, documentation, final verification |

Critical behavior is specified in tests before acceptance: CRUD state transitions, favorites, method multiplicity/synchronization, workbook structure, partial row failure, and full round-trip equality. The service layer keeps route handlers small and Excel parsing reusable.

