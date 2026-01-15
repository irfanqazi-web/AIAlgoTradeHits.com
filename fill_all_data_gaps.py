"""
Comprehensive Data Gap Filler - Multi-Source Parallel Fetcher
Uses TwelveData ($229 plan - 2M records/day), KrakenPro, FRED, Finnhub, CoinMarketCap

Based on masterquery.md recommendations
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import requests
import time
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery
import threading

# ==================== API CONFIGURATION ====================

# TwelveData - $229/month plan (800 calls/min, 5000 data points per call)
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
TWELVEDATA_BASE_URL = "https://api.twelvedata.com"
TWELVEDATA_RATE_LIMIT = 55  # calls per minute (conservative for 800/min)

# Kraken Pro - Public API
KRAKEN_BASE_URL = "https://api.kraken.com/0/public"
KRAKEN_RATE_LIMIT = 40  # calls per minute

# FRED - Federal Reserve Economic Data
FRED_API_KEY = "608f96800c8a5d9bdb8d53ad059f06c1"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"

# Finnhub - Analyst Recommendations
FINNHUB_API_KEY = "d4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg"
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# CoinMarketCap - Crypto Rankings
CMC_API_KEY = "059474ae48b84628be6f4a94f9840c30"
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Rate limiting
api_call_times = {
    'twelvedata': [],
    'kraken': [],
    'fred': [],
    'finnhub': [],
    'cmc': []
}
lock = threading.Lock()

# ==================== RATE LIMITING ====================

def rate_limit(api_name, max_calls_per_min):
    """Enforce rate limiting per API"""
    with lock:
        now = time.time()
        # Remove calls older than 60 seconds
        api_call_times[api_name] = [t for t in api_call_times[api_name] if now - t < 60]

        if len(api_call_times[api_name]) >= max_calls_per_min:
            sleep_time = 60 - (now - api_call_times[api_name][0]) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)

        api_call_times[api_name].append(time.time())

# ==================== TWELVEDATA FUNCTIONS ====================

def fetch_twelvedata_timeseries(symbol, interval="1h", outputsize=5000, asset_type="stock"):
    """Fetch time series data from TwelveData"""
    rate_limit('twelvedata', TWELVEDATA_RATE_LIMIT)

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": TWELVEDATA_API_KEY,
        "format": "JSON"
    }

    try:
        response = requests.get(f"{TWELVEDATA_BASE_URL}/time_series", params=params, timeout=30)
        data = response.json()

        if "values" in data:
            records = []
            for item in data["values"]:
                records.append({
                    "symbol": symbol,
                    "datetime": item["datetime"],
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"]),
                    "volume": int(float(item.get("volume", 0))),
                    "source": "twelvedata",
                    "asset_type": asset_type,
                    "fetch_timestamp": datetime.utcnow().isoformat()
                })
            return {"success": True, "symbol": symbol, "records": records, "count": len(records)}
        else:
            return {"success": False, "symbol": symbol, "error": data.get("message", "Unknown error")}
    except Exception as e:
        return {"success": False, "symbol": symbol, "error": str(e)}

def fetch_twelvedata_with_indicators(symbol, interval="1day", outputsize=5000, asset_type="stock"):
    """Fetch time series with technical indicators from TwelveData"""
    rate_limit('twelvedata', TWELVEDATA_RATE_LIMIT)

    # Fetch base time series
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": TWELVEDATA_API_KEY,
    }

    try:
        response = requests.get(f"{TWELVEDATA_BASE_URL}/time_series", params=params, timeout=30)
        data = response.json()

        if "values" not in data:
            return {"success": False, "symbol": symbol, "error": data.get("message", "No values")}

        records = []
        for item in data["values"]:
            records.append({
                "symbol": symbol,
                "datetime": item["datetime"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": int(float(item.get("volume", 0))),
                "source": "twelvedata",
                "asset_type": asset_type,
                "fetch_timestamp": datetime.utcnow().isoformat()
            })

        return {"success": True, "symbol": symbol, "records": records, "count": len(records)}
    except Exception as e:
        return {"success": False, "symbol": symbol, "error": str(e)}

# ==================== KRAKEN FUNCTIONS ====================

def fetch_kraken_ohlc(pair, interval=60):
    """Fetch OHLC data from Kraken with buy/sell volume"""
    rate_limit('kraken', KRAKEN_RATE_LIMIT)

    try:
        response = requests.get(f"{KRAKEN_BASE_URL}/OHLC", params={"pair": pair, "interval": interval}, timeout=30)
        data = response.json()

        if data.get("error"):
            return {"success": False, "symbol": pair, "error": str(data["error"])}

        result_key = list(data["result"].keys())[0] if data["result"] else None
        if not result_key or result_key == "last":
            return {"success": False, "symbol": pair, "error": "No data"}

        records = []
        for item in data["result"][result_key]:
            records.append({
                "symbol": pair.replace("USD", "/USD"),
                "datetime": datetime.utcfromtimestamp(item[0]).isoformat(),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[6]),
                "trade_count": int(item[7]) if len(item) > 7 else 0,
                "source": "kraken",
                "asset_type": "crypto",
                "fetch_timestamp": datetime.utcnow().isoformat()
            })

        return {"success": True, "symbol": pair, "records": records, "count": len(records)}
    except Exception as e:
        return {"success": False, "symbol": pair, "error": str(e)}

def fetch_kraken_recent_trades(pair):
    """Fetch recent trades from Kraken for buy/sell pressure"""
    rate_limit('kraken', KRAKEN_RATE_LIMIT)

    try:
        response = requests.get(f"{KRAKEN_BASE_URL}/Trades", params={"pair": pair}, timeout=30)
        data = response.json()

        if data.get("error"):
            return {"success": False, "symbol": pair, "error": str(data["error"])}

        result_key = list(data["result"].keys())[0] if data["result"] else None
        if not result_key or result_key == "last":
            return {"success": False, "symbol": pair, "error": "No trades"}

        trades = data["result"][result_key]
        buy_volume = sum(float(t[1]) for t in trades if t[3] == 'b')
        sell_volume = sum(float(t[1]) for t in trades if t[3] == 's')
        buy_count = sum(1 for t in trades if t[3] == 'b')
        sell_count = sum(1 for t in trades if t[3] == 's')

        return {
            "success": True,
            "symbol": pair,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "buy_pressure": buy_volume / (buy_volume + sell_volume) if (buy_volume + sell_volume) > 0 else 0.5
        }
    except Exception as e:
        return {"success": False, "symbol": pair, "error": str(e)}

# ==================== FRED FUNCTIONS ====================

def fetch_fred_series(series_id):
    """Fetch economic data from FRED"""
    rate_limit('fred', 100)

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1000
    }

    try:
        response = requests.get(f"{FRED_BASE_URL}/series/observations", params=params, timeout=30)
        data = response.json()

        if "observations" not in data:
            return {"success": False, "series_id": series_id, "error": "No observations"}

        records = []
        for obs in data["observations"]:
            if obs["value"] != ".":
                records.append({
                    "series_id": series_id,
                    "date": obs["date"],
                    "value": float(obs["value"]),
                    "source": "fred",
                    "fetch_timestamp": datetime.utcnow().isoformat()
                })

        return {"success": True, "series_id": series_id, "records": records, "count": len(records)}
    except Exception as e:
        return {"success": False, "series_id": series_id, "error": str(e)}

# ==================== FINNHUB FUNCTIONS ====================

def fetch_finnhub_recommendations(symbol):
    """Fetch analyst recommendations from Finnhub"""
    rate_limit('finnhub', 50)

    try:
        response = requests.get(
            f"{FINNHUB_BASE_URL}/stock/recommendation",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=30
        )
        data = response.json()

        if not data:
            return {"success": False, "symbol": symbol, "error": "No recommendations"}

        records = []
        for rec in data[:12]:  # Last 12 months
            records.append({
                "symbol": symbol,
                "period": rec.get("period"),
                "strong_buy": rec.get("strongBuy", 0),
                "buy": rec.get("buy", 0),
                "hold": rec.get("hold", 0),
                "sell": rec.get("sell", 0),
                "strong_sell": rec.get("strongSell", 0),
                "source": "finnhub",
                "fetch_timestamp": datetime.utcnow().isoformat()
            })

        return {"success": True, "symbol": symbol, "records": records, "count": len(records)}
    except Exception as e:
        return {"success": False, "symbol": symbol, "error": str(e)}

# ==================== COINMARKETCAP FUNCTIONS ====================

def fetch_cmc_rankings(limit=200):
    """Fetch crypto rankings from CoinMarketCap"""
    rate_limit('cmc', 10)

    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"limit": limit, "convert": "USD"}

    try:
        response = requests.get(f"{CMC_BASE_URL}/cryptocurrency/listings/latest", headers=headers, params=params, timeout=30)
        data = response.json()

        if "data" not in data:
            return {"success": False, "error": data.get("status", {}).get("error_message", "Unknown error")}

        records = []
        for crypto in data["data"]:
            quote = crypto.get("quote", {}).get("USD", {})
            records.append({
                "symbol": crypto["symbol"],
                "name": crypto["name"],
                "cmc_rank": crypto["cmc_rank"],
                "market_cap": quote.get("market_cap"),
                "volume_24h": quote.get("volume_24h"),
                "percent_change_24h": quote.get("percent_change_24h"),
                "percent_change_7d": quote.get("percent_change_7d"),
                "circulating_supply": crypto.get("circulating_supply"),
                "source": "coinmarketcap",
                "fetch_timestamp": datetime.utcnow().isoformat()
            })

        return {"success": True, "records": records, "count": len(records)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== BIGQUERY UPLOAD ====================

def upload_to_bigquery(records, table_name, dataset=DATASET_ID):
    """Upload records to BigQuery"""
    if not records:
        return {"success": False, "error": "No records to upload"}

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{dataset}.{table_name}"

    try:
        errors = client.insert_rows_json(table_ref, records)
        if errors:
            return {"success": False, "errors": errors[:5]}
        return {"success": True, "uploaded": len(records)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== SYMBOL LISTS ====================

# Top stocks for hourly data
TOP_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "JNJ",
    "V", "XOM", "WMT", "JPM", "MA", "PG", "HD", "CVX", "MRK", "ABBV",
    "LLY", "PFE", "KO", "PEP", "COST", "AVGO", "TMO", "MCD", "CSCO", "ACN",
    "ABT", "DHR", "CMCSA", "VZ", "ADBE", "NKE", "INTC", "CRM", "TXN", "PM",
    "NEE", "UPS", "MS", "RTX", "HON", "QCOM", "BA", "LOW", "SPGI", "IBM"
]

# Top cryptos
TOP_CRYPTOS = [
    "BTC/USD", "ETH/USD", "BNB/USD", "XRP/USD", "ADA/USD", "DOGE/USD", "SOL/USD",
    "DOT/USD", "MATIC/USD", "LTC/USD", "AVAX/USD", "LINK/USD", "ATOM/USD", "XLM/USD",
    "ALGO/USD", "VET/USD", "FIL/USD", "TRX/USD", "ETC/USD", "XMR/USD"
]

# Kraken pairs for buy/sell volume
KRAKEN_PAIRS = [
    "XXBTZUSD", "XETHZUSD", "XXRPZUSD", "ADAUSD", "DOTUSD", "SOLUSD",
    "DOGEUSD", "MATICUSD", "LTCUSD", "AVAXUSD", "LINKUSD", "ATOMUSD",
    "XLMUSD", "ALGOUSD", "TRXUSD", "XETCZUSD", "XXMRZUSD", "FILUSD"
]

# ETFs
TOP_ETFS = [
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "EFA", "AGG",
    "BND", "TLT", "GLD", "SLV", "USO", "XLF", "XLK", "XLE", "XLV", "XLI"
]

# Forex pairs
FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD",
    "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
]

# Indices
INDICES = ["SPX", "NDX", "DJI", "RUT", "VIX"]

# FRED series
FRED_SERIES = [
    "DGS10", "DGS2", "DGS30", "T10Y2Y", "FEDFUNDS", "VIXCLS",
    "UNRATE", "CPIAUCSL", "MORTGAGE30US", "GDP"
]

# ==================== MAIN EXECUTION ====================

def fill_stocks_hourly_gap():
    """Fill stocks hourly data gap (Dec 18 to now)"""
    print("\n" + "="*60)
    print("FILLING STOCKS HOURLY DATA GAP")
    print("="*60)

    results = {"success": 0, "failed": 0, "total_records": 0}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_twelvedata_timeseries, symbol, "1h", 5000, "stock"): symbol
            for symbol in TOP_STOCKS
        }

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                if result["success"]:
                    print(f"  [OK] {symbol}: {result['count']} records")
                    results["success"] += 1
                    results["total_records"] += result["count"]

                    # Upload to BigQuery
                    upload_result = upload_to_bigquery(result["records"], "stocks_hourly_clean")
                    if not upload_result["success"]:
                        print(f"    [WARN] Upload failed: {upload_result.get('error', 'Unknown')}")
                else:
                    print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown error')}")
                    results["failed"] += 1
            except Exception as e:
                print(f"  [ERROR] {symbol}: {str(e)}")
                results["failed"] += 1

    print(f"\nStocks Hourly: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
    return results

def fill_crypto_hourly_gap():
    """Fill crypto hourly data gap (Dec 19 to now)"""
    print("\n" + "="*60)
    print("FILLING CRYPTO HOURLY DATA GAP")
    print("="*60)

    results = {"success": 0, "failed": 0, "total_records": 0}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_twelvedata_timeseries, symbol, "1h", 5000, "crypto"): symbol
            for symbol in TOP_CRYPTOS
        }

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                if result["success"]:
                    print(f"  [OK] {symbol}: {result['count']} records")
                    results["success"] += 1
                    results["total_records"] += result["count"]

                    upload_result = upload_to_bigquery(result["records"], "crypto_hourly_clean")
                    if not upload_result["success"]:
                        print(f"    [WARN] Upload failed: {upload_result.get('error', 'Unknown')}")
                else:
                    print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown error')}")
                    results["failed"] += 1
            except Exception as e:
                print(f"  [ERROR] {symbol}: {str(e)}")
                results["failed"] += 1

    print(f"\nCrypto Hourly: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
    return results

def fetch_kraken_buy_sell_data():
    """Fetch buy/sell volume data from Kraken"""
    print("\n" + "="*60)
    print("FETCHING KRAKEN BUY/SELL VOLUME DATA")
    print("="*60)

    results = {"success": 0, "failed": 0}
    buy_sell_data = []

    for pair in KRAKEN_PAIRS:
        result = fetch_kraken_recent_trades(pair)
        if result["success"]:
            print(f"  [OK] {pair}: Buy pressure = {result['buy_pressure']:.2%}")
            buy_sell_data.append({
                "symbol": result["symbol"],
                "buy_volume": result["buy_volume"],
                "sell_volume": result["sell_volume"],
                "buy_count": result["buy_count"],
                "sell_count": result["sell_count"],
                "buy_pressure": result["buy_pressure"],
                "fetch_timestamp": datetime.utcnow().isoformat()
            })
            results["success"] += 1
        else:
            print(f"  [FAIL] {pair}: {result.get('error', 'Unknown')}")
            results["failed"] += 1

        time.sleep(1.5)  # Kraken rate limit

    print(f"\nKraken: {results['success']} success, {results['failed']} failed")
    return buy_sell_data

def fetch_fred_economic_data():
    """Fetch economic indicators from FRED"""
    print("\n" + "="*60)
    print("FETCHING FRED ECONOMIC DATA")
    print("="*60)

    results = {"success": 0, "failed": 0, "total_records": 0}
    all_records = []

    for series_id in FRED_SERIES:
        result = fetch_fred_series(series_id)
        if result["success"]:
            print(f"  [OK] {series_id}: {result['count']} records")
            all_records.extend(result["records"])
            results["success"] += 1
            results["total_records"] += result["count"]
        else:
            print(f"  [FAIL] {series_id}: {result.get('error', 'Unknown')}")
            results["failed"] += 1

        time.sleep(0.5)

    # Upload to BigQuery
    if all_records:
        upload_result = upload_to_bigquery(all_records, "fred_economic_data")
        print(f"  Upload: {upload_result}")

    print(f"\nFRED: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
    return results

def fetch_finnhub_analyst_data():
    """Fetch analyst recommendations from Finnhub"""
    print("\n" + "="*60)
    print("FETCHING FINNHUB ANALYST RECOMMENDATIONS")
    print("="*60)

    results = {"success": 0, "failed": 0, "total_records": 0}
    all_records = []

    for symbol in TOP_STOCKS[:30]:  # Top 30 stocks
        result = fetch_finnhub_recommendations(symbol)
        if result["success"]:
            print(f"  [OK] {symbol}: {result['count']} recommendations")
            all_records.extend(result["records"])
            results["success"] += 1
            results["total_records"] += result["count"]
        else:
            print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown')}")
            results["failed"] += 1

        time.sleep(1.2)  # Finnhub rate limit

    # Upload to BigQuery
    if all_records:
        upload_result = upload_to_bigquery(all_records, "finnhub_recommendations")
        print(f"  Upload: {upload_result}")

    print(f"\nFinnhub: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
    return results

def fetch_cmc_crypto_rankings():
    """Fetch crypto rankings from CoinMarketCap"""
    print("\n" + "="*60)
    print("FETCHING COINMARKETCAP RANKINGS")
    print("="*60)

    result = fetch_cmc_rankings(200)

    if result["success"]:
        print(f"  [OK] Fetched {result['count']} crypto rankings")

        # Upload to BigQuery
        upload_result = upload_to_bigquery(result["records"], "cmc_crypto_rankings")
        print(f"  Upload: {upload_result}")
        return result
    else:
        print(f"  [FAIL] {result.get('error', 'Unknown')}")
        return result

def fill_etfs_hourly():
    """Fill ETFs hourly data"""
    print("\n" + "="*60)
    print("FILLING ETFs HOURLY DATA")
    print("="*60)

    results = {"success": 0, "failed": 0, "total_records": 0}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_twelvedata_timeseries, symbol, "1h", 5000, "etf"): symbol
            for symbol in TOP_ETFS
        }

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                if result["success"]:
                    print(f"  [OK] {symbol}: {result['count']} records")
                    results["success"] += 1
                    results["total_records"] += result["count"]
                else:
                    print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown error')}")
                    results["failed"] += 1
            except Exception as e:
                print(f"  [ERROR] {symbol}: {str(e)}")
                results["failed"] += 1

    print(f"\nETFs Hourly: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
    return results

def fill_forex_hourly():
    """Fill Forex hourly data"""
    print("\n" + "="*60)
    print("FILLING FOREX HOURLY DATA")
    print("="*60)

    results = {"success": 0, "failed": 0, "total_records": 0}

    for symbol in FOREX_PAIRS:
        result = fetch_twelvedata_timeseries(symbol, "1h", 5000, "forex")
        if result["success"]:
            print(f"  [OK] {symbol}: {result['count']} records")
            results["success"] += 1
            results["total_records"] += result["count"]
        else:
            print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown error')}")
            results["failed"] += 1

    print(f"\nForex Hourly: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
    return results

def main():
    """Main execution - fill all data gaps"""
    print("="*70)
    print("COMPREHENSIVE DATA GAP FILLER")
    print(f"Started: {datetime.utcnow().isoformat()}")
    print("="*70)
    print("\nUsing APIs:")
    print("  - TwelveData ($229 plan - 800 calls/min, 2M records/day)")
    print("  - KrakenPro (Public API)")
    print("  - FRED (Economic Data)")
    print("  - Finnhub (Analyst Recommendations)")
    print("  - CoinMarketCap (Crypto Rankings)")
    print("="*70)

    all_results = {}

    # 1. Fill stocks hourly gap
    all_results["stocks_hourly"] = fill_stocks_hourly_gap()

    # 2. Fill crypto hourly gap
    all_results["crypto_hourly"] = fill_crypto_hourly_gap()

    # 3. Fill ETFs hourly
    all_results["etfs_hourly"] = fill_etfs_hourly()

    # 4. Fill Forex hourly
    all_results["forex_hourly"] = fill_forex_hourly()

    # 5. Fetch Kraken buy/sell data
    all_results["kraken_buy_sell"] = fetch_kraken_buy_sell_data()

    # 6. Fetch FRED economic data
    all_results["fred"] = fetch_fred_economic_data()

    # 7. Fetch Finnhub analyst data
    all_results["finnhub"] = fetch_finnhub_analyst_data()

    # 8. Fetch CoinMarketCap rankings
    all_results["cmc"] = fetch_cmc_crypto_rankings()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    total_records = 0
    for source, result in all_results.items():
        if isinstance(result, dict) and "total_records" in result:
            total_records += result["total_records"]
            print(f"  {source}: {result.get('success', 0)} success, {result.get('failed', 0)} failed, {result['total_records']} records")
        elif isinstance(result, list):
            print(f"  {source}: {len(result)} records")
            total_records += len(result)

    print(f"\nTOTAL RECORDS FETCHED: {total_records:,}")
    print(f"Completed: {datetime.utcnow().isoformat()}")
    print("="*70)

    return all_results

if __name__ == "__main__":
    main()
