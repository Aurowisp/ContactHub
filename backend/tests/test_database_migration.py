from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models.contact import Contact, ContactMethod
from scripts.migrate_database import migrate_data


def test_migration_preserves_ids_relationships_favorite_and_timestamps(tmp_path):
    source_engine = create_engine(f"sqlite:///{tmp_path / 'source.db'}")
    target_engine = create_engine(f"sqlite:///{tmp_path / 'target.db'}")
    Base.metadata.create_all(source_engine)
    timestamp = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    with Session(source_engine) as source:
        source.add(
            Contact(
                id=42,
                name="Migration Test",
                is_favorite=True,
                created_at=timestamp,
                updated_at=timestamp,
                contact_methods=[
                    ContactMethod(
                        id=84,
                        contact_id=42,
                        type="email",
                        label="Work",
                        value="migration@example.com",
                    )
                ],
            )
        )
        source.commit()

    assert migrate_data(source_engine, target_engine) == (1, 1)
    with Session(target_engine) as target:
        contact = target.get(Contact, 42)
        assert contact is not None
        assert contact.is_favorite is True
        assert contact.created_at.replace(tzinfo=timezone.utc) == timestamp
        assert [(method.id, method.contact_id) for method in contact.contact_methods] == [
            (84, 42)
        ]

    source_engine.dispose()
    target_engine.dispose()


def test_migration_refuses_non_empty_target_without_overwriting(tmp_path):
    source_engine = create_engine(f"sqlite:///{tmp_path / 'source.db'}")
    target_engine = create_engine(f"sqlite:///{tmp_path / 'target.db'}")
    Base.metadata.create_all(source_engine)
    Base.metadata.create_all(target_engine)
    with Session(source_engine) as source:
        source.add(Contact(name="Source"))
        source.commit()
    with Session(target_engine) as target:
        target.add(Contact(name="Existing target"))
        target.commit()

    with pytest.raises(RuntimeError, match="Target database is not empty"):
        migrate_data(source_engine, target_engine)

    with Session(target_engine) as target:
        assert target.scalar(select(func.count(Contact.id))) == 1
        assert target.scalar(select(Contact.name)) == "Existing target"

    source_engine.dispose()
    target_engine.dispose()
