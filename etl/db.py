"""Connect to our Supabase Postgres database."""
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def _env(key: str, default: str = None, required: bool = False) -> str:
    """Read env var; treat empty strings as missing (common GitHub Secrets trap)."""
    value = (os.environ.get(key) or "").strip()
    if not value:
        if required and default is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return default
    return value


def get_engine():
    """Build a safe connection using environment variables."""
    host     = _env("DB_HOST", required=True)
    user     = _env("DB_USER", required=True)
    password = _env("DB_PASSWORD", required=True)
    port     = int(_env("DB_PORT", default="5432"))   # empty → 5432
    database = _env("DB_NAME", default="postgres")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={"sslmode": "require"},
    )
    return create_engine(url, pool_pre_ping=True)
