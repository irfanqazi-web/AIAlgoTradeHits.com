from google.cloud import bigquery

client = bigquery.Client(project='cryptobot-462709')

tables = [
    'stock_analysis',
    'stock_hourly_data',
    'stock_5min_top10_gainers'
]

print("Stock Data Tables Status:")
print("="*70)

for table_name in tables:
    query = f"""
    SELECT
        COUNT(*) as count,
        MAX(datetime) as latest,
        MIN(datetime) as earliest,
        COUNT(DISTINCT symbol) as symbols
    FROM `cryptobot-462709.crypto_trading_data.{table_name}`
    """

    try:
        result = list(client.query(query).result())[0]
        print(f"\n{table_name}:")
        print(f"  Records: {result.count:,}")
        print(f"  Symbols: {result.symbols}")
        print(f"  Earliest: {result.earliest}")
        print(f"  Latest: {result.latest}")

        if result.count > 0:
            # Get sample records
            sample_query = f"""
            SELECT symbol, datetime, close, rsi, macd
            FROM `cryptobot-462709.crypto_trading_data.{table_name}`
            ORDER BY datetime DESC
            LIMIT 3
            """
            samples = list(client.query(sample_query).result())
            print(f"  Recent samples:")
            for s in samples:
                print(f"    {s.symbol}: {s.datetime} | Close: ${s.close:.2f} | RSI: {s.rsi:.2f}")
    except Exception as e:
        print(f"\n{table_name}: ERROR - {str(e)}")

print("\n" + "="*70)
