"""
Add 11 institutional indicator columns to stocks_daily_clean table
"""
from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

# Define the 11 new columns
new_columns = [
    "mfi FLOAT64",
    "cmf FLOAT64",
    "ichimoku_tenkan FLOAT64",
    "ichimoku_kijun FLOAT64",
    "ichimoku_senkou_a FLOAT64",
    "ichimoku_senkou_b FLOAT64",
    "ichimoku_chikou FLOAT64",
    "vwap_daily FLOAT64",
    "vwap_weekly FLOAT64",
    "volume_profile_poc FLOAT64",
    "volume_profile_vah FLOAT64",
    "volume_profile_val FLOAT64"
]

table_id = "aialgotradehits.crypto_trading_data.stocks_daily_clean"

print("="*100)
print("ADDING 11 INSTITUTIONAL INDICATOR COLUMNS TO stocks_daily_clean")
print("="*100)

for i, column_def in enumerate(new_columns, 1):
    column_name = column_def.split()[0]
    try:
        query = f"ALTER TABLE `{table_id}` ADD COLUMN IF NOT EXISTS {column_def}"
        client.query(query).result()
        print(f"[{i}/12] Added column: {column_name}")
    except Exception as e:
        print(f"[{i}/12] Column {column_name}: {e}")

print("\n" + "="*100)
print("COLUMN ADDITION COMPLETE")
print("="*100)
