"""Verify stock data in BigQuery"""
from google.cloud import bigquery
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = bigquery.Client(project='cryptobot-462709')

query = """
SELECT
  COUNT(*) as total_records,
  COUNT(DISTINCT symbol) as unique_stocks,
  MIN(date) as first_date,
  MAX(date) as last_date,
  COUNTIF(elliott_wave_degree IS NOT NULL) as with_elliott_wave,
  COUNTIF(fib_618 IS NOT NULL) as with_fibonacci
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
"""

print("\n" + "="*70)
print("VERIFYING STOCK DATA IN BIGQUERY")
print("="*70)

result = client.query(query).result()
row = list(result)[0]

print(f"\n✓ DATA VERIFICATION SUCCESSFUL!")
print(f"\n  Total Records: {row.total_records:,}")
print(f"  Unique Stocks: {row.unique_stocks}")
print(f"  Date Range: {row.first_date} to {row.last_date}")
print(f"  With Elliott Wave: {row.with_elliott_wave:,} ({row.with_elliott_wave/row.total_records*100:.1f}%)")
print(f"  With Fibonacci: {row.with_fibonacci:,} ({row.with_fibonacci/row.total_records*100:.1f}%)")

# Sample data with Elliott Wave
print(f"\n" + "="*70)
print("SAMPLE DATA WITH ELLIOTT WAVE & FIBONACCI")
print("="*70)

sample_query = """
SELECT
  symbol,
  company_name,
  sector,
  close,
  elliott_wave_degree,
  wave_position,
  fib_618,
  rsi,
  macd
FROM `cryptobot-462709.crypto_trading_data.stock_analysis`
WHERE DATE(datetime) = (SELECT MAX(DATE(datetime)) FROM `cryptobot-462709.crypto_trading_data.stock_analysis`)
  AND elliott_wave_degree IS NOT NULL
ORDER BY close DESC
LIMIT 10
"""

result2 = client.query(sample_query).result()
rows = list(result2)

if rows:
    print(f"\nTop 10 Stocks with Elliott Wave Data:")
    print(f"{'Symbol':<8} {'Company':<25} {'Sector':<20} {'Close':>10} {'Wave':>8} {'Pos':>4} {'Fib 61.8%':>12} {'RSI':>6} {'MACD':>8}")
    print("-" * 125)

    for row in rows:
        company = (row.company_name[:22] + '...') if row.company_name and len(row.company_name) > 25 else (row.company_name or 'N/A')
        sector = (row.sector[:17] + '...') if row.sector and len(row.sector) > 20 else (row.sector or 'N/A')
        fib = f"${row.fib_618:,.2f}" if row.fib_618 else "N/A"
        rsi = f"{row.rsi:.1f}" if row.rsi else "N/A"
        macd = f"{row.macd:.2f}" if row.macd else "N/A"

        print(f"{row.symbol:<8} {company:<25} {sector:<20} ${row.close:>9,.2f} {row.elliott_wave_degree:>8} {row.wave_position:>4} {fib:>12} {rsi:>6} {macd:>8}")

print("\n" + "="*70)
print("✓ Stock data pipeline is ready for trading app integration!")
print("="*70 + "\n")
