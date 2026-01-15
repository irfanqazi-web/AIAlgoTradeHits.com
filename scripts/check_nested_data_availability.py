"""
Check Data Availability for Nested Multi-Timeframe ML Model
Verifies hourly and 5-minute data exists with required indicators
"""

from google.cloud import bigquery
from datetime import datetime, timedelta

client = bigquery.Client(project='aialgotradehits')

print("=" * 80)
print("NESTED MULTI-TIMEFRAME DATA AVAILABILITY CHECK")
print("=" * 80)

# Required 16 variables for each timeframe
REQUIRED_VARS = [
    'ema_12', 'ema_26', 'sma_20', 'sma_50', 'sma_200',
    'rsi', 'macd', 'macd_signal', 'macd_histogram',
    'adx', 'atr', 'mfi', 'stoch_k', 'stoch_d',
    'volume', 'close'
]

# Alternative column names (some tables use different naming)
ALT_NAMES = {
    'rsi': ['rsi', 'rsi_14'],
    'atr': ['atr', 'atr_14'],
    'mfi': ['mfi', 'mfi_14'],
    'macd_histogram': ['macd_histogram', 'macd_hist'],
    'ema_12': ['ema_12', 'ema12'],
    'ema_26': ['ema_26', 'ema26'],
}

def check_table_schema(table_id):
    """Check what columns exist in a table"""
    try:
        table = client.get_table(table_id)
        columns = [field.name for field in table.schema]
        return columns
    except Exception as e:
        return None

def check_data_availability(table_id, date_col='datetime'):
    """Check record counts and date ranges"""
    try:
        # Get total count and date range - use TIMESTAMP casting
        query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN({date_col}) as min_date,
            MAX({date_col}) as max_date,
            COUNT(DISTINCT DATE({date_col})) as unique_days
        FROM `{table_id}`
        WHERE {date_col} >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        """
        result = list(client.query(query).result())[0]
        return {
            'total': result.total_records,
            'symbols': result.unique_symbols,
            'min_date': result.min_date,
            'max_date': result.max_date,
            'days': result.unique_days
        }
    except Exception as e:
        return {'error': str(e)}

def check_last_week_hourly(table_id):
    """Check hourly data for last week"""
    try:
        query = f"""
        SELECT
            DATE(datetime) as date,
            COUNT(*) as records,
            COUNT(DISTINCT symbol) as symbols,
            COUNT(DISTINCT EXTRACT(HOUR FROM datetime)) as hours
        FROM `{table_id}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY DATE(datetime)
        ORDER BY date DESC
        """
        return list(client.query(query).result())
    except Exception as e:
        print(f"  Error in hourly check: {e}")
        return []

def check_5min_data(table_id):
    """Check 5-minute data availability"""
    try:
        query = f"""
        SELECT
            DATE(datetime) as date,
            COUNT(*) as records,
            COUNT(DISTINCT symbol) as symbols,
            MIN(datetime) as first_bar,
            MAX(datetime) as last_bar
        FROM `{table_id}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY DATE(datetime)
        ORDER BY date DESC
        """
        return list(client.query(query).result())
    except Exception as e:
        print(f"  Error in 5min check: {e}")
        return []

# Tables to check
tables_to_check = [
    # Daily tables (baseline)
    ('aialgotradehits.crypto_trading_data.stocks_daily_clean', 'Daily Stocks'),
    ('aialgotradehits.crypto_trading_data.crypto_daily_clean', 'Daily Crypto'),
    # Hourly tables
    ('aialgotradehits.crypto_trading_data.stocks_hourly_clean', 'Hourly Stocks'),
    ('aialgotradehits.crypto_trading_data.crypto_hourly_clean', 'Hourly Crypto'),
    # 5-minute tables
    ('aialgotradehits.crypto_trading_data.stocks_5min_clean', '5-Min Stocks'),
    ('aialgotradehits.crypto_trading_data.crypto_5min_clean', '5-Min Crypto'),
]

print("\n" + "=" * 80)
print("SECTION 1: TABLE EXISTENCE AND SCHEMA CHECK")
print("=" * 80)

for table_id, label in tables_to_check:
    print(f"\n{label}: {table_id}")
    print("-" * 60)

    columns = check_table_schema(table_id)
    if columns is None:
        print("  TABLE DOES NOT EXIST")
        continue

    print(f"  Total columns: {len(columns)}")

    # Check for required variables
    found_vars = []
    missing_vars = []

    for var in REQUIRED_VARS:
        # Check main name and alternatives
        names_to_check = [var] + ALT_NAMES.get(var, [])
        found = False
        for name in names_to_check:
            if name.lower() in [c.lower() for c in columns]:
                found_vars.append(var)
                found = True
                break
        if not found:
            missing_vars.append(var)

    print(f"  Required vars found: {len(found_vars)}/16")
    if missing_vars:
        print(f"  MISSING: {', '.join(missing_vars)}")
    else:
        print(f"  All 16 required variables PRESENT")

print("\n" + "=" * 80)
print("SECTION 2: DATA AVAILABILITY (LAST 30 DAYS)")
print("=" * 80)

for table_id, label in tables_to_check:
    print(f"\n{label}:")
    print("-" * 40)

    data = check_data_availability(table_id)
    if 'error' in data:
        print(f"  Error: {data['error'][:80]}...")
    else:
        print(f"  Records (30d): {data['total']:,}")
        print(f"  Unique symbols: {data['symbols']}")
        print(f"  Date range: {data['min_date']} to {data['max_date']}")
        print(f"  Days with data: {data['days']}")

print("\n" + "=" * 80)
print("SECTION 3: HOURLY DATA DETAIL (LAST 7 DAYS)")
print("=" * 80)

hourly_table = 'aialgotradehits.crypto_trading_data.stocks_hourly_clean'
hourly_data = check_last_week_hourly(hourly_table)

if hourly_data:
    print(f"\nStocks Hourly ({hourly_table}):")
    print(f"{'Date':<12} {'Records':>10} {'Symbols':>10} {'Hours':>8}")
    print("-" * 45)
    for row in hourly_data[:7]:
        print(f"{str(row.date):<12} {row.records:>10,} {row.symbols:>10} {row.hours:>8}")
else:
    print("\nNo hourly stock data found or table doesn't exist")

# Check crypto hourly
hourly_crypto = 'aialgotradehits.crypto_trading_data.crypto_hourly_clean'
crypto_hourly_data = check_last_week_hourly(hourly_crypto)

if crypto_hourly_data:
    print(f"\nCrypto Hourly ({hourly_crypto}):")
    print(f"{'Date':<12} {'Records':>10} {'Symbols':>10} {'Hours':>8}")
    print("-" * 45)
    for row in crypto_hourly_data[:7]:
        print(f"{str(row.date):<12} {row.records:>10,} {row.symbols:>10} {row.hours:>8}")
else:
    print("\nNo hourly crypto data found")

print("\n" + "=" * 80)
print("SECTION 4: 5-MINUTE DATA DETAIL (LAST 7 DAYS)")
print("=" * 80)

fivemin_table = 'aialgotradehits.crypto_trading_data.stocks_5min_clean'
fivemin_data = check_5min_data(fivemin_table)

if fivemin_data:
    print(f"\nStocks 5-Min ({fivemin_table}):")
    print(f"{'Date':<12} {'Records':>12} {'Symbols':>10}")
    print("-" * 40)
    for row in fivemin_data[:7]:
        print(f"{str(row.date):<12} {row.records:>12,} {row.symbols:>10}")
else:
    print("\nNo 5-min stock data found or table doesn't exist")

# Check crypto 5min
fivemin_crypto = 'aialgotradehits.crypto_trading_data.crypto_5min_clean'
crypto_5min_data = check_5min_data(fivemin_crypto)

if crypto_5min_data:
    print(f"\nCrypto 5-Min ({fivemin_crypto}):")
    print(f"{'Date':<12} {'Records':>12} {'Symbols':>10}")
    print("-" * 40)
    for row in crypto_5min_data[:7]:
        print(f"{str(row.date):<12} {row.records:>12,} {row.symbols:>10}")
else:
    print("\nNo 5-min crypto data found")

print("\n" + "=" * 80)
print("SECTION 5: SAMPLE SYMBOLS WITH ALL TIMEFRAME DATA")
print("=" * 80)

# Check which symbols have data in all three timeframes
try:
    query = """
    WITH daily_symbols AS (
        SELECT DISTINCT symbol
        FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    ),
    hourly_symbols AS (
        SELECT DISTINCT symbol
        FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    ),
    fivemin_symbols AS (
        SELECT DISTINCT symbol
        FROM `aialgotradehits.crypto_trading_data.stocks_5min_clean`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    )
    SELECT
        d.symbol,
        CASE WHEN h.symbol IS NOT NULL THEN 'YES' ELSE 'NO' END as has_hourly,
        CASE WHEN f.symbol IS NOT NULL THEN 'YES' ELSE 'NO' END as has_5min
    FROM daily_symbols d
    LEFT JOIN hourly_symbols h ON d.symbol = h.symbol
    LEFT JOIN fivemin_symbols f ON d.symbol = f.symbol
    ORDER BY
        CASE WHEN h.symbol IS NOT NULL AND f.symbol IS NOT NULL THEN 0 ELSE 1 END,
        d.symbol
    LIMIT 50
    """
    results = list(client.query(query).result())

    if results:
        all_three = [r for r in results if r.has_hourly == 'YES' and r.has_5min == 'YES']
        daily_hourly = [r for r in results if r.has_hourly == 'YES' and r.has_5min == 'NO']
        daily_only = [r for r in results if r.has_hourly == 'NO']

        print(f"\nSymbols with ALL 3 timeframes: {len(all_three)}")
        if all_three:
            print(f"  {', '.join([r.symbol for r in all_three[:20]])}")

        print(f"\nSymbols with Daily + Hourly only: {len(daily_hourly)}")
        if daily_hourly:
            print(f"  {', '.join([r.symbol for r in daily_hourly[:20]])}")

        print(f"\nSymbols with Daily only: {len(daily_only)}")
        if daily_only:
            print(f"  {', '.join([r.symbol for r in daily_only[:15]])}")
except Exception as e:
    print(f"Error checking cross-timeframe symbols: {e}")

print("\n" + "=" * 80)
print("SECTION 6: INDICATOR COMPLETENESS CHECK")
print("=" * 80)

# Check if indicators are actually populated (not NULL)
for table_id, label in [
    ('aialgotradehits.crypto_trading_data.stocks_hourly_clean', 'Hourly Stocks'),
    ('aialgotradehits.crypto_trading_data.stocks_5min_clean', '5-Min Stocks'),
]:
    print(f"\n{label} Indicator Completeness:")
    print("-" * 50)

    try:
        # Check NULL rates for key indicators
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(ema_12 IS NOT NULL) as ema_12_count,
            COUNTIF(rsi IS NOT NULL OR rsi_14 IS NOT NULL) as rsi_count,
            COUNTIF(macd IS NOT NULL) as macd_count,
            COUNTIF(adx IS NOT NULL) as adx_count,
            COUNTIF(volume IS NOT NULL) as volume_count
        FROM `{table_id}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        """
        result = list(client.query(query).result())[0]

        if result.total > 0:
            print(f"  Total records: {result.total:,}")
            print(f"  EMA_12: {result.ema_12_count:,} ({100*result.ema_12_count/result.total:.1f}%)")
            print(f"  RSI: {result.rsi_count:,} ({100*result.rsi_count/result.total:.1f}%)")
            print(f"  MACD: {result.macd_count:,} ({100*result.macd_count/result.total:.1f}%)")
            print(f"  ADX: {result.adx_count:,} ({100*result.adx_count/result.total:.1f}%)")
            print(f"  Volume: {result.volume_count:,} ({100*result.volume_count/result.total:.1f}%)")
        else:
            print("  No data found")
    except Exception as e:
        print(f"  Error: {str(e)[:60]}...")

print("\n" + "=" * 80)
print("SECTION 7: DATA SUMMARY FOR ML TRAINING")
print("=" * 80)

# Get actual record counts for ML planning
try:
    summary_query = """
    SELECT
        'Daily Stocks' as timeframe,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as symbols,
        MIN(DATE(datetime)) as min_date,
        MAX(DATE(datetime)) as max_date
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)

    UNION ALL

    SELECT
        'Hourly Stocks' as timeframe,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as symbols,
        MIN(DATE(datetime)) as min_date,
        MAX(DATE(datetime)) as max_date
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)

    UNION ALL

    SELECT
        '5-Min Stocks' as timeframe,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as symbols,
        MIN(DATE(datetime)) as min_date,
        MAX(DATE(datetime)) as max_date
    FROM `aialgotradehits.crypto_trading_data.stocks_5min_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """

    results = list(client.query(summary_query).result())
    print(f"\n{'Timeframe':<15} {'Records':>12} {'Symbols':>10} {'Date Range':<25}")
    print("-" * 65)
    for r in results:
        print(f"{r.timeframe:<15} {r.total_records:>12,} {r.symbols:>10} {str(r.min_date)} to {str(r.max_date)}")

except Exception as e:
    print(f"Error in summary: {e}")

print("\n" + "=" * 80)
print("DATA AVAILABILITY CHECK COMPLETE")
print("=" * 80)
