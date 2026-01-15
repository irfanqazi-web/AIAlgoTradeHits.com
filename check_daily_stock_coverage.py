from google.cloud import bigquery

# Initialize client
client = bigquery.Client(project='aialgotradehits')

print("="*80)
print("CHECKING DAILY STOCK TABLE COVERAGE")
print("="*80)

# Query 1: Check symbols in v2_stocks_daily with their exchange info
query1 = """
SELECT DISTINCT
    d.symbol,
    COALESCE(m.exchange, 'UNKNOWN') as exchange,
    COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
    COALESCE(m.name, 'UNKNOWN') as name
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily` d
LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
    ON d.symbol = m.symbol
ORDER BY exchange, symbol
"""

print("\n1. SYMBOLS IN v2_stocks_daily (106 symbols):")
print("-"*80)
result1 = client.query(query1).result()

symbols_by_exchange = {}
all_symbols = []
for row in result1:
    symbol = row.symbol or 'NULL'
    exchange = row.exchange or 'UNKNOWN'
    mic_code = row.mic_code or 'UNKNOWN'
    name = (row.name or 'UNKNOWN')[:40]  # Truncate long names

    if exchange not in symbols_by_exchange:
        symbols_by_exchange[exchange] = []
    symbols_by_exchange[exchange].append(symbol)
    all_symbols.append(symbol)

    print(f"{symbol:8} {exchange:10} {mic_code:10} {name}")

print(f"\nTotal symbols: {len(all_symbols)}")

# Print summary by exchange
print("\n2. SUMMARY BY EXCHANGE:")
print("-"*80)
for exchange, symbols in sorted(symbols_by_exchange.items()):
    print(f"{exchange:15}: {len(symbols):4} symbols - {', '.join(sorted(symbols)[:10])}" +
          (f"... (+{len(symbols)-10} more)" if len(symbols) > 10 else ""))

# Query 2: Check allowed MIC codes (NASDAQ, NYSE, CBOE)
allowed_mic_codes = ['XNAS', 'XNGS', 'XNCM', 'XNMS', 'XNYS', 'ARCX', 'XASE', 'BATS', 'CBOE', 'XCBO']
print(f"\n3. SYMBOLS WITH ALLOWED MIC CODES:")
print(f"   Allowed: {', '.join(allowed_mic_codes)}")
print("-"*80)

allowed_symbols = [s for s, symbols in symbols_by_exchange.items() if s in ['NASDAQ', 'NYSE', 'CBOE']]
allowed_count = sum(len(symbols_by_exchange.get(ex, [])) for ex in ['NASDAQ', 'NYSE', 'CBOE'])

query2 = """
SELECT
    m.exchange,
    m.mic_code,
    COUNT(DISTINCT d.symbol) as symbol_count
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily` d
INNER JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
    ON d.symbol = m.symbol
WHERE m.mic_code IN UNNEST(@mic_codes)
GROUP BY m.exchange, m.mic_code
ORDER BY m.exchange, m.mic_code
"""

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ArrayQueryParameter("mic_codes", "STRING", allowed_mic_codes)
    ]
)
result2 = client.query(query2, job_config=job_config).result()

total_allowed = 0
for row in result2:
    print(f"  {row.exchange:10} {row.mic_code:10}: {row.symbol_count:4} symbols")
    total_allowed += row.symbol_count

print(f"\nTotal symbols with allowed MIC codes: {total_allowed}")
print(f"Total symbols with rejected MIC codes (OTC/Pink): {len(all_symbols) - total_allowed}")

# Query 3: Check stocks_unified_daily
print("\n4. CHECKING stocks_unified_daily:")
print("-"*80)
query3 = """
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(datetime) as min_date,
    MAX(datetime) as max_date
FROM `aialgotradehits.crypto_trading_data.stocks_unified_daily`
"""
try:
    result3 = client.query(query3).result()
    for row in result3:
        print(f"  Total rows: {row.total_rows:,}")
        print(f"  Unique symbols: {row.unique_symbols:,}")
        print(f"  Date range: {row.min_date} to {row.max_date}")
except Exception as e:
    print(f"  Error: {e}")

# Query 4: Check v2_stocks_historical_daily
print("\n5. CHECKING v2_stocks_historical_daily:")
print("-"*80)
query4 = """
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(datetime) as min_date,
    MAX(datetime) as max_date
FROM `aialgotradehits.crypto_trading_data.v2_stocks_historical_daily`
"""
try:
    result4 = client.query(query4).result()
    for row in result4:
        print(f"  Total rows: {row.total_rows:,}")
        print(f"  Unique symbols: {row.unique_symbols:,}")
        print(f"  Date range: {row.min_date} to {row.max_date}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*80)
print("RECOMMENDATIONS:")
print("="*80)
print(f"1. Current v2_stocks_daily has {len(all_symbols)} symbols")
print(f"2. After filtering to NASDAQ/NYSE/CBOE: {total_allowed} symbols")
print(f"3. Need to add more symbols from:")
print(f"   - S&P 500 index (~500 large-cap stocks)")
print(f"   - NASDAQ 100 (~100 largest NASDAQ stocks)")
print(f"   - Russell 2000 (~2000 small-cap stocks)")
print(f"   - Liquid ETFs (top 50-100 ETFs)")
print(f"\n4. Current coverage appears LIMITED - only {len(all_symbols)} symbols")
print(f"   Recommended: Expand to at least 500-1000 symbols for comprehensive coverage")
print("="*80)
