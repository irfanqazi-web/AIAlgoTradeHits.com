from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

print("="*80)
print("ANALYZING stocks_unified_daily TABLE (316 symbols, 1.68M rows)")
print("="*80)

# Check exchange distribution
query = """
SELECT DISTINCT
    symbol,
    exchange,
    name
FROM `aialgotradehits.crypto_trading_data.stocks_unified_daily`
ORDER BY exchange, symbol
LIMIT 400
"""

result = client.query(query).result()

symbols_by_exchange = {}
for row in result:
    symbol = row.symbol or 'NULL'
    exchange = row.exchange or 'UNKNOWN'
    name = (row.name or 'UNKNOWN')[:40]

    if exchange not in symbols_by_exchange:
        symbols_by_exchange[exchange] = []
    symbols_by_exchange[exchange].append(symbol)

print("\nSYMBOLS BY EXCHANGE:")
print("-"*80)
for exchange in sorted(symbols_by_exchange.keys()):
    symbols = symbols_by_exchange[exchange]
    print(f"\n{exchange} ({len(symbols)} symbols):")
    print(f"  {', '.join(sorted(symbols))}")

print("\n" + "="*80)
print("SUMMARY:")
print("="*80)
for exchange in sorted(symbols_by_exchange.keys()):
    count = len(symbols_by_exchange[exchange])
    print(f"  {exchange:15}: {count:4} symbols")

print("\nTOTAL:", sum(len(s) for s in symbols_by_exchange.values()))
print("="*80)
