from google.cloud import bigquery

client = bigquery.Client(project='cryptobot-462709')

# Get table schema
table_ref = client.dataset('crypto_trading_data').table('crypto_hourly_data')
table = client.get_table(table_ref)

print("Hourly table schema:")
print("="*70)
for field in table.schema:
    print(f"{field.name:30} {field.field_type}")

print("\n\nChecking which fields exist:")
query = """
SELECT * FROM `cryptobot-462709.crypto_trading_data.crypto_hourly_data`
LIMIT 1
"""
results = client.query(query).result()
for row in results:
    print("\nAvailable fields:")
    print(row.keys())
    break
