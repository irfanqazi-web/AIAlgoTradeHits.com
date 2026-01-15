"""Analyst Data Fetcher - Recommendations, Price Targets, Estimates from TwelveData"""
import functions_framework
from google.cloud import bigquery
import requests
import time
from datetime import datetime
import json

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
BASE_URL = "https://api.twelvedata.com"
API_DELAY = 0.5

TOP_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ",
    "UNH", "PG", "XOM", "HD", "CVX", "MA", "ABBV", "MRK", "LLY", "PEP",
    "KO", "COST", "AVGO", "TMO", "WMT", "MCD", "CSCO", "ABT", "ACN", "DHR",
    "VZ", "ADBE", "CRM", "CMCSA", "NKE", "TXN", "NEE", "PM", "WFC", "INTC",
    "UPS", "BMY", "RTX", "QCOM", "HON", "ORCL", "UNP", "AMD", "LOW", "CAT"]

client = bigquery.Client(project=PROJECT_ID)

def safe_float(v):
    try: return float(v) if v else None
    except: return None

def safe_int(v):
    try: return int(float(v)) if v else None
    except: return None

def fetch_recommendations(symbol):
    url = f"{BASE_URL}/recommendations"
    try:
        r = requests.get(url, params={"symbol": symbol, "apikey": TWELVEDATA_API_KEY}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "code" not in data:
                return data
    except Exception as e:
        print(f"Error recommendations {symbol}: {e}")
    return None

def fetch_price_target(symbol):
    url = f"{BASE_URL}/price_target"
    try:
        r = requests.get(url, params={"symbol": symbol, "apikey": TWELVEDATA_API_KEY}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "code" not in data:
                return data
    except Exception as e:
        print(f"Error price_target {symbol}: {e}")
    return None

def fetch_earnings_estimate(symbol):
    url = f"{BASE_URL}/earnings_estimate"
    try:
        r = requests.get(url, params={"symbol": symbol, "apikey": TWELVEDATA_API_KEY}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "earnings_estimate" in data:
                return data["earnings_estimate"]
    except Exception as e:
        print(f"Error earnings_estimate {symbol}: {e}")
    return None

def insert_recommendations(data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.analyst_recommendations"
    recs = data.get("recommendations", [{}])[0] if data.get("recommendations") else {}
    row = {
        "symbol": symbol,
        "datetime": datetime.utcnow().isoformat(),
        "strong_buy": safe_int(recs.get("strong_buy")),
        "buy": safe_int(recs.get("buy")),
        "hold": safe_int(recs.get("hold")),
        "sell": safe_int(recs.get("sell")),
        "strong_sell": safe_int(recs.get("strong_sell")),
        "total_analysts": safe_int(recs.get("total")),
        "consensus_rating": recs.get("rating"),
        "consensus_score": safe_float(recs.get("score")),
        "fetch_timestamp": datetime.utcnow().isoformat()
    }
    errors = client.insert_rows_json(table_id, [row])
    return len(errors) == 0

def insert_price_target(data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.analyst_price_targets"
    row = {
        "symbol": symbol,
        "datetime": datetime.utcnow().isoformat(),
        "target_high": safe_float(data.get("target_high")),
        "target_low": safe_float(data.get("target_low")),
        "target_mean": safe_float(data.get("target_mean")),
        "target_median": safe_float(data.get("target_median")),
        "current_price": safe_float(data.get("current_price")),
        "upside_percent": safe_float(data.get("upside")),
        "number_of_analysts": safe_int(data.get("number_of_analysts")),
        "fetch_timestamp": datetime.utcnow().isoformat()
    }
    errors = client.insert_rows_json(table_id, [row])
    return len(errors) == 0

def insert_earnings_estimates(data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.analyst_earnings_estimates"
    rows = []
    for est in data[:4]:
        row = {
            "symbol": symbol,
            "datetime": datetime.utcnow().isoformat(),
            "period": est.get("period"),
            "eps_avg": safe_float(est.get("eps_avg")),
            "eps_high": safe_float(est.get("eps_high")),
            "eps_low": safe_float(est.get("eps_low")),
            "number_of_analysts": safe_int(est.get("number_of_analysts")),
            "revenue_avg": safe_float(est.get("revenue_avg")),
            "revenue_high": safe_float(est.get("revenue_high")),
            "revenue_low": safe_float(est.get("revenue_low")),
            "growth_estimate": safe_float(est.get("growth")),
            "fetch_timestamp": datetime.utcnow().isoformat()
        }
        rows.append(row)
    if rows:
        errors = client.insert_rows_json(table_id, rows)
        return len(errors) == 0
    return False

@functions_framework.http
def analyst_fetcher(request):
    start = datetime.utcnow()
    results = {"recommendations": 0, "price_targets": 0, "estimates": 0, "errors": 0}

    for symbol in TOP_STOCKS:
        try:
            rec = fetch_recommendations(symbol)
            if rec and insert_recommendations(rec, symbol):
                results["recommendations"] += 1
            time.sleep(API_DELAY)

            pt = fetch_price_target(symbol)
            if pt and insert_price_target(pt, symbol):
                results["price_targets"] += 1
            time.sleep(API_DELAY)

            est = fetch_earnings_estimate(symbol)
            if est and insert_earnings_estimates(est, symbol):
                results["estimates"] += 1
            time.sleep(API_DELAY)
        except Exception as e:
            results["errors"] += 1
            print(f"Error {symbol}: {e}")

    duration = (datetime.utcnow() - start).total_seconds()
    return json.dumps({"status": "success", "duration": duration, "results": results}), 200
