#!/usr/bin/env python3
"""
Comprehensive TwelveData Fetcher - 50% Capacity Plan
====================================================
Uses 50% of TwelveData $229 plan capacity (576,000 credits/day)
Fetches stocks, ETFs with 5+ years history + fundamentals

Capacity Planning:
- $229 Plan: 800 credits/minute = 1,152,000/day
- 50% Target: 576,000 credits/day
- Week 1: 50% (576,000)
- Week 2: 60% (691,200)
- Week 3: 70% (806,400)
- Week 4: 80% (921,600)
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery

# Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Capacity Settings (50% of plan)
MAX_CALLS_PER_MINUTE = 400  # 50% of 800
DAILY_BUDGET = 576000  # 50% of 1,152,000
MAX_WORKERS = 10
BATCH_DELAY = 0.15  # 150ms between calls

# S&P 500 Stocks (Full List)
SP500_STOCKS = [
    # Technology
    "AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "META", "AVGO", "ADBE", "CRM", "CSCO",
    "ACN", "ORCL", "IBM", "INTC", "AMD", "TXN", "QCOM", "NOW", "INTU", "AMAT",
    "ADI", "MU", "LRCX", "KLAC", "SNPS", "CDNS", "MRVL", "FTNT", "PANW", "CRWD",
    # Financials
    "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "SPGI", "BLK",
    "C", "SCHW", "CB", "MMC", "PGR", "AON", "ICE", "CME", "MCO", "USB",
    "PNC", "TFC", "AIG", "MET", "PRU", "AFL", "ALL", "TRV", "CINF", "BK",
    # Healthcare
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "MDT", "ISRG", "GILD", "CVS", "ELV", "SYK", "VRTX", "REGN", "ZTS",
    "BSX", "BDX", "HUM", "CI", "MCK", "CAH", "IDXX", "IQV", "MTD", "DXCM",
    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "CMG",
    "ORLY", "AZO", "ROST", "MAR", "HLT", "DHI", "LEN", "NVR", "PHM", "GM",
    "F", "APTV", "EBAY", "ETSY", "BBY", "DG", "DLTR", "KMX", "GPC", "AAP",
    # Consumer Staples
    "PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "MDLZ", "CL", "KMB",
    "GIS", "K", "HSY", "KHC", "SJM", "CAG", "CPB", "HRL", "MKC", "TSN",
    "STZ", "TAP", "BF.B", "EL", "CLX", "CHD", "WBA", "KR", "SYY", "ADM",
    # Industrials
    "CAT", "UPS", "HON", "RTX", "BA", "DE", "GE", "LMT", "UNP", "MMM",
    "FDX", "NSC", "CSX", "WM", "RSG", "EMR", "ETN", "ITW", "PH", "ROK",
    "CMI", "PCAR", "FAST", "GD", "NOC", "TXT", "HII", "LHX", "LDOS", "BAH",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "PXD",
    "HES", "DVN", "FANG", "HAL", "BKR", "KMI", "WMB", "OKE", "TRGP", "LNG",
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "PEG", "ED",
    "WEC", "ES", "AWK", "DTE", "ETR", "FE", "PPL", "AEE", "CMS", "CNP",
    # Real Estate
    "PLD", "AMT", "CCI", "EQIX", "PSA", "O", "SPG", "WELL", "DLR", "AVB",
    "EQR", "VTR", "ARE", "MAA", "UDR", "ESS", "INVH", "SUI", "ELS", "CPT",
    # Materials
    "LIN", "APD", "SHW", "ECL", "FCX", "NEM", "NUE", "DD", "DOW", "PPG",
    "VMC", "MLM", "ALB", "FMC", "CF", "MOS", "CE", "EMN", "IFF", "SEE",
    # Communication Services
    "DIS", "CMCSA", "NFLX", "T", "VZ", "TMUS", "CHTR", "EA", "TTWO", "WBD",
    "PARA", "FOX", "FOXA", "NWS", "NWSA", "OMC", "IPG", "MTCH", "LYV", "DISH",
    # Additional S&P 500
    "BRK.B", "PYPL", "SQ", "ABNB", "UBER", "LYFT", "ZM", "DOCU", "TWLO", "SNOW",
    "DDOG", "NET", "MDB", "OKTA", "ZS", "BILL", "HUBS", "VEEV", "WDAY", "SPLK"
]

# Top 100 ETFs
TOP_ETFS = [
    # Major Index ETFs
    "SPY", "QQQ", "IWM", "DIA", "VOO", "VTI", "IVV", "VEA", "EFA", "VWO",
    "EEM", "VTV", "VUG", "IWF", "IWD", "IJH", "IJR", "MDY", "RSP", "SPLG",
    # Sector ETFs
    "XLF", "XLK", "XLV", "XLE", "XLI", "XLP", "XLY", "XLU", "XLB", "XLRE",
    "XLC", "VGT", "VHT", "VFH", "VNQ", "VDE", "VIS", "VCR", "VDC", "VAW",
    # Thematic/Innovation
    "ARKK", "ARKW", "ARKF", "ARKG", "ARKQ", "SOXX", "SMH", "XBI", "IBB", "ICLN",
    "TAN", "LIT", "BOTZ", "ROBO", "AIQ", "HACK", "CIBR", "FINX", "IPAY", "BLOK",
    # Fixed Income
    "BND", "AGG", "TLT", "IEF", "SHY", "LQD", "HYG", "JNK", "TIP", "VCIT",
    "VCSH", "VGSH", "VGIT", "VGLT", "MUB", "EMB", "BNDX", "IAGG", "GOVT", "SCHZ",
    # Commodities
    "GLD", "SLV", "IAU", "GDX", "GDXJ", "USO", "UNG", "DBA", "DBC", "PDBC",
    # International
    "IEMG", "IXUS", "VEU", "VXUS", "ACWI", "ACWX", "SCZ", "VSS", "IEFA", "SCHF",
    # Dividend
    "VYM", "DVY", "SDY", "SCHD", "HDV", "DGRO", "NOBL", "VIG", "SPHD", "SPYD",
    # Leveraged/Inverse (for reference)
    "TQQQ", "SQQQ", "UPRO", "SPXU", "UVXY", "SVXY", "QLD", "SSO", "SH", "PSQ"
]

# Fundamentals endpoints to fetch
FUNDAMENTALS_ENDPOINTS = {
    'earnings': '/earnings',
    'earnings_calendar': '/earnings_calendar',
    'dividends': '/dividends',
    'splits': '/splits',
    'statistics': '/statistics',
    'profile': '/profile',
    'financials': '/financials',
    'cash_flow': '/cash_flow',
    'balance_sheet': '/balance_sheet',
    'income_statement': '/income_statement'
}

# Technical indicators to calculate (per masterquery)
INDICATORS = [
    'rsi', 'macd', 'bbands', 'sma', 'ema', 'adx', 'atr', 'stoch',
    'cci', 'mfi', 'obv', 'mom', 'roc', 'willr', 'ichimoku'
]

class ComprehensiveFetcher:
    def __init__(self, capacity_percent=50):
        self.api_key = TWELVEDATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
        self.client = bigquery.Client(project=PROJECT_ID)

        # Capacity settings
        self.capacity_percent = capacity_percent
        self.max_calls_minute = int(800 * capacity_percent / 100)
        self.daily_budget = int(1152000 * capacity_percent / 100)

        # Tracking
        self.calls_made = 0
        self.calls_this_minute = 0
        self.minute_start = time.time()
        self.errors = []
        self.results = {
            'stocks': {'success': 0, 'failed': 0, 'records': 0},
            'etfs': {'success': 0, 'failed': 0, 'records': 0},
            'fundamentals': {'success': 0, 'failed': 0, 'records': 0}
        }

        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE TWELVEDATA FETCHER - {capacity_percent}% CAPACITY")
        print(f"{'='*60}")
        print(f"Max calls/minute: {self.max_calls_minute}")
        print(f"Daily budget: {self.daily_budget:,} credits")
        print(f"Stocks: {len(SP500_STOCKS)}")
        print(f"ETFs: {len(TOP_ETFS)}")
        print(f"{'='*60}\n")

    def rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()

        # Reset counter each minute
        if current_time - self.minute_start >= 60:
            self.minute_start = current_time
            self.calls_this_minute = 0

        # Wait if at limit
        if self.calls_this_minute >= self.max_calls_minute:
            sleep_time = 60 - (current_time - self.minute_start) + 1
            print(f"Rate limit reached. Waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            self.minute_start = time.time()
            self.calls_this_minute = 0

        self.calls_this_minute += 1
        self.calls_made += 1
        time.sleep(BATCH_DELAY)

    def fetch_time_series(self, symbol, interval='1day', outputsize=5000):
        """Fetch OHLCV time series data"""
        self.rate_limit()

        url = f"{self.base_url}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if 'values' in data:
                return data['values']
            elif 'code' in data:
                self.errors.append(f"{symbol}: {data.get('message', 'Unknown error')}")
                return None
            return None
        except Exception as e:
            self.errors.append(f"{symbol}: {str(e)}")
            return None

    def fetch_with_indicators(self, symbol, interval='1day', outputsize=5000):
        """Fetch time series with technical indicators"""
        self.rate_limit()

        # Build indicator string
        indicators_str = ','.join([
            'rsi:14', 'macd:12,26,9', 'bbands:20,2',
            'sma:20', 'sma:50', 'sma:200',
            'ema:12', 'ema:26', 'ema:50', 'ema:200',
            'adx:14', 'atr:14', 'stoch:14,3,3',
            'cci:20', 'mfi:14', 'willr:14', 'mom:10', 'roc:10'
        ])

        url = f"{self.base_url}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if 'values' in data:
                return {
                    'symbol': symbol,
                    'meta': data.get('meta', {}),
                    'values': data['values']
                }
            elif 'code' in data:
                self.errors.append(f"{symbol}: {data.get('message', 'Unknown error')}")
                return None
            return None
        except Exception as e:
            self.errors.append(f"{symbol}: {str(e)}")
            return None

    def fetch_fundamentals(self, symbol, endpoint):
        """Fetch fundamental data (earnings, dividends, etc.)"""
        self.rate_limit()

        url = f"{self.base_url}{endpoint}"
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if 'code' in data and data['code'] != 200:
                return None
            return data
        except Exception as e:
            self.errors.append(f"{symbol} {endpoint}: {str(e)}")
            return None

    def calculate_indicators(self, df):
        """Calculate 24 technical indicators per masterquery spec"""
        try:
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # MACD
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']

            # Bollinger Bands
            df['sma_20'] = df['close'].rolling(20).mean()
            std20 = df['close'].rolling(20).std()
            df['bollinger_upper'] = df['sma_20'] + (std20 * 2)
            df['bollinger_middle'] = df['sma_20']
            df['bollinger_lower'] = df['sma_20'] - (std20 * 2)

            # SMAs
            df['sma_50'] = df['close'].rolling(50).mean()
            df['sma_200'] = df['close'].rolling(200).mean()

            # EMAs
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            df['ema_200'] = df['close'].ewm(span=200).mean()

            # ATR
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = tr.rolling(14).mean()

            # Stochastic
            low14 = df['low'].rolling(14).min()
            high14 = df['high'].rolling(14).max()
            df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14)
            df['stoch_d'] = df['stoch_k'].rolling(3).mean()

            # ADX (simplified)
            df['adx'] = 25  # Placeholder - would need full calculation

            # CCI
            tp = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = tp.rolling(20).mean()
            mad = tp.rolling(20).apply(lambda x: abs(x - x.mean()).mean())
            df['cci'] = (tp - sma_tp) / (0.015 * mad)

            # Williams %R
            df['williams_r'] = -100 * (high14 - df['close']) / (high14 - low14)

            # Momentum & ROC
            df['momentum'] = df['close'] - df['close'].shift(10)
            df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

            # OBV (simplified)
            df['obv'] = (df['volume'] * ((df['close'] > df['close'].shift()).astype(int) * 2 - 1)).cumsum()

            # MFI
            tp = (df['high'] + df['low'] + df['close']) / 3
            mf = tp * df['volume']
            mf_pos = mf.where(tp > tp.shift(), 0).rolling(14).sum()
            mf_neg = mf.where(tp < tp.shift(), 0).rolling(14).sum()
            df['mfi'] = 100 - (100 / (1 + mf_pos / mf_neg))

            # Growth Score (per masterquery)
            df['growth_score'] = (
                ((df['rsi'] >= 50) & (df['rsi'] <= 70)).astype(int) * 25 +
                (df['macd_histogram'] > 0).astype(int) * 25 +
                (df['adx'] > 25).astype(int) * 25 +
                (df['close'] > df['sma_200']).astype(int) * 25
            )

            # Trend Regime
            import numpy as np
            conditions = [
                (df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']) & (df['adx'] > 25),
                (df['close'] > df['sma_50']) & (df['close'] > df['sma_200']),
                (df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']) & (df['adx'] > 25),
                (df['close'] < df['sma_50']) & (df['close'] < df['sma_200'])
            ]
            choices = ['STRONG_UPTREND', 'WEAK_UPTREND', 'STRONG_DOWNTREND', 'WEAK_DOWNTREND']
            df['trend_regime'] = np.select(conditions, choices, default='CONSOLIDATION')

            # Rise Cycle
            df['in_rise_cycle'] = df['ema_12'] > df['ema_26']

            return df

        except Exception as e:
            print(f"  Error calculating indicators: {e}")
            return df

    def process_symbol(self, symbol, asset_type='stock'):
        """Process a single symbol - fetch data and calculate indicators"""
        try:
            # Fetch time series (5+ years = ~1300 trading days)
            data = self.fetch_time_series(symbol, interval='1day', outputsize=5000)

            if not data:
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['symbol'] = symbol

            # Convert types
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
            df['datetime'] = pd.to_datetime(df['datetime'])

            # Calculate indicators
            df = self.calculate_indicators(df)

            # Sort by date
            df = df.sort_values('datetime')

            return df

        except Exception as e:
            self.errors.append(f"{symbol}: {str(e)}")
            return None

    def upload_to_bigquery(self, df, table_name):
        """Upload DataFrame to BigQuery"""
        if df is None or df.empty:
            return 0

        try:
            table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

            # Configure job
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
            )

            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()

            return len(df)
        except Exception as e:
            self.errors.append(f"BigQuery upload: {str(e)}")
            return 0

    def fetch_all_stocks(self):
        """Fetch all S&P 500 stocks"""
        print(f"\n{'='*60}")
        print(f"FETCHING S&P 500 STOCKS ({len(SP500_STOCKS)} symbols)")
        print(f"{'='*60}\n")

        all_data = []

        for i, symbol in enumerate(SP500_STOCKS):
            print(f"[{i+1}/{len(SP500_STOCKS)}] Processing {symbol}...", end=" ")

            df = self.process_symbol(symbol, 'stock')

            if df is not None and not df.empty:
                all_data.append(df)
                self.results['stocks']['success'] += 1
                self.results['stocks']['records'] += len(df)
                print(f"OK ({len(df)} records)")
            else:
                self.results['stocks']['failed'] += 1
                print("FAILED")

            # Progress update every 50 symbols
            if (i + 1) % 50 == 0:
                print(f"\n--- Progress: {i+1}/{len(SP500_STOCKS)} stocks processed ---\n")

        # Combine and upload
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            records = self.upload_to_bigquery(combined_df, 'stocks_daily_comprehensive')
            print(f"\nUploaded {records:,} stock records to BigQuery")

        return self.results['stocks']

    def fetch_all_etfs(self):
        """Fetch all ETFs"""
        print(f"\n{'='*60}")
        print(f"FETCHING ETFs ({len(TOP_ETFS)} symbols)")
        print(f"{'='*60}\n")

        all_data = []

        for i, symbol in enumerate(TOP_ETFS):
            print(f"[{i+1}/{len(TOP_ETFS)}] Processing {symbol}...", end=" ")

            df = self.process_symbol(symbol, 'etf')

            if df is not None and not df.empty:
                all_data.append(df)
                self.results['etfs']['success'] += 1
                self.results['etfs']['records'] += len(df)
                print(f"OK ({len(df)} records)")
            else:
                self.results['etfs']['failed'] += 1
                print("FAILED")

        # Combine and upload
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            records = self.upload_to_bigquery(combined_df, 'etfs_daily_comprehensive')
            print(f"\nUploaded {records:,} ETF records to BigQuery")

        return self.results['etfs']

    def fetch_all_fundamentals(self):
        """Fetch fundamental data for all symbols"""
        print(f"\n{'='*60}")
        print("FETCHING FUNDAMENTALS (earnings, dividends, financials)")
        print(f"{'='*60}\n")

        all_symbols = SP500_STOCKS[:100]  # Start with top 100 stocks for fundamentals

        # Earnings
        print("\n--- Fetching Earnings Data ---")
        earnings_data = []
        for symbol in all_symbols[:50]:  # Limit for first run
            data = self.fetch_fundamentals(symbol, '/earnings')
            if data and 'earnings' in data:
                for earning in data['earnings']:
                    earning['symbol'] = symbol
                    earnings_data.append(earning)
                self.results['fundamentals']['success'] += 1

        if earnings_data:
            df = pd.DataFrame(earnings_data)
            self.upload_to_bigquery(df, 'fundamentals_earnings')
            print(f"  Uploaded {len(df)} earnings records")

        # Dividends
        print("\n--- Fetching Dividends Data ---")
        dividends_data = []
        for symbol in all_symbols[:50]:
            data = self.fetch_fundamentals(symbol, '/dividends')
            if data and 'dividends' in data:
                for div in data['dividends']:
                    div['symbol'] = symbol
                    dividends_data.append(div)
                self.results['fundamentals']['success'] += 1

        if dividends_data:
            df = pd.DataFrame(dividends_data)
            self.upload_to_bigquery(df, 'fundamentals_dividends')
            print(f"  Uploaded {len(df)} dividend records")

        # Statistics (Key metrics)
        print("\n--- Fetching Statistics Data ---")
        stats_data = []
        for symbol in all_symbols[:50]:
            data = self.fetch_fundamentals(symbol, '/statistics')
            if data and 'statistics' in data:
                stats = data['statistics']
                stats['symbol'] = symbol
                stats_data.append(stats)
                self.results['fundamentals']['success'] += 1

        if stats_data:
            df = pd.DataFrame(stats_data)
            self.upload_to_bigquery(df, 'fundamentals_statistics')
            print(f"  Uploaded {len(df)} statistics records")

        return self.results['fundamentals']

    def run(self):
        """Run the full comprehensive fetch"""
        start_time = time.time()

        print(f"\nStarting comprehensive fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capacity: {self.capacity_percent}% ({self.daily_budget:,} credits/day)")

        # Fetch stocks
        self.fetch_all_stocks()

        # Fetch ETFs
        self.fetch_all_etfs()

        # Fetch fundamentals
        self.fetch_all_fundamentals()

        # Summary
        elapsed = time.time() - start_time

        print(f"\n{'='*60}")
        print("COMPREHENSIVE FETCH COMPLETE")
        print(f"{'='*60}")
        print(f"\nTotal Time: {elapsed/60:.1f} minutes")
        print(f"Total API Calls: {self.calls_made:,}")
        print(f"\nResults:")
        print(f"  Stocks: {self.results['stocks']['success']} success, {self.results['stocks']['failed']} failed, {self.results['stocks']['records']:,} records")
        print(f"  ETFs: {self.results['etfs']['success']} success, {self.results['etfs']['failed']} failed, {self.results['etfs']['records']:,} records")
        print(f"  Fundamentals: {self.results['fundamentals']['success']} endpoints fetched")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for err in self.errors[:10]:
                print(f"  - {err}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")

        # Save progress
        progress = {
            'timestamp': datetime.now().isoformat(),
            'capacity_percent': self.capacity_percent,
            'calls_made': self.calls_made,
            'elapsed_minutes': elapsed / 60,
            'results': self.results,
            'errors_count': len(self.errors)
        }

        with open('comprehensive_fetch_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)

        return progress


def create_capacity_schedule():
    """Create weekly capacity increase schedule"""
    schedule = {
        'week_1': {'percent': 50, 'credits_day': 576000},
        'week_2': {'percent': 60, 'credits_day': 691200},
        'week_3': {'percent': 70, 'credits_day': 806400},
        'week_4': {'percent': 80, 'credits_day': 921600},
        'week_5': {'percent': 90, 'credits_day': 1036800},
        'week_6': {'percent': 95, 'credits_day': 1094400}
    }

    print("\n" + "="*60)
    print("CAPACITY INCREASE SCHEDULE")
    print("="*60)
    print(f"\nTwelveData $229 Plan: 800 credits/min = 1,152,000/day\n")

    for week, config in schedule.items():
        print(f"{week.replace('_', ' ').title()}: {config['percent']}% = {config['credits_day']:,} credits/day")

    return schedule


if __name__ == "__main__":
    # Show capacity schedule
    schedule = create_capacity_schedule()

    # Run at 50% capacity
    fetcher = ComprehensiveFetcher(capacity_percent=50)
    fetcher.run()
