import os
from collections.abc import Generator
from collections.abc import Mapping
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DEFAULT_DATABASE_URL = "sqlite:///./data/contacthub.db"


def normalize_database_url(database_url: str) -> str:
    """Select Psycopg 3 for URLs commonly supplied by hosting providers."""
    value = database_url.strip()
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value.removeprefix("postgres://")
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value.removeprefix("postgresql://")
    return value


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite:")


def is_postgresql_url(database_url: str) -> bool:
    return database_url.startswith("postgresql+psycopg:")


def validate_database_url(database_url: str, environment: str) -> None:
    if not (is_sqlite_url(database_url) or is_postgresql_url(database_url)):
        raise RuntimeError("DATABASE_URL must use SQLite or PostgreSQL with Psycopg 3")
    if environment.strip().lower() == "production" and not is_postgresql_url(database_url):
        raise RuntimeError(
            "ENVIRONMENT=production requires a PostgreSQL DATABASE_URL; "
            "ephemeral production SQLite is not allowed"
        )


def _positive_int(environment: Mapping[str, str], key: str, default: int) -> int:
    try:
        value = int(environment.get(key, str(default)))
    except ValueError as exc:
        raise RuntimeError(f"{key} must be a positive integer") from exc
    if value <= 0:
        raise RuntimeError(f"{key} must be a positive integer")
    return value


def get_engine_options(
    database_url: str, environment: Mapping[str, str] | None = None
) -> dict[str, Any]:
    values = os.environ if environment is None else environment
    if is_sqlite_url(database_url):
        return {"connect_args": {"check_same_thread": False}}
    return {
        "pool_pre_ping": True,
        "pool_size": _positive_int(values, "DB_POOL_SIZE", 3),
        "max_overflow": _positive_int(values, "DB_MAX_OVERFLOW", 2),
        "pool_recycle": _positive_int(values, "DB_POOL_RECYCLE", 300),
        "pool_timeout": _positive_int(values, "DB_POOL_TIMEOUT", 30),
        "connect_args": {"connect_timeout": 10},
    }


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))
validate_database_url(DATABASE_URL, ENVIRONMENT)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, **get_engine_options(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


if is_sqlite_url(DATABASE_URL):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    # Import all mapped classes before create_all so startup is independent of route imports.
    from app import models as _models  # noqa: F401

    if is_sqlite_url(DATABASE_URL):
        path = make_url(DATABASE_URL).database
        if not path or path == ":memory:":
            Base.metadata.create_all(bind=engine)
            return
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    Base.metadata.create_all(bind=engine)

