"""ETF Analytics Fetcher - Profile, Performance, Holdings from TwelveData"""
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

TOP_ETFS = ["SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "EEM", "EFA",
    "GLD", "SLV", "USO", "XLF", "XLE", "XLK", "XLV", "XLI", "XLP", "XLY",
    "XLU", "XLB", "XLRE", "VNQ", "TLT", "IEF", "LQD", "HYG", "AGG", "BND",
    "ARKK", "ARKG", "ARKW", "XBI", "IBB", "SMH", "SOXX", "KWEB", "FXI", "INDA",
    "VGK", "IEMG", "SCHD", "VIG", "DVY", "HDV", "NOBL", "RSP", "MTUM", "VTV"]

client = bigquery.Client(project=PROJECT_ID)

def safe_float(v):
    try: return float(v) if v else None
    except: return None

def safe_int(v):
    try: return int(float(v)) if v else None
    except: return None

def fetch_etf_summary(symbol):
    try:
        r = requests.get(f"{BASE_URL}/etf", params={"symbol": symbol, "apikey": TWELVEDATA_API_KEY}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "code" not in data:
                return data
    except Exception as e:
        print(f"Error etf_summary {symbol}: {e}")
    return None

def fetch_etf_performance(symbol):
    try:
        r = requests.get(f"{BASE_URL}/quote", params={"symbol": symbol, "apikey": TWELVEDATA_API_KEY}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "code" not in data:
                return data
    except Exception as e:
        print(f"Error etf_performance {symbol}: {e}")
    return None

def insert_etf_profile(data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.etf_profile"
    row = {
        "symbol": symbol,
        "name": data.get("name"),
        "fund_family": data.get("fund_family"),
        "fund_type": data.get("fund_type"),
        "currency": data.get("currency"),
        "exchange": data.get("exchange"),
        "inception_date": data.get("inception_date"),
        "expense_ratio": safe_float(data.get("expense_ratio")),
        "total_assets": safe_float(data.get("total_assets")),
        "nav": safe_float(data.get("nav")),
        "average_volume": safe_int(data.get("average_volume")),
        "category": data.get("category"),
        "benchmark": data.get("benchmark_index"),
        "investment_strategy": data.get("investment_strategy"),
        "fetch_timestamp": datetime.utcnow().isoformat()
    }
    errors = client.insert_rows_json(table_id, [row])
    return len(errors) == 0

def insert_etf_performance(data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.etf_performance"
    row = {
        "symbol": symbol,
        "datetime": datetime.utcnow().isoformat(),
        "return_1d": safe_float(data.get("percent_change")),
        "return_1w": None,
        "return_1m": None,
        "return_3m": None,
        "return_6m": None,
        "return_ytd": None,
        "return_1y": safe_float(data.get("change_52_week")),
        "return_3y": None,
        "return_5y": None,
        "return_10y": None,
        "return_since_inception": None,
        "fetch_timestamp": datetime.utcnow().isoformat()
    }
    errors = client.insert_rows_json(table_id, [row])
    return len(errors) == 0

@functions_framework.http
def etf_analytics_fetcher(request):
    start = datetime.utcnow()
    results = {"profiles": 0, "performance": 0, "errors": 0}

    for symbol in TOP_ETFS:
        try:
            summary = fetch_etf_summary(symbol)
            if summary and insert_etf_profile(summary, symbol):
                results["profiles"] += 1
            time.sleep(API_DELAY)

            perf = fetch_etf_performance(symbol)
            if perf and insert_etf_performance(perf, symbol):
                results["performance"] += 1
            time.sleep(API_DELAY)
        except Exception as e:
            results["errors"] += 1
            print(f"Error {symbol}: {e}")

    duration = (datetime.utcnow() - start).total_seconds()
    return json.dumps({"status": "success", "duration": duration, "results": results}), 200
