import krakenex
import pandas as pd
import time
from datetime import datetime, timedelta
import json

# Initialize Kraken API
kraken = krakenex.API()

# Step 1: Get all tradable asset pairs
print("Fetching all tradable asset pairs from Kraken...")
pairs_response = kraken.query_public('AssetPairs')

if pairs_response['error']:
    print(f"Error fetching pairs: {pairs_response['error']}")
    exit()

# Filter for USD pairs (most common)
all_pairs = pairs_response['result']
usd_pairs = {k: v for k, v in all_pairs.items() if 'USD' in k and v.get('status') == 'online'}

print(f"\nFound {len(usd_pairs)} USD trading pairs")
print(f"Total pairs available: {len(all_pairs)}")

# Save pairs list
pairs_df = pd.DataFrame([
    {
        'pair': k,
        'base': v.get('base'),
        'quote': v.get('quote'),
        'wsname': v.get('wsname', ''),
        'altname': v.get('altname', '')
    }
    for k, v in usd_pairs.items()
])
pairs_df.to_csv('kraken_usd_pairs.csv', index=False)
print(f"\nSaved {len(pairs_df)} USD pairs to kraken_usd_pairs.csv")

# Step 2: Fetch 6 months of OHLC data for each pair
print("\n" + "="*60)
print("Starting to fetch 6 months of OHLC data for all pairs...")
print("="*60)

# Calculate timestamp for 6 months ago
six_months_ago = datetime.now() - timedelta(days=180)
since_timestamp = int(six_months_ago.timestamp())

all_ohlc_data = []
failed_pairs = []
successful_pairs = 0

for idx, (pair, info) in enumerate(usd_pairs.items(), 1):
    try:
        print(f"\n[{idx}/{len(usd_pairs)}] Fetching {pair} ({info.get('altname', pair)})...", end=' ')

        # Fetch OHLC data (1 day interval = 1440 minutes)
        # Using daily candles to get 6 months of data efficiently
        ohlc_response = kraken.query_public('OHLC', {
            'pair': pair,
            'interval': 1440,  # Daily candles
            'since': since_timestamp
        })

        if ohlc_response['error']:
            print(f"ERROR: {ohlc_response['error']}")
            failed_pairs.append({'pair': pair, 'error': str(ohlc_response['error'])})
            continue

        # Parse OHLC data
        ohlc_list = list(ohlc_response['result'].values())[0]  # Get the data array

        for candle in ohlc_list:
            all_ohlc_data.append({
                'pair': pair,
                'altname': info.get('altname', pair),
                'base': info.get('base', ''),
                'quote': info.get('quote', ''),
                'timestamp': candle[0],
                'datetime': datetime.fromtimestamp(candle[0]).strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'vwap': float(candle[5]),
                'volume': float(candle[6]),
                'count': int(candle[7])
            })

        successful_pairs += 1
        print(f"OK - Got {len(ohlc_list)} candles")

        # Rate limiting: Kraken allows 1 call per second for public API
        time.sleep(1.5)

    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        failed_pairs.append({'pair': pair, 'error': str(e)})
        time.sleep(2)

# Step 3: Save all data
print("\n" + "="*60)
print("Saving data...")
print("="*60)

# Save OHLC data
if all_ohlc_data:
    ohlc_df = pd.DataFrame(all_ohlc_data)
    ohlc_df.to_csv('kraken_6month_ohlc_data.csv', index=False)
    print(f"\nOK - Saved {len(ohlc_df)} OHLC records to kraken_6month_ohlc_data.csv")
    print(f"  - Covering {successful_pairs} pairs")
    print(f"  - Date range: {ohlc_df['datetime'].min()} to {ohlc_df['datetime'].max()}")
else:
    print("\nERROR - No OHLC data collected")

# Save failed pairs
if failed_pairs:
    failed_df = pd.DataFrame(failed_pairs)
    failed_df.to_csv('kraken_failed_pairs.csv', index=False)
    print(f"\nERROR - {len(failed_pairs)} pairs failed - saved to kraken_failed_pairs.csv")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total USD pairs attempted: {len(usd_pairs)}")
print(f"Successfully fetched: {successful_pairs}")
print(f"Failed: {len(failed_pairs)}")
print(f"Total OHLC records: {len(all_ohlc_data)}")
print("\nFiles created:")
print("  1. kraken_usd_pairs.csv - List of all USD trading pairs")
print("  2. kraken_6month_ohlc_data.csv - 6 months of OHLC data")
if failed_pairs:
    print("  3. kraken_failed_pairs.csv - Failed pairs for debugging")
