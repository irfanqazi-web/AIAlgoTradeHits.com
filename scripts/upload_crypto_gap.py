"""
Upload crypto hourly data to BigQuery with correct schema
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
from google.cloud import bigquery

# API Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
TWELVEDATA_BASE_URL = "https://api.twelvedata.com"

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Crypto hourly clean schema fields (from bq show)
CRYPTO_HOURLY_FIELDS = [
    "datetime", "open", "high", "low", "close", "symbol", "volume", "asset_type", "interval",
    "rsi", "macd", "macd_signal", "macd_histogram", "stoch_k", "stoch_d", "williams_r",
    "roc", "momentum", "sma_20", "sma_50", "sma_200", "ema_12", "ema_26", "ema_50",
    "adx", "plus_di", "minus_di", "atr", "bollinger_upper", "bollinger_middle", "bollinger_lower",
    "obv", "mfi", "cci", "data_source", "created_at", "updated_at"
]

TOP_CRYPTOS = [
    "BTC/USD", "ETH/USD", "BNB/USD", "XRP/USD", "ADA/USD", "DOGE/USD", "SOL/USD",
    "DOT/USD", "LTC/USD", "AVAX/USD", "LINK/USD", "ATOM/USD", "XLM/USD", "ALGO/USD"
]

def calculate_crypto_indicators(df):
    """Calculate technical indicators for crypto (matching schema)"""
    if len(df) < 50:
        return df

    df = df.sort_values('datetime').copy()

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
    df['sma_200'] = df['close'].rolling(window=200).mean() if len(df) >= 200 else None

    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

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

    # CCI
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14).replace(0, np.nan))

    # ROC
    df['roc'] = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12)) * 100

    # Momentum
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

    # ADX
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    plus_dm[plus_dm < minus_dm] = 0
    minus_dm[minus_dm < plus_dm] = 0

    tr = true_range.rolling(window=14).sum()
    df['plus_di'] = 100 * (plus_dm.rolling(window=14).sum() / tr.replace(0, np.nan))
    df['minus_di'] = 100 * (minus_dm.rolling(window=14).sum() / tr.replace(0, np.nan))
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, np.nan)
    df['adx'] = dx.rolling(window=14).mean()

    # MFI (Money Flow Index)
    tp = (df['high'] + df['low'] + df['close']) / 3
    raw_money_flow = tp * df['volume']
    positive_flow = raw_money_flow.where(tp > tp.shift(1), 0)
    negative_flow = raw_money_flow.where(tp < tp.shift(1), 0)
    money_ratio = positive_flow.rolling(14).sum() / negative_flow.rolling(14).sum().replace(0, np.nan)
    df['mfi'] = 100 - (100 / (1 + money_ratio))

    return df

def fetch_crypto_data(symbol, interval="1h", outputsize=400):
    """Fetch crypto data from TwelveData"""
    time.sleep(0.15)  # Rate limiting

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

        # Create DataFrame
        records = []
        for item in data["values"]:
            records.append({
                "datetime": item["datetime"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": int(float(item.get("volume", 0))),
            })

        df = pd.DataFrame(records)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['symbol'] = symbol
        df['asset_type'] = 'crypto'
        df['data_source'] = 'twelvedata'
        df['interval'] = interval

        # Calculate indicators
        df = calculate_crypto_indicators(df)

        # Add timestamps
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        df['created_at'] = now
        df['updated_at'] = now

        # Convert datetime to string
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Replace NaN with None
        df = df.replace({np.nan: None})

        # Filter to only valid schema fields
        valid_cols = [col for col in CRYPTO_HOURLY_FIELDS if col in df.columns]
        df = df[valid_cols]

        return {"success": True, "symbol": symbol, "records": df.to_dict('records'), "count": len(df)}

    except Exception as e:
        return {"success": False, "symbol": symbol, "error": str(e)}

def upload_to_bigquery(records, table_name):
    """Upload records to BigQuery"""
    if not records:
        return {"success": False, "error": "No records"}

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Get only records from recent dates (last 15 days)
    recent_records = [r for r in records if r.get('datetime', '') >= '2025-12-20']

    if not recent_records:
        return {"success": True, "uploaded": 0, "message": "No recent records"}

    try:
        errors = client.insert_rows_json(table_ref, recent_records)
        if errors:
            return {"success": False, "errors": errors[:3]}
        return {"success": True, "uploaded": len(recent_records)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("="*70)
    print("CRYPTO HOURLY GAP FILLER")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("="*70)

    results = {"success": 0, "failed": 0, "uploaded": 0}

    for symbol in TOP_CRYPTOS:
        result = fetch_crypto_data(symbol, "1h", 400)
        if result["success"]:
            print(f"  [OK] {symbol}: {result['count']} records fetched")
            upload_result = upload_to_bigquery(result["records"], "crypto_hourly_clean")
            if upload_result.get("success"):
                uploaded = upload_result.get('uploaded', 0)
                print(f"       Uploaded: {uploaded} recent records")
                results["uploaded"] += uploaded
            else:
                print(f"       Upload error: {str(upload_result)[:80]}")
            results["success"] += 1
        else:
            print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown')[:60]}")
            results["failed"] += 1

    print(f"\n" + "="*70)
    print(f"SUMMARY: {results['success']} success, {results['failed']} failed, {results['uploaded']} uploaded")
    print(f"Completed: {datetime.now(timezone.utc).isoformat()}")
    print("="*70)

if __name__ == "__main__":
    main()
