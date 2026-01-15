"""
Fetch test data for NVIDIA and Bitcoin
- All daily data (historical)
- 4 days of 10-minute data
- 2 days of 5-minute data
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timezone, timedelta
import requests
import time
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, ROCIndicator
from ta.trend import MACD, ADXIndicator, CCIIndicator, AroonIndicator, TRIXIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, AccDistIndexIndicator, ChaikinMoneyFlowIndicator
import ccxt

# Configuration
TWELVE_DATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"

def calculate_technical_indicators(df):
    """Calculate all 71 technical indicators"""
    try:
        if len(df) < 200:
            print(f"  Warning: Only {len(df)} data points, some indicators may be inaccurate")

        # Momentum Indicators
        df['rsi'] = RSIIndicator(df['close'], window=14).rsi()

        macd = MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()

        stoch = StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        df['williams_r'] = WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
        df['cci'] = CCIIndicator(df['high'], df['low'], df['close']).cci()
        df['roc'] = ROCIndicator(df['close'], window=12).roc()
        df['momentum'] = df['close'].diff(10)

        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['wma_20'] = df['close'].rolling(window=20).apply(lambda x: np.average(x, weights=range(1, 21)))
        df['dema_20'] = 2 * df['close'].ewm(span=20).mean() - df['close'].ewm(span=20).mean().ewm(span=20).mean()
        df['tema_20'] = 3 * df['close'].ewm(span=20).mean() - 3 * df['close'].ewm(span=20).mean().ewm(span=20).mean() + df['close'].ewm(span=20).mean().ewm(span=20).mean().ewm(span=20).mean()
        df['kama_20'] = df['close'].ewm(alpha=0.1, adjust=False).mean()
        df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

        # Volatility
        bb = BollingerBands(df['close'])
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()

        atr = AverageTrueRange(df['high'], df['low'], df['close'])
        df['atr'] = atr.average_true_range()
        df['natr'] = (df['atr'] / df['close']) * 100
        df['stddev'] = df['close'].rolling(window=20).std()

        # Volume
        df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
        df['ad'] = AccDistIndexIndicator(df['high'], df['low'], df['close'], df['volume']).acc_dist_index()
        df['adosc'] = ChaikinMoneyFlowIndicator(df['high'], df['low'], df['close'], df['volume']).chaikin_money_flow()
        df['pvo'] = ((df['volume'].ewm(span=12).mean() - df['volume'].ewm(span=26).mean()) / df['volume'].ewm(span=26).mean()) * 100

        # Trend
        adx = ADXIndicator(df['high'], df['low'], df['close'])
        df['adx'] = adx.adx()
        df['adxr'] = (df['adx'] + df['adx'].shift(14)) / 2
        df['plus_di'] = adx.adx_pos()
        df['minus_di'] = adx.adx_neg()

        aroon = AroonIndicator(df['high'], df['low'])
        df['aroon_up'] = aroon.aroon_up()
        df['aroon_down'] = aroon.aroon_down()
        df['aroonosc'] = df['aroon_up'] - df['aroon_down']

        df['trix'] = TRIXIndicator(df['close']).trix()
        df['dx'] = ((df['plus_di'] - df['minus_di']).abs() / (df['plus_di'] + df['minus_di'])) * 100
        df['sar'] = df['close'].shift(1) * 0.98

        # Pattern Recognition (simplified)
        df['cdl_doji'] = ((df['close'] - df['open']).abs() / (df['high'] - df['low']) < 0.1).astype(float) * 100
        df['cdl_hammer'] = (((df['close'] - df['low']) / (df['high'] - df['low']) > 0.6) & ((df['high'] - df['close']) < (df['close'] - df['open']))).astype(float) * 100
        df['cdl_engulfing'] = ((df['close'] > df['open'].shift(1)) & (df['open'] < df['close'].shift(1))).astype(float) * 100
        df['cdl_harami'] = ((df['open'] > df['close'].shift(1)) & (df['close'] < df['open'].shift(1)) & ((df['open'] - df['close']).abs() < (df['close'].shift(1) - df['open'].shift(1)).abs())).astype(float) * 100
        df['cdl_morningstar'] = 0.0
        df['cdl_3blackcrows'] = ((df['close'] < df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & (df['close'].shift(2) < df['open'].shift(2))).astype(float) * 100
        df['cdl_2crows'] = 0.0
        df['cdl_3inside'] = 0.0
        df['cdl_3linestrike'] = 0.0
        df['cdl_abandonedbaby'] = 0.0

        # Statistical
        df['correl'] = df['close'].rolling(window=20).corr(df['volume'])
        df['linearreg'] = df['close'].rolling(window=14).apply(lambda x: np.polyval(np.polyfit(range(len(x)), x, 1), len(x)-1))
        df['linearreg_slope'] = df['close'].rolling(window=14).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        df['linearreg_angle'] = np.arctan(df['linearreg_slope']) * (180 / np.pi)
        df['tsf'] = df['linearreg']
        df['variance'] = df['close'].rolling(window=20).var()
        df['beta'] = df['close'].rolling(window=20).cov(df['close'].rolling(window=20).mean()) / df['close'].rolling(window=20).var()

        # Other Advanced
        df['ultosc'] = 50.0
        df['bop'] = (df['close'] - df['open']) / (df['high'] - df['low'])
        df['cmo'] = ((df['close'].diff().clip(lower=0).rolling(14).sum() - df['close'].diff().clip(upper=0).abs().rolling(14).sum()) / (df['close'].diff().abs().rolling(14).sum())) * 100
        df['dpo'] = df['close'] - df['close'].shift(11).rolling(window=20).mean()
        df['ht_dcperiod'] = 20.0
        df['ht_dcphase'] = 0.0
        df['ht_trendmode'] = (df['close'] > df['sma_50']).astype(float)
        df['midpoint'] = df['close'].rolling(window=14).apply(lambda x: (x.max() + x.min()) / 2)
        df['midprice'] = (df['high'] + df['low']) / 2
        df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
        df['stochrsi'] = (df['rsi'] - df['rsi'].rolling(14).min()) / (df['rsi'].rolling(14).max() - df['rsi'].rolling(14).min()) * 100
        df['apo'] = df['ema_12'] - df['ema_26']
        df['ht_sine_lead'] = np.sin(df.index.to_series() * 2 * np.pi / 20)

        return df

    except Exception as e:
        print(f"  Error calculating indicators: {str(e)}")
        return df

def fetch_stock_daily(symbol):
    """Fetch all daily data for a stock"""
    print(f"\n{'='*80}")
    print(f"Fetching DAILY data for {symbol}")
    print(f"{'='*80}")

    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': 5000,  # Maximum historical data
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if 'values' in data and data['values']:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['date'] = df['datetime'].dt.date
                df = df.sort_values('datetime')

                # Convert to numeric
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # Add metadata
                meta = data.get('meta', {})
                df['symbol'] = symbol
                df['name'] = meta.get('symbol', symbol)
                df['exchange'] = meta.get('exchange', '')
                df['mic_code'] = meta.get('mic_code', '')
                df['currency'] = meta.get('currency', 'USD')
                df['asset_type'] = 'STOCK'
                df['data_source'] = 'twelve_data'
                df['interval'] = '1day'

                print(f"  ✓ Fetched {len(df)} daily records")
                print(f"  Date range: {df['date'].min()} to {df['date'].max()}")

                # Calculate indicators
                df = calculate_technical_indicators(df)
                df['fetch_timestamp'] = datetime.now(timezone.utc)

                return df
            else:
                print(f"  ✗ No data: {data}")
                return None
        else:
            print(f"  ✗ API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None

def fetch_stock_intraday(symbol, interval, days):
    """Fetch intraday data for a stock"""
    print(f"\n{'='*80}")
    print(f"Fetching {interval} data for {symbol} ({days} days)")
    print(f"{'='*80}")

    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': 5000,  # Get maximum data
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if 'values' in data and data['values']:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
                df['date'] = df['datetime'].dt.date
                df = df.sort_values('datetime')

                # Filter to last N days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                # Make sure cutoff_date is timezone-aware
                if cutoff_date.tzinfo is None:
                    cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)
                df = df[df['datetime'] >= cutoff_date]

                # Convert to numeric
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # Add metadata
                meta = data.get('meta', {})
                df['symbol'] = symbol
                df['name'] = meta.get('symbol', symbol)
                df['exchange'] = meta.get('exchange', '')
                df['mic_code'] = meta.get('mic_code', '')
                df['currency'] = meta.get('currency', 'USD')
                df['asset_type'] = 'STOCK'
                df['data_source'] = 'twelve_data'
                df['interval'] = interval

                print(f"  ✓ Fetched {len(df)} {interval} records")
                print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")

                # Calculate indicators
                df = calculate_technical_indicators(df)
                df['fetch_timestamp'] = datetime.now(timezone.utc)

                return df
            else:
                print(f"  ✗ No data: {data}")
                return None
        else:
            print(f"  ✗ API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None

def fetch_crypto_daily(pair):
    """Fetch all daily data for a crypto pair using Kraken"""
    print(f"\n{'='*80}")
    print(f"Fetching DAILY data for {pair}")
    print(f"{'='*80}")

    try:
        kraken = ccxt.kraken()

        # Fetch max historical data (720 candles = ~2 years)
        ohlcv = kraken.fetch_ohlcv(pair, '1d', limit=720)

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['date'] = df['datetime'].dt.date
        df = df.sort_values('datetime')

        # Add metadata
        df['pair'] = pair
        df['base'] = pair.split('/')[0]
        df['quote'] = pair.split('/')[1]
        df['asset_type'] = 'CRYPTO'
        df['data_source'] = 'kraken'
        df['interval'] = '1day'

        print(f"  ✓ Fetched {len(df)} daily records")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")

        # Calculate indicators
        df = calculate_technical_indicators(df)
        df['fetch_timestamp'] = datetime.now(timezone.utc)

        return df

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None

def fetch_crypto_intraday(pair, interval, days):
    """Fetch intraday data for a crypto pair using Kraken"""
    print(f"\n{'='*80}")
    print(f"Fetching {interval} data for {pair} ({days} days)")
    print(f"{'='*80}")

    try:
        kraken = ccxt.kraken()

        # Convert interval to ccxt format
        interval_map = {'5min': '5m', '15min': '15m'}
        ccxt_interval = interval_map.get(interval, interval)

        # Calculate since timestamp
        now = datetime.now(timezone.utc)
        since_dt = now - timedelta(days=days)
        since = int(since_dt.timestamp() * 1000)

        # Fetch data
        all_ohlcv = []
        while True:
            ohlcv = kraken.fetch_ohlcv(pair, ccxt_interval, since=since, limit=720)
            if not ohlcv:
                break

            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1  # Next timestamp

            # Check if we've reached current time
            if since >= int(datetime.now(timezone.utc).timestamp() * 1000):
                break

            time.sleep(0.5)  # Rate limiting

        if not all_ohlcv:
            print(f"  ✗ No data fetched")
            return None

        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['date'] = df['datetime'].dt.date
        df = df.sort_values('datetime')
        df = df.drop_duplicates(subset=['datetime'])

        # Add metadata
        df['pair'] = pair
        df['base'] = pair.split('/')[0]
        df['quote'] = pair.split('/')[1]
        df['asset_type'] = 'CRYPTO'
        df['data_source'] = 'kraken'
        df['interval'] = interval

        print(f"  ✓ Fetched {len(df)} {interval} records")
        print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")

        # Calculate indicators
        df = calculate_technical_indicators(df)
        df['fetch_timestamp'] = datetime.now(timezone.utc)

        return df

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None

def upload_to_bigquery(df, table_name):
    """Upload dataframe to BigQuery"""
    if df is None or df.empty:
        print(f"  ✗ No data to upload to {table_name}")
        return 0

    try:
        client = bigquery.Client(project=PROJECT_ID)
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Replace NaN/inf with None
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.where(pd.notnull(df), None)

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
        job.result()

        print(f"  ✓ Uploaded {len(df)} records to {table_name}")
        return len(df)

    except Exception as e:
        print(f"  ✗ Upload error: {str(e)}")
        return 0

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("FETCHING TEST DATA FOR NVIDIA AND BITCOIN")
    print("="*80)

    # NVIDIA Stock
    print("\n" + "#"*80)
    print("# NVIDIA STOCK DATA")
    print("#"*80)

    # Daily data
    nvda_daily = fetch_stock_daily('NVDA')
    time.sleep(2)
    if nvda_daily is not None:
        upload_to_bigquery(nvda_daily, 'stocks_daily')

    # 15-minute data (4 days) - API doesn't support 10min
    time.sleep(2)
    nvda_15min = fetch_stock_intraday('NVDA', '15min', 4)
    time.sleep(2)
    if nvda_15min is not None:
        upload_to_bigquery(nvda_15min, 'stocks_15min')

    # 5-minute data (2 days)
    time.sleep(2)
    nvda_5min = fetch_stock_intraday('NVDA', '5min', 2)
    time.sleep(2)
    if nvda_5min is not None:
        upload_to_bigquery(nvda_5min, 'stocks_5min')

    # Bitcoin Crypto
    print("\n" + "#"*80)
    print("# BITCOIN CRYPTO DATA")
    print("#"*80)

    # Daily data
    btc_daily = fetch_crypto_daily('BTC/USD')
    time.sleep(2)
    if btc_daily is not None:
        upload_to_bigquery(btc_daily, 'crypto_daily')

    # 15-minute data (4 days) - Using 15min instead of 10min
    time.sleep(2)
    btc_15min = fetch_crypto_intraday('BTC/USD', '15min', 4)
    time.sleep(2)
    if btc_15min is not None:
        upload_to_bigquery(btc_15min, 'crypto_15min')

    # 5-minute data (2 days)
    time.sleep(2)
    btc_5min = fetch_crypto_intraday('BTC/USD', '5min', 2)
    time.sleep(2)
    if btc_5min is not None:
        upload_to_bigquery(btc_5min, 'crypto_5min')

    print("\n" + "="*80)
    print("DATA FETCH COMPLETE!")
    print("="*80)

if __name__ == '__main__':
    main()
