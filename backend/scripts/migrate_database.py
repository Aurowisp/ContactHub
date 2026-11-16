"""Copy ContactHub data between empty SQLite/PostgreSQL databases.

The script never deletes source data and refuses to write to a non-empty target.
Connection strings are read from environment variables to keep passwords out of
shell history:

    MIGRATION_SOURCE_DATABASE_URL=sqlite:///./data/contacthub.db
    MIGRATION_TARGET_DATABASE_URL=postgresql://...
    python scripts/migrate_database.py --confirm-empty-target
"""

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, selectinload

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database import Base, get_engine_options, normalize_database_url  # noqa: E402
from app.models.contact import Contact, ContactMethod  # noqa: E402


def _counts(session: Session) -> tuple[int, int]:
    return (
        session.scalar(select(func.count(Contact.id))) or 0,
        session.scalar(select(func.count(ContactMethod.id))) or 0,
    )


def _reset_postgresql_sequences(session: Session) -> None:
    if session.bind is None or session.bind.dialect.name != "postgresql":
        return
    for table in ("contacts", "contact_methods"):
        session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1), "
                f"EXISTS(SELECT 1 FROM {table}))"
            )
        )


def migrate_data(source_engine: Engine, target_engine: Engine) -> tuple[int, int]:
    """Copy all records to an empty target in one target-side transaction."""
    Base.metadata.create_all(target_engine)
    with Session(source_engine) as source, Session(target_engine) as target:
        source_counts = _counts(source)
        contacts = list(
            source.scalars(
                select(Contact)
                .options(selectinload(Contact.contact_methods))
                .order_by(Contact.id)
            ).all()
        )
        with target.begin():
            if _counts(target) != (0, 0):
                raise RuntimeError("Target database is not empty; migration was not started")
            for source_contact in contacts:
                target.add(
                    Contact(
                        id=source_contact.id,
                        name=source_contact.name,
                        company=source_contact.company,
                        job_title=source_contact.job_title,
                        category=source_contact.category,
                        notes=source_contact.notes,
                        is_favorite=source_contact.is_favorite,
                        created_at=source_contact.created_at,
                        updated_at=source_contact.updated_at,
                        contact_methods=[
                            ContactMethod(
                                id=method.id,
                                contact_id=source_contact.id,
                                type=method.type,
                                label=method.label,
                                value=method.value,
                            )
                            for method in source_contact.contact_methods
                        ],
                    )
                )
            target.flush()
            target_counts = _counts(target)
            if target_counts != source_counts:
                raise RuntimeError(
                    f"Count verification failed: source={source_counts}, "
                    f"target={target_counts}"
                )
            _reset_postgresql_sequences(target)
    return source_counts


def _engine(database_url: str) -> Engine:
    normalized = normalize_database_url(database_url)
    return create_engine(normalized, **get_engine_options(normalized))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy ContactHub records to an empty database without overwriting data."
    )
    parser.add_argument(
        "--confirm-empty-target",
        action="store_true",
        help="confirm that the destination is dedicated to this migration",
    )
    args = parser.parse_args()
    if not args.confirm_empty_target:
        parser.error("--confirm-empty-target is required")

    source_url = os.getenv(
        "MIGRATION_SOURCE_DATABASE_URL", "sqlite:///./data/contacthub.db"
    )
    target_url = os.getenv("MIGRATION_TARGET_DATABASE_URL", "").strip()
    if not target_url:
        parser.error("MIGRATION_TARGET_DATABASE_URL is required")
    if normalize_database_url(source_url) == normalize_database_url(target_url):
        parser.error("source and target database URLs must be different")

    source_engine = _engine(source_url)
    target_engine = _engine(target_url)
    try:
        contacts, methods = migrate_data(source_engine, target_engine)
    finally:
        source_engine.dispose()
        target_engine.dispose()
    print(f"Migration completed: contacts={contacts}, contact_methods={methods}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
