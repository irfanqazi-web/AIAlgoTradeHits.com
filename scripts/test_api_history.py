import urllib.request
import json

# Test with ETHUSD
try:
    r = urllib.request.urlopen('https://trading-api-252370699783.us-central1.run.app/api/crypto/hourly/history?pair=ETHUSD&limit=3')
    data = json.loads(r.read())
    print(f'Success: {data.get("success")}')
    print(f'Count: {data.get("count")} candles')
    if data.get('data'):
        first = data['data'][0]
        print(f'First candle: {first["datetime"]} close: ${first["close"]}')
        print(f'Has RSI: {first.get("rsi")}')
        print(f'Has MACD: {first.get("macd")}')
        print('API TEST: PASSED')
except Exception as e:
    print(f'Error: {e}')
    print('API TEST: FAILED')
