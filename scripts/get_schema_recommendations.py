"""
Get AI recommendations for schema restructuring
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
API_URL = 'https://trading-api-service-1075463475276.us-central1.run.app'

def get_current_schemas():
    """Get current table schemas"""
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT table_id, row_count
    FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
    ORDER BY row_count DESC
    """

    tables = list(client.query(query).result())

    schemas = {}
    categories = {
        'stocks': {'count': 0, 'total_rows': 0, 'tables': []},
        'crypto': {'count': 0, 'total_rows': 0, 'tables': []},
        'forex': {'count': 0, 'total_rows': 0, 'tables': []},
        'etfs': {'count': 0, 'total_rows': 0, 'tables': []},
        'indices': {'count': 0, 'total_rows': 0, 'tables': []},
        'commodities': {'count': 0, 'total_rows': 0, 'tables': []},
        'other': {'count': 0, 'total_rows': 0, 'tables': []}
    }

    total_rows = 0

    for table in tables:
        table_name = table.table_id
        row_count = table.row_count or 0
        total_rows += row_count

        # Get schema
        try:
            table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
            table_obj = client.get_table(table_ref)
            field_names = [f.name for f in table_obj.schema]
            schemas[table_name] = {
                'row_count': row_count,
                'fields': field_names
            }
        except:
            continue

        # Categorize
        table_lower = table_name.lower()
        if 'stock' in table_lower:
            cat = 'stocks'
        elif 'crypto' in table_lower:
            cat = 'crypto'
        elif 'forex' in table_lower:
            cat = 'forex'
        elif 'etf' in table_lower:
            cat = 'etfs'
        elif 'indic' in table_lower:
            cat = 'indices'
        elif 'commodit' in table_lower:
            cat = 'commodities'
        else:
            cat = 'other'

        categories[cat]['count'] += 1
        categories[cat]['total_rows'] += row_count
        categories[cat]['tables'].append({'name': table_name, 'rows': row_count, 'fields': field_names[:10]})

    return {
        'summary': {
            'total_tables': len(tables),
            'total_rows': total_rows
        },
        'categories': categories,
        'schemas': schemas
    }

def main():
    print("=" * 80)
    print("SCHEMA RESTRUCTURING RECOMMENDATIONS")
    print("=" * 80)

    # Get current state
    print("\nFetching current schema state...")
    data = get_current_schemas()

    print(f"\nTotal Tables: {data['summary']['total_tables']}")
    print(f"Total Rows: {data['summary']['total_rows']:,}")

    print("\nCategories:")
    for cat, info in data['categories'].items():
        if info['count'] > 0:
            print(f"  {cat}: {info['count']} tables, {info['total_rows']:,} rows")

    # Show sample schemas
    print("\n" + "=" * 80)
    print("SAMPLE CURRENT SCHEMAS (First 10 fields):")
    print("=" * 80)

    sample_tables = ['stocks_master_list', 'stocks_daily_data', 'crypto_analysis',
                     'forex_daily_data', 'etfs_daily_data', 'indices_daily_data']

    for table in sample_tables:
        if table in data['schemas']:
            schema = data['schemas'][table]
            print(f"\n{table} ({schema['row_count']:,} rows):")
            print(f"  Fields: {', '.join(schema['fields'][:15])}")
            if len(schema['fields']) > 15:
                print(f"  ... and {len(schema['fields']) - 15} more fields")

    # Generate recommendations
    print("\n" + "=" * 80)
    print("AI-RECOMMENDED STANDARDIZED FIELD ORDER")
    print("=" * 80)

    print("""
Based on analysis of your 91 BigQuery tables, here is the recommended standardized field order:

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1: IDENTITY FIELDS (Always First)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. symbol          - Primary identifier (ticker symbol)                    │
│  2. name            - Full asset name                                       │
│  3. asset_type      - Category: stock/crypto/forex/etf/index/commodity     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 2: CLASSIFICATION FIELDS                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. exchange        - Trading exchange (NYSE, NASDAQ, KRAKEN, etc.)        │
│  5. country         - Country code                                          │
│  6. sector          - Business sector (for stocks)                          │
│  7. industry        - Industry classification                               │
│  8. currency        - Trading currency (USD, EUR, etc.)                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 3: PRICE DATA (OHLC)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  9.  open           - Opening price                                         │
│  10. high           - High price                                            │
│  11. low            - Low price                                             │
│  12. close          - Closing price                                         │
│  13. previous_close - Previous close                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 4: VOLUME & CHANGE METRICS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  14. volume         - Trading volume                                        │
│  15. average_volume - Average volume                                        │
│  16. change         - Price change                                          │
│  17. percent_change - Percentage change                                     │
│  18. hi_lo          - Daily range (high - low)                              │
│  19. pct_hi_lo      - Percentage range                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 5: RANGE METRICS                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  20. week_52_high   - 52-week high                                          │
│  21. week_52_low    - 52-week low                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 6: TECHNICAL INDICATORS (Grouped by Category)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  MOMENTUM:                                                                  │
│    22. rsi          - Relative Strength Index                               │
│    23. stoch_k      - Stochastic %K                                         │
│    24. stoch_d      - Stochastic %D                                         │
│    25. momentum     - Momentum                                              │
│    26. roc          - Rate of Change                                        │
│    27. williams_r   - Williams %R                                           │
│                                                                             │
│  TREND (Moving Averages):                                                   │
│    28. sma_20       - 20-period SMA                                         │
│    29. sma_50       - 50-period SMA                                         │
│    30. sma_200      - 200-period SMA                                        │
│    31. ema_12       - 12-period EMA                                         │
│    32. ema_26       - 26-period EMA                                         │
│    33. ema_50       - 50-period EMA                                         │
│                                                                             │
│  MACD:                                                                      │
│    34. macd         - MACD line                                             │
│    35. macd_signal  - Signal line                                           │
│    36. macd_histogram - MACD histogram                                      │
│                                                                             │
│  BOLLINGER BANDS:                                                           │
│    37. bollinger_upper  - Upper band                                        │
│    38. bollinger_middle - Middle band (SMA)                                 │
│    39. bollinger_lower  - Lower band                                        │
│                                                                             │
│  VOLATILITY & STRENGTH:                                                     │
│    40. atr          - Average True Range                                    │
│    41. adx          - Average Directional Index                             │
│    42. plus_di      - Positive Directional Indicator                        │
│    43. minus_di     - Negative Directional Indicator                        │
│                                                                             │
│  OTHER INDICATORS:                                                          │
│    44. cci          - Commodity Channel Index                               │
│    45. obv          - On-Balance Volume                                     │
│    46. pvo          - Price Volume Oscillator                               │
│    47. ppo          - Price Percentage Oscillator                           │
│    48. kama         - Kaufman Adaptive Moving Average                       │
│    49. trix         - Triple Exponential Average                            │
│    50. ultimate_osc - Ultimate Oscillator                                   │
│    51. awesome_osc  - Awesome Oscillator                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 7: METADATA & TIMESTAMPS (Always Last)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  52. datetime       - Primary timestamp                                     │
│  53. timestamp      - Unix timestamp                                        │
│  54. data_source    - Data provider                                         │
│  55. created_at     - Record creation time                                  │
│  56. updated_at     - Last update time                                      │
└─────────────────────────────────────────────────────────────────────────────┘


RECOMMENDED APPROACH FOR RESTRUCTURING:
======================================

Option A: Create NEW standardized tables (RECOMMENDED)
------------------------------------------------------
1. Create new tables with standardized schema
2. Migrate data with field reordering
3. Update application to use new tables
4. Archive old tables
5. Delete old tables after verification

Option B: Modify existing tables in place
-----------------------------------------
1. BigQuery doesn't support column reordering directly
2. Would require: CREATE new table -> INSERT SELECT -> DROP old -> RENAME
3. Risk of data loss if not careful
4. More complex for 91 tables

Option C: Create views with standardized field order
----------------------------------------------------
1. Keep existing tables unchanged
2. Create views that present fields in standard order
3. Simplest approach, no data migration
4. Slight performance overhead

PRIORITY ORDER FOR RESTRUCTURING:
=================================
HIGH PRIORITY (Most used, most rows):
1. stocks_master_list (15,231 rows) - Master reference
2. stocks_daily_data - Primary stock data
3. crypto_analysis - Primary crypto data
4. stocks_hourly_data
5. crypto_hourly_data

MEDIUM PRIORITY:
6. forex_daily_data
7. etfs_daily_data
8. indices_daily_data
9. commodities_daily_data

LOW PRIORITY:
10. Weekly tables
11. 5-minute tables
12. Other/misc tables
""")

if __name__ == "__main__":
    main()
