"""
Create Top 20 ETF Reference Table in BigQuery
Based on comprehensive ETF analysis document
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 60)
print("CREATING TOP 20 ETF REFERENCE TABLE")
print("=" * 60)

# Top 20 ETFs by AUM with metadata from analysis document
TOP_20_ETFS = [
    # S&P 500 ETFs
    {'symbol': 'VOO', 'name': 'Vanguard S&P 500 ETF', 'category': 'S&P 500', 'aum_billions': 848.55,
     'expense_ratio': 0.03, 'return_1y': 17.61, 'return_5y': 14.76, 'issuer': 'Vanguard'},
    {'symbol': 'IVV', 'name': 'iShares Core S&P 500 ETF', 'category': 'S&P 500', 'aum_billions': 784.42,
     'expense_ratio': 0.03, 'return_1y': 17.64, 'return_5y': 14.76, 'issuer': 'BlackRock'},
    {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF Trust', 'category': 'S&P 500', 'aum_billions': 713.16,
     'expense_ratio': 0.09, 'return_1y': 17.56, 'return_5y': 14.69, 'issuer': 'State Street'},
    {'symbol': 'SPLG', 'name': 'SPDR Portfolio S&P 500 ETF', 'category': 'S&P 500', 'aum_billions': 101.10,
     'expense_ratio': 0.02, 'return_1y': 17.68, 'return_5y': 14.78, 'issuer': 'State Street'},

    # Total Market
    {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'category': 'Total US Market', 'aum_billions': 577.62,
     'expense_ratio': 0.03, 'return_1y': 17.19, 'return_5y': 13.41, 'issuer': 'Vanguard'},

    # Growth & Technology
    {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'category': 'Growth/Tech', 'aum_billions': 406.40,
     'expense_ratio': 0.20, 'return_1y': 19.45, 'return_5y': 15.87, 'issuer': 'Invesco'},
    {'symbol': 'VUG', 'name': 'Vanguard Growth ETF', 'category': 'Growth', 'aum_billions': 203.34,
     'expense_ratio': 0.04, 'return_1y': 16.92, 'return_5y': 15.19, 'issuer': 'Vanguard'},
    {'symbol': 'VGT', 'name': 'Vanguard Information Technology ETF', 'category': 'Technology', 'aum_billions': 113.45,
     'expense_ratio': 0.10, 'return_1y': 20.01, 'return_5y': 18.12, 'issuer': 'Vanguard'},
    {'symbol': 'IWF', 'name': 'iShares Russell 1000 Growth ETF', 'category': 'Growth', 'aum_billions': 124.52,
     'expense_ratio': 0.19, 'return_1y': 15.94, 'return_5y': 15.72, 'issuer': 'BlackRock'},

    # Value
    {'symbol': 'VTV', 'name': 'Vanguard Value ETF', 'category': 'Value', 'aum_billions': 160.75,
     'expense_ratio': 0.04, 'return_1y': 17.89, 'return_5y': 12.80, 'issuer': 'Vanguard'},

    # International Developed
    {'symbol': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'category': 'International Developed', 'aum_billions': 198.17,
     'expense_ratio': 0.05, 'return_1y': 36.92, 'return_5y': 9.19, 'issuer': 'Vanguard'},
    {'symbol': 'IEFA', 'name': 'iShares Core MSCI EAFE ETF', 'category': 'International Developed', 'aum_billions': 167.13,
     'expense_ratio': 0.07, 'return_1y': 33.60, 'return_5y': 8.66, 'issuer': 'BlackRock'},
    {'symbol': 'VXUS', 'name': 'Vanguard Total International Stock ETF', 'category': 'International Total', 'aum_billions': 123.54,
     'expense_ratio': 0.07, 'return_1y': 34.64, 'return_5y': 7.70, 'issuer': 'Vanguard'},

    # Emerging Markets
    {'symbol': 'IEMG', 'name': 'iShares Core MSCI Emerging Markets ETF', 'category': 'Emerging Markets', 'aum_billions': 115.23,
     'expense_ratio': 0.09, 'return_1y': 30.46, 'return_5y': 5.27, 'issuer': 'BlackRock'},
    {'symbol': 'VWO', 'name': 'Vanguard FTSE Emerging Markets ETF', 'category': 'Emerging Markets', 'aum_billions': 104.89,
     'expense_ratio': 0.08, 'return_1y': 30.18, 'return_5y': 4.99, 'issuer': 'Vanguard'},

    # Bonds
    {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'category': 'Bonds', 'aum_billions': 125.67,
     'expense_ratio': 0.03, 'return_1y': 2.87, 'return_5y': -0.42, 'issuer': 'Vanguard'},
    {'symbol': 'AGG', 'name': 'iShares Core U.S. Aggregate Bond ETF', 'category': 'Bonds', 'aum_billions': 123.45,
     'expense_ratio': 0.03, 'return_1y': 2.75, 'return_5y': -0.56, 'issuer': 'BlackRock'},

    # Mid-Cap & Dividend
    {'symbol': 'IJH', 'name': 'iShares Core S&P Mid-Cap ETF', 'category': 'Mid-Cap', 'aum_billions': 105.34,
     'expense_ratio': 0.05, 'return_1y': 14.23, 'return_5y': 9.87, 'issuer': 'BlackRock'},
    {'symbol': 'VIG', 'name': 'Vanguard Dividend Appreciation ETF', 'category': 'Dividend Growth', 'aum_billions': 101.56,
     'expense_ratio': 0.06, 'return_1y': 18.45, 'return_5y': 12.34, 'issuer': 'Vanguard'},

    # Commodities
    {'symbol': 'GLD', 'name': 'SPDR Gold Shares', 'category': 'Gold', 'aum_billions': 108.90,
     'expense_ratio': 0.40, 'return_1y': 69.90, 'return_5y': 12.56, 'issuer': 'State Street'},
]

# Create table
create_table_sql = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.top20_etf_reference` (
    symbol STRING NOT NULL,
    name STRING,
    category STRING,
    aum_billions FLOAT64,
    expense_ratio FLOAT64,
    return_1y FLOAT64,
    return_5y FLOAT64,
    issuer STRING,
    rank INT64,
    is_top20 BOOL,
    updated_at TIMESTAMP
)
"""

print("\nCreating table...")
bq_client.query(create_table_sql).result()
print("  Table created: top20_etf_reference")

# Insert data
print("\nInserting ETF data...")
rows_to_insert = []
for i, etf in enumerate(TOP_20_ETFS, 1):
    rows_to_insert.append({
        'symbol': etf['symbol'],
        'name': etf['name'],
        'category': etf['category'],
        'aum_billions': etf['aum_billions'],
        'expense_ratio': etf['expense_ratio'],
        'return_1y': etf['return_1y'],
        'return_5y': etf['return_5y'],
        'issuer': etf['issuer'],
        'rank': i,
        'is_top20': True,
        'updated_at': datetime.utcnow().isoformat()
    })

# Use load job for insert
import pandas as pd
df = pd.DataFrame(rows_to_insert)
df['updated_at'] = pd.to_datetime(df['updated_at'])

table_ref = f"{PROJECT_ID}.{DATASET_ID}.top20_etf_reference"
job = bq_client.load_table_from_dataframe(df, table_ref)
job.result()

print(f"  Inserted {len(TOP_20_ETFS)} ETFs")

# Verify
verify_query = f"""
SELECT symbol, name, category, aum_billions, return_1y, return_5y
FROM `{PROJECT_ID}.{DATASET_ID}.top20_etf_reference`
ORDER BY aum_billions DESC
LIMIT 10
"""

print("\nTop 10 ETFs by AUM:")
print("-" * 80)
for row in bq_client.query(verify_query).result():
    print(f"  {row.symbol:6} | ${row.aum_billions:,.0f}B | 1Y: {row.return_1y:+.2f}% | 5Y: {row.return_5y:+.2f}% | {row.name[:40]}")

# Summary by category
cat_query = f"""
SELECT
    category,
    COUNT(*) as count,
    ROUND(SUM(aum_billions), 1) as total_aum_b,
    ROUND(AVG(return_1y), 2) as avg_1y_return,
    ROUND(AVG(return_5y), 2) as avg_5y_return
FROM `{PROJECT_ID}.{DATASET_ID}.top20_etf_reference`
GROUP BY category
ORDER BY total_aum_b DESC
"""

print("\n\nAUM by Category:")
print("-" * 80)
for row in bq_client.query(cat_query).result():
    print(f"  {row.category:25} | {row.count} ETFs | ${row.total_aum_b:,.0f}B | 1Y: {row.avg_1y_return:+.2f}% | 5Y: {row.avg_5y_return:+.2f}%")

print("\n" + "=" * 60)
print("TOP 20 ETF REFERENCE TABLE CREATED SUCCESSFULLY")
print("=" * 60)
print(f"""
Table: {PROJECT_ID}.{DATASET_ID}.top20_etf_reference

Query Example:
SELECT e.*, r.category, r.aum_billions, r.expense_ratio
FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean` e
JOIN `{PROJECT_ID}.{DATASET_ID}.top20_etf_reference` r ON e.symbol = r.symbol
WHERE r.is_top20 = TRUE
ORDER BY r.rank

Completed: {datetime.now()}
""")
