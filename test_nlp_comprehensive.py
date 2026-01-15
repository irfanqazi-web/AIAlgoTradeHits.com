"""
Comprehensive NLP Engine Test
Tests all query types after table renaming
"""
import requests
import json
import sys
import io
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = 'https://trading-api-cnyn5l4u2a-uc.a.run.app/api/nlp/query'

test_queries = [
    ('daily oversold crypto', 'daily_crypto', 'crypto'),
    ('Bitcoin daily', 'daily_crypto', 'crypto'),
    ('hourly overbought crypto', 'hourly_crypto', 'crypto'),
    ('Ethereum hourly', 'hourly_crypto', 'crypto'),
    ('5 minute top gainers crypto', '5min_crypto', 'crypto'),
    ('daily oversold stocks', 'daily_stock', 'stock'),
    ('Tesla', 'daily_stock', 'stock'),
    ('Netflix', 'daily_stock', 'stock'),
    ('hourly AAPL', 'hourly_stock', 'stock'),
    ('5 minute stock gainers', '5min_stock', 'stock'),
]

print('=' * 80)
print('NLP ENGINE TEST - POST TABLE NAME FIX')
print(f'Time: {datetime.now()}')
print('=' * 80)
print()

passed = 0
warnings = 0
failed = 0

for query, expected_table, expected_market in test_queries:
    try:
        response = requests.post(API_URL, json={'query': query}, timeout=30)

        if response.status_code == 200:
            data = response.json()

            interp = data.get('interpretation', {})
            table_used = interp.get('table', '').split('.')[-1].replace('`', '')
            market = interp.get('market', '')
            timeframe = interp.get('timeframe', '')
            count = data.get('count', 0)

            correct_table = expected_table in table_used
            correct_market = expected_market == market

            if correct_table and correct_market:
                if count > 0:
                    status = '✅ PASS'
                    passed += 1
                else:
                    status = '⚠️ EMPTY'
                    warnings += 1
            else:
                status = '❌ FAIL'
                failed += 1

            print(f'{status} "{query}"')
            print(f'   Table: {table_used} | Market: {market} | TF: {timeframe}')
            print(f'   Results: {count}')
            print()
        else:
            print(f'❌ HTTP {response.status_code}: "{query}"')
            print(f'   Error: {response.text[:100]}')
            print()
            failed += 1

    except Exception as e:
        print(f'❌ ERROR: "{query}"')
        print(f'   {str(e)[:100]}')
        print()
        failed += 1

print('=' * 80)
print('SUMMARY')
print('=' * 80)
total = len(test_queries)
print(f'✅ Passed (correct table + data): {passed}/{total} ({passed/total*100:.0f}%)')
print(f'⚠️ Warnings (correct table, empty): {warnings}/{total} ({warnings/total*100:.0f}%)')
print(f'❌ Failed: {failed}/{total} ({failed/total*100:.0f}%)')
print(f'')
print(f'Table Routing Accuracy: {((passed+warnings)/total*100):.0f}%')
print(f'Data Availability: {(passed/(passed+warnings)*100 if (passed+warnings) > 0 else 0):.0f}%')
print()
