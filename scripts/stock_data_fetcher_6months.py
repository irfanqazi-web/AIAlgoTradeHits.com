"""
Stock Data Fetcher - 6 Months Historical Data
Fetches 6 months of daily OHLC data for major US stocks using Yahoo Finance API
Similar structure to kraken_data_fetcher.py but for stocks
"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Major stock symbols to track (similar to top crypto pairs)
# Categories: Tech Giants, Financial, Energy, Healthcare, Consumer, Industrial
STOCK_SYMBOLS = [
    # Tech Giants (FAANG+)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX',

    # Financial
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BLK',

    # Technology & Semiconductors
    'ORCL', 'CSCO', 'INTC', 'AMD', 'CRM', 'ADBE', 'NOW', 'AVGO', 'QCOM', 'TXN',

    # Healthcare & Pharma
    'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK', 'ABT', 'DHR', 'LLY', 'BMY',

    # Consumer & Retail
    'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'COST', 'DIS', 'CMCSA',

    # Energy & Utilities
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'NEE', 'DUK', 'SO', 'D',

    # Industrial & Manufacturing
    'BA', 'CAT', 'HON', 'UNP', 'UPS', 'RTX', 'LMT', 'GE', 'MMM', 'DE',

    # Communication Services
    'T', 'VZ', 'TMUS', 'CHTR', 'GOOGL', 'META', 'NFLX', 'DIS',

    # Materials & Chemicals
    'LIN', 'APD', 'ECL', 'SHW', 'DD', 'DOW', 'NEM', 'FCX',

    # Real Estate & REITs
    'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG', 'O', 'WELL',

    # ETFs (Market Indices)
    'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'TLT'
]

# Remove duplicates
STOCK_SYMBOLS = sorted(list(set(STOCK_SYMBOLS)))

print("=" * 70)
print("STOCK DATA FETCHER - 6 MONTHS HISTORICAL DATA")
print("=" * 70)
print(f"\nTotal symbols to fetch: {len(STOCK_SYMBOLS)}")
print(f"Date range: {(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
print("\n" + "=" * 70)

# Calculate date range
end_date = datetime.now()
start_date = end_date - timedelta(days=180)  # 6 months

all_stock_data = []
failed_symbols = []
successful_symbols = 0

for idx, symbol in enumerate(STOCK_SYMBOLS, 1):
    try:
        print(f"\n[{idx}/{len(STOCK_SYMBOLS)}] Fetching {symbol}...", end=' ')

        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Fetch historical data
        hist = ticker.history(start=start_date, end=end_date, interval='1d')

        if hist.empty:
            print(f"NO DATA")
            failed_symbols.append({'symbol': symbol, 'error': 'No data returned'})
            continue

        # Get stock info
        try:
            info = ticker.info
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            exchange = info.get('exchange', 'Unknown')
        except:
            company_name = symbol
            sector = 'Unknown'
            industry = 'Unknown'
            exchange = 'Unknown'

        # Process each day's data
        for date, row in hist.iterrows():
            all_stock_data.append({
                'symbol': symbol,
                'company_name': company_name,
                'sector': sector,
                'industry': industry,
                'exchange': exchange,
                'date': date.strftime('%Y-%m-%d'),
                'datetime': date.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': int(date.timestamp()),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
                'dividends': float(row.get('Dividends', 0)),
                'stock_splits': float(row.get('Stock Splits', 0))
            })

        successful_symbols += 1
        print(f"OK - Got {len(hist)} days")

        # Rate limiting: Be respectful to Yahoo Finance
        time.sleep(0.5)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        failed_symbols.append({'symbol': symbol, 'error': str(e)})
        time.sleep(1)

# Save all data
print("\n" + "=" * 70)
print("SAVING DATA")
print("=" * 70)

if all_stock_data:
    stock_df = pd.DataFrame(all_stock_data)
    stock_df.to_csv('stock_6month_ohlc_data.csv', index=False)
    print(f"\n✓ Saved {len(stock_df)} OHLC records to stock_6month_ohlc_data.csv")
    print(f"  - Covering {successful_symbols} stocks")
    print(f"  - Date range: {stock_df['date'].min()} to {stock_df['date'].max()}")

    # Save summary by symbol
    summary = stock_df.groupby('symbol').agg({
        'close': ['first', 'last', 'min', 'max'],
        'volume': 'sum',
        'date': 'count'
    }).round(2)
    summary.columns = ['First_Close', 'Last_Close', 'Min_Close', 'Max_Close', 'Total_Volume', 'Days']
    summary['Change_%'] = ((summary['Last_Close'] - summary['First_Close']) / summary['First_Close'] * 100).round(2)
    summary = summary.sort_values('Change_%', ascending=False)
    summary.to_csv('stock_6month_summary.csv')
    print(f"✓ Saved summary to stock_6month_summary.csv")
else:
    print("\n✗ No stock data collected")

# Save failed symbols
if failed_symbols:
    failed_df = pd.DataFrame(failed_symbols)
    failed_df.to_csv('stock_failed_symbols.csv', index=False)
    print(f"\n✗ {len(failed_symbols)} symbols failed - saved to stock_failed_symbols.csv")

# Create stock symbols list
symbols_df = pd.DataFrame([
    {
        'symbol': symbol,
        'category': 'Tech' if symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX'] else
                   'Financial' if symbol in ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA'] else
                   'Healthcare' if symbol in ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK'] else
                   'Energy' if symbol in ['XOM', 'CVX', 'COP', 'SLB', 'EOG'] else
                   'Consumer' if symbol in ['WMT', 'HD', 'MCD', 'NKE', 'SBUX'] else
                   'ETF' if symbol in ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI'] else 'Other'
    }
    for symbol in STOCK_SYMBOLS
])
symbols_df.to_csv('stock_symbols_list.csv', index=False)
print(f"✓ Saved stock symbols list to stock_symbols_list.csv")

# Final summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total symbols attempted: {len(STOCK_SYMBOLS)}")
print(f"Successfully fetched: {successful_symbols}")
print(f"Failed: {len(failed_symbols)}")
print(f"Total OHLC records: {len(all_stock_data)}")
print(f"\nFiles created:")
print(f"  1. stock_symbols_list.csv - List of all stock symbols")
print(f"  2. stock_6month_ohlc_data.csv - 6 months of OHLC data")
print(f"  3. stock_6month_summary.csv - Summary statistics by symbol")
if failed_symbols:
    print(f"  4. stock_failed_symbols.csv - Failed symbols for debugging")
print("\n" + "=" * 70)
