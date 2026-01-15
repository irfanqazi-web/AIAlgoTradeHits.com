import urllib.request
import json

# Test with AAVEUSD (known to exist)
print("Testing API with AAVEUSD...")
try:
    r = urllib.request.urlopen('https://trading-api-252370699783.us-central1.run.app/api/crypto/hourly/history?pair=AAVEUSD&limit=5')
    data = json.loads(r.read())
    print(f'Success: {data.get("success")}')
    print(f'Count: {data.get("count")} candles')
    if data.get('data') and len(data['data']) > 0:
        first = data['data'][0]
        print(f'First candle: {first["datetime"]} close: ${first["close"]}')
        print(f'Has RSI: {first.get("rsi")}')
        print(f'Has MACD: {first.get("macd")}')
        print(f'Has SMA_20: {first.get("sma_20")}')
        print(f'Has SMA_50: {first.get("sma_50")}')
        print('\n*** API TEST: PASSED ***')
    else:
        print('No data returned')
except Exception as e:
    print(f'Error: {e}')
    print('\n*** API TEST: FAILED ***')

# Test summary endpoint
print("\n\nTesting market summary endpoint...")
try:
    r = urllib.request.urlopen('https://trading-api-252370699783.us-central1.run.app/api/summary/crypto')
    data = json.loads(r.read())
    print(f'Success: {data.get("success")}')
    if data.get('summary'):
        summary = data['summary']
        print(f'Total pairs: {summary.get("total_pairs")}')
        print(f'Top gainers count: {len(summary.get("top_gainers", []))}')
        print(f'Top losers count: {len(summary.get("top_losers", []))}')
        print('\n*** SUMMARY TEST: PASSED ***')
except Exception as e:
    print(f'Error: {e}')
    print('\n*** SUMMARY TEST: FAILED ***')
