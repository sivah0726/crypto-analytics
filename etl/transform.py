"""Turn raw API JSON into a clean, validated table."""
from datetime import datetime, timezone
import pandas as pd


def to_dataframe(coins: list) -> pd.DataFrame:
    snapshot = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    rows = []
    for c in coins:
        rows.append({
            "coin_id":              c.get("id"),
            "symbol":               c.get("symbol"),
            "coin_name":            c.get("name"),
            "current_price":        c.get("current_price"),
            "market_cap":           c.get("market_cap"),
            "total_volume":         c.get("total_volume"),
            "price_change_pct_24h": c.get("price_change_percentage_24h"),
            "high_24h":             c.get("high_24h"),
            "low_24h":              c.get("low_24h"),
            "market_cap_rank":      c.get("market_cap_rank"),
            "image_url":            c.get("image"),
            "snapshot_time":        snapshot,
        })
    return pd.DataFrame(rows)


def validate(df: pd.DataFrame) -> None:
    errors = []
    if df.empty:
        errors.append("empty dataframe")
    if df["coin_id"].isna().any():
        errors.append("null coin_id")
    if df["current_price"].isna().any():
        errors.append("null price")
    if (df["current_price"] <= 0).any():
        errors.append("non-positive price")
    if errors:
        raise ValueError("Data quality failed: " + "; ".join(errors))
