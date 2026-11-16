from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import contacts, excel, stats
from app.database import create_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="ContactHub API",
    version="1.0.0",
    description="Contact management and Excel interchange API",
    lifespan=lifespan,
)
app.include_router(excel.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.exception_handler(SQLAlchemyError)
async def database_error(_request: Request, _exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "A database error occurred"})
