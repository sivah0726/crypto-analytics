"""Connect to our Supabase Postgres database."""
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def get_engine():
    """Build a safe connection using environment variables."""
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        database=os.environ.get("DB_NAME", "postgres"),
        query={"sslmode": "require"},
    )
    return create_engine(url, pool_pre_ping=True)
