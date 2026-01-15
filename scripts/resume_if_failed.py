"""
RECOVERY SCRIPT - Resume indicator calculation if overnight process failed
This script checks which symbols already have indicators and only processes the missing ones
"""

from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

print("="*80)
print("CHECKING INDICATOR CALCULATION STATUS")
print("="*80)

# Check overall completion
status_query = """
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as total_symbols,
    COUNTIF(rsi IS NOT NULL) as rows_with_indicators,
    COUNTIF(rsi IS NOT NULL) * 100.0 / COUNT(*) as pct_complete
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
"""

result = client.query(status_query).result()
for row in result:
    print(f"\nTotal rows: {row.total_rows:,}")
    print(f"Total symbols: {row.total_symbols}")
    print(f"Rows with indicators: {row.rows_with_indicators:,}")
    print(f"Completion: {row.pct_complete:.1f}%")

# Get symbols that need processing
missing_query = """
SELECT
    symbol,
    COUNT(*) as total_rows,
    COUNTIF(rsi IS NOT NULL) as rows_with_indicators
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
GROUP BY symbol
HAVING rows_with_indicators = 0
ORDER BY symbol
"""

result = client.query(missing_query).result()
missing_symbols = [row.symbol for row in result]

if len(missing_symbols) == 0:
    print("\n✅ ALL SYMBOLS COMPLETE! No recovery needed.")
else:
    print(f"\n⚠️  {len(missing_symbols)} symbols need indicators:")
    for symbol in missing_symbols:
        print(f"  - {symbol}")

    print(f"\nTo resume, run:")
    print(f"  python calculate_all_indicators.py")
    print(f"\nOr modify the script to only process these {len(missing_symbols)} symbols.")

print("="*80)
