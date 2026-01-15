"""
Create crypto_daily_clean table for USD pairs only with all 85 indicators
Industry best practices: Partitioning, clustering, proper schema
"""
from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

# Define complete schema with all 85 fields
schema = [
    # Base fields (1-16)
    bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("open", "FLOAT64"),
    bigquery.SchemaField("high", "FLOAT64"),
    bigquery.SchemaField("low", "FLOAT64"),
    bigquery.SchemaField("close", "FLOAT64"),
    bigquery.SchemaField("volume", "INT64"),
    bigquery.SchemaField("sector", "STRING"),
    bigquery.SchemaField("industry", "STRING"),
    bigquery.SchemaField("market_cap", "FLOAT64"),
    bigquery.SchemaField("exchange", "STRING"),
    bigquery.SchemaField("mic_code", "STRING"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("country", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),

    # Momentum Indicators (17-25)
    bigquery.SchemaField("rsi", "FLOAT64"),
    bigquery.SchemaField("macd", "FLOAT64"),
    bigquery.SchemaField("macd_signal", "FLOAT64"),
    bigquery.SchemaField("macd_hist", "FLOAT64"),
    bigquery.SchemaField("roc", "FLOAT64"),
    bigquery.SchemaField("momentum", "FLOAT64"),
    bigquery.SchemaField("stoch_k", "FLOAT64"),
    bigquery.SchemaField("stoch_d", "FLOAT64"),
    bigquery.SchemaField("williams_r", "FLOAT64"),

    # Moving Averages (26-35)
    bigquery.SchemaField("sma_20", "FLOAT64"),
    bigquery.SchemaField("sma_50", "FLOAT64"),
    bigquery.SchemaField("sma_200", "FLOAT64"),
    bigquery.SchemaField("ema_12", "FLOAT64"),
    bigquery.SchemaField("ema_26", "FLOAT64"),
    bigquery.SchemaField("ema_50", "FLOAT64"),
    bigquery.SchemaField("ema_200", "FLOAT64"),
    bigquery.SchemaField("kama", "FLOAT64"),
    bigquery.SchemaField("tema", "FLOAT64"),
    bigquery.SchemaField("trix", "FLOAT64"),

    # Bollinger Bands (36-39)
    bigquery.SchemaField("bb_upper", "FLOAT64"),
    bigquery.SchemaField("bb_middle", "FLOAT64"),
    bigquery.SchemaField("bb_lower", "FLOAT64"),
    bigquery.SchemaField("bb_bandwidth", "FLOAT64"),

    # ADX Trend (40-42)
    bigquery.SchemaField("adx", "FLOAT64"),
    bigquery.SchemaField("plus_di", "FLOAT64"),
    bigquery.SchemaField("minus_di", "FLOAT64"),

    # Other Volatility/Trend (43-45)
    bigquery.SchemaField("atr", "FLOAT64"),
    bigquery.SchemaField("supertrend", "FLOAT64"),
    bigquery.SchemaField("supertrend_direction", "INT64"),

    # Volume Indicators (46-48)
    bigquery.SchemaField("obv", "FLOAT64"),
    bigquery.SchemaField("pvo", "FLOAT64"),
    bigquery.SchemaField("pvo_signal", "FLOAT64"),

    # Oscillators (49-50)
    bigquery.SchemaField("cci", "FLOAT64"),
    bigquery.SchemaField("ppo", "FLOAT64"),

    # Institutional Indicators (51-62) - NEW
    bigquery.SchemaField("mfi", "FLOAT64"),
    bigquery.SchemaField("cmf", "FLOAT64"),
    bigquery.SchemaField("ichimoku_tenkan", "FLOAT64"),
    bigquery.SchemaField("ichimoku_kijun", "FLOAT64"),
    bigquery.SchemaField("ichimoku_senkou_a", "FLOAT64"),
    bigquery.SchemaField("ichimoku_senkou_b", "FLOAT64"),
    bigquery.SchemaField("ichimoku_chikou", "FLOAT64"),
    bigquery.SchemaField("vwap_daily", "FLOAT64"),
    bigquery.SchemaField("vwap_weekly", "FLOAT64"),
    bigquery.SchemaField("volume_profile_poc", "FLOAT64"),
    bigquery.SchemaField("volume_profile_vah", "FLOAT64"),
    bigquery.SchemaField("volume_profile_val", "FLOAT64"),

    # ML Features - Returns (63-65)
    bigquery.SchemaField("return_1d", "FLOAT64"),
    bigquery.SchemaField("return_5d", "FLOAT64"),
    bigquery.SchemaField("return_20d", "FLOAT64"),

    # ML Features - Relative Positions (66-68)
    bigquery.SchemaField("price_to_sma20", "FLOAT64"),
    bigquery.SchemaField("price_to_sma50", "FLOAT64"),
    bigquery.SchemaField("price_to_sma200", "FLOAT64"),

    # ML Features - Indicator Dynamics (69-79)
    bigquery.SchemaField("rsi_delta", "FLOAT64"),
    bigquery.SchemaField("macd_delta", "FLOAT64"),
    bigquery.SchemaField("volume_ratio_20d", "FLOAT64"),
    bigquery.SchemaField("volatility_20d", "FLOAT64"),
    bigquery.SchemaField("price_momentum_5d", "FLOAT64"),
    bigquery.SchemaField("obv_slope_5d", "FLOAT64"),
    bigquery.SchemaField("bb_percent", "FLOAT64"),
    bigquery.SchemaField("atr_percent", "FLOAT64"),
    bigquery.SchemaField("volume_spike", "FLOAT64"),
    bigquery.SchemaField("price_range", "FLOAT64"),
    bigquery.SchemaField("high_low_spread", "FLOAT64"),

    # ML Features - Market Structure (80-82)
    bigquery.SchemaField("higher_high", "BOOL"),
    bigquery.SchemaField("lower_low", "BOOL"),
    bigquery.SchemaField("trend_strength", "FLOAT64"),

    # ML Features - Regime Detection (83-85)
    bigquery.SchemaField("regime_volatility", "STRING"),
    bigquery.SchemaField("regime_trend", "STRING"),
    bigquery.SchemaField("regime_volume", "STRING"),

    # Metadata
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
]

table_id = "aialgotradehits.crypto_trading_data.crypto_daily_clean"

# Table configuration with partitioning and clustering
table = bigquery.Table(table_id, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.MONTH,
    field="datetime"
)
table.clustering_fields = ["symbol", "sector", "exchange"]

print("="*100)
print("CREATING crypto_daily_clean TABLE (USD PAIRS ONLY)")
print("="*100)

try:
    client.delete_table(table_id, not_found_ok=True)
    print(f"Deleted existing table: {table_id}")
except:
    pass

table = client.create_table(table)
print(f"✅ Created table: {table_id}")
print(f"   - Fields: {len(schema)}")
print(f"   - Partitioning: MONTH on datetime")
print(f"   - Clustering: symbol, sector, exchange")
print("="*100)
