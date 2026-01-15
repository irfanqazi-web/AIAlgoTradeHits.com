"""
Fundamentals Data Fetcher
Fetches company profiles, statistics, and financial statements from TwelveData
"""

import functions_framework
from google.cloud import bigquery
import requests
import time
from datetime import datetime
import json

# Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
BASE_URL = "https://api.twelvedata.com"

# Rate limiting
API_DELAY = 0.5  # 500ms between calls

# S&P 500 Top 100 Stocks
TOP_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "JNJ",
    "JPM", "V", "PG", "XOM", "HD", "CVX", "MA", "ABBV", "MRK", "LLY",
    "PEP", "KO", "COST", "AVGO", "TMO", "WMT", "MCD", "CSCO", "ABT", "ACN",
    "DHR", "VZ", "ADBE", "CRM", "CMCSA", "NKE", "TXN", "NEE", "PM", "WFC",
    "INTC", "UPS", "BMY", "RTX", "QCOM", "HON", "ORCL", "UNP", "AMD", "LOW",
    "CAT", "ELV", "IBM", "GS", "SPGI", "BA", "SBUX", "AMAT", "DE", "BLK",
    "GE", "INTU", "PLD", "AXP", "LMT", "ISRG", "MDLZ", "CVS", "GILD", "ADI",
    "TJX", "MS", "ADP", "SYK", "AMT", "BKNG", "VRTX", "SCHW", "CB", "C",
    "MMC", "REGN", "MO", "CI", "NOW", "LRCX", "ZTS", "SO", "CME", "PGR",
    "EQIX", "DUK", "BDX", "ETN", "ITW", "AON", "SHW", "CL", "NOC", "ATVI"
]

client = bigquery.Client(project=PROJECT_ID)


def fetch_company_profile(symbol):
    url = f"{BASE_URL}/profile"
    params = {"symbol": symbol, "apikey": TWELVEDATA_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "code" not in data:
                return data
    except Exception as e:
        print(f"Error fetching profile for {symbol}: {e}")
    return None


def fetch_statistics(symbol):
    url = f"{BASE_URL}/statistics"
    params = {"symbol": symbol, "apikey": TWELVEDATA_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "code" not in data:
                return data
    except Exception as e:
        print(f"Error fetching statistics for {symbol}: {e}")
    return None


def safe_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except:
        return None


def safe_int(value):
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except:
        return None


def insert_profile(profile_data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.fundamentals_company_profile"
    row = {
        "symbol": symbol,
        "name": profile_data.get("name"),
        "exchange": profile_data.get("exchange"),
        "mic_code": profile_data.get("mic_code"),
        "sector": profile_data.get("sector"),
        "industry": profile_data.get("industry"),
        "employees": safe_int(profile_data.get("employees")),
        "website": profile_data.get("website"),
        "description": profile_data.get("description", "")[:5000] if profile_data.get("description") else None,
        "ceo": profile_data.get("ceo"),
        "address": profile_data.get("address"),
        "city": profile_data.get("city"),
        "zip": profile_data.get("zip"),
        "state": profile_data.get("state"),
        "country": profile_data.get("country"),
        "phone": profile_data.get("phone"),
        "logo_url": profile_data.get("logo"),
        "asset_type": profile_data.get("type"),
        "fetch_timestamp": datetime.utcnow().isoformat()
    }
    errors = client.insert_rows_json(table_id, [row])
    return len(errors) == 0


def insert_statistics(stats_data, symbol):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.fundamentals_statistics"
    stats = stats_data.get("statistics", {})
    valuations = stats.get("valuations_metrics", {})
    financials = stats.get("financials", {})
    stock_stats = stats.get("stock_statistics", {})

    row = {
        "symbol": symbol,
        "datetime": datetime.utcnow().isoformat(),
        "market_cap": safe_float(valuations.get("market_capitalization")),
        "enterprise_value": safe_float(valuations.get("enterprise_value")),
        "trailing_pe": safe_float(valuations.get("trailing_pe")),
        "forward_pe": safe_float(valuations.get("forward_pe")),
        "peg_ratio": safe_float(valuations.get("peg_ratio")),
        "price_to_sales": safe_float(valuations.get("price_to_sales_ttm")),
        "price_to_book": safe_float(valuations.get("price_to_book_mrq")),
        "enterprise_to_revenue": safe_float(valuations.get("enterprise_to_revenue")),
        "enterprise_to_ebitda": safe_float(valuations.get("enterprise_to_ebitda")),
        "profit_margin": safe_float(financials.get("profit_margin")),
        "operating_margin": safe_float(financials.get("operating_margin")),
        "return_on_assets": safe_float(financials.get("return_on_assets_ttm")),
        "return_on_equity": safe_float(financials.get("return_on_equity_ttm")),
        "revenue_ttm": safe_float(financials.get("revenue_ttm")),
        "quarterly_revenue_growth": safe_float(financials.get("quarterly_revenue_growth")),
        "gross_profit_ttm": safe_float(financials.get("gross_profit_ttm")),
        "ebitda": safe_float(financials.get("ebitda")),
        "diluted_eps": safe_float(financials.get("diluted_eps_ttm")),
        "total_cash": safe_float(financials.get("total_cash_mrq")),
        "total_debt": safe_float(financials.get("total_debt_mrq")),
        "debt_to_equity": safe_float(financials.get("total_debt_to_equity_mrq")),
        "current_ratio": safe_float(financials.get("current_ratio_mrq")),
        "beta": safe_float(stock_stats.get("beta")),
        "fifty_two_week_low": safe_float(stock_stats.get("52_week_low")),
        "fifty_two_week_high": safe_float(stock_stats.get("52_week_high")),
        "shares_outstanding": safe_int(stock_stats.get("shares_outstanding")),
        "fetch_timestamp": datetime.utcnow().isoformat()
    }
    errors = client.insert_rows_json(table_id, [row])
    return len(errors) == 0


@functions_framework.http
def fundamentals_fetcher(request):
    start_time = datetime.utcnow()
    results = {"profiles": 0, "statistics": 0, "errors": 0}

    for symbol in TOP_STOCKS[:50]:
        try:
            profile = fetch_company_profile(symbol)
            if profile and insert_profile(profile, symbol):
                results["profiles"] += 1
            time.sleep(API_DELAY)

            stats = fetch_statistics(symbol)
            if stats and insert_statistics(stats, symbol):
                results["statistics"] += 1
            time.sleep(API_DELAY)
        except Exception as e:
            results["errors"] += 1
            print(f"Error: {symbol} - {e}")

    duration = (datetime.utcnow() - start_time).total_seconds()
    return json.dumps({"status": "success", "duration": duration, "results": results}), 200
