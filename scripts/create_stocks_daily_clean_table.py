"""
Create stocks_daily_clean table with complete 85-field schema
Based on STOCK_FIELDS_SCHEMA_COMPLETE.md
"""
from google.cloud import bigquery

# Initialize client
client = bigquery.Client(project='aialgotradehits')

# Define the 85-field schema
schema = [
    # CORE IDENTIFIERS (1-2)
    bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED",
                        description="Market DateTime"),
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED",
                        description="Stock Ticker Symbol"),

    # OHLCV DATA (3-8)
    bigquery.SchemaField("open", "FLOAT", mode="NULLABLE",
                        description="Opening Price"),
    bigquery.SchemaField("high", "FLOAT", mode="NULLABLE",
                        description="Highest Price"),
    bigquery.SchemaField("low", "FLOAT", mode="NULLABLE",
                        description="Lowest Price"),
    bigquery.SchemaField("close", "FLOAT", mode="NULLABLE",
                        description="Closing Price"),
    bigquery.SchemaField("previous_close", "FLOAT", mode="NULLABLE",
                        description="Previous Closing Price"),
    bigquery.SchemaField("volume", "INTEGER", mode="NULLABLE",
                        description="Trading Volume"),

    # PRICE STATISTICS (9-15)
    bigquery.SchemaField("average_volume", "INTEGER", mode="NULLABLE",
                        description="Average Trading Volume"),
    bigquery.SchemaField("change", "FLOAT", mode="NULLABLE",
                        description="Price Change (Absolute)"),
    bigquery.SchemaField("percent_change", "FLOAT", mode="NULLABLE",
                        description="Price Change (Percentage)"),
    bigquery.SchemaField("high_low", "FLOAT", mode="NULLABLE",
                        description="High-Low Range (Absolute) = high - low"),
    bigquery.SchemaField("pct_high_low", "FLOAT", mode="NULLABLE",
                        description="High-Low Range vs Low (%) = (high - low) * 100 / low"),
    bigquery.SchemaField("week_52_high", "FLOAT", mode="NULLABLE",
                        description="52-Week High"),
    bigquery.SchemaField("week_52_low", "FLOAT", mode="NULLABLE",
                        description="52-Week Low"),

    # MOMENTUM INDICATORS (16-24)
    bigquery.SchemaField("rsi", "FLOAT", mode="NULLABLE",
                        description="Relative Strength Index"),
    bigquery.SchemaField("macd", "FLOAT", mode="NULLABLE",
                        description="MACD Line"),
    bigquery.SchemaField("macd_signal", "FLOAT", mode="NULLABLE",
                        description="MACD Signal Line"),
    bigquery.SchemaField("macd_histogram", "FLOAT", mode="NULLABLE",
                        description="MACD Histogram"),
    bigquery.SchemaField("stoch_k", "FLOAT", mode="NULLABLE",
                        description="Stochastic %K"),
    bigquery.SchemaField("stoch_d", "FLOAT", mode="NULLABLE",
                        description="Stochastic %D"),
    bigquery.SchemaField("cci", "FLOAT", mode="NULLABLE",
                        description="Commodity Channel Index"),
    bigquery.SchemaField("williams_r", "FLOAT", mode="NULLABLE",
                        description="Williams %R"),
    bigquery.SchemaField("momentum", "FLOAT", mode="NULLABLE",
                        description="Momentum Indicator"),

    # MOVING AVERAGES (25-33)
    bigquery.SchemaField("sma_20", "FLOAT", mode="NULLABLE",
                        description="Simple Moving Average (20-day)"),
    bigquery.SchemaField("sma_50", "FLOAT", mode="NULLABLE",
                        description="Simple Moving Average (50-day)"),
    bigquery.SchemaField("sma_200", "FLOAT", mode="NULLABLE",
                        description="Simple Moving Average (200-day)"),
    bigquery.SchemaField("ema_12", "FLOAT", mode="NULLABLE",
                        description="Exponential Moving Average (12-day)"),
    bigquery.SchemaField("ema_20", "FLOAT", mode="NULLABLE",
                        description="Exponential Moving Average (20-day)"),
    bigquery.SchemaField("ema_26", "FLOAT", mode="NULLABLE",
                        description="Exponential Moving Average (26-day)"),
    bigquery.SchemaField("ema_50", "FLOAT", mode="NULLABLE",
                        description="Exponential Moving Average (50-day)"),
    bigquery.SchemaField("ema_200", "FLOAT", mode="NULLABLE",
                        description="Exponential Moving Average (200-day)"),
    bigquery.SchemaField("kama", "FLOAT", mode="NULLABLE",
                        description="Kaufman Adaptive Moving Average"),

    # TREND & VOLATILITY (34-43)
    bigquery.SchemaField("bollinger_upper", "FLOAT", mode="NULLABLE",
                        description="Bollinger Band (Upper)"),
    bigquery.SchemaField("bollinger_middle", "FLOAT", mode="NULLABLE",
                        description="Bollinger Band (Middle)"),
    bigquery.SchemaField("bollinger_lower", "FLOAT", mode="NULLABLE",
                        description="Bollinger Band (Lower)"),
    bigquery.SchemaField("bb_width", "FLOAT", mode="NULLABLE",
                        description="Bollinger Band Width"),
    bigquery.SchemaField("adx", "FLOAT", mode="NULLABLE",
                        description="Average Directional Index"),
    bigquery.SchemaField("plus_di", "FLOAT", mode="NULLABLE",
                        description="Plus Directional Indicator (+DI)"),
    bigquery.SchemaField("minus_di", "FLOAT", mode="NULLABLE",
                        description="Minus Directional Indicator (-DI)"),
    bigquery.SchemaField("atr", "FLOAT", mode="NULLABLE",
                        description="Average True Range"),
    bigquery.SchemaField("trix", "FLOAT", mode="NULLABLE",
                        description="TRIX Indicator"),
    bigquery.SchemaField("roc", "FLOAT", mode="NULLABLE",
                        description="Rate of Change"),

    # VOLUME INDICATORS (44-46)
    bigquery.SchemaField("obv", "FLOAT", mode="NULLABLE",
                        description="On-Balance Volume"),
    bigquery.SchemaField("pvo", "FLOAT", mode="NULLABLE",
                        description="Percentage Volume Oscillator"),
    bigquery.SchemaField("ppo", "FLOAT", mode="NULLABLE",
                        description="Percentage Price Oscillator"),

    # ADVANCED OSCILLATORS (47-48)
    bigquery.SchemaField("ultimate_osc", "FLOAT", mode="NULLABLE",
                        description="Ultimate Oscillator"),
    bigquery.SchemaField("awesome_osc", "FLOAT", mode="NULLABLE",
                        description="Awesome Oscillator"),

    # ML FEATURES - RETURNS (49-51)
    bigquery.SchemaField("log_return", "FLOAT", mode="NULLABLE",
                        description="Logarithmic Return (1-day)"),
    bigquery.SchemaField("return_2w", "FLOAT", mode="NULLABLE",
                        description="Forward Return (2-week)"),
    bigquery.SchemaField("return_4w", "FLOAT", mode="NULLABLE",
                        description="Forward Return (4-week)"),

    # ML FEATURES - RELATIVE POSITIONS (52-54)
    bigquery.SchemaField("close_vs_sma20_pct", "FLOAT", mode="NULLABLE",
                        description="Close vs SMA20 (Percentage)"),
    bigquery.SchemaField("close_vs_sma50_pct", "FLOAT", mode="NULLABLE",
                        description="Close vs SMA50 (Percentage)"),
    bigquery.SchemaField("close_vs_sma200_pct", "FLOAT", mode="NULLABLE",
                        description="Close vs SMA200 (Percentage)"),

    # ML FEATURES - INDICATOR DYNAMICS (55-65)
    bigquery.SchemaField("rsi_slope", "FLOAT", mode="NULLABLE",
                        description="RSI Slope (Rate of Change)"),
    bigquery.SchemaField("rsi_zscore", "FLOAT", mode="NULLABLE",
                        description="RSI Z-Score"),
    bigquery.SchemaField("rsi_overbought", "INTEGER", mode="NULLABLE",
                        description="RSI Overbought Flag (1=overbought)"),
    bigquery.SchemaField("rsi_oversold", "INTEGER", mode="NULLABLE",
                        description="RSI Oversold Flag (1=oversold)"),
    bigquery.SchemaField("macd_cross", "INTEGER", mode="NULLABLE",
                        description="MACD Crossover Signal (1=bullish, -1=bearish)"),
    bigquery.SchemaField("ema20_slope", "FLOAT", mode="NULLABLE",
                        description="EMA20 Slope"),
    bigquery.SchemaField("ema50_slope", "FLOAT", mode="NULLABLE",
                        description="EMA50 Slope"),
    bigquery.SchemaField("atr_zscore", "FLOAT", mode="NULLABLE",
                        description="ATR Z-Score"),
    bigquery.SchemaField("atr_slope", "FLOAT", mode="NULLABLE",
                        description="ATR Slope"),
    bigquery.SchemaField("volume_zscore", "FLOAT", mode="NULLABLE",
                        description="Volume Z-Score"),
    bigquery.SchemaField("volume_ratio", "FLOAT", mode="NULLABLE",
                        description="Volume Ratio (current/average)"),

    # ML FEATURES - MARKET STRUCTURE (66-69)
    bigquery.SchemaField("pivot_high_flag", "INTEGER", mode="NULLABLE",
                        description="Pivot High Flag"),
    bigquery.SchemaField("pivot_low_flag", "INTEGER", mode="NULLABLE",
                        description="Pivot Low Flag"),
    bigquery.SchemaField("dist_to_pivot_high", "FLOAT", mode="NULLABLE",
                        description="Distance to Last Pivot High"),
    bigquery.SchemaField("dist_to_pivot_low", "FLOAT", mode="NULLABLE",
                        description="Distance to Last Pivot Low"),

    # ML FEATURES - REGIME DETECTION (70-72)
    bigquery.SchemaField("trend_regime", "INTEGER", mode="NULLABLE",
                        description="Trend Regime Classification (1=uptrend, -1=downtrend, 0=sideways)"),
    bigquery.SchemaField("vol_regime", "INTEGER", mode="NULLABLE",
                        description="Volatility Regime Classification (1=high, 0=low)"),
    bigquery.SchemaField("regime_confidence", "FLOAT", mode="NULLABLE",
                        description="Regime Classification Confidence"),

    # ASSET METADATA (73-81)
    bigquery.SchemaField("name", "STRING", mode="NULLABLE",
                        description="Company/Asset Full Name"),
    bigquery.SchemaField("sector", "STRING", mode="NULLABLE",
                        description="Economic Sector"),
    bigquery.SchemaField("industry", "STRING", mode="NULLABLE",
                        description="Industry Classification"),
    bigquery.SchemaField("asset_type", "STRING", mode="NULLABLE",
                        description="Asset Type (Common Stock, ETF, etc)"),
    bigquery.SchemaField("exchange", "STRING", mode="NULLABLE",
                        description="Exchange Name"),
    bigquery.SchemaField("mic_code", "STRING", mode="NULLABLE",
                        description="Market Identifier Code"),
    bigquery.SchemaField("country", "STRING", mode="NULLABLE",
                        description="Country Code"),
    bigquery.SchemaField("currency", "STRING", mode="NULLABLE",
                        description="Trading Currency"),
    bigquery.SchemaField("type", "STRING", mode="NULLABLE",
                        description="Security Type"),

    # SYSTEM METADATA (82-85)
    bigquery.SchemaField("timestamp", "INTEGER", mode="NULLABLE",
                        description="Unix Timestamp"),
    bigquery.SchemaField("data_source", "STRING", mode="NULLABLE",
                        description="Data Source Provider (TwelveData, etc)"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE",
                        description="Record Creation Timestamp"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE",
                        description="Record Update Timestamp"),
]

# Table configuration
dataset_id = "crypto_trading_data"
table_id = "stocks_daily_clean"
full_table_id = f"aialgotradehits.{dataset_id}.{table_id}"

# Create table with partitioning and clustering
table = bigquery.Table(full_table_id, schema=schema)

# Partition by MONTH (not DAY - we have 27 years of data = 4100+ days, exceeds 4000 limit)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.MONTH,
    field="datetime"
)

# Cluster by symbol, sector, exchange for fast queries
table.clustering_fields = ["symbol", "sector", "exchange"]

# Add table description
table.description = """
Clean consolidated daily stock data table with 85 fields.
Includes OHLCV data, 40+ technical indicators, and ML features.
Sources: v2_stocks_daily, stocks_unified_daily, v2_stocks_historical_daily
Filtered to NASDAQ, NYSE, CBOE exchanges only (no OTC/Pink Sheets).
"""

# Create the table
print(f"Creating table: {full_table_id}")
print("="*80)

try:
    # Delete table if exists
    client.delete_table(full_table_id, not_found_ok=True)
    print("[OK] Deleted existing table (if any)")

    # Create new table
    table = client.create_table(table)
    print(f"[OK] Created table {table.project}.{table.dataset_id}.{table.table_id}")
    print(f"    - Schema: {len(schema)} fields")
    print(f"    - Partitioned by: DATE(datetime)")
    print(f"    - Clustered by: symbol, sector, exchange")
    print("="*80)
    print("\nTable created successfully!")
    print("\nNext steps:")
    print("1. Run migration script to populate data from source tables")
    print("2. Calculate all technical indicators")
    print("3. Validate and test")

except Exception as e:
    print(f"[ERROR] Failed to create table: {e}")
