"""
Create Weekly Stocks Table in BigQuery
Designed to hold ALL US stocks (~20,000) with weekly summary data
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def create_weekly_stocks_table():
    """Create the weekly stocks summary table"""
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_ID}.stocks_weekly_summary"

    schema = [
        # Basic Information
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Stock ticker symbol"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="Company name"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE", description="Exchange (NYSE, NASDAQ, etc.)"),
        bigquery.SchemaField("type", "STRING", mode="NULLABLE", description="Security type (Common Stock, ETF, etc.)"),
        bigquery.SchemaField("sector", "STRING", mode="NULLABLE", description="Business sector"),
        bigquery.SchemaField("industry", "STRING", mode="NULLABLE", description="Industry within sector"),
        bigquery.SchemaField("country", "STRING", mode="NULLABLE", description="Country of listing"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE", description="Trading currency"),

        # Current Price Data
        bigquery.SchemaField("current_price", "FLOAT64", mode="NULLABLE", description="Current/Latest price"),
        bigquery.SchemaField("open_price", "FLOAT64", mode="NULLABLE", description="Week open price"),
        bigquery.SchemaField("high_price", "FLOAT64", mode="NULLABLE", description="Week high price"),
        bigquery.SchemaField("low_price", "FLOAT64", mode="NULLABLE", description="Week low price"),
        bigquery.SchemaField("close_price", "FLOAT64", mode="NULLABLE", description="Week close price"),
        bigquery.SchemaField("previous_close", "FLOAT64", mode="NULLABLE", description="Previous week close"),

        # Volume Data
        bigquery.SchemaField("volume", "INT64", mode="NULLABLE", description="Weekly trading volume"),
        bigquery.SchemaField("average_volume", "INT64", mode="NULLABLE", description="Average daily volume"),

        # Performance Metrics
        bigquery.SchemaField("weekly_change", "FLOAT64", mode="NULLABLE", description="Price change this week ($)"),
        bigquery.SchemaField("weekly_change_percent", "FLOAT64", mode="NULLABLE", description="Price change this week (%)"),
        bigquery.SchemaField("monthly_change_percent", "FLOAT64", mode="NULLABLE", description="30-day price change (%)"),
        bigquery.SchemaField("ytd_change_percent", "FLOAT64", mode="NULLABLE", description="Year-to-date change (%)"),

        # Valuation Metrics
        bigquery.SchemaField("market_cap", "FLOAT64", mode="NULLABLE", description="Market capitalization"),
        bigquery.SchemaField("pe_ratio", "FLOAT64", mode="NULLABLE", description="Price-to-Earnings ratio"),
        bigquery.SchemaField("eps", "FLOAT64", mode="NULLABLE", description="Earnings per share"),
        bigquery.SchemaField("dividend_yield", "FLOAT64", mode="NULLABLE", description="Dividend yield (%)"),
        bigquery.SchemaField("beta", "FLOAT64", mode="NULLABLE", description="Beta (volatility vs market)"),

        # Trading Ranges
        bigquery.SchemaField("week_52_high", "FLOAT64", mode="NULLABLE", description="52-week high price"),
        bigquery.SchemaField("week_52_low", "FLOAT64", mode="NULLABLE", description="52-week low price"),
        bigquery.SchemaField("percent_from_52_high", "FLOAT64", mode="NULLABLE", description="% below 52-week high"),
        bigquery.SchemaField("percent_from_52_low", "FLOAT64", mode="NULLABLE", description="% above 52-week low"),

        # Volatility Metrics (for day trading analysis)
        bigquery.SchemaField("volatility_weekly", "FLOAT64", mode="NULLABLE", description="Weekly price volatility %"),
        bigquery.SchemaField("volatility_monthly", "FLOAT64", mode="NULLABLE", description="Monthly price volatility %"),
        bigquery.SchemaField("atr", "FLOAT64", mode="NULLABLE", description="Average True Range"),
        bigquery.SchemaField("atr_percent", "FLOAT64", mode="NULLABLE", description="ATR as % of price"),

        # Day Trading Scoring
        bigquery.SchemaField("day_trade_score", "FLOAT64", mode="NULLABLE", description="Day trading suitability score 0-100"),
        bigquery.SchemaField("liquidity_score", "FLOAT64", mode="NULLABLE", description="Liquidity score 0-100"),
        bigquery.SchemaField("momentum_score", "FLOAT64", mode="NULLABLE", description="Momentum score 0-100"),

        # Technical Indicators (Weekly)
        bigquery.SchemaField("rsi_weekly", "FLOAT64", mode="NULLABLE", description="Weekly RSI"),
        bigquery.SchemaField("macd_weekly", "FLOAT64", mode="NULLABLE", description="Weekly MACD"),
        bigquery.SchemaField("macd_signal_weekly", "FLOAT64", mode="NULLABLE", description="Weekly MACD Signal"),
        bigquery.SchemaField("sma_20", "FLOAT64", mode="NULLABLE", description="20-day SMA"),
        bigquery.SchemaField("sma_50", "FLOAT64", mode="NULLABLE", description="50-day SMA"),
        bigquery.SchemaField("sma_200", "FLOAT64", mode="NULLABLE", description="200-day SMA"),

        # Trend Analysis
        bigquery.SchemaField("trend_short", "STRING", mode="NULLABLE", description="Short-term trend (bullish/bearish/neutral)"),
        bigquery.SchemaField("trend_medium", "STRING", mode="NULLABLE", description="Medium-term trend"),
        bigquery.SchemaField("trend_long", "STRING", mode="NULLABLE", description="Long-term trend"),
        bigquery.SchemaField("above_sma_20", "BOOLEAN", mode="NULLABLE", description="Price above 20-day SMA"),
        bigquery.SchemaField("above_sma_50", "BOOLEAN", mode="NULLABLE", description="Price above 50-day SMA"),
        bigquery.SchemaField("above_sma_200", "BOOLEAN", mode="NULLABLE", description="Price above 200-day SMA"),

        # Classification for NLP Search
        bigquery.SchemaField("market_cap_category", "STRING", mode="NULLABLE", description="mega/large/mid/small/micro cap"),
        bigquery.SchemaField("volatility_category", "STRING", mode="NULLABLE", description="high/medium/low volatility"),
        bigquery.SchemaField("momentum_category", "STRING", mode="NULLABLE", description="strong_up/up/neutral/down/strong_down"),
        bigquery.SchemaField("value_category", "STRING", mode="NULLABLE", description="undervalued/fair/overvalued"),

        # Metadata
        bigquery.SchemaField("week_start_date", "DATE", mode="NULLABLE", description="Start of the week"),
        bigquery.SchemaField("week_end_date", "DATE", mode="NULLABLE", description="End of the week"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="When data was fetched"),
        bigquery.SchemaField("data_source", "STRING", mode="NULLABLE", description="Data source (twelvedata)"),

        # Active List Flag
        bigquery.SchemaField("is_active_pick", "BOOLEAN", mode="NULLABLE", description="Selected for active trading list"),
        bigquery.SchemaField("active_pick_reason", "STRING", mode="NULLABLE", description="Why selected for active list"),
    ]

    # Create table with clustering for faster queries
    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="fetch_timestamp"
    )
    table.clustering_fields = ["sector", "market_cap_category", "volatility_category"]

    try:
        table = client.create_table(table)
        print(f"Created table {table_id}")
        print(f"Columns: {len(schema)}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_id} already exists")
            return True
        print(f"Error creating table: {e}")
        return False


def create_weekly_cryptos_table():
    """Create the weekly cryptos summary table"""
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_ID}.cryptos_weekly_summary"

    schema = [
        # Basic Information
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Crypto symbol (BTC, ETH, etc.)"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="Full name (Bitcoin, Ethereum, etc.)"),
        bigquery.SchemaField("pair", "STRING", mode="NULLABLE", description="Trading pair (BTC/USD)"),
        bigquery.SchemaField("category", "STRING", mode="NULLABLE", description="Category (DeFi, Layer1, Meme, etc.)"),
        bigquery.SchemaField("subcategory", "STRING", mode="NULLABLE", description="Subcategory"),

        # Current Price Data
        bigquery.SchemaField("current_price", "FLOAT64", mode="NULLABLE", description="Current/Latest price"),
        bigquery.SchemaField("open_price", "FLOAT64", mode="NULLABLE", description="Week open price"),
        bigquery.SchemaField("high_price", "FLOAT64", mode="NULLABLE", description="Week high price"),
        bigquery.SchemaField("low_price", "FLOAT64", mode="NULLABLE", description="Week low price"),
        bigquery.SchemaField("close_price", "FLOAT64", mode="NULLABLE", description="Week close price"),
        bigquery.SchemaField("previous_close", "FLOAT64", mode="NULLABLE", description="Previous week close"),

        # Volume Data
        bigquery.SchemaField("volume_24h", "FLOAT64", mode="NULLABLE", description="24-hour trading volume USD"),
        bigquery.SchemaField("volume_weekly", "FLOAT64", mode="NULLABLE", description="Weekly trading volume USD"),

        # Performance Metrics
        bigquery.SchemaField("weekly_change", "FLOAT64", mode="NULLABLE", description="Price change this week ($)"),
        bigquery.SchemaField("weekly_change_percent", "FLOAT64", mode="NULLABLE", description="Price change this week (%)"),
        bigquery.SchemaField("monthly_change_percent", "FLOAT64", mode="NULLABLE", description="30-day price change (%)"),
        bigquery.SchemaField("ytd_change_percent", "FLOAT64", mode="NULLABLE", description="Year-to-date change (%)"),

        # Market Data
        bigquery.SchemaField("market_cap", "FLOAT64", mode="NULLABLE", description="Market capitalization USD"),
        bigquery.SchemaField("market_cap_rank", "INT64", mode="NULLABLE", description="Market cap ranking"),
        bigquery.SchemaField("circulating_supply", "FLOAT64", mode="NULLABLE", description="Circulating supply"),
        bigquery.SchemaField("total_supply", "FLOAT64", mode="NULLABLE", description="Total supply"),
        bigquery.SchemaField("max_supply", "FLOAT64", mode="NULLABLE", description="Maximum supply"),

        # Trading Ranges
        bigquery.SchemaField("ath", "FLOAT64", mode="NULLABLE", description="All-time high price"),
        bigquery.SchemaField("ath_date", "DATE", mode="NULLABLE", description="Date of all-time high"),
        bigquery.SchemaField("percent_from_ath", "FLOAT64", mode="NULLABLE", description="% below all-time high"),
        bigquery.SchemaField("atl", "FLOAT64", mode="NULLABLE", description="All-time low price"),
        bigquery.SchemaField("atl_date", "DATE", mode="NULLABLE", description="Date of all-time low"),

        # Volatility Metrics
        bigquery.SchemaField("volatility_weekly", "FLOAT64", mode="NULLABLE", description="Weekly price volatility %"),
        bigquery.SchemaField("volatility_monthly", "FLOAT64", mode="NULLABLE", description="Monthly price volatility %"),
        bigquery.SchemaField("atr", "FLOAT64", mode="NULLABLE", description="Average True Range"),
        bigquery.SchemaField("atr_percent", "FLOAT64", mode="NULLABLE", description="ATR as % of price"),

        # Day Trading Scoring
        bigquery.SchemaField("day_trade_score", "FLOAT64", mode="NULLABLE", description="Day trading suitability score 0-100"),
        bigquery.SchemaField("liquidity_score", "FLOAT64", mode="NULLABLE", description="Liquidity score 0-100"),
        bigquery.SchemaField("momentum_score", "FLOAT64", mode="NULLABLE", description="Momentum score 0-100"),

        # Technical Indicators (Weekly)
        bigquery.SchemaField("rsi_weekly", "FLOAT64", mode="NULLABLE", description="Weekly RSI"),
        bigquery.SchemaField("macd_weekly", "FLOAT64", mode="NULLABLE", description="Weekly MACD"),
        bigquery.SchemaField("macd_signal_weekly", "FLOAT64", mode="NULLABLE", description="Weekly MACD Signal"),
        bigquery.SchemaField("sma_20", "FLOAT64", mode="NULLABLE", description="20-day SMA"),
        bigquery.SchemaField("sma_50", "FLOAT64", mode="NULLABLE", description="50-day SMA"),
        bigquery.SchemaField("sma_200", "FLOAT64", mode="NULLABLE", description="200-day SMA"),

        # Trend Analysis
        bigquery.SchemaField("trend_short", "STRING", mode="NULLABLE", description="Short-term trend"),
        bigquery.SchemaField("trend_medium", "STRING", mode="NULLABLE", description="Medium-term trend"),
        bigquery.SchemaField("trend_long", "STRING", mode="NULLABLE", description="Long-term trend"),
        bigquery.SchemaField("above_sma_20", "BOOLEAN", mode="NULLABLE", description="Price above 20-day SMA"),
        bigquery.SchemaField("above_sma_50", "BOOLEAN", mode="NULLABLE", description="Price above 50-day SMA"),
        bigquery.SchemaField("above_sma_200", "BOOLEAN", mode="NULLABLE", description="Price above 200-day SMA"),

        # Classification for NLP Search
        bigquery.SchemaField("market_cap_category", "STRING", mode="NULLABLE", description="large/mid/small/micro cap"),
        bigquery.SchemaField("volatility_category", "STRING", mode="NULLABLE", description="high/medium/low volatility"),
        bigquery.SchemaField("momentum_category", "STRING", mode="NULLABLE", description="strong_up/up/neutral/down/strong_down"),

        # Metadata
        bigquery.SchemaField("week_start_date", "DATE", mode="NULLABLE", description="Start of the week"),
        bigquery.SchemaField("week_end_date", "DATE", mode="NULLABLE", description="End of the week"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="When data was fetched"),
        bigquery.SchemaField("data_source", "STRING", mode="NULLABLE", description="Data source"),

        # Active List Flag
        bigquery.SchemaField("is_active_pick", "BOOLEAN", mode="NULLABLE", description="Selected for active trading list"),
        bigquery.SchemaField("active_pick_reason", "STRING", mode="NULLABLE", description="Why selected for active list"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="fetch_timestamp"
    )
    table.clustering_fields = ["category", "market_cap_category", "volatility_category"]

    try:
        table = client.create_table(table)
        print(f"Created table {table_id}")
        print(f"Columns: {len(schema)}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_id} already exists")
            return True
        print(f"Error creating table: {e}")
        return False


def create_active_trading_list_table():
    """Create the active trading list table - generated from weekly analysis"""
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_ID}.active_trading_list"

    schema = [
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED", description="stock or crypto"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Ticker/Symbol"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="Company/Crypto name"),
        bigquery.SchemaField("current_price", "FLOAT64", mode="NULLABLE", description="Current price"),
        bigquery.SchemaField("sector", "STRING", mode="NULLABLE", description="Sector/Category"),

        # Why selected
        bigquery.SchemaField("selection_rank", "INT64", mode="NULLABLE", description="Ranking 1-100"),
        bigquery.SchemaField("day_trade_score", "FLOAT64", mode="NULLABLE", description="Day trading score 0-100"),
        bigquery.SchemaField("selection_reason", "STRING", mode="NULLABLE", description="Why selected"),

        # Key metrics for quick reference
        bigquery.SchemaField("weekly_change_percent", "FLOAT64", mode="NULLABLE", description="Weekly change %"),
        bigquery.SchemaField("volatility_percent", "FLOAT64", mode="NULLABLE", description="Volatility %"),
        bigquery.SchemaField("volume_ratio", "FLOAT64", mode="NULLABLE", description="Volume vs average"),
        bigquery.SchemaField("rsi", "FLOAT64", mode="NULLABLE", description="RSI"),
        bigquery.SchemaField("trend", "STRING", mode="NULLABLE", description="Overall trend"),

        # Metadata
        bigquery.SchemaField("generated_date", "DATE", mode="REQUIRED", description="When list was generated"),
        bigquery.SchemaField("valid_until", "DATE", mode="NULLABLE", description="List valid until"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="Timestamp"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="generated_date"
    )

    try:
        table = client.create_table(table)
        print(f"Created table {table_id}")
        print(f"Columns: {len(schema)}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_id} already exists")
            return True
        print(f"Error creating table: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CREATING WEEKLY ANALYSIS TABLES IN BIGQUERY")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("=" * 60)

    print("\n1. Creating stocks_weekly_summary table...")
    create_weekly_stocks_table()

    print("\n2. Creating cryptos_weekly_summary table...")
    create_weekly_cryptos_table()

    print("\n3. Creating active_trading_list table...")
    create_active_trading_list_table()

    print("\n" + "=" * 60)
    print("DONE - Tables created successfully!")
    print("=" * 60)
