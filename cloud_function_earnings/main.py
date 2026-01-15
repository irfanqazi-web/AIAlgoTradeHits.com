"""Earnings, Dividends, Splits Calendar Fetcher from TwelveData"""
import functions_framework
from google.cloud import bigquery
import requests
from datetime import datetime, timedelta
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

def fetch_earnings_calendar():
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/earnings_calendar"
    try:
        r = requests.get(url, params={"start_date": start, "end_date": end, "apikey": TWELVEDATA_API_KEY}, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if "earnings" in data:
                return data["earnings"]
    except Exception as e:
        print(f"Error earnings_calendar: {e}")
    return []

def fetch_dividends_calendar():
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/dividends_calendar"
    try:
        r = requests.get(url, params={"start_date": start, "end_date": end, "apikey": TWELVEDATA_API_KEY}, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if "dividends" in data:
                return data["dividends"]
    except Exception as e:
        print(f"Error dividends_calendar: {e}")
    return []

def fetch_splits_calendar():
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/splits_calendar"
    try:
        r = requests.get(url, params={"start_date": start, "end_date": end, "apikey": TWELVEDATA_API_KEY}, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if "splits" in data:
                return data["splits"]
    except Exception as e:
        print(f"Error splits_calendar: {e}")
    return []

def fetch_ipo_calendar():
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/ipo_calendar"
    try:
        r = requests.get(url, params={"start_date": start, "end_date": end, "apikey": TWELVEDATA_API_KEY}, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if "ipo" in data:
                return data["ipo"]
    except Exception as e:
        print(f"Error ipo_calendar: {e}")
    return []

def insert_earnings(data):
    if not data or not isinstance(data, list): return 0
    table_id = f"{PROJECT_ID}.{DATASET_ID}.earnings_calendar"
    rows = []
    for e in list(data)[:100]:
        row = {
            "symbol": e.get("symbol"),
            "name": e.get("name"),
            "currency": e.get("currency"),
            "exchange": e.get("exchange"),
            "mic_code": e.get("mic_code"),
            "country": e.get("country"),
            "earnings_time": e.get("time"),
            "earnings_date": e.get("date"),
            "eps_estimate": safe_float(e.get("eps_estimate")),
            "eps_actual": safe_float(e.get("eps_actual")),
            "eps_surprise": safe_float(e.get("difference")),
            "eps_surprise_percent": safe_float(e.get("surprise_prc")),
            "revenue_estimate": safe_float(e.get("revenue_estimate")),
            "revenue_actual": safe_float(e.get("revenue_actual")),
            "revenue_surprise": None,
            "fetch_timestamp": datetime.utcnow().isoformat()
        }
        rows.append(row)
    if rows:
        errors = client.insert_rows_json(table_id, rows)
        return len(rows) - len(errors)
    return 0

def insert_dividends(data):
    if not data or not isinstance(data, list): return 0
    table_id = f"{PROJECT_ID}.{DATASET_ID}.dividends_calendar"
    rows = []
    for d in list(data)[:100]:
        row = {
            "symbol": d.get("symbol"),
            "name": d.get("name"),
            "exchange": d.get("exchange"),
            "mic_code": d.get("mic_code"),
            "currency": d.get("currency"),
            "declaration_date": d.get("declaration_date"),
            "ex_date": d.get("ex_date"),
            "record_date": d.get("record_date"),
            "payment_date": d.get("payment_date"),
            "amount": safe_float(d.get("amount")),
            "dividend_type": d.get("dividend_type"),
            "frequency": d.get("frequency"),
            "fetch_timestamp": datetime.utcnow().isoformat()
        }
        rows.append(row)
    if rows:
        errors = client.insert_rows_json(table_id, rows)
        return len(rows) - len(errors)
    return 0

def insert_splits(data):
    if not data or not isinstance(data, list): return 0
    table_id = f"{PROJECT_ID}.{DATASET_ID}.splits_calendar"
    rows = []
    for s in list(data)[:100]:
        row = {
            "symbol": s.get("symbol"),
            "name": s.get("name"),
            "exchange": s.get("exchange"),
            "split_date": s.get("date"),
            "from_factor": safe_int(s.get("from_factor")),
            "to_factor": safe_int(s.get("to_factor")),
            "split_ratio": safe_float(s.get("ratio")),
            "description": s.get("description"),
            "fetch_timestamp": datetime.utcnow().isoformat()
        }
        rows.append(row)
    if rows:
        errors = client.insert_rows_json(table_id, rows)
        return len(rows) - len(errors)
    return 0

def insert_ipos(data):
    if not data or not isinstance(data, list): return 0
    table_id = f"{PROJECT_ID}.{DATASET_ID}.ipo_calendar"
    rows = []
    for i in list(data)[:100]:
        row = {
            "symbol": i.get("symbol"),
            "name": i.get("name"),
            "exchange": i.get("exchange"),
            "currency": i.get("currency"),
            "ipo_date": i.get("date"),
            "price_range_low": safe_float(i.get("price_range_low")),
            "price_range_high": safe_float(i.get("price_range_high")),
            "offer_price": safe_float(i.get("offer_price")),
            "shares_offered": safe_int(i.get("shares")),
            "deal_size": safe_float(i.get("deal_size")),
            "underwriters": i.get("underwriters"),
            "status": i.get("status"),
            "fetch_timestamp": datetime.utcnow().isoformat()
        }
        rows.append(row)
    if rows:
        errors = client.insert_rows_json(table_id, rows)
        return len(rows) - len(errors)
    return 0

@functions_framework.http
def earnings_fetcher(request):
    start = datetime.utcnow()
    results = {}

    earnings = fetch_earnings_calendar()
    results["earnings"] = insert_earnings(earnings)

    dividends = fetch_dividends_calendar()
    results["dividends"] = insert_dividends(dividends)

    splits = fetch_splits_calendar()
    results["splits"] = insert_splits(splits)

    ipos = fetch_ipo_calendar()
    results["ipos"] = insert_ipos(ipos)

    duration = (datetime.utcnow() - start).total_seconds()
    return json.dumps({"status": "success", "duration": duration, "results": results}), 200
