"""
Continue Historical Data Fetch - Use Remaining API Quota
We have 630 API calls remaining (used 170 of 800)
Adding more symbols to maximize daily quota utilization
"""
import requests
import time
import sys
import io
import warnings
import json
import os
from datetime import datetime, timezone
from google.cloud import bigquery
import pandas as pd
import numpy as np

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'

# Rate limiting: 8 calls/minute = 7.5 seconds between calls
RATE_LIMIT_SECONDS = 8

# Progress file
PROGRESS_FILE = 'historical_fetch_progress_v3.json'

# Additional symbols - focusing on quality stocks and popular assets
# Target: ~600 more API calls
SYMBOLS = {
    'stocks': {
        'table': 'stocks_historical_daily',
        'symbols': [
            # Additional Mega Caps and Popular Stocks
            'BX', 'MS', 'GS', 'SCHW', 'C', 'BAC', 'WFC', 'USB', 'PNC', 'TFC',
            'AIG', 'MET', 'PRU', 'ALL', 'TRV', 'PGR', 'CB', 'AON', 'MSCI', 'MCO',
            'T', 'TMUS', 'NFLX', 'DIS', 'CMCSA', 'CHTR', 'ROKU', 'SPOT', 'WBD', 'PARA',
            'PEP', 'KO', 'MNST', 'STZ', 'TAP', 'BUD', 'DEO', 'SAM', 'FIZZ', 'COKE',
            'PFE', 'LLY', 'BMY', 'AMGN', 'BIIB', 'MRNA', 'BNTX', 'JAZZ', 'SGEN', 'TECH',
            'CVS', 'WBA', 'CI', 'HUM', 'CNC', 'ANTM', 'ELV', 'MOH', 'UHS', 'HCA',
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'VLO', 'PSX', 'HES',
            'LIN', 'APD', 'ECL', 'SHW', 'PPG', 'DD', 'DOW', 'LYB', 'CE', 'EMN',
            'UPS', 'FDX', 'JBHT', 'CHRW', 'EXPD', 'KNX', 'XPO', 'ODFL', 'SAIA', 'JBLU',
            'DE', 'CAT', 'CMI', 'PH', 'ETN', 'EMR', 'ITW', 'ROK', 'DOV', 'FLS',
            # Tech and Software
            'ADBE', 'CRM', 'NOW', 'INTU', 'WDAY', 'TEAM', 'HUBS', 'TWLO', 'ZM', 'DOCU',
            'PANW', 'FTNT', 'ZS', 'CRWD', 'S', 'NET', 'DDOG', 'CFLT', 'TENB', 'QLYS',
            'UBER', 'LYFT', 'DASH', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'PCLN', 'MMYT', 'TCOM',
            'SHOP', 'ETSY', 'W', 'CHWY', 'CHEWY', 'PINS', 'SNAP', 'TWTR', 'FB', 'MTCH',
            # Semiconductors
            'NVDA', 'AMD', 'INTC', 'TSM', 'AVGO', 'TXN', 'QCOM', 'AMAT', 'LRCX', 'KLAC',
            'ADI', 'MCHP', 'NXPI', 'MU', 'WDC', 'STX', 'SNPS', 'CDNS', 'MPWR', 'ENTG',
            # Industrials
            'BA', 'GE', 'HON', 'MMM', 'LMT', 'RTX', 'NOC', 'GD', 'LHX', 'TXT',
            'UNP', 'CSX', 'NSC', 'CP', 'CNI', 'KSU', 'RAIL', 'UNH', 'JBHT', 'CHRW',
            # Consumer
            'AMZN', 'WMT', 'COST', 'TGT', 'HD', 'LOW', 'TJX', 'ROST', 'DG', 'DLTR',
            'MCD', 'SBUX', 'YUM', 'QSR', 'CMG', 'DPZ', 'WEN', 'JACK', 'DRI', 'EAT',
            # REITs
            'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'WELL', 'O', 'SPG', 'AVB',
            'EQR', 'UDR', 'ESS', 'MAA', 'CPT', 'AIV', 'BXP', 'VTR', 'PEAK', 'IRM',
            # Utilities
            'NEE', 'DUK', 'SO', 'D', 'EXC', 'AEP', 'SRE', 'PCG', 'ED', 'XEL',
            'WEC', 'ES', 'ETR', 'FE', 'AES', 'PPL', 'CMS', 'DTE', 'NI', 'LNT',
            # Materials
            'LIN', 'APD', 'SHW', 'ECL', 'FCX', 'NEM', 'GOLD', 'NUE', 'STLD', 'CLF',
            'AA', 'CENX', 'RS', 'VMC', 'MLM', 'MDU', 'SUM', 'CX', 'MTZ', 'HUN',
            # Biotech
            'GILD', 'VRTX', 'REGN', 'BIIB', 'ALXN', 'ILMN', 'INCY', 'BMRN', 'SGEN', 'EXAS',
            'NBIX', 'SRPT', 'BLUE', 'ARWR', 'IONS', 'FOLD', 'SAGE', 'RGNX', 'ALNY', 'RARE',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'OXY', 'HAL', 'DVN', 'FANG',
            'MRO', 'APA', 'CTRA', 'OVV', 'NOG', 'CLR', 'MTDR', 'AR', 'CHRD', 'RRC'
        ]
    },
    'cryptos': {
        'table': 'cryptos_historical_daily',
        'symbols': [
            # Additional Layer 1s and DeFi
            'MATIC/USD', 'FTM/USD', 'NEAR/USD', 'ROSE/USD', 'ONE/USD', 'HBAR/USD',
            'THETA/USD', 'WAVES/USD', 'QTUM/USD', 'ZIL/USD', 'ICX/USD', 'IOTA/USD',
            # More DeFi
            'CAKE/USD', '1INCH/USD', 'AAVE/USD', 'MKR/USD', 'COMP/USD', 'SNX/USD',
            'CRV/USD', 'BAL/USD', 'YFI/USD', 'SUSHI/USD', 'LDO/USD', 'RPL/USD',
            # Gaming/Metaverse
            'AXS/USD', 'SAND/USD', 'MANA/USD', 'ENJ/USD', 'GALA/USD', 'IMX/USD',
            'APE/USD', 'GMT/USD', 'MAGIC/USD', 'ILV/USD', 'ALICE/USD', 'TLM/USD',
            # Infrastructure
            'GRT/USD', 'FIL/USD', 'AR/USD', 'STX/USD', 'STORJ/USD', 'OCEAN/USD',
            'RNDR/USD', 'LPT/USD', 'BAT/USD', 'GLM/USD', 'POKT/USD', 'ANKR/USD',
            # Derivatives/Perps
            'GMX/USD', 'GNS/USD', 'DYDX/USD', 'PERP/USD', 'VELO/USD', 'SYN/USD'
        ]
    },
    'etfs': {
        'table': 'etfs_historical_daily',
        'symbols': [
            # Sector Rotation
            'XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY',
            # Semiconductors
            'SMH', 'SOXX', 'PSI', 'SOXL', 'SOXS', 'USD', 'FNGS', 'IGV', 'QTEC', 'XSD',
            # Tech
            'QQQ', 'QQQM', 'TQQQ', 'SQQQ', 'VGT', 'IYW', 'FTEC', 'TECL', 'FIVG', 'IPAY',
            # China/EM
            'FXI', 'MCHI', 'KWEB', 'YINN', 'YANG', 'EEM', 'VWO', 'IEMG', 'SCHE', 'DEM',
            # Crypto
            'BITO', 'BITI', 'GBTC', 'ETHE', 'GDLC', 'BLOK', 'LEGR', 'BITQ', 'KOIN', 'DAPP',
            # Bonds
            'TLT', 'IEF', 'SHY', 'AGG', 'BND', 'LQD', 'HYG', 'JNK', 'EMB', 'TIP',
            # Commodities
            'GLD', 'SLV', 'GDX', 'GDXJ', 'USO', 'UNG', 'DBA', 'DBC', 'PDBC', 'GSG',
            # International
            'EFA', 'VEA', 'IEFA', 'EWJ', 'EWZ', 'EWY', 'EWW', 'EWC', 'EWA', 'EWU',
            # Smart Beta
            'MTUM', 'QUAL', 'SIZE', 'VLUE', 'USMV', 'SPLV', 'SPHD', 'VIG', 'NOBL', 'DGRO',
            # Thematic
            'ARKK', 'ARKG', 'ARKF', 'ARKQ', 'ARKW', 'MOON', 'NERD', 'HERO', 'ESPO', 'GAMR'
        ]
    },
    'forex': {
        'table': 'forex_historical_daily',
        'symbols': [
            # Additional Major Crosses
            'EUR/NZD', 'GBP/NZD', 'AUD/NZD', 'NZD/JPY', 'NZD/CAD', 'NZD/CHF',
            'GBP/CHF', 'AUD/CAD', 'CAD/JPY', 'CHF/JPY', 'EUR/SGD', 'GBP/SGD',
            # Exotic Pairs
            'USD/TRY', 'USD/BRL', 'USD/RUB', 'USD/PLN', 'USD/SEK', 'USD/NOK',
            'USD/DKK', 'USD/CZK', 'USD/HUF', 'USD/ILS', 'USD/CNY', 'USD/KRW',
            'USD/THB', 'USD/PHP', 'USD/IDR', 'USD/MYR', 'USD/VND', 'USD/TWD',
            # Cross Exotics
            'EUR/TRY', 'EUR/ZAR', 'EUR/MXN', 'EUR/PLN', 'EUR/HUF', 'EUR/CZK',
            'GBP/TRY', 'GBP/ZAR', 'GBP/MXN', 'GBP/PLN', 'GBP/HUF', 'GBP/CZK'
        ]
    },
    'indices': {
        'table': 'indices_historical_daily',
        'symbols': [
            # US Indices
            'SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'OEX', 'MID', 'SOX', 'TRAN', 'UTIL',
            # European
            'FTSE', 'DAX', 'CAC', 'IBEX', 'FTSEMIB', 'AEX', 'SMI', 'OMX', 'BEL20', 'PSI20',
            # Asian
            'NIKKEI', 'HSI', 'SSE', 'KOSPI', 'TWSE', 'STI', 'SET', 'KLSE', 'JCI', 'PSEI',
            # Pacific
            'ASX', 'NZX50', 'SENSEX', 'NIFTY', 'BSE', 'NSEBANK', 'NIFTYIT', 'NIFTYPHARMA',
            # LATAM
            'BOVESPA', 'IPC', 'MERVAL', 'IPSA', 'IGBC', 'IGBVL', 'COLCAP', 'SPBLPGPT'
        ]
    },
    'commodities': {
        'table': 'commodities_historical_daily',
        'symbols': [
            # Precious Metals
            'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD', 'XRH/USD', 'XIR/USD', 'XRU/USD', 'XOS/USD',
            # Energy
            'CL', 'BZ', 'NG', 'HO', 'RB', 'ULSD', 'RBOB', 'WTI', 'BRENT', 'CRUDE',
            # Grains
            'ZC', 'ZS', 'ZW', 'ZM', 'ZL', 'ZO', 'ZR', 'KE', 'MW', 'MWE',
            # Softs
            'KC', 'CC', 'SB', 'CT', 'OJ', 'LBS', 'DC', 'RC', 'RSS', 'FCOJ',
            # Meats
            'LC', 'LH', 'GF', 'HE', 'FC', 'FD', 'DA', 'DL', 'PB', 'PRK',
            # Metals
            'HG', 'ALI', 'ZNC', 'NI', 'PB', 'SN', 'CO', 'MO', 'TI', 'MN'
        ]
    }
}

def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'api_calls': 0, 'last_run': None}

def save_progress(progress):
    """Save progress to file"""
    progress['last_run'] = datetime.now(timezone.utc).isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def calculate_all_indicators(df):
    """Calculate ALL 31 missing technical indicators from Phase 1 Methodology"""

    # Ensure we have enough data
    if len(df) < 200:
        print(f"    Warning: Only {len(df)} rows, some indicators may be inaccurate")

    # Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)

    # PRIORITY 1 INDICATORS

    # 1. Weekly log return
    df['weekly_log_return'] = np.log(df['close'] / df['close'].shift(5))

    # 2-4. Multi-week returns
    df['return_2w'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10)
    df['return_4w'] = (df['close'] - df['close'].shift(20)) / df['close'].shift(20)
    df['return_8w'] = (df['close'] - df['close'].shift(40)) / df['close'].shift(40)

    # 5-6. RSI slope and z-score (need RSI first)
    if 'rsi' not in df.columns:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

    df['rsi_slope'] = df['rsi'].diff(5)
    df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(20).mean()) / df['rsi'].rolling(20).std()

    # 7-8. RSI flags
    df['rsi_overbought_flag'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold_flag'] = (df['rsi'] < 30).astype(int)

    # 9. MACD cross flag (need MACD first)
    if 'macd' not in df.columns or 'macd_signal' not in df.columns:
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    df['macd_cross_flag'] = ((df['macd'] > df['macd_signal']) &
                             (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)

    # 10-11. EMA 12 and 26
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # 12-16. Price vs Moving Averages
    if 'sma_20' not in df.columns:
        df['sma_20'] = df['close'].rolling(window=20).mean()
    if 'sma_50' not in df.columns:
        df['sma_50'] = df['close'].rolling(window=50).mean()
    if 'sma_200' not in df.columns:
        df['sma_200'] = df['close'].rolling(window=200).mean()

    df['close_vs_sma20_pct'] = (df['close'] - df['sma_20']) / df['sma_20']
    df['close_vs_sma50_pct'] = (df['close'] - df['sma_50']) / df['sma_50']
    df['close_vs_sma200_pct'] = (df['close'] - df['sma_200']) / df['sma_200']

    ema_20 = df['close'].ewm(span=20, adjust=False).mean()
    ema_50 = df['close'].ewm(span=50, adjust=False).mean()

    df['close_vs_ema20_pct'] = (df['close'] - ema_20) / ema_20
    df['close_vs_ema50_pct'] = (df['close'] - ema_50) / ema_50

    # 17-18. EMA slopes
    df['ema_slope_20'] = ema_20.diff(5)
    df['ema_slope_50'] = ema_50.diff(5)

    # PRIORITY 2 INDICATORS

    # 19-21. ATR metrics (need ATR first)
    if 'atr' not in df.columns:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()

    df['atr_pct'] = df['atr'] / df['close']
    df['atr_slope'] = df['atr'].diff(5)
    df['atr_zscore'] = (df['atr'] - df['atr'].rolling(20).mean()) / df['atr'].rolling(20).std()

    # 22-23. Volume metrics
    df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

    # 24-27. ADX and Directional Indicators
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    if 'atr' in df.columns:
        df['plus_di'] = 100 * (plus_dm.rolling(14).mean() / df['atr'])
        df['minus_di'] = 100 * (minus_dm.rolling(14).mean() / df['atr'])
        df['dx'] = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        df['adx'] = df['dx'].rolling(14).mean()
    else:
        df['plus_di'] = 0
        df['minus_di'] = 0
        df['dx'] = 0
        df['adx'] = 0

    # 28-31. Candle patterns
    df['candle_body_pct'] = np.abs(df['close'] - df['open']) / (df['high'] - df['low'])
    df['candle_range_pct'] = (df['high'] - df['low']) / df['close']
    df['upper_shadow_pct'] = (df['high'] - df[['open', 'close']].max(axis=1)) / (df['high'] - df['low'])
    df['lower_shadow_pct'] = (df[['open', 'close']].min(axis=1) - df['low']) / (df['high'] - df['low'])

    # Replace inf/nan with 0
    df = df.replace([np.inf, -np.inf], 0)
    df = df.fillna(0)

    return df

def fetch_and_upload(asset_type, symbol, table_name, client):
    """Fetch historical data and upload to BigQuery"""
    try:
        # Fetch 5000 days of data
        url = f"https://api.twelvedata.com/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': 5000,
            'apikey': TWELVE_DATA_API_KEY
        }

        print(f"    Fetching {symbol}...")
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            print(f"    ✗ {symbol}: {data.get('message', 'No data')}")
            return 0

        # Convert to DataFrame
        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])

        # Add symbol and asset type
        df['symbol'] = symbol
        df['asset_type'] = asset_type

        # Calculate all technical indicators
        df = calculate_all_indicators(df)

        # Upload to BigQuery
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
            ]
        )

        job = client.load_table_from_dataframe(
            df,
            f"{PROJECT_ID}.{DATASET_ID}.{table_name}",
            job_config=job_config
        )
        job.result()

        print(f"    ✓ {symbol}: {len(df)} records uploaded")
        return len(df)

    except Exception as e:
        print(f"    ✗ {symbol}: Error - {str(e)[:100]}")
        return 0

def main():
    """Main execution"""
    print("="*70)
    print("CONTINUE HISTORICAL DATA FETCH - PHASE 3")
    print(f"Target: Use remaining ~630 API calls")
    print(f"Started: {datetime.now()}")
    print("="*70)
    print()

    # Initialize
    client = bigquery.Client(project=PROJECT_ID)
    progress = load_progress()

    total_records = 0
    total_symbols = 0
    api_calls_today = progress.get('api_calls', 0)
    max_calls = 800

    print(f"API Calls Used: {api_calls_today}/{max_calls}")
    print(f"API Calls Remaining: {max_calls - api_calls_today}")
    print()

    # Process each asset type
    for asset_type, config in SYMBOLS.items():
        table_name = config['table']
        symbols = config['symbols']

        print(f"\n{'='*70}")
        print(f"Processing: {asset_type.upper()} ({len(symbols)} symbols)")
        print(f"Table: {table_name}")
        print(f"{'='*70}\n")

        for i, symbol in enumerate(symbols, 1):
            # Check if already processed
            key = f"{asset_type}:{symbol}"
            if key in progress['completed']:
                print(f"  [{i}/{len(symbols)}] {symbol} - Already processed")
                continue

            # Check API limit
            if api_calls_today >= max_calls:
                print(f"\n⚠ API limit reached ({max_calls} calls)")
                break

            print(f"  [{i}/{len(symbols)}] Processing {symbol}...")

            # Fetch and upload
            records = fetch_and_upload(asset_type, symbol, table_name, client)

            if records > 0:
                total_records += records
                total_symbols += 1
                progress['completed'].append(key)
                api_calls_today += 1
                progress['api_calls'] = api_calls_today
                save_progress(progress)

            # Rate limiting
            time.sleep(RATE_LIMIT_SECONDS)

        if api_calls_today >= max_calls:
            break

    # Summary
    print("\n" + "="*70)
    print("FETCH COMPLETE")
    print("="*70)
    print(f"Symbols processed: {total_symbols}")
    print(f"Records uploaded: {total_records:,}")
    print(f"API calls used today: {api_calls_today}/{max_calls}")
    print(f"Finished: {datetime.now()}")
    print("="*70)

if __name__ == "__main__":
    main()
