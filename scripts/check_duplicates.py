from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

# Check hourly duplicates
print("Checking hourly data duplicates...")
query_hourly = """
SELECT COUNT(*) as total_dups
FROM (
    SELECT symbol, datetime, COUNT(*) as dup_count
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    GROUP BY symbol, datetime
    HAVING COUNT(*) > 1
)
"""
result_hourly = client.query(query_hourly).to_dataframe()
print(f"Hourly duplicate (symbol, datetime) pairs: {result_hourly['total_dups'].values[0]}")

# Check daily duplicates
print("\nChecking daily data duplicates...")
query_daily = """
SELECT COUNT(*) as total_dups
FROM (
    SELECT symbol, datetime, COUNT(*) as dup_count
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    GROUP BY symbol, datetime
    HAVING COUNT(*) > 1
)
"""
result_daily = client.query(query_daily).to_dataframe()
print(f"Daily duplicate (symbol, datetime) pairs: {result_daily['total_dups'].values[0]}")

print("\nDone!")
