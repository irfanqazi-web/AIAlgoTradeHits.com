"""
Create BigQuery tables for TwelveData integration
Supports: Stocks, ETFs, Forex, Crypto, Commodities, Indices, Bonds
"""
import sys
import io
from google.cloud import bigquery

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"  # Using existing dataset

def create_bigquery_client():
    """Create BigQuery client"""
    return bigquery.Client(project=PROJECT_ID)

def get_twelvedata_ohlcv_schema():
    """
    Standard schema for TwelveData OHLCV + technical indicators
    Covers all asset types: stocks, ETFs, forex, crypto, commodities, indices, bonds
    """
    return [
        # Asset identification
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Trading symbol (e.g., AAPL, BTC/USD)"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="Full name of asset"),
        bigquery.SchemaField("exchange", "STRING", mode="NULLABLE", description="Exchange (NASDAQ, NYSE, etc)"),
        bigquery.SchemaField("mic_code", "STRING", mode="NULLABLE", description="Market Identifier Code"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE", description="Quote currency (USD, EUR, etc)"),
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED", description="Asset class: stock, etf, forex, crypto, commodity, index, bond"),
        bigquery.SchemaField("country", "STRING", mode="NULLABLE", description="Country code"),

        # Timing
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Candle timestamp"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED", description="Candle date"),
        bigquery.SchemaField("interval", "STRING", mode="REQUIRED", description="Timeframe: 1min, 5min, 15min, 1h, 1day, etc"),

        # OHLCV data
        bigquery.SchemaField("open", "FLOAT64", mode="NULLABLE", description="Opening price"),
        bigquery.SchemaField("high", "FLOAT64", mode="NULLABLE", description="High price"),
        bigquery.SchemaField("low", "FLOAT64", mode="NULLABLE", description="Low price"),
        bigquery.SchemaField("close", "FLOAT64", mode="REQUIRED", description="Closing price"),
        bigquery.SchemaField("volume", "INT64", mode="NULLABLE", description="Trading volume"),

        # TwelveData metadata
        bigquery.SchemaField("data_source", "STRING", mode="REQUIRED", description="Always 'twelvedata'"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="When data was fetched"),
        bigquery.SchemaField("api_status", "STRING", mode="NULLABLE", description="API response status"),
    ]

def get_technical_indicators_schema():
    """
    71 technical indicators compatible with TwelveData API
    All indicators are NULLABLE since they require historical data
    """
    return [
        # Momentum Indicators (10)
        bigquery.SchemaField("rsi", "FLOAT64", mode="NULLABLE", description="Relative Strength Index (14)"),
        bigquery.SchemaField("macd", "FLOAT64", mode="NULLABLE", description="MACD line"),
        bigquery.SchemaField("macd_signal", "FLOAT64", mode="NULLABLE", description="MACD signal line"),
        bigquery.SchemaField("macd_hist", "FLOAT64", mode="NULLABLE", description="MACD histogram"),
        bigquery.SchemaField("stoch_k", "FLOAT64", mode="NULLABLE", description="Stochastic %K"),
        bigquery.SchemaField("stoch_d", "FLOAT64", mode="NULLABLE", description="Stochastic %D"),
        bigquery.SchemaField("williams_r", "FLOAT64", mode="NULLABLE", description="Williams %R"),
        bigquery.SchemaField("cci", "FLOAT64", mode="NULLABLE", description="Commodity Channel Index"),
        bigquery.SchemaField("roc", "FLOAT64", mode="NULLABLE", description="Rate of Change"),
        bigquery.SchemaField("momentum", "FLOAT64", mode="NULLABLE", description="Momentum (10)"),

        # Moving Averages (11)
        bigquery.SchemaField("sma_20", "FLOAT64", mode="NULLABLE", description="Simple MA 20"),
        bigquery.SchemaField("sma_50", "FLOAT64", mode="NULLABLE", description="Simple MA 50"),
        bigquery.SchemaField("sma_200", "FLOAT64", mode="NULLABLE", description="Simple MA 200"),
        bigquery.SchemaField("ema_12", "FLOAT64", mode="NULLABLE", description="Exponential MA 12"),
        bigquery.SchemaField("ema_26", "FLOAT64", mode="NULLABLE", description="Exponential MA 26"),
        bigquery.SchemaField("ema_50", "FLOAT64", mode="NULLABLE", description="Exponential MA 50"),
        bigquery.SchemaField("wma_20", "FLOAT64", mode="NULLABLE", description="Weighted MA 20"),
        bigquery.SchemaField("dema_20", "FLOAT64", mode="NULLABLE", description="Double Exponential MA 20"),
        bigquery.SchemaField("tema_20", "FLOAT64", mode="NULLABLE", description="Triple Exponential MA 20"),
        bigquery.SchemaField("kama_20", "FLOAT64", mode="NULLABLE", description="Kaufman Adaptive MA 20"),
        bigquery.SchemaField("vwap", "FLOAT64", mode="NULLABLE", description="Volume Weighted Average Price"),

        # Volatility (6)
        bigquery.SchemaField("bb_upper", "FLOAT64", mode="NULLABLE", description="Bollinger Band upper"),
        bigquery.SchemaField("bb_middle", "FLOAT64", mode="NULLABLE", description="Bollinger Band middle"),
        bigquery.SchemaField("bb_lower", "FLOAT64", mode="NULLABLE", description="Bollinger Band lower"),
        bigquery.SchemaField("atr", "FLOAT64", mode="NULLABLE", description="Average True Range (14)"),
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
        bigquery.SchemaField("cdl_doji", "INT64", mode="NULLABLE", description="Doji candlestick"),
        bigquery.SchemaField("cdl_hammer", "INT64", mode="NULLABLE", description="Hammer candlestick"),
        bigquery.SchemaField("cdl_engulfing", "INT64", mode="NULLABLE", description="Engulfing pattern"),
        bigquery.SchemaField("cdl_harami", "INT64", mode="NULLABLE", description="Harami pattern"),
        bigquery.SchemaField("cdl_morningstar", "INT64", mode="NULLABLE", description="Morning Star"),
        bigquery.SchemaField("cdl_3blackcrows", "INT64", mode="NULLABLE", description="Three Black Crows"),
        bigquery.SchemaField("cdl_2crows", "INT64", mode="NULLABLE", description="Two Crows"),
        bigquery.SchemaField("cdl_3inside", "INT64", mode="NULLABLE", description="Three Inside"),
        bigquery.SchemaField("cdl_3linestrike", "INT64", mode="NULLABLE", description="Three Line Strike"),
        bigquery.SchemaField("cdl_abandonedbaby", "INT64", mode="NULLABLE", description="Abandoned Baby"),

        # Statistical (7)
        bigquery.SchemaField("correl", "FLOAT64", mode="NULLABLE", description="Pearson Correlation"),
        bigquery.SchemaField("linearreg", "FLOAT64", mode="NULLABLE", description="Linear Regression"),
        bigquery.SchemaField("linearreg_slope", "FLOAT64", mode="NULLABLE", description="Linear Reg Slope"),
        bigquery.SchemaField("linearreg_angle", "FLOAT64", mode="NULLABLE", description="Linear Reg Angle"),
        bigquery.SchemaField("tsf", "FLOAT64", mode="NULLABLE", description="Time Series Forecast"),
        bigquery.SchemaField("variance", "FLOAT64", mode="NULLABLE", description="Variance"),
        bigquery.SchemaField("beta", "FLOAT64", mode="NULLABLE", description="Beta coefficient"),

        # Other Advanced (13)
        bigquery.SchemaField("ultosc", "FLOAT64", mode="NULLABLE", description="Ultimate Oscillator"),
        bigquery.SchemaField("bop", "FLOAT64", mode="NULLABLE", description="Balance of Power"),
        bigquery.SchemaField("cmo", "FLOAT64", mode="NULLABLE", description="Chande Momentum Oscillator"),
        bigquery.SchemaField("dpo", "FLOAT64", mode="NULLABLE", description="Detrended Price Oscillator"),
        bigquery.SchemaField("ht_dcperiod", "FLOAT64", mode="NULLABLE", description="HT Dominant Cycle Period"),
        bigquery.SchemaField("ht_dcphase", "FLOAT64", mode="NULLABLE", description="HT Dominant Cycle Phase"),
        bigquery.SchemaField("ht_trendmode", "INT64", mode="NULLABLE", description="HT Trend Mode"),
        bigquery.SchemaField("midpoint", "FLOAT64", mode="NULLABLE", description="MidPoint"),
        bigquery.SchemaField("midprice", "FLOAT64", mode="NULLABLE", description="MidPrice"),
        bigquery.SchemaField("ppo", "FLOAT64", mode="NULLABLE", description="Percentage Price Oscillator"),
        bigquery.SchemaField("stochrsi", "FLOAT64", mode="NULLABLE", description="Stochastic RSI"),
        bigquery.SchemaField("apo", "FLOAT64", mode="NULLABLE", description="Absolute Price Oscillator"),
        bigquery.SchemaField("ht_sine_lead", "FLOAT64", mode="NULLABLE", description="HT Sine Lead"),
    ]

def create_twelvedata_table(client, table_name, description, interval_desc):
    """Create a TwelveData OHLCV table with indicators"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    schema = get_twelvedata_ohlcv_schema() + get_technical_indicators_schema()

    table = bigquery.Table(table_id, schema=schema)
    table.description = f"{description} - {interval_desc} - from TwelveData API"

    # Partition by date for efficient queries
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date"
    )

    # Cluster by symbol and datetime for optimal performance
    table.clustering_fields = ["asset_type", "symbol", "datetime"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table: {table_name}")
        return True
    except Exception as e:
        print(f"❌ Error creating {table_name}: {str(e)}")
        return False

def create_finnhub_news_table(client):
    """Create table for Finnhub news and sentiment data"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.market_news_sentiment"

    schema = [
        # Article identification
        bigquery.SchemaField("article_id", "STRING", mode="REQUIRED", description="Unique article ID"),
        bigquery.SchemaField("category", "STRING", mode="NULLABLE", description="News category"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Article publish time"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED", description="Article publish date"),

        # Content
        bigquery.SchemaField("headline", "STRING", mode="REQUIRED", description="Article headline"),
        bigquery.SchemaField("summary", "STRING", mode="NULLABLE", description="Article summary"),
        bigquery.SchemaField("source", "STRING", mode="NULLABLE", description="News source"),
        bigquery.SchemaField("url", "STRING", mode="NULLABLE", description="Article URL"),
        bigquery.SchemaField("image", "STRING", mode="NULLABLE", description="Article image URL"),

        # Related symbols
        bigquery.SchemaField("related_symbols", "STRING", mode="REPEATED", description="Related stock symbols"),

        # Sentiment analysis
        bigquery.SchemaField("sentiment_score", "FLOAT64", mode="NULLABLE", description="Sentiment score (-1 to 1)"),
        bigquery.SchemaField("sentiment_label", "STRING", mode="NULLABLE", description="Positive, Negative, Neutral"),
        bigquery.SchemaField("bullish_percent", "FLOAT64", mode="NULLABLE", description="Bullish percentage"),
        bigquery.SchemaField("bearish_percent", "FLOAT64", mode="NULLABLE", description="Bearish percentage"),

        # Metadata
        bigquery.SchemaField("data_source", "STRING", mode="REQUIRED", description="Always 'finnhub'"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="When data was fetched"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Market news with sentiment analysis from Finnhub"

    # Partition by date
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date"
    )

    # Cluster by category and datetime
    table.clustering_fields = ["category", "datetime"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table: market_news_sentiment")
        return True
    except Exception as e:
        print(f"❌ Error creating market_news_sentiment: {str(e)}")
        return False

def create_finnhub_social_sentiment_table(client):
    """Create table for Finnhub social media sentiment (Reddit, Twitter)"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.social_sentiment"

    schema = [
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Stock symbol"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED", description="Sentiment date"),
        bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED", description="Timestamp"),

        # Reddit sentiment
        bigquery.SchemaField("reddit_mention", "INT64", mode="NULLABLE", description="Reddit mentions"),
        bigquery.SchemaField("reddit_positive_mention", "INT64", mode="NULLABLE", description="Positive mentions"),
        bigquery.SchemaField("reddit_negative_mention", "INT64", mode="NULLABLE", description="Negative mentions"),
        bigquery.SchemaField("reddit_score", "FLOAT64", mode="NULLABLE", description="Reddit sentiment score"),

        # Twitter sentiment
        bigquery.SchemaField("twitter_mention", "INT64", mode="NULLABLE", description="Twitter mentions"),
        bigquery.SchemaField("twitter_positive_mention", "INT64", mode="NULLABLE", description="Positive tweets"),
        bigquery.SchemaField("twitter_negative_mention", "INT64", mode="NULLABLE", description="Negative tweets"),
        bigquery.SchemaField("twitter_score", "FLOAT64", mode="NULLABLE", description="Twitter sentiment score"),

        # Aggregated
        bigquery.SchemaField("total_mentions", "INT64", mode="NULLABLE", description="Total mentions across platforms"),
        bigquery.SchemaField("overall_sentiment", "FLOAT64", mode="NULLABLE", description="Overall sentiment score"),

        # Metadata
        bigquery.SchemaField("data_source", "STRING", mode="REQUIRED", description="Always 'finnhub'"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", mode="REQUIRED", description="When data was fetched"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.description = "Social media sentiment from Reddit and Twitter via Finnhub"

    # Partition by date
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date"
    )

    # Cluster by symbol
    table.clustering_fields = ["symbol", "date"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Created table: social_sentiment")
        return True
    except Exception as e:
        print(f"❌ Error creating social_sentiment: {str(e)}")
        return False

def main():
    print("=" * 100)
    print("CREATING TWELVEDATA AND FINNHUB BIGQUERY TABLES")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("=" * 100)

    client = create_bigquery_client()

    print("\n📊 Creating TwelveData OHLCV Tables...")
    print("-" * 100)

    # TwelveData tables - organized by timeframe and asset type
    twelvedata_tables = [
        # Stocks
        ("stocks_daily_td", "US Stocks", "Daily OHLCV"),
        ("stocks_hourly_td", "US Stocks", "Hourly OHLCV"),
        ("stocks_5min_td", "US Stocks", "5-minute OHLCV"),

        # ETFs
        ("etfs_daily_td", "US ETFs", "Daily OHLCV"),
        ("etfs_hourly_td", "US ETFs", "Hourly OHLCV"),

        # Forex
        ("forex_daily_td", "Forex Pairs", "Daily OHLCV"),
        ("forex_hourly_td", "Forex Pairs", "Hourly OHLCV"),
        ("forex_5min_td", "Forex Pairs", "5-minute OHLCV"),

        # Crypto (supplement Kraken data)
        ("crypto_daily_td", "Cryptocurrencies", "Daily OHLCV"),
        ("crypto_hourly_td", "Cryptocurrencies", "Hourly OHLCV"),

        # Commodities
        ("commodities_daily_td", "Commodities", "Daily OHLCV"),
        ("commodities_hourly_td", "Commodities", "Hourly OHLCV"),

        # Indices
        ("indices_daily_td", "Market Indices", "Daily OHLCV"),
        ("indices_hourly_td", "Market Indices", "Hourly OHLCV"),

        # Bonds
        ("bonds_daily_td", "Treasury Bonds", "Daily OHLCV"),
    ]

    success_count = 0
    for table_name, description, interval in twelvedata_tables:
        if create_twelvedata_table(client, table_name, description, interval):
            success_count += 1

    print(f"\n✅ Created {success_count}/{len(twelvedata_tables)} TwelveData tables")

    print("\n📰 Creating Finnhub News & Sentiment Tables...")
    print("-" * 100)

    finnhub_success = 0
    if create_finnhub_news_table(client):
        finnhub_success += 1
    if create_finnhub_social_sentiment_table(client):
        finnhub_success += 1

    print(f"\n✅ Created {finnhub_success}/2 Finnhub tables")

    print("\n" + "=" * 100)
    print("✅ TABLE CREATION COMPLETE!")
    print("=" * 100)
    print(f"\nTotal Tables Created: {success_count + finnhub_success}")
    print(f"  - TwelveData OHLCV: {success_count} tables")
    print(f"  - Finnhub News/Sentiment: {finnhub_success} tables")
    print("\nNext Steps:")
    print("1. Build Cloud Functions to fetch data from TwelveData and Finnhub")
    print("2. Test data collection locally")
    print("3. Set up Cloud Schedulers for automated collection")
    print("4. Verify data in BigQuery")

if __name__ == "__main__":
    main()
