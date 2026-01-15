import requests
import json

# Fetch crypto summary
resp = requests.get('https://trading-api-252370699783.us-central1.run.app/api/summary/crypto', timeout=30)
data = resp.json()

# Combine all pairs
all_pairs = []
all_pairs.extend(data['summary']['top_gainers'])
all_pairs.extend(data['summary']['top_losers'])
all_pairs.extend(data['summary']['highest_volume'])

# Remove duplicates
unique_pairs = {}
for p in all_pairs:
    unique_pairs[p['pair']] = p

print(f"Total unique pairs in summary: {len(unique_pairs)}")
print(f"\nSearching for top cryptos:")
print("="*70)

target_coins = {
    'BTC': ['BTCUSD', 'XBTCUSD', 'XXBTZUSD', 'XBTUSD'],
    'ETH': ['ETHUSD', 'XETHUSD', 'XETHZUSD'],
    'BNB': ['BNBUSD'],
    'DOGE': ['DOGEUSD', 'XDGUSD', 'XDGEUSD'],
    'SOL': ['SOLUSD', 'XSOLUSD']
}

for coin, variants in target_coins.items():
    print(f"\n{coin} (checking {', '.join(variants)}):")
    found = False
    for variant in variants:
        if variant in unique_pairs:
            p = unique_pairs[variant]
            print(f"  FOUND {p['pair']}: ${p['close']:.2f} | ROC: {p['roc']:.2f}% | RSI: {p['rsi']:.2f} | Vol: {p['volume']:,.0f}")
            found = True
            break
    if not found:
        print(f"  X Not found in summary (top gainers/losers/volume)")

# Also check if they exist in full dataset by querying individually
print("\n" + "="*70)
print("Direct API check for major cryptos:")
print("="*70)

for coin, variants in target_coins.items():
    for variant in variants:
        try:
            resp = requests.get(
                f'https://trading-api-252370699783.us-central1.run.app/api/crypto/hourly/history',
                params={'pair': variant, 'limit': 1},
                timeout=10
            )
            if resp.ok:
                result = resp.json()
                if result.get('data') and len(result['data']) > 0:
                    candle = result['data'][0]
                    print(f"\n{coin} ({variant}):")
                    print(f"  Latest: {candle.get('datetime', 'N/A')}")
                    print(f"  Close: ${candle.get('close', 0):.2f}")
                    print(f"  RSI: {candle.get('rsi', 0):.2f}")
                    break
        except:
            pass
