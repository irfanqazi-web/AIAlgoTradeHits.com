"""Test all API endpoints comprehensively"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

base_url = 'http://localhost:8080/api'

tests = [
    ('Stock Daily', f'{base_url}/stocks/history?symbol=NVDA&limit=100'),
    ('Stock Hourly', f'{base_url}/stocks/15min/history?symbol=NVDA&limit=100'),
    ('Stock 5min', f'{base_url}/stocks/5min/history?symbol=NVDA&limit=100'),
    ('Crypto Daily', f'{base_url}/crypto/daily/history?pair=BTC/USD&limit=100'),
    ('Crypto Hourly', f'{base_url}/crypto/15min/history?pair=BTC/USD&limit=100'),
    ('Crypto 5min', f'{base_url}/crypto/5min/history?pair=BTC/USD&limit=100'),
]

print('Testing All Chart Data Endpoints:')
print('='*70)

issues = []

for name, url in tests:
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        count = data.get('count', 0)
        has_data = len(data.get('data', [])) > 0

        # Check if data has required fields
        if has_data:
            sample = data['data'][0]
            has_ohlc = all(k in sample for k in ['open', 'high', 'low', 'close'])
            has_indicators = 'rsi' in sample and 'macd' in sample
            has_timestamp = 'timestamp' in sample or 'datetime' in sample

            status = 'PASS' if has_ohlc and has_indicators and has_timestamp else 'FAIL'

            if status == 'PASS':
                print(f'✓ {name:20} Count: {count:4}  OHLC: {has_ohlc}  Indicators: {has_indicators}')
            else:
                print(f'✗ {name:20} Count: {count:4}  OHLC: {has_ohlc}  Indicators: {has_indicators}')
                issues.append(f'{name}: Missing fields - OHLC: {has_ohlc}, Indicators: {has_indicators}, Timestamp: {has_timestamp}')
        else:
            print(f'✗ {name:20} NO DATA')
            issues.append(f'{name}: No data returned')
    except Exception as e:
        print(f'✗ {name:20} ERROR: {str(e)[:50]}')
        issues.append(f'{name}: {str(e)[:100]}')

print('\n' + '='*70)

if issues:
    print('\nISSUES FOUND:')
    for i, issue in enumerate(issues, 1):
        print(f'{i}. {issue}')
else:
    print('\n✓ ALL TESTS PASSED - No issues found')

print('='*70)
