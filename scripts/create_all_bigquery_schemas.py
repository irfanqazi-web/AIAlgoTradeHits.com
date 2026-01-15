"""
Create all BigQuery tables for multi-asset trading data platform
"""
import sys
import io
from google.cloud import bigquery
from google.oauth2 import service_account

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "cryptobot-462709"
DATASET_ID = "trading_data_unified"

def create_bigquery_client():
    """Create BigQuery client"""
    return bigquery.Client(project=PROJECT_ID)

def create_dataset(client):
    """Create dataset if it doesn't exist"""
    dataset_id = f"{PROJECT_ID}.{DATASET_ID}"

    try:
        client.get_dataset(dataset_id)
        print(f"✅ Dataset {dataset_id} already exists")
    except:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        dataset.description = "Unified multi-asset trading data with technical indicators"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"✅ Created dataset {dataset_id}")

def get_standard_ohlcv_schema():
    """Get standard OHLCV + metadata schema (15 fields)"""
    return [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Trading symbol"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="Full name"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE", description="Exchange name"),
        bigquery.SchemaField("mic_code", "STRING", mode="NULLABLE", description="Market identifier code"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE", description="Trading currency"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Timestamp"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED", description="Date"),
        bigquery.SchemaField("open", "FLOAT64", mode="NULLABLE", description="Opening price"),
        bigquery.SchemaField("high", "FLOAT64", mode="NULLABLE", description="High price"),
        bigquery.SchemaField("low", "FLOAT64", mode="NULLABLE", description="Low price"),
        bigquery.SchemaField("close", "FLOAT64", mode="REQUIRED", description="Closing price"),
        bigquery.SchemaField("volume", "INT64", mode="NULLABLE", description="Trading volume"),
        bigquery.SchemaField("adjusted_close", "FLOAT64", mode="NULLABLE", description="Adjusted close"),
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED", description="Asset class"),
        bigquery.SchemaField("data_source", "STRING", mode="REQUIRED", description="Data provider"),
    ]

def get_technical_indicators_schema():
    """Get all 71 technical indicators schema"""
    return [
        # Momentum Indicators (10)
        bigquery.SchemaField("rsi", "FLOAT64", mode="NULLABLE", description="Relative Strength Index"),
        bigquery.SchemaField("macd", "FLOAT64", mode="NULLABLE", description="MACD"),
        bigquery.SchemaField("macd_signal", "FLOAT64", mode="NULLABLE", description="MACD Signal"),
        bigquery.SchemaField("macd_hist", "FLOAT64", mode="NULLABLE", description="MACD Histogram"),
        bigquery.SchemaField("stoch_k", "FLOAT64", mode="NULLABLE", description="Stochastic %K"),
        bigquery.SchemaField("stoch_d", "FLOAT64", mode="NULLABLE", description="Stochastic %D"),
        bigquery.SchemaField("williams_r", "FLOAT64", mode="NULLABLE", description="Williams %R"),
        bigquery.SchemaField("cci", "FLOAT64", mode="NULLABLE", description="Commodity Channel Index"),
        bigquery.SchemaField("roc", "FLOAT64", mode="NULLABLE", description="Rate of Change"),
        bigquery.SchemaField("momentum", "FLOAT64", mode="NULLABLE", description="Momentum"),

        # Moving Averages (11)
        bigquery.SchemaField("sma_20", "FLOAT64", mode="NULLABLE", description="SMA 20"),
        bigquery.SchemaField("sma_50", "FLOAT64", mode="NULLABLE", description="SMA 50"),
        bigquery.SchemaField("sma_200", "FLOAT64", mode="NULLABLE", description="SMA 200"),
        bigquery.SchemaField("ema_12", "FLOAT64", mode="NULLABLE", description="EMA 12"),
        bigquery.SchemaField("ema_26", "FLOAT64", mode="NULLABLE", description="EMA 26"),
        bigquery.SchemaField("ema_50", "FLOAT64", mode="NULLABLE", description="EMA 50"),
        bigquery.SchemaField("wma_20", "FLOAT64", mode="NULLABLE", description="WMA 20"),
        bigquery.SchemaField("dema_20", "FLOAT64", mode="NULLABLE", description="DEMA 20"),
        bigquery.SchemaField("tema_20", "FLOAT64", mode="NULLABLE", description="TEMA 20"),
        bigquery.SchemaField("kama_20", "FLOAT64", mode="NULLABLE", description="KAMA 20"),
        bigquery.SchemaField("vwap", "FLOAT64", mode="NULLABLE", description="VWAP"),

        # Volatility (6)
        bigquery.SchemaField("bb_upper", "FLOAT64", mode="NULLABLE", description="Bollinger Upper"),
        bigquery.SchemaField("bb_middle", "FLOAT64", mode="NULLABLE", description="Bollinger Middle"),
        bigquery.SchemaField("bb_lower", "FLOAT64", mode="NULLABLE", description="Bollinger Lower"),
        bigquery.SchemaField("atr", "FLOAT64", mode="NULLABLE", description="Average True Range"),
        bigquery.SchemaField("natr", "FLOAT64", mode="NULLABLE", description="Normalized ATR"),
        bigquery.SchemaField("stddev", "FLOAT64", mode="NULLABLE", description="Standard Deviation"),

        # Volume (4)
        bigquery.SchemaField("obv", "FLOAT64", mode="NULLABLE", description="On Balance Volume"),
        bigquery.SchemaField("ad", "FLOAT64", mode="NULLABLE", description="Accumulation/Distribution"),
        bigquery.SchemaField("adosc", "FLOAT64", mode="NULLABLE", description="Chaikin A/D Oscillator"),
        bigquery.SchemaField("pvo", "FLOAT64", mode="NULLABLE", description="Percentage Volume Oscillator"),

        # Trend (10)
        bigquery.SchemaField("adx", "FLOAT64", mode="NULLABLE", description="Average Directional Index"),
        bigquery.SchemaField("adxr", "FLOAT64", mode="NULLABLE", description="ADX Rating"),
        bigquery.SchemaField("plus_di", "FLOAT64", mode="NULLABLE", description="Plus Directional Indicator"),
        bigquery.SchemaField("minus_di", "FLOAT64", mode="NULLABLE", description="Minus Directional Indicator"),
        bigquery.SchemaField("aroon_up", "FLOAT64", mode="NULLABLE", description="Aroon Up"),
        bigquery.SchemaField("aroon_down", "FLOAT64", mode="NULLABLE", description="Aroon Down"),
        bigquery.SchemaField("aroonosc", "FLOAT64", mode="NULLABLE", description="Aroon Oscillator"),
        bigquery.SchemaField("trix", "FLOAT64", mode="NULLABLE", description="TRIX"),
        bigquery.SchemaField("dx", "FLOAT64", mode="NULLABLE", description="Directional Movement Index"),
        bigquery.SchemaField("sar", "FLOAT64", mode="NULLABLE", description="Parabolic SAR"),

        # Pattern Recognition (10)
        bigquery.SchemaField("cdl_doji", "FLOAT64", mode="NULLABLE", description="Doji Pattern"),
        bigquery.SchemaField("cdl_hammer", "FLOAT64", mode="NULLABLE", description="Hammer Pattern"),
        bigquery.SchemaField("cdl_engulfing", "FLOAT64", mode="NULLABLE", description="Engulfing Pattern"),
        bigquery.SchemaField("cdl_harami", "FLOAT64", mode="NULLABLE", description="Harami Pattern"),
        bigquery.SchemaField("cdl_morningstar", "FLOAT64", mode="NULLABLE", description="Morning Star"),
        bigquery.SchemaField("cdl_3blackcrows", "FLOAT64", mode="NULLABLE", description="Three Black Crows"),
        bigquery.SchemaField("cdl_2crows", "FLOAT64", mode="NULLABLE", description="Two Crows"),
        bigquery.SchemaField("cdl_3inside", "FLOAT64", mode="NULLABLE", description="Three Inside"),
        bigquery.SchemaField("cdl_3linestrike", "FLOAT64", mode="NULLABLE", description="Three Line Strike"),
        bigquery.SchemaField("cdl_abandonedbaby", "FLOAT64", mode="NULLABLE", description="Abandoned Baby"),

        # Statistical (7)
        bigquery.SchemaField("correl", "FLOAT64", mode="NULLABLE", description="Correlation"),
        bigquery.SchemaField("linearreg", "FLOAT64", mode="NULLABLE", description="Linear Regression"),
        bigquery.SchemaField("linearreg_slope", "FLOAT64", mode="NULLABLE", description="Linear Reg Slope"),
        bigquery.SchemaField("linearreg_angle", "FLOAT64", mode="NULLABLE", description="Linear Reg Angle"),
        bigquery.SchemaField("tsf", "FLOAT64", mode="NULLABLE", description="Time Series Forecast"),
        bigquery.SchemaField("variance", "FLOAT64", mode="NULLABLE", description="Variance"),
        bigquery.SchemaField("beta", "FLOAT64", mode="NULLABLE", description="Beta"),

        # Other Advanced (13)
        bigquery.SchemaField("ultosc", "FLOAT64", mode="NULLABLE", description="Ultimate Oscillator"),
        bigquery.SchemaField("bop", "FLOAT64", mode="NULLABLE", description="Balance of Power"),
        bigquery.SchemaField("cmo", "FLOAT64", mode="NULLABLE", description="Chande Momentum Oscillator"),
        bigquery.SchemaField("dpo", "FLOAT64", mode="NULLABLE", description="Detrended Price Oscillator"),
        bigquery.SchemaField("ht_dcperiod", "FLOAT64", mode="NULLABLE", description="HT Dominant Cycle Period"),
        bigquery.SchemaField("ht_dcphase", "FLOAT64", mode="NULLABLE", description="HT Dominant Cycle Phase"),
        bigquery.SchemaField("ht_trendmode", "FLOAT64", mode="NULLABLE", description="HT Trend Mode"),
        bigquery.SchemaField("midpoint", "FLOAT64", mode="NULLABLE", description="MidPoint"),
        bigquery.SchemaField("midprice", "FLOAT64", mode="NULLABLE", description="MidPrice"),
        bigquery.SchemaField("ppo", "FLOAT64", mode="NULLABLE", description="PPO"),
        bigquery.SchemaField("stochrsi", "FLOAT64", mode="NULLABLE", description="Stochastic RSI"),
        bigquery.SchemaField("apo", "FLOAT64", mode="NULLABLE", description="APO"),
        bigquery.SchemaField("ht_sine_lead", "FLOAT64", mode="NULLABLE", description="HT Sine Lead"),

        # Metadata
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="Data fetch time"),
    ]

def create_ohlcv_table(client, table_name, asset_type_desc):
    """Create standard OHLCV table with indicators"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    schema = get_standard_ohlcv_schema() + get_technical_indicators_schema()

    table = bigquery.Table(table_id, schema=schema)
    table.description = f"{asset_type_desc} with 71 technical indicators"

    # Partition by date
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date"
    )

    # Cluster by symbol for better query performance
    table.clustering_fields = ["symbol", "datetime"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def create_fundamentals_table(client):
    """Create stock fundamentals table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.stock_fundamentals"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("industry", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("market_cap", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("enterprise_value", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("trailing_pe", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("forward_pe", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("peg_ratio", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("price_to_sales", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("price_to_book", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("enterprise_to_revenue", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("enterprise_to_ebitda", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("profit_margin", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("operating_margin", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("return_on_assets", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("return_on_equity", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("revenue_ttm", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("revenue_per_share", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("quarterly_revenue_growth", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("gross_profit_ttm", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ebitda", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("net_income_ttm", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("diluted_eps", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("quarterly_earnings_growth", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("total_cash", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("total_cash_per_share", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("total_debt", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("debt_to_equity", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("current_ratio", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("book_value_per_share", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("operating_cash_flow", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("free_cash_flow", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fifty_two_week_low", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fifty_two_week_high", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("ceo", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("employees", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("website", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("last_updated", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Stock fundamental data and company information"
    table.clustering_fields = ["symbol"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def create_earnings_table(client):
    """Create earnings calendar table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.earnings_calendar"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("earnings_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("earnings_time", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("eps_estimate", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("eps_actual", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("eps_difference", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("eps_surprise_percent", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("revenue_estimate", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("revenue_actual", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("fiscal_quarter", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("fiscal_year", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Earnings calendar with estimates and actuals"
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="earnings_date"
    )
    table.clustering_fields = ["symbol", "earnings_date"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def create_dividends_table(client):
    """Create dividends history table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.dividends_history"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("ex_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("payment_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("record_date", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("dividend_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("frequency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Dividend payment history"
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="ex_date"
    )
    table.clustering_fields = ["symbol", "ex_date"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def create_splits_table(client):
    """Create stock splits table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.stock_splits_history"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("split_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("split_ratio", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("from_factor", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("to_factor", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("pre_split_price", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Stock split history"
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="split_date"
    )
    table.clustering_fields = ["symbol", "split_date"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def create_insider_table(client):
    """Create insider transactions table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.insider_transactions"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("full_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("position", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("transaction_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("date_reported", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("transaction_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("is_direct", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("shares", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("value", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("price_per_share", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("shares_owned_after", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Insider trading transactions"
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="transaction_date"
    )
    table.clustering_fields = ["symbol", "transaction_date"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def create_market_movers_table(client):
    """Create market movers table"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.market_movers_daily"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("last_price", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("high", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("low", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("volume", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("change", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("percent_change", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("rank", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Top market movers across all asset classes"
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date"
    )
    table.clustering_fields = ["asset_type", "category", "date"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table {table_id}")
    except Exception as e:
        print(f"❌ Error creating {table_id}: {str(e)}")

def main():
    print("=" * 100)
    print("CREATING ALL BIGQUERY TABLES FOR MULTI-ASSET TRADING PLATFORM")
    print("=" * 100)

    client = create_bigquery_client()

    # Create dataset
    print("\n1. Creating Dataset...")
    create_dataset(client)

    # Create OHLCV tables
    print("\n2. Creating OHLCV Tables with 71 Indicators...")

    ohlcv_tables = [
        ("stocks_daily", "US Stocks daily data"),
        ("stocks_hourly", "US Stocks hourly data"),
        ("stocks_5min_top100", "Top 100 stocks 5-minute data"),
        ("etfs_daily", "US ETFs daily data"),
        ("etfs_hourly", "US ETFs hourly data"),
        ("etfs_5min_top50", "Top 50 ETFs 5-minute data"),
        ("forex_daily", "Forex daily data"),
        ("forex_hourly", "Forex hourly data"),
        ("forex_5min_major20", "Major 20 forex pairs 5-minute data"),
        ("commodities_daily", "Commodities daily data"),
        ("commodities_hourly", "Commodities hourly data"),
        ("indices_daily", "US Indices daily data"),
        ("indices_hourly", "US Indices hourly data"),
        ("bonds_daily", "US Treasury bonds daily data"),
    ]

    for table_name, description in ohlcv_tables:
        create_ohlcv_table(client, table_name, description)

    # Create fundamental data tables
    print("\n3. Creating Fundamental Data Tables...")
    create_fundamentals_table(client)
    create_earnings_table(client)
    create_dividends_table(client)
    create_splits_table(client)
    create_insider_table(client)
    create_market_movers_table(client)

    print("\n" + "=" * 100)
    print("✅ ALL TABLES CREATED SUCCESSFULLY!")
    print("=" * 100)
    print(f"\nDataset: {PROJECT_ID}.{DATASET_ID}")
    print(f"Total Tables: 20")
    print(f"  - 14 OHLCV tables (daily/hourly/5-min)")
    print(f"  - 6 Fundamental data tables")
    print("\nNext Steps:")
    print("1. Build Cloud Functions to populate these tables")
    print("2. Set up Cloud Schedulers for automated data collection")
    print("3. Test data collection across all asset classes")

if __name__ == "__main__":
    main()
