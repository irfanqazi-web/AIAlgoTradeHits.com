"""Check data freshness in BigQuery tables"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timezone

client = bigquery.Client(project='aialgotradehits')

tables = [
    'v2_stocks_daily',
    'v2_crypto_daily',
    'v2_forex_daily',
    'v2_etfs_daily',
    'v2_indices_daily',
    'v2_commodities_daily'
]

print('DATA FRESHNESS REPORT')
print('=' * 70)
print(f'Report Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 70)

for table in tables:
    try:
        query = f"""
        SELECT
            COUNT(*) as total,
            MAX(datetime) as latest,
            COUNT(DISTINCT symbol) as symbols
        FROM `aialgotradehits.crypto_trading_data.{table}`
        """
        result = list(client.query(query).result())[0]
        latest = result.latest
        if latest:
            days = (datetime.now(timezone.utc) - latest.replace(tzinfo=timezone.utc)).days
            status = "FRESH" if days <= 1 else "STALE"
            print(f'{table}:')
            print(f'  Records: {result.total:,}')
            print(f'  Symbols: {result.symbols}')
            print(f'  Latest:  {latest.date()} ({days}d ago) [{status}]')
        else:
            print(f'{table}: No data')
    except Exception as e:
        print(f'{table}: Error - {str(e)[:50]}')
    print()

print('=' * 70)
print('Data refresh complete!')
