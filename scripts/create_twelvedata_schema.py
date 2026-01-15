"""
Create TwelveData-Only BigQuery Schema
6 Asset Types × 4 Timeframes = 24 Tables
All data comes from TwelveData API only
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Asset types
ASSET_TYPES = ['stocks', 'crypto', 'forex', 'etfs', 'indices', 'commodities']

# Timeframes
TIMEFRAMES = ['weekly', 'daily', 'hourly', '5min']

def get_base_schema():
    """Base schema for all tables"""
    return [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Asset symbol"),
        bigquery.SchemaField("name", "STRING", description="Asset name"),
        bigquery.SchemaField("exchange", "STRING", description="Exchange"),
        bigquery.SchemaField("currency", "STRING", description="Currency"),
        bigquery.SchemaField("asset_type", "STRING", description="Asset type"),

        # OHLCV Data
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Timestamp"),
        bigquery.SchemaField("open", "FLOAT64", description="Open price"),
        bigquery.SchemaField("high", "FLOAT64", description="High price"),
        bigquery.SchemaField("low", "FLOAT64", description="Low price"),
        bigquery.SchemaField("close", "FLOAT64", description="Close price"),
        bigquery.SchemaField("volume", "FLOAT64", description="Volume"),

        # TwelveData Technical Indicators
        # Momentum Indicators
        bigquery.SchemaField("rsi", "FLOAT64", description="Relative Strength Index (14)"),
        bigquery.SchemaField("rsi_7", "FLOAT64", description="RSI (7)"),
        bigquery.SchemaField("rsi_21", "FLOAT64", description="RSI (21)"),
        bigquery.SchemaField("stoch_k", "FLOAT64", description="Stochastic %K"),
        bigquery.SchemaField("stoch_d", "FLOAT64", description="Stochastic %D"),
        bigquery.SchemaField("stoch_rsi", "FLOAT64", description="Stochastic RSI"),
        bigquery.SchemaField("willr", "FLOAT64", description="Williams %R"),
        bigquery.SchemaField("cci", "FLOAT64", description="Commodity Channel Index"),
        bigquery.SchemaField("roc", "FLOAT64", description="Rate of Change"),
        bigquery.SchemaField("mom", "FLOAT64", description="Momentum"),
        bigquery.SchemaField("ao", "FLOAT64", description="Awesome Oscillator"),
        bigquery.SchemaField("uo", "FLOAT64", description="Ultimate Oscillator"),

        # Trend Indicators
        bigquery.SchemaField("sma_10", "FLOAT64", description="SMA (10)"),
        bigquery.SchemaField("sma_20", "FLOAT64", description="SMA (20)"),
        bigquery.SchemaField("sma_50", "FLOAT64", description="SMA (50)"),
        bigquery.SchemaField("sma_100", "FLOAT64", description="SMA (100)"),
        bigquery.SchemaField("sma_200", "FLOAT64", description="SMA (200)"),
        bigquery.SchemaField("ema_10", "FLOAT64", description="EMA (10)"),
        bigquery.SchemaField("ema_20", "FLOAT64", description="EMA (20)"),
        bigquery.SchemaField("ema_50", "FLOAT64", description="EMA (50)"),
        bigquery.SchemaField("ema_100", "FLOAT64", description="EMA (100)"),
        bigquery.SchemaField("ema_200", "FLOAT64", description="EMA (200)"),
        bigquery.SchemaField("wma_20", "FLOAT64", description="WMA (20)"),
        bigquery.SchemaField("dema_20", "FLOAT64", description="DEMA (20)"),
        bigquery.SchemaField("tema_20", "FLOAT64", description="TEMA (20)"),
        bigquery.SchemaField("kama", "FLOAT64", description="Kaufman Adaptive MA"),
        bigquery.SchemaField("t3ma", "FLOAT64", description="T3 Moving Average"),
        bigquery.SchemaField("vwma", "FLOAT64", description="Volume Weighted MA"),
        bigquery.SchemaField("hma", "FLOAT64", description="Hull Moving Average"),

        # MACD
        bigquery.SchemaField("macd", "FLOAT64", description="MACD Line"),
        bigquery.SchemaField("macd_signal", "FLOAT64", description="MACD Signal"),
        bigquery.SchemaField("macd_hist", "FLOAT64", description="MACD Histogram"),

        # Trend Strength
        bigquery.SchemaField("adx", "FLOAT64", description="Average Directional Index"),
        bigquery.SchemaField("plus_di", "FLOAT64", description="+DI"),
        bigquery.SchemaField("minus_di", "FLOAT64", description="-DI"),
        bigquery.SchemaField("aroon_up", "FLOAT64", description="Aroon Up"),
        bigquery.SchemaField("aroon_down", "FLOAT64", description="Aroon Down"),
        bigquery.SchemaField("aroon_osc", "FLOAT64", description="Aroon Oscillator"),
        bigquery.SchemaField("psar", "FLOAT64", description="Parabolic SAR"),
        bigquery.SchemaField("supertrend", "FLOAT64", description="Supertrend"),
        bigquery.SchemaField("trix", "FLOAT64", description="TRIX"),
        bigquery.SchemaField("vortex_pos", "FLOAT64", description="Vortex +VI"),
        bigquery.SchemaField("vortex_neg", "FLOAT64", description="Vortex -VI"),

        # Volatility Indicators
        bigquery.SchemaField("atr", "FLOAT64", description="Average True Range"),
        bigquery.SchemaField("atr_percent", "FLOAT64", description="ATR as % of price"),
        bigquery.SchemaField("bbands_upper", "FLOAT64", description="Bollinger Upper Band"),
        bigquery.SchemaField("bbands_middle", "FLOAT64", description="Bollinger Middle Band"),
        bigquery.SchemaField("bbands_lower", "FLOAT64", description="Bollinger Lower Band"),
        bigquery.SchemaField("bbands_width", "FLOAT64", description="Bollinger Band Width"),
        bigquery.SchemaField("bbands_percent", "FLOAT64", description="Bollinger %B"),
        bigquery.SchemaField("keltner_upper", "FLOAT64", description="Keltner Upper"),
        bigquery.SchemaField("keltner_middle", "FLOAT64", description="Keltner Middle"),
        bigquery.SchemaField("keltner_lower", "FLOAT64", description="Keltner Lower"),
        bigquery.SchemaField("donchian_upper", "FLOAT64", description="Donchian Upper"),
        bigquery.SchemaField("donchian_middle", "FLOAT64", description="Donchian Middle"),
        bigquery.SchemaField("donchian_lower", "FLOAT64", description="Donchian Lower"),
        bigquery.SchemaField("natr", "FLOAT64", description="Normalized ATR"),

        # Volume Indicators
        bigquery.SchemaField("obv", "FLOAT64", description="On Balance Volume"),
        bigquery.SchemaField("ad", "FLOAT64", description="Accumulation/Distribution"),
        bigquery.SchemaField("adosc", "FLOAT64", description="Chaikin A/D Oscillator"),
        bigquery.SchemaField("cmf", "FLOAT64", description="Chaikin Money Flow"),
        bigquery.SchemaField("mfi", "FLOAT64", description="Money Flow Index"),
        bigquery.SchemaField("vwap", "FLOAT64", description="Volume Weighted Avg Price"),
        bigquery.SchemaField("pvo", "FLOAT64", description="Percentage Volume Osc"),
        bigquery.SchemaField("eom", "FLOAT64", description="Ease of Movement"),
        bigquery.SchemaField("fi", "FLOAT64", description="Force Index"),
        bigquery.SchemaField("nvi", "FLOAT64", description="Negative Volume Index"),

        # Price Transform
        bigquery.SchemaField("typical_price", "FLOAT64", description="(H+L+C)/3"),
        bigquery.SchemaField("median_price", "FLOAT64", description="(H+L)/2"),
        bigquery.SchemaField("weighted_close", "FLOAT64", description="(H+L+2C)/4"),

        # Pivot Points
        bigquery.SchemaField("pivot", "FLOAT64", description="Pivot Point"),
        bigquery.SchemaField("r1", "FLOAT64", description="Resistance 1"),
        bigquery.SchemaField("r2", "FLOAT64", description="Resistance 2"),
        bigquery.SchemaField("r3", "FLOAT64", description="Resistance 3"),
        bigquery.SchemaField("s1", "FLOAT64", description="Support 1"),
        bigquery.SchemaField("s2", "FLOAT64", description="Support 2"),
        bigquery.SchemaField("s3", "FLOAT64", description="Support 3"),

        # Fibonacci Levels
        bigquery.SchemaField("fib_0", "FLOAT64", description="Fibonacci 0%"),
        bigquery.SchemaField("fib_236", "FLOAT64", description="Fibonacci 23.6%"),
        bigquery.SchemaField("fib_382", "FLOAT64", description="Fibonacci 38.2%"),
        bigquery.SchemaField("fib_500", "FLOAT64", description="Fibonacci 50%"),
        bigquery.SchemaField("fib_618", "FLOAT64", description="Fibonacci 61.8%"),
        bigquery.SchemaField("fib_786", "FLOAT64", description="Fibonacci 78.6%"),
        bigquery.SchemaField("fib_100", "FLOAT64", description="Fibonacci 100%"),

        # Ichimoku Cloud
        bigquery.SchemaField("ichimoku_tenkan", "FLOAT64", description="Tenkan-sen"),
        bigquery.SchemaField("ichimoku_kijun", "FLOAT64", description="Kijun-sen"),
        bigquery.SchemaField("ichimoku_senkou_a", "FLOAT64", description="Senkou Span A"),
        bigquery.SchemaField("ichimoku_senkou_b", "FLOAT64", description="Senkou Span B"),
        bigquery.SchemaField("ichimoku_chikou", "FLOAT64", description="Chikou Span"),

        # Custom Signals
        bigquery.SchemaField("trend_direction", "STRING", description="Trend: up/down/neutral"),
        bigquery.SchemaField("signal_strength", "FLOAT64", description="Signal strength 0-100"),
        bigquery.SchemaField("buy_signal", "BOOLEAN", description="Buy signal flag"),
        bigquery.SchemaField("sell_signal", "BOOLEAN", description="Sell signal flag"),

        # Performance Metrics
        bigquery.SchemaField("change_percent", "FLOAT64", description="% change from previous"),
        bigquery.SchemaField("change_1d", "FLOAT64", description="1-day change %"),
        bigquery.SchemaField("change_1w", "FLOAT64", description="1-week change %"),
        bigquery.SchemaField("change_1m", "FLOAT64", description="1-month change %"),
        bigquery.SchemaField("high_52w", "FLOAT64", description="52-week high"),
        bigquery.SchemaField("low_52w", "FLOAT64", description="52-week low"),
        bigquery.SchemaField("from_52w_high", "FLOAT64", description="% from 52w high"),
        bigquery.SchemaField("from_52w_low", "FLOAT64", description="% from 52w low"),

        # Metadata
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", description="When data was fetched"),
        bigquery.SchemaField("data_source", "STRING", description="Always 'twelvedata'"),
    ]


def create_table(client, asset_type, timeframe):
    """Create a single table"""
    table_name = f"{asset_type}_{timeframe}"
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    schema = get_base_schema()

    # Add category field for certain asset types
    if asset_type in ['stocks', 'etfs']:
        schema.insert(4, bigquery.SchemaField("sector", "STRING", description="Sector"))
        schema.insert(5, bigquery.SchemaField("industry", "STRING", description="Industry"))
    elif asset_type == 'crypto':
        schema.insert(4, bigquery.SchemaField("category", "STRING", description="Crypto category"))
    elif asset_type == 'forex':
        schema.insert(4, bigquery.SchemaField("base_currency", "STRING", description="Base currency"))
        schema.insert(5, bigquery.SchemaField("quote_currency", "STRING", description="Quote currency"))
    elif asset_type == 'indices':
        schema.insert(4, bigquery.SchemaField("region", "STRING", description="Region"))
    elif asset_type == 'commodities':
        schema.insert(4, bigquery.SchemaField("category", "STRING", description="Commodity category"))

    table = bigquery.Table(table_id, schema=schema)

    # Add partitioning and clustering
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="datetime"
    )
    table.clustering_fields = ["symbol", "asset_type"]

    try:
        table = client.create_table(table)
        print(f"✓ Created {table_name}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  {table_name} already exists")
            return True
        print(f"✗ Error creating {table_name}: {e}")
        return False


def create_support_tables(client):
    """Create supporting tables"""

    # Users table
    users_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("username", "STRING"),
        bigquery.SchemaField("password_hash", "STRING"),
        bigquery.SchemaField("role", "STRING"),
        bigquery.SchemaField("first_login_completed", "BOOLEAN"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("last_login", "TIMESTAMP"),
        bigquery.SchemaField("preferences", "STRING"),  # JSON for user preferences
    ]

    users_table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.users", schema=users_schema)
    try:
        client.create_table(users_table)
        print("✓ Created users table")
    except Exception as e:
        if "Already Exists" not in str(e):
            print(f"✗ Error creating users: {e}")

    # Search history table
    search_schema = [
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("query", "STRING"),
        bigquery.SchemaField("query_type", "STRING"),  # text or voice
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("results_count", "INTEGER"),
        bigquery.SchemaField("selected_symbol", "STRING"),
        bigquery.SchemaField("search_timestamp", "TIMESTAMP"),
    ]

    search_table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.search_history", schema=search_schema)
    search_table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="search_timestamp"
    )
    try:
        client.create_table(search_table)
        print("✓ Created search_history table")
    except Exception as e:
        if "Already Exists" not in str(e):
            print(f"✗ Error creating search_history: {e}")

    # Watchlist table
    watchlist_schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("added_at", "TIMESTAMP"),
        bigquery.SchemaField("notes", "STRING"),
    ]

    watchlist_table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.watchlist", schema=watchlist_schema)
    try:
        client.create_table(watchlist_table)
        print("✓ Created watchlist table")
    except Exception as e:
        if "Already Exists" not in str(e):
            print(f"✗ Error creating watchlist: {e}")


def main():
    print("=" * 60)
    print("CREATING TWELVEDATA-ONLY BIGQUERY SCHEMA")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    # Create 24 tables (6 asset types × 4 timeframes)
    print("\nCreating data tables...")
    for asset_type in ASSET_TYPES:
        print(f"\n{asset_type.upper()}:")
        for timeframe in TIMEFRAMES:
            create_table(client, asset_type, timeframe)

    # Create support tables
    print("\nCreating support tables...")
    create_support_tables(client)

    print("\n" + "=" * 60)
    print("SCHEMA CREATION COMPLETE!")
    print(f"Total tables: {len(ASSET_TYPES) * len(TIMEFRAMES) + 3}")
    print("=" * 60)


if __name__ == "__main__":
    main()
