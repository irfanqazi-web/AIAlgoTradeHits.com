"""Market Movers Fetcher - Top Gainers/Losers from TwelveData"""
import functions_framework
from google.cloud import bigquery
import requests
from datetime import datetime
import json

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
BASE_URL = "https://api.twelvedata.com"

client = bigquery.Client(project=PROJECT_ID)

def safe_float(v):
    try: return float(v) if v else None
    except: return None

def safe_int(v):
    try: return int(float(v)) if v else None
    except: return None

def fetch_market_movers(market, direction="gainers"):
    url = f"{BASE_URL}/market_movers/{market}"
    try:
        r = requests.get(url, params={"direction": direction, "outputsize": 25, "apikey": TWELVEDATA_API_KEY}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "values" in data:
                return data["values"]
    except Exception as e:
        print(f"Error market_movers {market}/{direction}: {e}")
    return []

def insert_market_movers(data, market, category):
    if not data: return 0
    table_id = f"{PROJECT_ID}.{DATASET_ID}.market_movers"
    rows = []
    now = datetime.utcnow().isoformat()
    for rank, m in enumerate(data, 1):
        row = {
            "datetime": now,
            "market": market,
            "category": category,
            "rank": rank,
            "symbol": m.get("symbol"),
            "name": m.get("name"),
            "exchange": m.get("exchange"),
            "price": safe_float(m.get("close")),
            "change": safe_float(m.get("change")),
            "percent_change": safe_float(m.get("percent_change")),
            "volume": safe_int(m.get("volume")),
            "market_cap": safe_float(m.get("market_cap")),
            "fetch_timestamp": now
        }
        rows.append(row)
    if rows:
        errors = client.insert_rows_json(table_id, rows)
        return len(rows) - len(errors)
    return 0

@functions_framework.http
def market_movers_fetcher(request):
    start = datetime.utcnow()
    results = {}

    markets = ["stocks", "etf", "crypto"]
    categories = ["gainers", "losers"]

    for market in markets:
        for category in categories:
            data = fetch_market_movers(market, category)
            key = f"{market}_{category}"
            results[key] = insert_market_movers(data, market, category)

    duration = (datetime.utcnow() - start).total_seconds()
    return json.dumps({"status": "success", "duration": duration, "results": results}), 200
