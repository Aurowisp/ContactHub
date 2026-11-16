from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes import contacts, excel, stats
from app.config import get_cors_origins
from app.database import create_tables, get_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="ContactHub API",
    version="1.0.1",
    description="Contact management and Excel interchange API",
    lifespan=lifespan,
)
cors_origins = get_cors_origins()
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )
app.include_router(excel.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "error"})
    return {"status": "ok", "version": "1.0.1"}


@app.exception_handler(SQLAlchemyError)
async def database_error(_request: Request, _exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "A database error occurred"})
