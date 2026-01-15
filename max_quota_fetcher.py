#!/usr/bin/env python3
"""
Maximum Quota TwelveData Fetcher
Target: 1 Million Records/Day
$229 Pro Plan - 1,597 credits/min
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone
import time
import concurrent.futures
import threading

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Rate limiting - Pro plan: 1,597 credits/min
MAX_REQUESTS_PER_MIN = 90  # Stay safe under limit
request_count = 0
last_reset = time.time()
rate_lock = threading.Lock()
total_records = 0
records_lock = threading.Lock()

# Initialize BigQuery
bq_client = bigquery.Client(project=PROJECT_ID)

# ============================================================================
# COMPREHENSIVE SYMBOL LISTS
# ============================================================================

# Top 200 US Stocks by market cap
US_STOCKS = [
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
    'AIG', 'FDX', 'OXY', 'ECL', 'F', 'AFL', 'TEL', 'CPRT', 'HES', 'DXCM',
    'KMB', 'FTNT', 'SRE', 'PAYX', 'D', 'AEP', 'A', 'PSA', 'MSCI', 'O',
    'DHI', 'BK', 'IDXX', 'GIS', 'CCI', 'ROST', 'KDP', 'JCI', 'MNST', 'FAST',
    'KMI', 'YUM', 'CTVA', 'AME', 'AMP', 'ODFL', 'EXC', 'GWW', 'CMI', 'LHX',
    'ALL', 'VRSK', 'OTIS', 'IQV', 'HAL', 'XEL', 'PCG', 'GEHC', 'CTSH', 'IT',
    'HUM', 'DVN', 'MLM', 'KR', 'EW', 'WEC', 'ED', 'VMC', 'FANG', 'DD'
]

# Top 100 Cryptocurrencies
CRYPTO_SYMBOLS = [
    'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
    'AVAX/USD', 'LINK/USD', 'DOT/USD', 'MATIC/USD', 'SHIB/USD', 'TRX/USD', 'UNI/USD',
    'ATOM/USD', 'LTC/USD', 'NEAR/USD', 'APT/USD', 'FIL/USD', 'ARB/USD',
    'XMR/USD', 'BCH/USD', 'XLM/USD', 'ETC/USD', 'HBAR/USD', 'VET/USD', 'ALGO/USD',
    'FTM/USD', 'SAND/USD', 'MANA/USD', 'AAVE/USD', 'THETA/USD', 'XTZ/USD', 'EOS/USD',
    'AXS/USD', 'MKR/USD', 'SNX/USD', 'COMP/USD', 'ZEC/USD', 'DASH/USD',
    'ENJ/USD', 'BAT/USD', 'CRV/USD', 'LRC/USD', 'SUSHI/USD', 'YFI/USD', '1INCH/USD',
    'GRT/USD', 'CHZ/USD', 'IOTA/USD', 'KAVA/USD', 'CELO/USD', 'ZRX/USD', 'ANKR/USD',
    'GALA/USD', 'IMX/USD', 'LDO/USD', 'RPL/USD', 'OP/USD', 'INJ/USD',
    'RUNE/USD', 'KSM/USD', 'FLOW/USD', 'EGLD/USD', 'NEO/USD', 'WAVES/USD', 'QTUM/USD',
    'ICX/USD', 'ONT/USD', 'ZIL/USD', 'STORJ/USD', 'REN/USD', 'SKL/USD', 'OCEAN/USD'
]

# Major ETFs - TOP 20 by AUM (>$4.8 trillion combined) + Additional
ETF_SYMBOLS = [
    # TOP 20 ETFs by AUM - Priority
    'VOO', 'IVV', 'SPY', 'SPLG',  # S&P 500 ($2.4T)
    'VTI', 'QQQ', 'VUG', 'VGT', 'IWF',  # Total Market & Growth
    'VTV',  # Value
    'VEA', 'IEFA', 'VXUS',  # International Developed
    'IEMG', 'VWO',  # Emerging Markets
    'BND', 'AGG',  # Bonds
    'IJH', 'VIG',  # Mid-Cap & Dividend
    'GLD',  # Gold
    # Additional ETFs
    'IWM', 'DIA', 'EFA', 'EEM',
    'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLY', 'XLP', 'XLB', 'XLU', 'XLRE',
    'SLV', 'USO', 'UNG', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'JNK',
    'VNQ', 'ARKK', 'ARKG', 'ARKW', 'ARKF', 'SMH', 'XBI', 'IBB', 'KRE', 'XHB'
]

# Forex Pairs
FOREX_SYMBOLS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'EUR/AUD', 'EUR/CAD', 'EUR/NZD',
    'GBP/CHF', 'GBP/AUD', 'GBP/CAD', 'GBP/NZD', 'AUD/JPY', 'AUD/NZD',
    'AUD/CAD', 'CAD/JPY', 'NZD/JPY', 'CHF/JPY', 'USD/MXN', 'USD/ZAR', 'USD/TRY',
    'USD/SGD', 'USD/HKD', 'USD/SEK'
]

# Global Indices
INDEX_SYMBOLS = [
    'SPX', 'NDX', 'DJI', 'VIX', 'FTSE', 'DAX', 'CAC', 'STOXX50E', 'N225',
    'HSI', 'SSEC', 'KOSPI', 'ASX200', 'IBEX', 'SMI', 'AEX', 'SENSEX', 'NIFTY'
]

# Commodities
COMMODITY_SYMBOLS = [
    'XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD',  # Precious metals
    'WTI', 'BRENT', 'NATGAS',  # Energy
    'WHEAT', 'CORN', 'SOYBEAN', 'COFFEE', 'SUGAR', 'COTTON'  # Agriculture
]


def rate_limit():
    """Thread-safe rate limiter"""
    global request_count, last_reset
    with rate_lock:
        current_time = time.time()
        if current_time - last_reset >= 60:
            request_count = 0
            last_reset = current_time

        if request_count >= MAX_REQUESTS_PER_MIN:
            sleep_time = 60 - (current_time - last_reset) + 1
            if sleep_time > 0:
                print(f"    Rate limit ({request_count} reqs), waiting {sleep_time:.0f}s...")
                time.sleep(sleep_time)
                request_count = 0
                last_reset = time.time()

        request_count += 1


def update_record_count(count):
    """Thread-safe record counter"""
    global total_records
    with records_lock:
        total_records += count


def fetch_time_series(symbol, interval='1day', outputsize=5000):
    """Fetch OHLCV time series - max outputsize for historical data"""
    try:
        rate_limit()
        url = f"{BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=60)
        data = response.json()

        if 'values' not in data:
            return None, 0

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert numeric columns
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        else:
            df['volume'] = 0

        return df, len(df)

    except Exception as e:
        return None, 0


def fetch_symbol_batch(symbols, asset_type, interval='1day', outputsize=5000):
    """Fetch batch of symbols sequentially"""
    results = []

    for i, symbol in enumerate(symbols):
        print(f"  [{i+1}/{len(symbols)}] {symbol}...", end=" ")

        df, count = fetch_time_series(symbol, interval, outputsize)

        if df is not None and count > 0:
            df['asset_type'] = asset_type
            df['interval'] = interval
            results.append(df)
            update_record_count(count)
            print(f"OK ({count:,} records)")
        else:
            print("SKIP")

        time.sleep(0.1)  # Small delay between requests

    return results


def upload_to_bigquery(df, table_name):
    """Upload dataframe to BigQuery"""
    if df is None or df.empty:
        return False

    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        return True

    except Exception as e:
        print(f"    BigQuery error: {e}")
        return False


def main():
    global total_records

    print("="*80)
    print("MAXIMUM QUOTA TWELVEDATA FETCHER")
    print(f"Target: 1,000,000 Records | Started: {datetime.now()}")
    print("="*80)

    all_data = []

    # ========================================================================
    # 1. US STOCKS - Daily (200 symbols x 5000 days = 1M records potential)
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[1/7] US STOCKS - DAILY (200 symbols, max 5000 days each)")
    print(f"{'='*80}")

    stock_data = fetch_symbol_batch(US_STOCKS, 'STOCK', '1day', 5000)
    if stock_data:
        combined = pd.concat(stock_data, ignore_index=True)
        all_data.append(combined)
        print(f"  Stocks Daily: {len(combined):,} records from {len(stock_data)} symbols")

        # Upload stocks
        upload_to_bigquery(combined, 'stocks_daily_clean')

    # ========================================================================
    # 2. US STOCKS - Hourly (top 50 x 5000 hours)
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[2/7] US STOCKS - HOURLY (Top 50 symbols)")
    print(f"{'='*80}")

    stock_hourly = fetch_symbol_batch(US_STOCKS[:50], 'STOCK', '1h', 5000)
    if stock_hourly:
        combined = pd.concat(stock_hourly, ignore_index=True)
        all_data.append(combined)
        print(f"  Stocks Hourly: {len(combined):,} records from {len(stock_hourly)} symbols")
        upload_to_bigquery(combined, 'stocks_hourly_clean')

    # ========================================================================
    # 3. CRYPTO - Daily (75 symbols)
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[3/7] CRYPTO - DAILY ({len(CRYPTO_SYMBOLS)} symbols)")
    print(f"{'='*80}")

    crypto_data = fetch_symbol_batch(CRYPTO_SYMBOLS, 'CRYPTO', '1day', 5000)
    if crypto_data:
        combined = pd.concat(crypto_data, ignore_index=True)
        all_data.append(combined)
        print(f"  Crypto Daily: {len(combined):,} records from {len(crypto_data)} symbols")
        upload_to_bigquery(combined, 'crypto_daily_clean')

    # ========================================================================
    # 4. CRYPTO - Hourly (top 30)
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[4/7] CRYPTO - HOURLY (Top 30 symbols)")
    print(f"{'='*80}")

    crypto_hourly = fetch_symbol_batch(CRYPTO_SYMBOLS[:30], 'CRYPTO', '1h', 5000)
    if crypto_hourly:
        combined = pd.concat(crypto_hourly, ignore_index=True)
        all_data.append(combined)
        print(f"  Crypto Hourly: {len(combined):,} records from {len(crypto_hourly)} symbols")
        upload_to_bigquery(combined, 'crypto_hourly_clean')

    # ========================================================================
    # 5. ETFs - Daily
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[5/7] ETFs - DAILY ({len(ETF_SYMBOLS)} symbols)")
    print(f"{'='*80}")

    etf_data = fetch_symbol_batch(ETF_SYMBOLS, 'ETF', '1day', 5000)
    if etf_data:
        combined = pd.concat(etf_data, ignore_index=True)
        all_data.append(combined)
        print(f"  ETF Daily: {len(combined):,} records from {len(etf_data)} symbols")
        upload_to_bigquery(combined, 'etf_daily_clean')

    # ========================================================================
    # 6. FOREX - Daily
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[6/7] FOREX - DAILY ({len(FOREX_SYMBOLS)} pairs)")
    print(f"{'='*80}")

    forex_data = fetch_symbol_batch(FOREX_SYMBOLS, 'FOREX', '1day', 5000)
    if forex_data:
        combined = pd.concat(forex_data, ignore_index=True)
        all_data.append(combined)
        print(f"  Forex Daily: {len(combined):,} records from {len(forex_data)} symbols")
        upload_to_bigquery(combined, 'forex_daily_clean')

    # ========================================================================
    # 7. INDICES - Daily
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[7/7] INDICES - DAILY ({len(INDEX_SYMBOLS)} indices)")
    print(f"{'='*80}")

    index_data = fetch_symbol_batch(INDEX_SYMBOLS, 'INDEX', '1day', 5000)
    if index_data:
        combined = pd.concat(index_data, ignore_index=True)
        all_data.append(combined)
        print(f"  Index Daily: {len(combined):,} records from {len(index_data)} symbols")
        upload_to_bigquery(combined, 'indices_daily_clean')

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total Records Fetched: {total_records:,}")
    print(f"Target: 1,000,000")
    print(f"Achievement: {(total_records/1000000)*100:.1f}%")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        # Save master CSV
        csv_path = f"C:/1AITrading/Trading/max_fetch_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        final_df.to_csv(csv_path, index=False)
        print(f"\nSaved to: {csv_path}")

        # Summary by asset type
        print(f"\n{'='*80}")
        print("RECORDS BY ASSET TYPE")
        print(f"{'='*80}")
        summary = final_df.groupby(['asset_type', 'interval']).agg({
            'symbol': 'nunique',
            'datetime': 'count'
        }).rename(columns={'symbol': 'symbols', 'datetime': 'records'})
        print(summary.to_string())

    print(f"\n{'='*80}")
    print(f"COMPLETED: {datetime.now()}")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
