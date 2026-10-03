"""Download live crypto prices from CoinGecko."""
import requests

API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def extract(top_n: int = 20) -> list:
    """Return the top N coins as a list of dictionaries."""
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": top_n,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
