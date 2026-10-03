"""Write data into Supabase."""
import json
from psycopg2.extras import execute_values
import pandas as pd


def land_raw(engine, coins: list, batch_id: str) -> None:
    """Save raw JSON response for auditing."""
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO raw.coins_landing (batch_id, payload) VALUES %s",
                [(batch_id, json.dumps(c)) for c in coins],
                page_size=200,
            )
        raw.commit()
    finally:
        raw.close()


def upsert_prices(engine, df: pd.DataFrame) -> int:
    """Insert new prices; update if same (coin_id, snapshot_time) exists."""
    cols = list(df.columns)
    sql = (
        "INSERT INTO analytics.coin_prices (" + ", ".join(cols) + ") VALUES %s "
        "ON CONFLICT (coin_id, snapshot_time) DO UPDATE SET "
        "current_price        = EXCLUDED.current_price, "
        "market_cap           = EXCLUDED.market_cap, "
        "total_volume         = EXCLUDED.total_volume, "
        "price_change_pct_24h = EXCLUDED.price_change_pct_24h, "
        "high_24h             = EXCLUDED.high_24h, "
        "low_24h              = EXCLUDED.low_24h, "
        "loaded_at            = now()"
    )
    records = [
        tuple(None if pd.isna(v) else v for v in row)
        for row in df.itertuples(index=False, name=None)
    ]
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            execute_values(cur, sql, records, page_size=200)
        raw.commit()
    finally:
        raw.close()
    return len(records)
