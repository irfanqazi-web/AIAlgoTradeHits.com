"""
Maximum Quota TwelveData Fetcher
$229 Plan: 800 calls/min, 5000 points/call = 2M records/day

Strategy:
- 2,000,000 ÷ 5000 = 400 API calls needed
- At 800 calls/min, can complete in ~30 seconds (but spread over time for stability)
- Fetch hourly data for ALL available symbols
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery
import threading

# API Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
TWELVEDATA_BASE_URL = "https://api.twelvedata.com"

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Rate limiting - 800 calls/min = 13.3 calls/sec, use 12/sec to be safe
MAX_CALLS_PER_SECOND = 12
call_times = []
lock = threading.Lock()

# Quota tracking
quota_tracker = {
    'calls_made': 0,
    'records_fetched': 0,
    'target_records': 2_000_000,
    'start_time': None
}

# Extended symbol lists for maximum data
STOCKS_EXTENDED = [
    # Top 100 S&P 500
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "JNJ",
    "V", "XOM", "WMT", "JPM", "MA", "PG", "HD", "CVX", "MRK", "ABBV",
    "LLY", "PFE", "KO", "PEP", "COST", "AVGO", "TMO", "MCD", "CSCO", "ACN",
    "ABT", "DHR", "CMCSA", "VZ", "ADBE", "NKE", "INTC", "CRM", "TXN", "PM",
    "NEE", "UPS", "MS", "RTX", "HON", "QCOM", "BA", "LOW", "SPGI", "IBM",
    "GE", "CAT", "AMAT", "BLK", "INTU", "ISRG", "AMD", "GILD", "MDT", "AXP",
    "SYK", "BKNG", "ADI", "MDLZ", "REGN", "VRTX", "LRCX", "ADP", "PANW", "MU",
    "SNPS", "KLAC", "CDNS", "NXPI", "MRVL", "FTNT", "ABNB", "WDAY", "TEAM", "DDOG",
    "ZS", "CRWD", "NET", "SNOW", "MDB", "OKTA", "HUBS", "VEEV", "TTD", "ROKU",
    "SQ", "PYPL", "COIN", "HOOD", "SOFI", "UPST", "AFRM", "BILL", "TOST", "DOCS"
]

CRYPTOS_EXTENDED = [
    "BTC/USD", "ETH/USD", "BNB/USD", "XRP/USD", "ADA/USD", "DOGE/USD", "SOL/USD",
    "DOT/USD", "LTC/USD", "AVAX/USD", "LINK/USD", "ATOM/USD", "XLM/USD", "ALGO/USD",
    "MATIC/USD", "NEAR/USD", "FTM/USD", "SAND/USD", "MANA/USD", "AXS/USD",
    "AAVE/USD", "UNI/USD", "CRV/USD", "COMP/USD", "MKR/USD", "SNX/USD",
    "SUSHI/USD", "YFI/USD", "BAL/USD", "REN/USD", "LRC/USD", "ENJ/USD",
    "CHZ/USD", "GALA/USD", "IMX/USD", "APE/USD", "GMT/USD", "OP/USD",
    "ARB/USD", "SUI/USD", "APT/USD", "SEI/USD", "TIA/USD", "INJ/USD"
]

ETFS_EXTENDED = [
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "EFA", "AGG",
    "BND", "TLT", "GLD", "SLV", "USO", "XLF", "XLK", "XLE", "XLV", "XLI",
    "XLY", "XLP", "XLU", "XLRE", "XLC", "XLB", "VNQ", "ARKK", "ARKG", "ARKF",
    "SOXL", "TQQQ", "UPRO", "SPXL", "FAS", "TNA", "LABU", "TECL", "CURE", "NAIL"
]

FOREX_EXTENDED = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD",
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "EUR/CHF", "AUD/JPY", "GBP/CHF", "EUR/AUD",
    "EUR/CAD", "AUD/NZD", "GBP/AUD", "GBP/CAD", "CHF/JPY", "CAD/JPY"
]

def rate_limit():
    """Enforce 12 calls per second rate limit"""
    with lock:
        now = time.time()
        # Remove calls older than 1 second
        call_times[:] = [t for t in call_times if now - t < 1.0]

        if len(call_times) >= MAX_CALLS_PER_SECOND:
            sleep_time = 1.0 - (now - call_times[0]) + 0.05
            if sleep_time > 0:
                time.sleep(sleep_time)

        call_times.append(time.time())
        quota_tracker['calls_made'] += 1

def fetch_timeseries(symbol, interval, outputsize, asset_type, table_name):
    """Fetch maximum data points from TwelveData"""
    rate_limit()

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,  # Max 5000
        "apikey": TWELVEDATA_API_KEY,
    }

    try:
        response = requests.get(f"{TWELVEDATA_BASE_URL}/time_series", params=params, timeout=30)
        data = response.json()

        if "values" not in data:
            return {"success": False, "symbol": symbol, "error": data.get("message", "No values")[:50]}

        records = []
        for item in data["values"]:
            records.append({
                "datetime": item["datetime"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": int(float(item.get("volume", 0))),
                "symbol": symbol,
                "asset_type": asset_type,
                "interval": interval,
                "data_source": "twelvedata",
            })

        quota_tracker['records_fetched'] += len(records)

        return {
            "success": True,
            "symbol": symbol,
            "records": records,
            "count": len(records),
            "table": table_name,
            "asset_type": asset_type
        }

    except Exception as e:
        return {"success": False, "symbol": symbol, "error": str(e)[:50]}

def calculate_indicators_batch(records):
    """Calculate technical indicators for a batch of records"""
    if len(records) < 50:
        return records

    df = pd.DataFrame(records)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bollinger_middle'] = df['sma_20']
    std_20 = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = df['bollinger_middle'] + (std_20 * 2)
    df['bollinger_lower'] = df['bollinger_middle'] - (std_20 * 2)

    # ATR
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift())
    tr3 = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()

    # Stochastic
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14).replace(0, np.nan))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # ADX components
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr_sum = true_range.rolling(window=14).sum()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).sum() / tr_sum.replace(0, np.nan))
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).sum() / tr_sum.replace(0, np.nan))
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, np.nan)
    df['adx'] = dx.rolling(window=14).mean()

    # CCI
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14).replace(0, np.nan))

    # ROC & Momentum
    df['roc'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100
    df['momentum'] = df['close'] - df['close'].shift(10)

    # OBV
    close = df['close'].values
    volume = df['volume'].values.astype(float)
    obv = [0]
    for i in range(1, len(df)):
        if close[i] > close[i-1]:
            obv.append(obv[-1] + volume[i])
        elif close[i] < close[i-1]:
            obv.append(obv[-1] - volume[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # Timestamps
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    df['created_at'] = now
    df['updated_at'] = now
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df = df.replace({np.nan: None})

    return df.to_dict('records')

def upload_batch(records, table_name):
    """Upload batch to BigQuery"""
    if not records:
        return 0

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        errors = client.insert_rows_json(table_ref, records)
        if errors:
            return 0
        return len(records)
    except Exception as e:
        return 0

def main():
    quota_tracker['start_time'] = datetime.now(timezone.utc)

    print("="*70)
    print("MAXIMUM QUOTA TWELVEDATA FETCHER")
    print("="*70)
    print(f"Plan: $229/month - 800 calls/min, 5000 points/call")
    print(f"Target: 2,000,000 records/day")
    print(f"Strategy: {len(STOCKS_EXTENDED)} stocks + {len(CRYPTOS_EXTENDED)} cryptos + {len(ETFS_EXTENDED)} ETFs + {len(FOREX_EXTENDED)} forex")
    print(f"Started: {quota_tracker['start_time'].isoformat()}")
    print("="*70)

    all_tasks = []

    # Stocks - 5000 points each (hourly = ~7 months of data)
    for symbol in STOCKS_EXTENDED:
        all_tasks.append((symbol, "1h", 5000, "stock", "stocks_hourly_clean"))

    # Cryptos - 5000 points each
    for symbol in CRYPTOS_EXTENDED:
        all_tasks.append((symbol, "1h", 5000, "crypto", "crypto_hourly_clean"))

    # ETFs - 5000 points each
    for symbol in ETFS_EXTENDED:
        all_tasks.append((symbol, "1h", 5000, "etf", "etfs_daily_clean"))

    # Forex - 5000 points each
    for symbol in FOREX_EXTENDED:
        all_tasks.append((symbol, "1h", 5000, "forex", "forex_daily_clean"))

    # Also fetch daily data for more coverage
    for symbol in STOCKS_EXTENDED[:50]:
        all_tasks.append((symbol, "1day", 5000, "stock", "stocks_daily_clean"))

    for symbol in CRYPTOS_EXTENDED[:20]:
        all_tasks.append((symbol, "1day", 5000, "crypto", "crypto_daily_clean"))

    total_expected = len(all_tasks) * 5000
    print(f"\nTotal tasks: {len(all_tasks)}")
    print(f"Expected records: ~{total_expected:,}")
    print(f"API calls needed: {len(all_tasks)}")
    print(f"Estimated time: {len(all_tasks) / 12:.0f} seconds at 12 calls/sec")
    print("\n" + "-"*70)

    results = {
        'stocks_hourly': {'success': 0, 'failed': 0, 'records': 0},
        'crypto_hourly': {'success': 0, 'failed': 0, 'records': 0},
        'etfs': {'success': 0, 'failed': 0, 'records': 0},
        'forex': {'success': 0, 'failed': 0, 'records': 0},
        'stocks_daily': {'success': 0, 'failed': 0, 'records': 0},
        'crypto_daily': {'success': 0, 'failed': 0, 'records': 0},
    }

    uploaded_total = 0

    # Process with parallel execution
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(fetch_timeseries, *task): task
            for task in all_tasks
        }

        completed = 0
        for future in as_completed(futures):
            task = futures[future]
            symbol, interval, _, asset_type, table = task
            completed += 1

            try:
                result = future.result()

                # Determine category
                if asset_type == 'stock' and interval == '1h':
                    cat = 'stocks_hourly'
                elif asset_type == 'crypto' and interval == '1h':
                    cat = 'crypto_hourly'
                elif asset_type == 'etf':
                    cat = 'etfs'
                elif asset_type == 'forex':
                    cat = 'forex'
                elif asset_type == 'stock' and interval == '1day':
                    cat = 'stocks_daily'
                else:
                    cat = 'crypto_daily'

                if result['success']:
                    results[cat]['success'] += 1
                    results[cat]['records'] += result['count']

                    # Calculate indicators and upload
                    records_with_indicators = calculate_indicators_batch(result['records'])
                    uploaded = upload_batch(records_with_indicators, table)
                    uploaded_total += uploaded

                    if completed % 20 == 0:
                        print(f"  Progress: {completed}/{len(all_tasks)} | Records: {quota_tracker['records_fetched']:,} | Uploaded: {uploaded_total:,}")
                else:
                    results[cat]['failed'] += 1
                    if completed % 50 == 0:
                        print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown')}")

            except Exception as e:
                print(f"  [ERROR] {symbol}: {str(e)[:40]}")

    # Summary
    elapsed = (datetime.now(timezone.utc) - quota_tracker['start_time']).total_seconds()

    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    for cat, data in results.items():
        if data['success'] > 0 or data['failed'] > 0:
            print(f"  {cat}: {data['success']} success, {data['failed']} failed, {data['records']:,} records")

    print(f"\n  TOTAL RECORDS FETCHED: {quota_tracker['records_fetched']:,}")
    print(f"  TOTAL UPLOADED: {uploaded_total:,}")
    print(f"  API CALLS MADE: {quota_tracker['calls_made']}")
    print(f"  ELAPSED TIME: {elapsed:.1f} seconds")
    print(f"  RATE: {quota_tracker['records_fetched']/elapsed:.0f} records/sec")
    print(f"\n  Quota usage: {quota_tracker['records_fetched']/2_000_000*100:.1f}% of 2M daily limit")
    print("="*70)

if __name__ == "__main__":
    main()
