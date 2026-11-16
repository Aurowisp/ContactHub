import pytest
from sqlalchemy import create_engine

from app.database import (
    get_engine_options,
    normalize_database_url,
    validate_database_url,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "postgres://user:password@host:5432/postgres?sslmode=require",
            "postgresql+psycopg://user:password@host:5432/postgres?sslmode=require",
        ),
        (
            "postgresql://user:password@host:5432/postgres",
            "postgresql+psycopg://user:password@host:5432/postgres",
        ),
        (
            "postgresql+psycopg://user:password@host:5432/postgres",
            "postgresql+psycopg://user:password@host:5432/postgres",
        ),
        ("sqlite:///./data/contacthub.db", "sqlite:///./data/contacthub.db"),
    ],
)
def test_normalize_database_url(source, expected):
    assert normalize_database_url(source) == expected


def test_production_requires_postgresql_and_development_keeps_sqlite():
    validate_database_url("sqlite:///./data/contacthub.db", "development")
    validate_database_url("postgresql+psycopg://user:password@host/db", "production")

    with pytest.raises(RuntimeError, match="production requires a PostgreSQL"):
        validate_database_url("sqlite:///./data/contacthub.db", "production")
    with pytest.raises(RuntimeError, match="must use SQLite or PostgreSQL"):
        validate_database_url("mysql://user:password@host/db", "development")


def test_engine_options_are_backend_specific_and_pool_is_small():
    sqlite_options = get_engine_options("sqlite:///./data/contacthub.db", {})
    assert sqlite_options == {"connect_args": {"check_same_thread": False}}

    postgres_options = get_engine_options(
        "postgresql+psycopg://user:password@host/db", {}
    )
    assert postgres_options["pool_pre_ping"] is True
    assert postgres_options["pool_size"] == 3
    assert postgres_options["max_overflow"] == 2
    assert postgres_options["pool_recycle"] == 300
    assert postgres_options["connect_args"] == {"connect_timeout": 10}

    engine = create_engine(
        "postgresql+psycopg://user:password@localhost/contacthub",
        **postgres_options,
    )
    try:
        assert engine.dialect.name == "postgresql"
        assert engine.dialect.driver == "psycopg"
    finally:
        engine.dispose()


def test_invalid_pool_configuration_is_rejected():
    with pytest.raises(RuntimeError, match="DB_POOL_SIZE must be a positive integer"):
        get_engine_options(
            "postgresql+psycopg://user:password@host/db", {"DB_POOL_SIZE": "0"}
        )
