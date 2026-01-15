"""
Create all 24 BigQuery tables for AIAlgoTradeHits
6 asset types x 4 timeframes = 24 tables
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from google.api_core.exceptions import Conflict

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Asset types and timeframes
ASSET_TYPES = ['stocks', 'crypto', 'forex', 'etfs', 'indices', 'commodities']
TIMEFRAMES = ['weekly', 'daily', 'hourly', '5min']

# Common schema for all tables
def get_table_schema():
    return [
        # Primary Key
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),

        # Symbol Info
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),

        # Timestamp
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="NULLABLE"),

        # OHLCV
        bigquery.SchemaField("open", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("high", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("low", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("close", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("volume", "FLOAT64", mode="NULLABLE"),

        # Moving Averages - SMA
        bigquery.SchemaField("sma_5", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("sma_10", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("sma_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("sma_50", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("sma_100", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("sma_200", "FLOAT64", mode="NULLABLE"),

        # Moving Averages - EMA
        bigquery.SchemaField("ema_5", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_10", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_12", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_26", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_50", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_100", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ema_200", "FLOAT64", mode="NULLABLE"),

        # Other Moving Averages
        bigquery.SchemaField("wma_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("dema_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("tema_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("kama_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("vwap", "FLOAT64", mode="NULLABLE"),

        # Momentum - RSI
        bigquery.SchemaField("rsi_7", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("rsi_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("rsi_21", "FLOAT64", mode="NULLABLE"),

        # Momentum - MACD
        bigquery.SchemaField("macd_line", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("macd_signal", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("macd_histogram", "FLOAT64", mode="NULLABLE"),

        # Momentum - Stochastic
        bigquery.SchemaField("stoch_k", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("stoch_d", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("stochrsi_k", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("stochrsi_d", "FLOAT64", mode="NULLABLE"),

        # Momentum - Other
        bigquery.SchemaField("willr_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("cci_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("cci_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("mfi_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("mom_10", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("roc_10", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("cmo_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ultosc", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ppo_line", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ppo_signal", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("apo", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("bop", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("percent_b", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("crsi", "FLOAT64", mode="NULLABLE"),

        # Trend - ADX
        bigquery.SchemaField("adx_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("adxr_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("dx_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("plus_di", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("minus_di", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("plus_dm", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("minus_dm", "FLOAT64", mode="NULLABLE"),

        # Trend - Aroon
        bigquery.SchemaField("aroon_up", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("aroon_down", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("aroon_osc", "FLOAT64", mode="NULLABLE"),

        # Volatility - ATR
        bigquery.SchemaField("atr_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("natr_14", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("trange", "FLOAT64", mode="NULLABLE"),

        # Volatility - Bollinger Bands
        bigquery.SchemaField("bbands_upper", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("bbands_middle", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("bbands_lower", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("bbands_bandwidth", "FLOAT64", mode="NULLABLE"),

        # Volatility - Keltner
        bigquery.SchemaField("keltner_upper", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("keltner_middle", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("keltner_lower", "FLOAT64", mode="NULLABLE"),

        # Volatility - SuperTrend
        bigquery.SchemaField("supertrend", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("supertrend_direction", "INT64", mode="NULLABLE"),

        # Volume Indicators
        bigquery.SchemaField("obv", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ad", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("adosc", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("rvol", "FLOAT64", mode="NULLABLE"),

        # Ichimoku
        bigquery.SchemaField("ichimoku_tenkan", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ichimoku_kijun", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ichimoku_senkou_a", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ichimoku_senkou_b", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ichimoku_chikou", "FLOAT64", mode="NULLABLE"),

        # Statistics
        bigquery.SchemaField("stddev_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("variance_20", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("beta", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("correlation", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("linearreg", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("linearreg_slope", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("linearreg_angle", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("linearreg_intercept", "FLOAT64", mode="NULLABLE"),

        # Price Transform
        bigquery.SchemaField("avgprice", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("medprice", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("typprice", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("wclprice", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("hlc3", "FLOAT64", mode="NULLABLE"),

        # Derived Metrics
        bigquery.SchemaField("change_pct", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("range_pct", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("body_pct", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("volume_sma_20", "FLOAT64", mode="NULLABLE"),

        # AI-Derived Classifications
        bigquery.SchemaField("trend_short", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("trend_medium", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("trend_long", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("is_oversold", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("is_overbought", "BOOL", mode="NULLABLE"),

        # Metadata
        bigquery.SchemaField("data_source", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]


def create_table(client, table_id, schema):
    """Create a BigQuery table"""
    table = bigquery.Table(table_id, schema=schema)

    # Set partitioning
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="datetime",
    )

    # Set clustering
    table.clustering_fields = ["symbol"]

    try:
        table = client.create_table(table)
        return True, f"Created table {table.table_id}"
    except Conflict:
        return False, f"Table {table_id} already exists"
    except Exception as e:
        return False, f"Error creating {table_id}: {str(e)}"


def create_support_tables(client, dataset_ref):
    """Create support tables (users, search_history, etc.)"""

    # Users table
    users_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("username", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("password_hash", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("role", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Search history table
    search_schema = [
        bigquery.SchemaField("search_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("query_text", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("query_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sql_generated", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("result_count", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("execution_time_ms", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Watchlists table
    watchlist_schema = [
        bigquery.SchemaField("watchlist_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbols", "STRING", mode="REPEATED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    # Symbols master table
    symbols_schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("industry", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    support_tables = [
        ("users", users_schema),
        ("search_history", search_schema),
        ("watchlists", watchlist_schema),
        ("symbols_master", symbols_schema),
    ]

    results = []
    for table_name, schema in support_tables:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        success, msg = create_table(client, table_id, schema)
        results.append((table_name, success, msg))

    return results


def main():
    print("=" * 60)
    print("CREATING BIGQUERY TABLES FOR AIAlgoTradeHits")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print()

    # Initialize client
    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset if it doesn't exist
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {DATASET_ID}")

    print()

    # Get schema
    schema = get_table_schema()
    print(f"Schema has {len(schema)} columns")
    print()

    # Create all 24 data tables
    print("Creating 24 data tables (6 assets x 4 timeframes)...")
    print("-" * 40)

    created = 0
    existed = 0
    failed = 0

    for asset_type in ASSET_TYPES:
        for timeframe in TIMEFRAMES:
            table_name = f"{asset_type}_{timeframe}"
            table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

            success, msg = create_table(client, table_id, schema)

            if success:
                print(f"  [+] {table_name}")
                created += 1
            elif "already exists" in msg:
                print(f"  [=] {table_name} (exists)")
                existed += 1
            else:
                print(f"  [!] {table_name} - {msg}")
                failed += 1

    print()
    print("-" * 40)
    print("Creating support tables...")
    print("-" * 40)

    # Create support tables
    support_results = create_support_tables(client, dataset_ref)
    for table_name, success, msg in support_results:
        if success:
            print(f"  [+] {table_name}")
            created += 1
        elif "already exists" in msg:
            print(f"  [=] {table_name} (exists)")
            existed += 1
        else:
            print(f"  [!] {table_name} - {msg}")
            failed += 1

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Created:  {created}")
    print(f"Existed:  {existed}")
    print(f"Failed:   {failed}")
    print(f"Total:    {created + existed + failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
