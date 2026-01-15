"""
Upload fetched data to BigQuery with correct schema and technical indicators
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

# API Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
TWELVEDATA_BASE_URL = "https://api.twelvedata.com"

# BigQuery Configuration
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Top symbols for gap fill
TOP_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "UNH",
    "MA", "HD", "PG", "JNJ", "XOM", "WMT", "CVX", "LLY", "ABBV", "MRK"
]

TOP_CRYPTOS = [
    "BTC/USD", "ETH/USD", "BNB/USD", "XRP/USD", "ADA/USD", "DOGE/USD", "SOL/USD",
    "DOT/USD", "LTC/USD", "AVAX/USD", "LINK/USD", "ATOM/USD", "XLM/USD", "ALGO/USD"
]

def calculate_technical_indicators(df):
    """Calculate all technical indicators for the DataFrame"""
    if len(df) < 50:
        return df

    df = df.sort_values('datetime').copy()

    # Price columns
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    volume = df['volume'].values.astype(float)

    # Change calculations
    df['change'] = df['close'] - df['close'].shift(1)
    df['percent_change'] = (df['change'] / df['close'].shift(1)) * 100
    df['high_low'] = df['high'] - df['low']
    df['pct_high_low'] = ((df['high'] - df['low']) / df['low']) * 100

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean() if len(df) >= 200 else None

    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
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
    df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / df['bollinger_middle']

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

    # Close vs SMA percentages
    df['close_vs_sma20_pct'] = ((df['close'] - df['sma_20']) / df['sma_20']) * 100
    df['close_vs_sma50_pct'] = ((df['close'] - df['sma_50']) / df['sma_50']) * 100

    # Volume ratio
    avg_vol = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / avg_vol.replace(0, np.nan)

    # Log return
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))

    # Trend regime
    df['trend_regime'] = np.where(df['close'] > df['sma_50'], 1, np.where(df['close'] < df['sma_50'], -1, 0))

    return df

def fetch_and_calculate(symbol, interval="1h", outputsize=400, asset_type="stock"):
    """Fetch data from TwelveData and calculate indicators"""
    time.sleep(0.1)  # Rate limiting

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
        df['asset_type'] = asset_type
        df['data_source'] = 'twelvedata'
        df['interval'] = interval

        # Calculate indicators
        df = calculate_technical_indicators(df)

        # Add timestamps
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        df['created_at'] = now
        df['updated_at'] = now

        # Convert datetime to string for BigQuery
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Replace NaN with None
        df = df.replace({np.nan: None})

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
    recent_records = [r for r in records if r.get('datetime', '') >= '2025-12-19']

    if not recent_records:
        return {"success": True, "uploaded": 0, "message": "No recent records to upload"}

    try:
        errors = client.insert_rows_json(table_ref, recent_records)
        if errors:
            return {"success": False, "errors": errors[:3]}
        return {"success": True, "uploaded": len(recent_records)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("="*70)
    print("DATA GAP FILLER - WITH TECHNICAL INDICATORS")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("="*70)

    # Fill stocks hourly gap
    print("\n" + "="*60)
    print("FILLING STOCKS HOURLY GAP (Dec 19 - Jan 3)")
    print("="*60)

    stock_results = {"success": 0, "failed": 0, "uploaded": 0}

    for symbol in TOP_STOCKS:
        result = fetch_and_calculate(symbol, "1h", 400, "stock")
        if result["success"]:
            print(f"  [OK] {symbol}: {result['count']} records fetched")
            upload_result = upload_to_bigquery(result["records"], "stocks_hourly_clean")
            if upload_result.get("success"):
                uploaded = upload_result.get('uploaded', 0)
                print(f"       Uploaded: {uploaded} recent records")
                stock_results["uploaded"] += uploaded
            else:
                print(f"       Upload error: {upload_result.get('error', upload_result.get('errors', 'Unknown'))[:60]}")
            stock_results["success"] += 1
        else:
            print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown')[:60]}")
            stock_results["failed"] += 1

    print(f"\nStocks: {stock_results['success']} success, {stock_results['failed']} failed, {stock_results['uploaded']} uploaded")

    # Fill crypto hourly gap
    print("\n" + "="*60)
    print("FILLING CRYPTO HOURLY GAP (Dec 19 - Jan 3)")
    print("="*60)

    crypto_results = {"success": 0, "failed": 0, "uploaded": 0}

    for symbol in TOP_CRYPTOS:
        result = fetch_and_calculate(symbol, "1h", 400, "crypto")
        if result["success"]:
            print(f"  [OK] {symbol}: {result['count']} records fetched")
            upload_result = upload_to_bigquery(result["records"], "crypto_hourly_clean")
            if upload_result.get("success"):
                uploaded = upload_result.get('uploaded', 0)
                print(f"       Uploaded: {uploaded} recent records")
                crypto_results["uploaded"] += uploaded
            else:
                print(f"       Upload error: {upload_result.get('error', upload_result.get('errors', 'Unknown'))[:60]}")
            crypto_results["success"] += 1
        else:
            print(f"  [FAIL] {symbol}: {result.get('error', 'Unknown')[:60]}")
            crypto_results["failed"] += 1

    print(f"\nCrypto: {crypto_results['success']} success, {crypto_results['failed']} failed, {crypto_results['uploaded']} uploaded")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  Stocks: {stock_results['uploaded']} records uploaded")
    print(f"  Crypto: {crypto_results['uploaded']} records uploaded")
    print(f"  Total: {stock_results['uploaded'] + crypto_results['uploaded']} records")
    print(f"\nCompleted: {datetime.now(timezone.utc).isoformat()}")
    print("="*70)

if __name__ == "__main__":
    main()
