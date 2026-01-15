#!/usr/bin/env python3
"""Create BigQuery tables for comprehensive 50% capacity data"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

client = bigquery.Client(project=PROJECT_ID)

# Comprehensive daily table schema (stocks & ETFs)
COMPREHENSIVE_DAILY_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("datetime", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("open", "FLOAT64"),
    bigquery.SchemaField("high", "FLOAT64"),
    bigquery.SchemaField("low", "FLOAT64"),
    bigquery.SchemaField("close", "FLOAT64"),
    bigquery.SchemaField("volume", "INT64"),
    # Momentum Indicators
    bigquery.SchemaField("rsi", "FLOAT64"),
    bigquery.SchemaField("macd", "FLOAT64"),
    bigquery.SchemaField("macd_signal", "FLOAT64"),
    bigquery.SchemaField("macd_histogram", "FLOAT64"),
    bigquery.SchemaField("stoch_k", "FLOAT64"),
    bigquery.SchemaField("stoch_d", "FLOAT64"),
    bigquery.SchemaField("mfi", "FLOAT64"),
    bigquery.SchemaField("williams_r", "FLOAT64"),
    bigquery.SchemaField("momentum", "FLOAT64"),
    bigquery.SchemaField("roc", "FLOAT64"),
    # Trend Indicators
    bigquery.SchemaField("sma_20", "FLOAT64"),
    bigquery.SchemaField("sma_50", "FLOAT64"),
    bigquery.SchemaField("sma_200", "FLOAT64"),
    bigquery.SchemaField("ema_12", "FLOAT64"),
    bigquery.SchemaField("ema_26", "FLOAT64"),
    bigquery.SchemaField("ema_50", "FLOAT64"),
    bigquery.SchemaField("ema_200", "FLOAT64"),
    # Volatility
    bigquery.SchemaField("atr", "FLOAT64"),
    bigquery.SchemaField("bollinger_upper", "FLOAT64"),
    bigquery.SchemaField("bollinger_middle", "FLOAT64"),
    bigquery.SchemaField("bollinger_lower", "FLOAT64"),
    # Trend Strength
    bigquery.SchemaField("adx", "FLOAT64"),
    bigquery.SchemaField("cci", "FLOAT64"),
    # Volume
    bigquery.SchemaField("obv", "FLOAT64"),
    # Computed Signals (per masterquery)
    bigquery.SchemaField("growth_score", "INT64"),
    bigquery.SchemaField("trend_regime", "STRING"),
    bigquery.SchemaField("in_rise_cycle", "BOOL"),
]

# Earnings table schema
EARNINGS_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("time", "STRING"),
    bigquery.SchemaField("eps_estimate", "FLOAT64"),
    bigquery.SchemaField("eps_actual", "FLOAT64"),
    bigquery.SchemaField("difference", "FLOAT64"),
    bigquery.SchemaField("surprise_pct", "FLOAT64"),
]

# Dividends table schema
DIVIDENDS_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ex_date", "DATE"),
    bigquery.SchemaField("payment_date", "DATE"),
    bigquery.SchemaField("record_date", "DATE"),
    bigquery.SchemaField("declaration_date", "DATE"),
    bigquery.SchemaField("amount", "FLOAT64"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("frequency", "STRING"),
]

# Statistics table schema
STATISTICS_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("market_cap", "FLOAT64"),
    bigquery.SchemaField("pe_ratio", "FLOAT64"),
    bigquery.SchemaField("forward_pe", "FLOAT64"),
    bigquery.SchemaField("peg_ratio", "FLOAT64"),
    bigquery.SchemaField("price_to_book", "FLOAT64"),
    bigquery.SchemaField("price_to_sales", "FLOAT64"),
    bigquery.SchemaField("enterprise_value", "FLOAT64"),
    bigquery.SchemaField("ev_to_revenue", "FLOAT64"),
    bigquery.SchemaField("ev_to_ebitda", "FLOAT64"),
    bigquery.SchemaField("profit_margin", "FLOAT64"),
    bigquery.SchemaField("operating_margin", "FLOAT64"),
    bigquery.SchemaField("return_on_assets", "FLOAT64"),
    bigquery.SchemaField("return_on_equity", "FLOAT64"),
    bigquery.SchemaField("revenue", "FLOAT64"),
    bigquery.SchemaField("revenue_per_share", "FLOAT64"),
    bigquery.SchemaField("quarterly_revenue_growth", "FLOAT64"),
    bigquery.SchemaField("gross_profit", "FLOAT64"),
    bigquery.SchemaField("ebitda", "FLOAT64"),
    bigquery.SchemaField("net_income", "FLOAT64"),
    bigquery.SchemaField("eps", "FLOAT64"),
    bigquery.SchemaField("quarterly_earnings_growth", "FLOAT64"),
    bigquery.SchemaField("total_cash", "FLOAT64"),
    bigquery.SchemaField("total_debt", "FLOAT64"),
    bigquery.SchemaField("debt_to_equity", "FLOAT64"),
    bigquery.SchemaField("current_ratio", "FLOAT64"),
    bigquery.SchemaField("book_value", "FLOAT64"),
    bigquery.SchemaField("dividend_yield", "FLOAT64"),
    bigquery.SchemaField("payout_ratio", "FLOAT64"),
    bigquery.SchemaField("beta", "FLOAT64"),
    bigquery.SchemaField("52_week_high", "FLOAT64"),
    bigquery.SchemaField("52_week_low", "FLOAT64"),
    bigquery.SchemaField("50_day_ma", "FLOAT64"),
    bigquery.SchemaField("200_day_ma", "FLOAT64"),
    bigquery.SchemaField("shares_outstanding", "FLOAT64"),
    bigquery.SchemaField("float_shares", "FLOAT64"),
    bigquery.SchemaField("short_ratio", "FLOAT64"),
    bigquery.SchemaField("short_percent", "FLOAT64"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
]

# Profile table schema
PROFILE_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("exchange", "STRING"),
    bigquery.SchemaField("sector", "STRING"),
    bigquery.SchemaField("industry", "STRING"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("ceo", "STRING"),
    bigquery.SchemaField("employees", "INT64"),
    bigquery.SchemaField("headquarters", "STRING"),
    bigquery.SchemaField("founded", "STRING"),
    bigquery.SchemaField("website", "STRING"),
    bigquery.SchemaField("phone", "STRING"),
]

# Splits table schema
SPLITS_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("from_factor", "INT64"),
    bigquery.SchemaField("to_factor", "INT64"),
]

TABLES_TO_CREATE = [
    ("stocks_daily_comprehensive", COMPREHENSIVE_DAILY_SCHEMA),
    ("etfs_daily_comprehensive", COMPREHENSIVE_DAILY_SCHEMA),
    ("fundamentals_earnings", EARNINGS_SCHEMA),
    ("fundamentals_dividends", DIVIDENDS_SCHEMA),
    ("fundamentals_statistics", STATISTICS_SCHEMA),
    ("fundamentals_profile", PROFILE_SCHEMA),
    ("fundamentals_splits", SPLITS_SCHEMA),
]


def create_tables():
    print(f"Creating comprehensive tables in {PROJECT_ID}.{DATASET_ID}")
    print("=" * 60)

    for table_name, schema in TABLES_TO_CREATE:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        try:
            # Check if exists
            client.get_table(table_id)
            print(f"[EXISTS] {table_name}")
        except Exception:
            # Create table
            table = bigquery.Table(table_id, schema=schema)
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="datetime" if "datetime" in [f.name for f in schema] else None
            )
            client.create_table(table)
            print(f"[CREATED] {table_name} ({len(schema)} columns)")

    print("\n" + "=" * 60)
    print("All tables ready!")


if __name__ == "__main__":
    create_tables()
