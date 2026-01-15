#!/usr/bin/env python3
"""
Fill Remaining TwelveData Quota
Target: ~150,000 more records to reach 2M daily limit
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
from datetime import datetime
import time

PROJECT_ID = 'aialgotradehits'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Additional symbols to fetch (~150K more records)
ADDITIONAL_SYMBOLS = {
    # More US Stocks - Daily (30 more * 5000 = 150,000)
    'stocks_daily': [
        'PYPL', 'NOW', 'UBER', 'ABNB', 'SQ', 'SHOP', 'SNOW', 'PLTR', 'COIN', 'RIVN',
        'LCID', 'NIO', 'XPEV', 'LI', 'DKNG', 'RBLX', 'U', 'CRWD', 'ZS', 'OKTA',
        'DDOG', 'NET', 'MDB', 'TWLO', 'DOCU', 'ZM', 'SPOT', 'PINS', 'SNAP', 'TTD'
    ],
    # More ETFs - Hourly (10 * 5000 = 50,000)
    'etfs_hourly': [
        'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'XLF', 'XLE', 'XLK', 'GLD', 'TLT'
    ],
}

def fetch_data(symbol, interval='1day', outputsize=5000):
    """Fetch OHLCV data from TwelveData"""
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
            return None, 0

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        return df, len(df)

    except Exception as e:
        return None, 0

def main():
    print("="*70)
    print("FILL REMAINING TWELVEDATA QUOTA")
    print(f"Target: ~200,000 more records | Started: {datetime.now()}")
    print("="*70)

    all_data = []
    total_records = 0

    # Fetch additional stocks daily
    print(f"\n[1/2] ADDITIONAL STOCKS - DAILY (30 symbols)")
    print("="*70)

    for i, symbol in enumerate(ADDITIONAL_SYMBOLS['stocks_daily'], 1):
        print(f"  [{i}/30] {symbol}...", end=" ")
        df, count = fetch_data(symbol, '1day', 5000)
        if df is not None and count > 0:
            df['asset_type'] = 'STOCK'
            df['interval'] = '1day'
            all_data.append(df)
            total_records += count
            print(f"OK ({count:,} records)")
        else:
            print("SKIP")
        time.sleep(0.7)

    # Fetch ETFs hourly
    print(f"\n[2/2] ETFs - HOURLY (10 symbols)")
    print("="*70)

    for i, symbol in enumerate(ADDITIONAL_SYMBOLS['etfs_hourly'], 1):
        print(f"  [{i}/10] {symbol}...", end=" ")
        df, count = fetch_data(symbol, '1h', 5000)
        if df is not None and count > 0:
            df['asset_type'] = 'ETF'
            df['interval'] = '1h'
            all_data.append(df)
            total_records += count
            print(f"OK ({count:,} records)")
        else:
            print("SKIP")
        time.sleep(0.7)

    # Save results
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        csv_path = f"C:/1AITrading/Trading/additional_fetch_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        final_df.to_csv(csv_path, index=False)

        print(f"\n{'='*70}")
        print("ADDITIONAL FETCH SUMMARY")
        print(f"{'='*70}")
        print(f"Additional Records: {total_records:,}")
        print(f"Previous Total: 1,850,210")
        print(f"NEW TOTAL: {1850210 + total_records:,}")
        print(f"Quota Used: {((1850210 + total_records) / 2000000 * 100):.1f}%")
        print(f"Saved to: {csv_path}")

    print(f"\n{'='*70}")
    print(f"COMPLETED: {datetime.now()}")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
