"""
TwelveData Max Quota Fetcher - Cloud Function
Runs daily to maximize $229 Pro plan quota (2M records/day)
"""
import functions_framework
from google.cloud import bigquery
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import time
import concurrent.futures

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# All symbols to fetch daily (~2M records)
SYMBOLS_CONFIG = {
    'stocks_daily': {
        'symbols': [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH',
            'LLY', 'JPM', 'XOM', 'V', 'JNJ', 'AVGO', 'PG', 'MA', 'HD', 'COST',
            'MRK', 'ABBV', 'CVX', 'CRM', 'KO', 'PEP', 'AMD', 'ADBE', 'WMT', 'MCD',
            'CSCO', 'BAC', 'ACN', 'NFLX', 'TMO', 'LIN', 'ORCL', 'ABT', 'DHR', 'INTC',
            'DIS', 'PM', 'CMCSA', 'VZ', 'WFC', 'TXN', 'NKE', 'COP', 'INTU', 'RTX',
            'NEE', 'QCOM', 'HON', 'IBM', 'AMGN', 'UNP', 'LOW', 'SPGI', 'CAT', 'GE',
            'BA', 'PLD', 'SBUX', 'DE', 'ELV', 'AMAT', 'BMY', 'GS', 'BLK', 'MDLZ',
            'ADI', 'ISRG', 'GILD', 'MMC', 'ADP', 'TJX', 'VRTX', 'AMT', 'SYK', 'REGN',
            'LMT', 'BKNG', 'MO', 'ETN', 'LRCX', 'CB', 'CI', 'PGR', 'C', 'ZTS',
            'PANW', 'BDX', 'SCHW', 'EOG', 'SO', 'MU', 'CME', 'NOC', 'DUK', 'SLB',
            'PNC', 'ICE', 'MCK', 'CL', 'SNPS', 'BSX', 'CDNS', 'AON', 'ITW', 'USB',
            'CMG', 'WM', 'EQIX', 'SHW', 'FCX', 'ORLY', 'APD', 'KLAC', 'MSI', 'GD',
            'MPC', 'TGT', 'EMR', 'PSX', 'MMM', 'PH', 'AJG', 'ROP', 'CARR', 'NSC',
            'PCAR', 'MAR', 'GM', 'CTAS', 'HLT', 'NEM', 'AZO', 'WELL', 'TRV', 'MCHP',
            'AIG', 'FDX', 'OXY', 'ECL', 'F', 'AFL', 'TEL', 'CPRT', 'DXCM', 'KMB',
            'FTNT', 'SRE', 'PAYX', 'D', 'AEP', 'A', 'PSA', 'MSCI', 'O', 'DHI',
            'BK', 'IDXX', 'GIS', 'CCI', 'ROST', 'KDP', 'JCI', 'MNST', 'FAST', 'KMI',
            'YUM', 'CTVA', 'AME', 'AMP', 'ODFL', 'EXC', 'GWW', 'CMI', 'LHX', 'ALL',
            'VRSK', 'OTIS', 'IQV', 'HAL', 'XEL', 'PCG', 'GEHC', 'CTSH', 'IT', 'HUM',
            'DVN', 'MLM', 'KR', 'EW', 'WEC', 'ED', 'VMC', 'FANG', 'DD', 'PYPL',
            'NOW', 'UBER', 'ABNB', 'SQ', 'SHOP', 'SNOW', 'PLTR', 'COIN', 'RIVN',
            'LCID', 'NIO', 'XPEV', 'LI', 'DKNG', 'RBLX', 'U', 'CRWD', 'ZS', 'OKTA',
            'DDOG', 'NET', 'MDB', 'TWLO', 'DOCU', 'ZM', 'SPOT', 'PINS', 'SNAP', 'TTD',
            'AFRM', 'PATH', 'BILL', 'HUBS', 'ESTC', 'MNDY', 'GTLB', 'S', 'IOT', 'AI'
        ],
        'interval': '1day',
        'outputsize': 5000
    },
    'stocks_hourly': {
        'symbols': [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH',
            'LLY', 'JPM', 'XOM', 'V', 'JNJ', 'AVGO', 'PG', 'MA', 'HD', 'COST',
            'MRK', 'ABBV', 'CVX', 'CRM', 'KO', 'PEP', 'AMD', 'ADBE', 'WMT', 'MCD',
            'CSCO', 'BAC', 'ACN', 'NFLX', 'TMO', 'LIN', 'ORCL', 'ABT', 'DHR', 'INTC',
            'DIS', 'PM', 'CMCSA', 'VZ', 'WFC', 'TXN', 'NKE', 'COP', 'INTU', 'RTX',
            'NEE', 'QCOM', 'HON', 'IBM', 'AMGN', 'UNP'
        ],
        'interval': '1h',
        'outputsize': 5000
    },
    'crypto_daily': {
        'symbols': [
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
            'AVAX/USD', 'LINK/USD', 'DOT/USD', 'SHIB/USD', 'TRX/USD', 'UNI/USD', 'ATOM/USD',
            'LTC/USD', 'NEAR/USD', 'APT/USD', 'FIL/USD', 'ARB/USD', 'XMR/USD',
            'BCH/USD', 'XLM/USD', 'ETC/USD', 'HBAR/USD', 'VET/USD', 'ALGO/USD',
            'SAND/USD', 'MANA/USD', 'AAVE/USD', 'THETA/USD', 'XTZ/USD', 'AXS/USD',
            'SNX/USD', 'COMP/USD', 'ZEC/USD', 'DASH/USD', 'ENJ/USD', 'BAT/USD',
            'CRV/USD', 'LRC/USD', 'SUSHI/USD', 'YFI/USD', '1INCH/USD', 'GRT/USD',
            'CHZ/USD', 'IOTA/USD', 'KAVA/USD', 'CELO/USD', 'ZRX/USD', 'ANKR/USD',
            'GALA/USD', 'IMX/USD', 'LDO/USD', 'RPL/USD', 'OP/USD', 'INJ/USD',
            'RUNE/USD', 'KSM/USD', 'FLOW/USD', 'EGLD/USD', 'NEO/USD', 'WAVES/USD',
            'QTUM/USD', 'ICX/USD', 'ONT/USD', 'ZIL/USD', 'STORJ/USD', 'SKL/USD'
        ],
        'interval': '1day',
        'outputsize': 5000
    },
    'crypto_hourly': {
        'symbols': [
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
            'AVAX/USD', 'LINK/USD', 'DOT/USD', 'SHIB/USD', 'TRX/USD', 'UNI/USD', 'ATOM/USD',
            'LTC/USD', 'NEAR/USD', 'APT/USD', 'FIL/USD', 'ARB/USD', 'XMR/USD',
            'BCH/USD', 'XLM/USD', 'ETC/USD', 'HBAR/USD', 'VET/USD', 'ALGO/USD',
            'SAND/USD', 'MANA/USD'
        ],
        'interval': '1h',
        'outputsize': 5000
    },
    'etf_daily': {
        'symbols': [
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
            'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLY', 'XLP', 'XLB', 'XLU', 'XLRE',
            'GLD', 'SLV', 'USO', 'UNG', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'JNK',
            'VNQ', 'ARKK', 'ARKG', 'ARKW', 'ARKF', 'SMH', 'XBI', 'IBB', 'KRE', 'XHB'
        ],
        'interval': '1day',
        'outputsize': 5000
    },
    'etf_hourly': {
        'symbols': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'XLF', 'XLE', 'XLK', 'GLD', 'TLT'],
        'interval': '1h',
        'outputsize': 5000
    },
    'forex_daily': {
        'symbols': [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
            'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'EUR/AUD', 'EUR/CAD', 'EUR/NZD',
            'GBP/CHF', 'GBP/AUD', 'GBP/CAD', 'GBP/NZD', 'AUD/JPY', 'AUD/NZD',
            'AUD/CAD', 'CAD/JPY', 'NZD/JPY', 'CHF/JPY', 'USD/MXN', 'USD/ZAR',
            'USD/TRY', 'USD/SGD', 'USD/HKD', 'USD/SEK'
        ],
        'interval': '1day',
        'outputsize': 5000
    },
    'index_daily': {
        'symbols': ['SPX', 'NDX', 'FTSE', 'DAX', 'CAC', 'HSI', 'IBEX', 'SMI', 'AEX'],
        'interval': '1day',
        'outputsize': 5000
    }
}


def fetch_symbol(symbol, interval, outputsize):
    """Fetch data for a single symbol"""
    try:
        url = f"{BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            return None

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['interval'] = interval

        # Convert numeric columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def calculate_indicators(df):
    """Calculate technical indicators"""
    if df is None or len(df) < 30:
        return df

    df = df.sort_values('datetime').copy()

    # Ensure volume exists
    if 'volume' not in df.columns:
        df['volume'] = 0

    close = df['close']
    high = df['high']
    low = df['low']

    # SMAs
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean() if len(df) >= 50 else np.nan
    df['sma_200'] = close.rolling(200).mean() if len(df) >= 200 else np.nan

    # EMAs
    df['ema_12'] = close.ewm(span=12).mean()
    df['ema_26'] = close.ewm(span=26).mean()

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['rsi_14'] = 100 - (100 / (1 + rs))

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bb_middle'] = df['sma_20']
    std = close.rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (2 * std)
    df['bb_lower'] = df['bb_middle'] - (2 * std)

    # ATR
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(14).mean()

    # ADX
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr = tr.ewm(span=14).mean()
    df['plus_di'] = 100 * (plus_dm.ewm(span=14).mean() / atr)
    df['minus_di'] = 100 * (minus_dm.ewm(span=14).mean() / atr)
    dx = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = dx.ewm(span=14).mean()

    # Growth Score
    df['growth_score'] = 0
    df.loc[(df['rsi_14'] >= 50) & (df['rsi_14'] <= 70), 'growth_score'] += 25
    df.loc[df['macd_hist'] > 0, 'growth_score'] += 25
    df.loc[df['adx'] > 25, 'growth_score'] += 25
    if 'sma_200' in df.columns:
        df.loc[df['close'] > df['sma_200'], 'growth_score'] += 25

    return df


@functions_framework.http
def max_quota_fetcher(request):
    """Main Cloud Function entry point"""
    start_time = datetime.now(timezone.utc)
    print(f"Starting max quota fetch at {start_time}")

    all_data = []
    total_records = 0

    for config_name, config in SYMBOLS_CONFIG.items():
        print(f"\nProcessing {config_name}...")
        symbols = config['symbols']
        interval = config['interval']
        outputsize = config['outputsize']

        for symbol in symbols:
            df = fetch_symbol(symbol, interval, outputsize)
            if df is not None and len(df) > 0:
                # Determine asset type
                if 'crypto' in config_name:
                    df['asset_type'] = 'CRYPTO'
                elif 'etf' in config_name:
                    df['asset_type'] = 'ETF'
                elif 'forex' in config_name:
                    df['asset_type'] = 'FOREX'
                elif 'index' in config_name:
                    df['asset_type'] = 'INDEX'
                else:
                    df['asset_type'] = 'STOCK'

                # Calculate indicators
                df = calculate_indicators(df)
                all_data.append(df)
                total_records += len(df)
                print(f"  {symbol}: {len(df)} records")

            time.sleep(0.7)  # Rate limiting

    # Combine and upload to BigQuery
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df['fetch_timestamp'] = datetime.now(timezone.utc)

        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{DATASET_ID}.twelvedata_max_quota"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True
        )

        job = client.load_table_from_dataframe(final_df, table_id, job_config=job_config)
        job.result()

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds() / 60

        result = {
            'status': 'success',
            'total_records': total_records,
            'quota_used': f"{(total_records / 2000000 * 100):.1f}%",
            'duration_minutes': round(duration, 1),
            'timestamp': end_time.isoformat()
        }

        print(f"\nCompleted: {total_records:,} records ({result['quota_used']} of quota)")
        return result, 200

    return {'status': 'error', 'message': 'No data fetched'}, 500
