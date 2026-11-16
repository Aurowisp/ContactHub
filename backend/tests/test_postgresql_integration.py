import os
import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_engine_options, normalize_database_url
from app.models.contact import Contact, ContactMethod
from app.schemas.contact import ContactCreate, ContactMethodCreate, ContactUpdate
from app.services.contact_service import (
    create_contact,
    get_contact,
    list_contacts,
    set_favorite,
    update_contact,
)
from app.services.excel_service import export_contacts, import_contacts


pytestmark = pytest.mark.postgres


@pytest.fixture(scope="module")
def postgres_session_factory() -> Generator[sessionmaker[Session], None, None]:
    raw_url = os.getenv("POSTGRES_TEST_DATABASE_URL", "").strip()
    confirmed = os.getenv("POSTGRES_TEST_CONFIRM_ISOLATED") == "1"
    if not raw_url or not confirmed:
        pytest.skip(
            "Set POSTGRES_TEST_DATABASE_URL and POSTGRES_TEST_CONFIRM_ISOLATED=1 "
            "for a dedicated non-production PostgreSQL project"
        )

    database_url = normalize_database_url(raw_url)
    if not database_url.startswith("postgresql+psycopg:"):
        pytest.fail("POSTGRES_TEST_DATABASE_URL must be PostgreSQL")
    production_url = os.getenv("DATABASE_URL", "").strip()
    if production_url and normalize_database_url(production_url) == database_url:
        pytest.fail("Refusing to run integration tests against DATABASE_URL")

    schema = f"contacthub_test_{uuid.uuid4().hex}"
    engine_options = get_engine_options(database_url)
    admin_engine = create_engine(database_url, **engine_options)
    with admin_engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))

    test_options = dict(engine_options)
    connect_args = dict(test_options.get("connect_args", {}))
    connect_args["options"] = f"-csearch_path={schema}"
    test_options["connect_args"] = connect_args
    test_engine = create_engine(database_url, **test_options)
    factory = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    try:
        Base.metadata.create_all(test_engine)
        Base.metadata.create_all(test_engine)
        yield factory
    finally:
        test_engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin_engine.dispose()


def test_postgresql_crud_search_excel_and_constraints(postgres_session_factory):
    with postgres_session_factory() as db:
        created = create_contact(
            db,
            ContactCreate(
                name="PostgreSQL Test Contact",
                company="ContactHub",
                category="Work",
                notes="Searchable PostgreSQL note",
                is_favorite=False,
                contact_methods=[
                    ContactMethodCreate(type="phone", label="Primary", value="10086"),
                    ContactMethodCreate(
                        type="email", label="Database Label", value="pg@example.com"
                    ),
                    ContactMethodCreate(type="social", label="Mastodon", value="@pg"),
                ],
            ),
        )
        contact_id = created.id
        method_ids = [method.id for method in created.contact_methods]
        assert created.created_at.utcoffset() is not None
        assert created.updated_at.utcoffset() is not None

        set_favorite(db, contact_id, True)
        assert get_contact(db, contact_id).is_favorite is True
        assert list_contacts(db, keyword="postgresql note")[1] == 1
        assert list_contacts(db, keyword="database label")[1] == 1
        assert list_contacts(db, category="work")[1] == 1

        updated = update_contact(
            db,
            contact_id,
            ContactUpdate(
                name="PostgreSQL Test Contact Updated",
                company="ContactHub",
                category="Work",
                notes="Updated",
                is_favorite=True,
                contact_methods=[
                    ContactMethodCreate(
                        id=method_ids[0], type="phone", label="Primary", value="10010"
                    ),
                    ContactMethodCreate(
                        id=method_ids[1],
                        type="email",
                        label="Database Label",
                        value="pg@example.com",
                    ),
                ],
            ),
        )
        assert updated.name.endswith("Updated")
        assert len(updated.contact_methods) == 2

        workbook = export_contacts(db)
        result = import_contacts(db, workbook)
        assert result == {"total": 1, "success": 1, "skipped": 0, "errors": []}
        assert db.scalar(select(func.count(Contact.id))) == 2

        db.add(ContactMethod(contact_id=999999, type="phone", label="Invalid", value="0"))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        imported_id = db.scalar(
            select(Contact.id).where(Contact.id != contact_id).order_by(Contact.id)
        )
        db.execute(delete(Contact).where(Contact.id == imported_id))
        db.commit()
        assert db.scalar(
            select(func.count(ContactMethod.id)).where(
                ContactMethod.contact_id == imported_id
            )
        ) == 0

        db.execute(delete(Contact).where(Contact.id == contact_id))
        db.commit()
        assert db.scalar(select(func.count(Contact.id))) == 0
        assert db.scalar(select(func.count(ContactMethod.id))) == 0
