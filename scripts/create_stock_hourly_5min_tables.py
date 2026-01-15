"""
Create BigQuery Tables for Stock Hourly and 5-Minute Data
Mirrors the crypto_hourly_data and crypto_5min_top10_gainers table structures
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


def create_stock_hourly_table():
    """Create stock_hourly_data table - mirrors crypto_hourly_data structure"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.stock_hourly_data'

    # Define schema - matches crypto hourly with stock-specific fields
    schema = [
        # Stock identification
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Stock ticker symbol"),
        bigquery.SchemaField("company_name", "STRING", description="Company name"),
        bigquery.SchemaField("sector", "STRING", description="Stock sector"),
        bigquery.SchemaField("exchange", "STRING", description="Exchange"),

        # Date and time fields
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Hourly timestamp"),
        bigquery.SchemaField("timestamp", "INTEGER", description="Unix timestamp"),

        # OHLC data
        bigquery.SchemaField("open", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("high", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("low", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("close", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("volume", "INTEGER"),

        # Moving Averages
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_50", "FLOAT"),
        bigquery.SchemaField("sma_200", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),
        bigquery.SchemaField("ema_50", "FLOAT"),

        # Momentum Indicators
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),

        # Bollinger Bands
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_middle", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_width", "FLOAT"),

        # Volatility
        bigquery.SchemaField("atr", "FLOAT"),

        # Trend Indicators
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("plus_di", "FLOAT"),
        bigquery.SchemaField("minus_di", "FLOAT"),

        # Oscillators
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),

        # Volume Indicators
        bigquery.SchemaField("obv", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("pvo_signal", "FLOAT"),

        # Advanced Indicators
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("ppo_signal", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
    ]

    table = bigquery.Table(table_ref, schema=schema)
    table.description = "Hourly stock data with technical indicators"

    # Partitioning and clustering
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.HOUR,
        field="datetime"
    )
    table.clustering_fields = ["symbol", "sector"]

    try:
        try:
            existing_table = client.get_table(table_ref)
            logger.info(f"Table {table_ref} already exists")
            existing_table.schema = schema
            client.update_table(existing_table, ["schema"])
            logger.info(f"Updated schema for {table_ref}")
            return True
        except:
            logger.info(f"Creating new table {table_ref}")
            client.create_table(table)
            logger.info(f"✓ Successfully created {table_ref}")
            logger.info(f"  - Total fields: {len(schema)}")
            logger.info(f"  - Partitioned by: datetime (hourly)")
            logger.info(f"  - Clustered by: symbol, sector")
            return True
    except Exception as e:
        logger.error(f"✗ Error creating stock hourly table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_stock_5min_table():
    """Create stock_5min_top10_gainers table - mirrors crypto_5min_top10_gainers"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.stock_5min_top10_gainers'

    # Define schema - same indicators but for 5-minute intervals
    schema = [
        # Stock identification (simpler than hourly)
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),

        # Date and time fields
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "INTEGER"),

        # OHLC data
        bigquery.SchemaField("open", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("high", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("low", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("close", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("volume", "INTEGER"),

        # Moving Averages
        bigquery.SchemaField("sma_20", "FLOAT"),
        bigquery.SchemaField("sma_50", "FLOAT"),
        bigquery.SchemaField("ema_12", "FLOAT"),
        bigquery.SchemaField("ema_26", "FLOAT"),

        # Momentum Indicators
        bigquery.SchemaField("rsi", "FLOAT"),
        bigquery.SchemaField("macd", "FLOAT"),
        bigquery.SchemaField("macd_signal", "FLOAT"),
        bigquery.SchemaField("macd_hist", "FLOAT"),
        bigquery.SchemaField("momentum", "FLOAT"),
        bigquery.SchemaField("roc", "FLOAT"),

        # Bollinger Bands
        bigquery.SchemaField("bb_upper", "FLOAT"),
        bigquery.SchemaField("bb_middle", "FLOAT"),
        bigquery.SchemaField("bb_lower", "FLOAT"),
        bigquery.SchemaField("bb_width", "FLOAT"),

        # Volatility
        bigquery.SchemaField("atr", "FLOAT"),

        # Trend Indicators
        bigquery.SchemaField("adx", "FLOAT"),
        bigquery.SchemaField("plus_di", "FLOAT"),
        bigquery.SchemaField("minus_di", "FLOAT"),

        # Oscillators
        bigquery.SchemaField("cci", "FLOAT"),
        bigquery.SchemaField("williams_r", "FLOAT"),
        bigquery.SchemaField("stoch_k", "FLOAT"),
        bigquery.SchemaField("stoch_d", "FLOAT"),

        # Volume Indicators
        bigquery.SchemaField("obv", "FLOAT"),
        bigquery.SchemaField("pvo", "FLOAT"),
        bigquery.SchemaField("pvo_signal", "FLOAT"),

        # Advanced Indicators
        bigquery.SchemaField("kama", "FLOAT"),
        bigquery.SchemaField("trix", "FLOAT"),
        bigquery.SchemaField("ppo", "FLOAT"),
        bigquery.SchemaField("ppo_signal", "FLOAT"),
        bigquery.SchemaField("ultimate_oscillator", "FLOAT"),
        bigquery.SchemaField("awesome_oscillator", "FLOAT"),
    ]

    table = bigquery.Table(table_ref, schema=schema)
    table.description = "5-minute data for top 10 stock gainers with technical indicators"

    # Partitioning and clustering
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.HOUR,
        field="datetime"
    )
    table.clustering_fields = ["symbol"]

    try:
        try:
            existing_table = client.get_table(table_ref)
            logger.info(f"Table {table_ref} already exists")
            existing_table.schema = schema
            client.update_table(existing_table, ["schema"])
            logger.info(f"Updated schema for {table_ref}")
            return True
        except:
            logger.info(f"Creating new table {table_ref}")
            client.create_table(table)
            logger.info(f"✓ Successfully created {table_ref}")
            logger.info(f"  - Total fields: {len(schema)}")
            logger.info(f"  - Partitioned by: datetime (hourly)")
            logger.info(f"  - Clustered by: symbol")
            return True
    except Exception as e:
        logger.error(f"✗ Error creating stock 5min table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to create both stock tables"""

    logger.info("=" * 70)
    logger.info("CREATING STOCK HOURLY AND 5-MINUTE TABLES IN BIGQUERY")
    logger.info("=" * 70)
    logger.info(f"\nProject: {PROJECT_ID}")
    logger.info(f"Dataset: {DATASET_ID}")
    logger.info("")

    # Create hourly table
    logger.info("Creating stock_hourly_data table...")
    hourly_success = create_stock_hourly_table()
    logger.info("")

    # Create 5-minute table
    logger.info("Creating stock_5min_top10_gainers table...")
    fivemin_success = create_stock_5min_table()
    logger.info("")

    logger.info("=" * 70)
    if hourly_success and fivemin_success:
        logger.info("✓ All stock tables created successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Create stock_hourly_fetcher Cloud Function")
        logger.info("  2. Create stock_5min_fetcher Cloud Function")
        logger.info("  3. Deploy both functions")
        logger.info("  4. Set up Cloud Schedulers")
    else:
        logger.error("✗ Some tables failed to create")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
