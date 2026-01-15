"""
Create BigQuery Schema for Daily Stock Analysis
Matches the crypto_analysis table structure with 81 fields including Elliott Wave and Fibonacci analysis
"""

from google.cloud import bigquery
import logging
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'stock_analysis'


def create_stock_analysis_table():
    """Create stock_analysis table with same structure as crypto_analysis"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Define stock table schema - matches crypto_analysis structure
    schema = [
        # Stock identification (different from crypto 'pair')
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Stock ticker symbol (e.g., AAPL)"),
        bigquery.SchemaField("company_name", "STRING", description="Company name"),
        bigquery.SchemaField("sector", "STRING", description="Stock sector"),
        bigquery.SchemaField("industry", "STRING", description="Stock industry"),
        bigquery.SchemaField("exchange", "STRING", description="Exchange (NYSE, NASDAQ, etc)"),

        # Date and time fields
        bigquery.SchemaField("date", "DATE", mode="REQUIRED", description="Trading date"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Trading datetime"),
        bigquery.SchemaField("timestamp", "INTEGER", description="Unix timestamp"),

        # OHLC data
        bigquery.SchemaField("open", "FLOAT", mode="REQUIRED", description="Opening price"),
        bigquery.SchemaField("high", "FLOAT", mode="REQUIRED", description="High price"),
        bigquery.SchemaField("low", "FLOAT", mode="REQUIRED", description="Low price"),
        bigquery.SchemaField("close", "FLOAT", mode="REQUIRED", description="Closing price"),
        bigquery.SchemaField("volume", "INTEGER", description="Trading volume"),
        bigquery.SchemaField("dividends", "FLOAT", description="Dividend amount"),
        bigquery.SchemaField("stock_splits", "FLOAT", description="Stock split ratio"),

        # Moving Averages
        bigquery.SchemaField("sma_20", "FLOAT", description="20-period Simple Moving Average"),
        bigquery.SchemaField("sma_50", "FLOAT", description="50-period Simple Moving Average"),
        bigquery.SchemaField("sma_200", "FLOAT", description="200-period Simple Moving Average"),
        bigquery.SchemaField("ema_12", "FLOAT", description="12-period Exponential Moving Average"),
        bigquery.SchemaField("ema_26", "FLOAT", description="26-period Exponential Moving Average"),
        bigquery.SchemaField("ema_50", "FLOAT", description="50-period Exponential Moving Average"),

        # Momentum Indicators
        bigquery.SchemaField("rsi", "FLOAT", description="Relative Strength Index (14-period)"),
        bigquery.SchemaField("macd", "FLOAT", description="MACD line"),
        bigquery.SchemaField("macd_signal", "FLOAT", description="MACD signal line"),
        bigquery.SchemaField("macd_hist", "FLOAT", description="MACD histogram"),
        bigquery.SchemaField("momentum", "FLOAT", description="Momentum indicator"),
        bigquery.SchemaField("roc", "FLOAT", description="Rate of Change"),

        # Bollinger Bands
        bigquery.SchemaField("bb_upper", "FLOAT", description="Bollinger Band upper"),
        bigquery.SchemaField("bb_middle", "FLOAT", description="Bollinger Band middle"),
        bigquery.SchemaField("bb_lower", "FLOAT", description="Bollinger Band lower"),
        bigquery.SchemaField("bb_width", "FLOAT", description="Bollinger Band width"),

        # Volatility
        bigquery.SchemaField("atr", "FLOAT", description="Average True Range"),

        # Trend Indicators
        bigquery.SchemaField("adx", "FLOAT", description="Average Directional Index"),
        bigquery.SchemaField("plus_di", "FLOAT", description="+DI (Positive Directional Indicator)"),
        bigquery.SchemaField("minus_di", "FLOAT", description="-DI (Negative Directional Indicator)"),

        # Oscillators
        bigquery.SchemaField("cci", "FLOAT", description="Commodity Channel Index"),
        bigquery.SchemaField("williams_r", "FLOAT", description="Williams %R"),
        bigquery.SchemaField("stoch_k", "FLOAT", description="Stochastic %K"),
        bigquery.SchemaField("stoch_d", "FLOAT", description="Stochastic %D"),

        # Volume Indicators
        bigquery.SchemaField("obv", "FLOAT", description="On-Balance Volume"),
        bigquery.SchemaField("pvo", "FLOAT", description="Percentage Volume Oscillator"),
        bigquery.SchemaField("pvo_signal", "FLOAT", description="PVO Signal Line"),

        # Advanced Indicators
        bigquery.SchemaField("kama", "FLOAT", description="Kaufman Adaptive Moving Average"),
        bigquery.SchemaField("trix", "FLOAT", description="TRIX indicator"),
        bigquery.SchemaField("ppo", "FLOAT", description="Percentage Price Oscillator"),
        bigquery.SchemaField("ppo_signal", "FLOAT", description="PPO Signal Line"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT", description="Ultimate Oscillator"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT", description="Awesome Oscillator"),

        # Fibonacci Retracement Levels
        bigquery.SchemaField("fib_0", "FLOAT", description="Fibonacci 0% level (swing low)"),
        bigquery.SchemaField("fib_236", "FLOAT", description="Fibonacci 23.6% retracement"),
        bigquery.SchemaField("fib_382", "FLOAT", description="Fibonacci 38.2% retracement"),
        bigquery.SchemaField("fib_500", "FLOAT", description="Fibonacci 50% retracement"),
        bigquery.SchemaField("fib_618", "FLOAT", description="Fibonacci 61.8% retracement (golden ratio)"),
        bigquery.SchemaField("fib_786", "FLOAT", description="Fibonacci 78.6% retracement"),
        bigquery.SchemaField("fib_100", "FLOAT", description="Fibonacci 100% level (swing high)"),

        # Fibonacci Extension Levels
        bigquery.SchemaField("fib_ext_1272", "FLOAT", description="Fibonacci 127.2% extension"),
        bigquery.SchemaField("fib_ext_1618", "FLOAT", description="Fibonacci 161.8% extension (golden ratio)"),
        bigquery.SchemaField("fib_ext_2618", "FLOAT", description="Fibonacci 261.8% extension"),

        # Fibonacci Distance Metrics
        bigquery.SchemaField("dist_to_fib_236", "FLOAT", description="% distance to 23.6% level"),
        bigquery.SchemaField("dist_to_fib_382", "FLOAT", description="% distance to 38.2% level"),
        bigquery.SchemaField("dist_to_fib_500", "FLOAT", description="% distance to 50% level"),
        bigquery.SchemaField("dist_to_fib_618", "FLOAT", description="% distance to 61.8% level"),

        # Elliott Wave Analysis
        bigquery.SchemaField("elliott_wave_degree", "STRING", description="Wave degree (Minute, Minor, Intermediate, Primary, Cycle)"),
        bigquery.SchemaField("wave_position", "INTEGER", description="Current wave position (1-5 for impulse, A-C for corrective)"),
        bigquery.SchemaField("impulse_wave_count", "INTEGER", description="Count of impulse waves detected"),
        bigquery.SchemaField("corrective_wave_count", "INTEGER", description="Count of corrective waves detected"),
        bigquery.SchemaField("wave_1_high", "FLOAT", description="Wave 1 peak price"),
        bigquery.SchemaField("wave_2_low", "FLOAT", description="Wave 2 trough price"),
        bigquery.SchemaField("wave_3_high", "FLOAT", description="Wave 3 peak price (typically longest)"),
        bigquery.SchemaField("wave_4_low", "FLOAT", description="Wave 4 trough price"),
        bigquery.SchemaField("wave_5_high", "FLOAT", description="Wave 5 peak price"),
        bigquery.SchemaField("trend_direction", "INTEGER", description="Trend direction (1: uptrend, -1: downtrend, 0: sideways)"),

        # Helper fields for wave detection
        bigquery.SchemaField("swing_high", "BOOLEAN", description="Is this a swing high point"),
        bigquery.SchemaField("swing_low", "BOOLEAN", description="Is this a swing low point"),
        bigquery.SchemaField("local_maxima", "BOOLEAN", description="Is this a local maximum"),
        bigquery.SchemaField("local_minima", "BOOLEAN", description="Is this a local minimum"),
        bigquery.SchemaField("trend_strength", "FLOAT", description="Strength of the current trend"),
        bigquery.SchemaField("volatility_regime", "STRING", description="Current volatility regime (low, normal, high)"),
        bigquery.SchemaField("price_change_1d", "FLOAT", description="1-day price change %"),
        bigquery.SchemaField("price_change_5d", "FLOAT", description="5-day price change %"),
        bigquery.SchemaField("price_change_20d", "FLOAT", description="20-day price change %"),
    ]

    # Table configuration
    table = bigquery.Table(table_ref, schema=schema)
    table.description = "Daily stock analysis with technical indicators, Elliott Wave, and Fibonacci levels"

    # Add clustering and partitioning for better query performance
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="datetime"
    )
    table.clustering_fields = ["symbol", "sector", "date"]

    try:
        # Check if table exists
        try:
            existing_table = client.get_table(table_ref)
            logger.info(f"Table {table_ref} already exists")

            # Update schema if needed
            existing_table.schema = schema
            updated_table = client.update_table(existing_table, ["schema"])
            logger.info(f"Updated schema for table {table_ref}")
            return True

        except Exception as e:
            # Table doesn't exist, create it
            logger.info(f"Creating new table {table_ref}")
            created_table = client.create_table(table)
            logger.info(f"✓ Successfully created table {table_ref}")
            logger.info(f"  - Total fields: {len(schema)}")
            logger.info(f"  - Partitioned by: datetime (daily)")
            logger.info(f"  - Clustered by: symbol, sector, date")
            return True

    except Exception as e:
        logger.error(f"✗ Error creating/updating stock table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to create stock analysis table"""

    logger.info("=" * 70)
    logger.info("CREATING STOCK ANALYSIS TABLE IN BIGQUERY")
    logger.info("=" * 70)
    logger.info(f"\nProject: {PROJECT_ID}")
    logger.info(f"Dataset: {DATASET_ID}")
    logger.info(f"Table: {TABLE_ID}")
    logger.info("")

    success = create_stock_analysis_table()

    logger.info("=" * 70)
    if success:
        logger.info("✓ Stock analysis table ready!")
        logger.info("\nNext steps:")
        logger.info("  1. Run stock_data_fetcher_6months.py to collect historical data")
        logger.info("  2. Run upload_stocks_to_bigquery.py to upload to BigQuery")
        logger.info("  3. Deploy daily stock Cloud Function for ongoing updates")
    else:
        logger.error("✗ Failed to create stock analysis table")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
