"""
Add sector/industry columns to weekly_stocks_all table
and populate from stocks_master_list
"""
import sys
import io
from datetime import datetime, timezone
from google.cloud import bigquery

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"

client = bigquery.Client(project=PROJECT_ID)

print("=" * 60)
print("ADDING SECTOR/INDUSTRY COLUMNS TO WEEKLY TABLES")
print(f"Started: {datetime.now(timezone.utc)}")
print("=" * 60)

# Step 1: Add columns to weekly_stocks_all
print("\n1. Adding columns to weekly_stocks_all...")

alter_queries = [
    "ALTER TABLE `cryptobot-462709.crypto_trading_data.weekly_stocks_all` ADD COLUMN IF NOT EXISTS sector STRING",
    "ALTER TABLE `cryptobot-462709.crypto_trading_data.weekly_stocks_all` ADD COLUMN IF NOT EXISTS industry STRING",
    "ALTER TABLE `cryptobot-462709.crypto_trading_data.weekly_stocks_all` ADD COLUMN IF NOT EXISTS market_cap FLOAT64",
    "ALTER TABLE `cryptobot-462709.crypto_trading_data.weekly_stocks_all` ADD COLUMN IF NOT EXISTS market_cap_category STRING",
]

for query in alter_queries:
    try:
        client.query(query).result()
        col_name = query.split("ADD COLUMN IF NOT EXISTS ")[1].split(" ")[0]
        print(f"   Added: {col_name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            col_name = query.split("ADD COLUMN IF NOT EXISTS ")[1].split(" ")[0]
            print(f"   Exists: {col_name}")
        else:
            print(f"   Error: {e}")

# Step 2: Check stocks_master_list for sector data
print("\n2. Checking stocks_master_list for sector data...")

check_query = """
SELECT
    COUNT(*) as total,
    COUNTIF(sector IS NOT NULL AND sector != '') as with_sector,
    COUNT(DISTINCT sector) as unique_sectors,
    COUNT(DISTINCT industry) as unique_industries
FROM `cryptobot-462709.crypto_trading_data.stocks_master_list`
"""

result = list(client.query(check_query).result())[0]
print(f"   Total stocks in master list: {result.total}")
print(f"   With sector data: {result.with_sector}")
print(f"   Unique sectors: {result.unique_sectors}")
print(f"   Unique industries: {result.unique_industries}")

# Step 3: Update weekly_stocks_all with sector data from master list
print("\n3. Updating weekly_stocks_all with sector data...")

update_query = """
UPDATE `cryptobot-462709.crypto_trading_data.weekly_stocks_all` w
SET
    sector = m.sector,
    industry = m.industry
FROM `cryptobot-462709.crypto_trading_data.stocks_master_list` m
WHERE w.symbol = m.symbol
  AND w.sector IS NULL
"""

try:
    job = client.query(update_query)
    job.result()
    print(f"   Updated {job.num_dml_affected_rows} rows with sector data")
except Exception as e:
    print(f"   Error updating: {e}")

# Step 4: Create sector momentum view
print("\n4. Creating sector momentum view...")

view_query = """
CREATE OR REPLACE VIEW `cryptobot-462709.crypto_trading_data.v_sector_momentum` AS
WITH latest_week AS (
    SELECT MAX(week_start) as max_week
    FROM `cryptobot-462709.crypto_trading_data.weekly_stocks_all`
),
sector_stats AS (
    SELECT
        w.sector,
        COUNT(DISTINCT w.symbol) as stock_count,
        AVG(w.week_change_pct) as avg_change_pct,
        SUM(w.volume) as total_volume,
        AVG(w.close) as avg_price,
        STDDEV(w.week_change_pct) as volatility
    FROM `cryptobot-462709.crypto_trading_data.weekly_stocks_all` w
    CROSS JOIN latest_week lw
    WHERE w.week_start = lw.max_week
      AND w.sector IS NOT NULL
      AND w.sector != ''
    GROUP BY w.sector
)
SELECT
    sector,
    stock_count,
    ROUND(avg_change_pct, 2) as avg_change_pct,
    total_volume,
    ROUND(avg_price, 2) as avg_price,
    ROUND(volatility, 2) as volatility,
    RANK() OVER (ORDER BY avg_change_pct DESC) as momentum_rank
FROM sector_stats
ORDER BY avg_change_pct DESC
"""

try:
    client.query(view_query).result()
    print("   Created view: v_sector_momentum")
except Exception as e:
    print(f"   Error creating view: {e}")

# Step 5: Create top stocks per sector view
print("\n5. Creating top stocks per sector view...")

top_stocks_view = """
CREATE OR REPLACE VIEW `cryptobot-462709.crypto_trading_data.v_top_stocks_by_sector` AS
WITH latest_week AS (
    SELECT MAX(week_start) as max_week
    FROM `cryptobot-462709.crypto_trading_data.weekly_stocks_all`
),
ranked_stocks AS (
    SELECT
        w.symbol,
        w.sector,
        w.industry,
        w.close,
        w.volume,
        w.week_change_pct,
        ROW_NUMBER() OVER (PARTITION BY w.sector ORDER BY w.week_change_pct DESC) as sector_rank
    FROM `cryptobot-462709.crypto_trading_data.weekly_stocks_all` w
    CROSS JOIN latest_week lw
    WHERE w.week_start = lw.max_week
      AND w.sector IS NOT NULL
      AND w.sector != ''
      AND w.week_change_pct IS NOT NULL
)
SELECT
    symbol,
    sector,
    industry,
    close as price,
    volume,
    ROUND(week_change_pct, 2) as week_change_pct,
    sector_rank
FROM ranked_stocks
WHERE sector_rank <= 20
ORDER BY sector, sector_rank
"""

try:
    client.query(top_stocks_view).result()
    print("   Created view: v_top_stocks_by_sector")
except Exception as e:
    print(f"   Error creating view: {e}")

# Step 6: Show current sector momentum (if data exists)
print("\n6. Current Sector Momentum Rankings...")

try:
    momentum_query = """
    SELECT sector, stock_count, avg_change_pct, momentum_rank
    FROM `cryptobot-462709.crypto_trading_data.v_sector_momentum`
    ORDER BY momentum_rank
    LIMIT 15
    """
    results = list(client.query(momentum_query).result())
    if results:
        print("\n   Rank | Sector                    | Stocks | Avg Change %")
        print("   " + "-" * 55)
        for row in results:
            print(f"   {row.momentum_rank:4} | {row.sector:25} | {row.stock_count:6} | {row.avg_change_pct:+.2f}%")
    else:
        print("   No sector data available yet (weekly data still loading)")
except Exception as e:
    print(f"   Error querying momentum: {e}")

print("\n" + "=" * 60)
print("SECTOR COLUMNS ADDED SUCCESSFULLY")
print("=" * 60)
print("""
New columns in weekly_stocks_all:
  - sector: Stock sector (Technology, Healthcare, etc.)
  - industry: Specific industry within sector
  - market_cap: Company market capitalization
  - market_cap_category: mega/large/mid/small/micro

New views created:
  - v_sector_momentum: Weekly sector rankings by avg change %
  - v_top_stocks_by_sector: Top 20 stocks per sector

These support the Sector Momentum Rotation (SMR) strategy.
""")
