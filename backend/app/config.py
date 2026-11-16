import os
from urllib.parse import urlparse


LOCAL_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def get_cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "").strip()
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    values = configured.split(",") if configured else (
        LOCAL_CORS_ORIGINS if environment != "production" else ()
    )

    origins: list[str] = []
    for raw_origin in values:
        origin = raw_origin.strip().rstrip("/")
        if not origin:
            continue
        parsed = urlparse(origin)
        if origin == "*" or parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(
                "CORS_ORIGINS must contain comma-separated http(s) origins; wildcards are not allowed"
            )
        if origin not in origins:
            origins.append(origin)
    return origins
