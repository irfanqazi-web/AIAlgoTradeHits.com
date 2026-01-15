from google.cloud import bigquery

client = bigquery.Client(project='cryptobot-462709')

query = """
SELECT DISTINCT pair
FROM `cryptobot-462709.crypto_trading_data.crypto_hourly_data`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR)
ORDER BY pair
LIMIT 100
"""

results = client.query(query).result()
pairs = [row.pair for row in results]

print(f'Found {len(pairs)} unique pairs in last 3 hours:')
print(pairs[:20])
print('\nChecking for BTC pairs...')
btc_pairs = [p for p in pairs if 'BTC' in p.upper()]
print(f'BTC pairs: {btc_pairs}')
