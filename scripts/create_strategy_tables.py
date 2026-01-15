"""
Create BigQuery tables for Trading Strategies Framework
- trading_strategies: Strategy definitions
- strategy_signals: Buy/sell signals detected
- paper_trades: Simulated trades
- strategy_backtests: Backtest results
- strategy_daily_summary: Daily performance
"""
import sys
import io
from datetime import datetime
from google.cloud import bigquery
import json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

client = bigquery.Client(project=PROJECT_ID)

def create_table(table_id, schema, partition_field=None, cluster_fields=None):
    """Create a BigQuery table with optional partitioning and clustering"""
    full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_id}"

    table = bigquery.Table(full_table_id, schema=schema)

    if partition_field:
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field
        )

    if cluster_fields:
        table.clustering_fields = cluster_fields

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"  Created: {table_id}")
        return True
    except Exception as e:
        print(f"  Error creating {table_id}: {e}")
        return False


print("=" * 60)
print("CREATING TRADING STRATEGY TABLES")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Started: {datetime.now()}")
print("=" * 60)

# 1. Trading Strategies Table
print("\n1. Creating trading_strategies table...")
schema = [
    bigquery.SchemaField("strategy_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("strategy_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("strategy_code", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("strategy_type", "STRING"),  # intraday, swing, position
    bigquery.SchemaField("asset_types", "STRING", mode="REPEATED"),
    bigquery.SchemaField("timeframes", "STRING", mode="REPEATED"),
    bigquery.SchemaField("parameters", "JSON"),
    bigquery.SchemaField("entry_rules", "JSON"),
    bigquery.SchemaField("exit_rules", "JSON"),
    bigquery.SchemaField("data_sources", "STRING", mode="REPEATED"),  # warehouse, live, both
    bigquery.SchemaField("is_active", "BOOL"),
    bigquery.SchemaField("is_paper_trading", "BOOL"),
    bigquery.SchemaField("is_live_trading", "BOOL"),
    bigquery.SchemaField("created_by", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
]
create_table("trading_strategies", schema)

# 2. Strategy Signals Table
print("\n2. Creating strategy_signals table...")
schema = [
    bigquery.SchemaField("signal_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("strategy_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("asset_type", "STRING"),
    bigquery.SchemaField("signal_type", "STRING", mode="REQUIRED"),  # BUY, SELL, HOLD
    bigquery.SchemaField("signal_strength", "FLOAT64"),
    bigquery.SchemaField("confidence_score", "FLOAT64"),
    bigquery.SchemaField("signal_price", "FLOAT64"),
    bigquery.SchemaField("signal_datetime", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("rsi", "FLOAT64"),
    bigquery.SchemaField("macd", "FLOAT64"),
    bigquery.SchemaField("volume", "INT64"),
    bigquery.SchemaField("volume_ratio", "FLOAT64"),
    bigquery.SchemaField("sma_5", "FLOAT64"),
    bigquery.SchemaField("sma_20", "FLOAT64"),
    bigquery.SchemaField("cycle_number", "INT64"),
    bigquery.SchemaField("cycle_type", "STRING"),
    bigquery.SchemaField("sector", "STRING"),
    bigquery.SchemaField("sector_rank", "INT64"),
    bigquery.SchemaField("stock_sector_rank", "INT64"),
    bigquery.SchemaField("ai_reasoning", "STRING"),
    bigquery.SchemaField("is_executed", "BOOL"),
    bigquery.SchemaField("execution_type", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]
create_table("strategy_signals", schema,
             partition_field="signal_datetime",
             cluster_fields=["strategy_id", "symbol"])

# 3. Paper Trades Table
print("\n3. Creating paper_trades table...")
schema = [
    bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("strategy_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("signal_id", "STRING"),
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("asset_type", "STRING"),
    bigquery.SchemaField("trade_type", "STRING", mode="REQUIRED"),  # BUY, SELL
    bigquery.SchemaField("quantity", "FLOAT64"),
    bigquery.SchemaField("entry_price", "FLOAT64"),
    bigquery.SchemaField("exit_price", "FLOAT64"),
    bigquery.SchemaField("entry_datetime", "TIMESTAMP"),
    bigquery.SchemaField("exit_datetime", "TIMESTAMP"),
    bigquery.SchemaField("hold_duration_minutes", "INT64"),
    bigquery.SchemaField("position_size", "FLOAT64"),
    bigquery.SchemaField("gross_pnl", "FLOAT64"),
    bigquery.SchemaField("commission", "FLOAT64"),
    bigquery.SchemaField("net_pnl", "FLOAT64"),
    bigquery.SchemaField("pnl_percent", "FLOAT64"),
    bigquery.SchemaField("cycle_number", "INT64"),
    bigquery.SchemaField("cycle_gain_pct", "FLOAT64"),
    bigquery.SchemaField("status", "STRING"),  # open, closed, stopped_out, take_profit
    bigquery.SchemaField("exit_reason", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]
create_table("paper_trades", schema,
             partition_field="entry_datetime",
             cluster_fields=["strategy_id", "symbol"])

# 4. Strategy Backtests Table
print("\n4. Creating strategy_backtests table...")
schema = [
    bigquery.SchemaField("backtest_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("strategy_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("start_date", "DATE"),
    bigquery.SchemaField("end_date", "DATE"),
    bigquery.SchemaField("symbols_tested", "STRING", mode="REPEATED"),
    bigquery.SchemaField("parameters", "JSON"),
    bigquery.SchemaField("total_trades", "INT64"),
    bigquery.SchemaField("winning_trades", "INT64"),
    bigquery.SchemaField("losing_trades", "INT64"),
    bigquery.SchemaField("win_rate", "FLOAT64"),
    bigquery.SchemaField("starting_capital", "FLOAT64"),
    bigquery.SchemaField("ending_capital", "FLOAT64"),
    bigquery.SchemaField("total_return_pct", "FLOAT64"),
    bigquery.SchemaField("max_drawdown_pct", "FLOAT64"),
    bigquery.SchemaField("sharpe_ratio", "FLOAT64"),
    bigquery.SchemaField("avg_win_pct", "FLOAT64"),
    bigquery.SchemaField("avg_loss_pct", "FLOAT64"),
    bigquery.SchemaField("largest_win", "FLOAT64"),
    bigquery.SchemaField("largest_loss", "FLOAT64"),
    bigquery.SchemaField("avg_hold_time_minutes", "FLOAT64"),
    bigquery.SchemaField("profit_factor", "FLOAT64"),
    bigquery.SchemaField("recovery_factor", "FLOAT64"),
    bigquery.SchemaField("ai_summary", "STRING"),
    bigquery.SchemaField("ai_recommendations", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]
create_table("strategy_backtests", schema)

# 5. Strategy Daily Summary Table
print("\n5. Creating strategy_daily_summary table...")
schema = [
    bigquery.SchemaField("summary_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("strategy_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("trade_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("trades_count", "INT64"),
    bigquery.SchemaField("cycles_detected", "INT64"),
    bigquery.SchemaField("winning_cycles", "INT64"),
    bigquery.SchemaField("gross_pnl", "FLOAT64"),
    bigquery.SchemaField("net_pnl", "FLOAT64"),
    bigquery.SchemaField("best_trade_pnl", "FLOAT64"),
    bigquery.SchemaField("worst_trade_pnl", "FLOAT64"),
    bigquery.SchemaField("symbols_traded", "STRING", mode="REPEATED"),
    bigquery.SchemaField("top_performer", "STRING"),
    bigquery.SchemaField("top_performer_pnl", "FLOAT64"),
    bigquery.SchemaField("market_condition", "STRING"),
    bigquery.SchemaField("vix_level", "FLOAT64"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]
create_table("strategy_daily_summary", schema,
             partition_field="trade_date",
             cluster_fields=["strategy_id"])

# 6. Sector Momentum Rankings Table
print("\n6. Creating sector_momentum_rankings table...")
schema = [
    bigquery.SchemaField("ranking_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ranking_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("timeframe", "STRING"),  # weekly, daily
    bigquery.SchemaField("sector", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("stock_count", "INT64"),
    bigquery.SchemaField("avg_change_pct", "FLOAT64"),
    bigquery.SchemaField("total_volume", "INT64"),
    bigquery.SchemaField("momentum_rank", "INT64"),
    bigquery.SchemaField("previous_rank", "INT64"),
    bigquery.SchemaField("rank_change", "INT64"),
    bigquery.SchemaField("top_5_stocks", "JSON"),  # [{symbol, change_pct, volume}]
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]
create_table("sector_momentum_rankings", schema,
             partition_field="ranking_date",
             cluster_fields=["sector"])

# 7. Rise Cycles Table (detailed cycle data)
print("\n7. Creating rise_cycles table...")
schema = [
    bigquery.SchemaField("cycle_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("trade_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("cycle_number", "INT64"),
    bigquery.SchemaField("entry_datetime", "TIMESTAMP"),
    bigquery.SchemaField("entry_price", "FLOAT64"),
    bigquery.SchemaField("entry_rsi", "FLOAT64"),
    bigquery.SchemaField("entry_volume", "INT64"),
    bigquery.SchemaField("exit_datetime", "TIMESTAMP"),
    bigquery.SchemaField("exit_price", "FLOAT64"),
    bigquery.SchemaField("exit_rsi", "FLOAT64"),
    bigquery.SchemaField("exit_reason", "STRING"),  # decline, stop_loss, take_profit, eod
    bigquery.SchemaField("duration_minutes", "INT64"),
    bigquery.SchemaField("gain_pct", "FLOAT64"),
    bigquery.SchemaField("peak_price", "FLOAT64"),
    bigquery.SchemaField("peak_gain_pct", "FLOAT64"),
    bigquery.SchemaField("drawdown_from_peak", "FLOAT64"),
    bigquery.SchemaField("volume_during_cycle", "INT64"),
    bigquery.SchemaField("bars_in_cycle", "INT64"),
    bigquery.SchemaField("timeframe", "STRING"),  # 1min, 5min, hourly
    bigquery.SchemaField("sector", "STRING"),
    bigquery.SchemaField("industry", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]
create_table("rise_cycles", schema,
             partition_field="trade_date",
             cluster_fields=["symbol"])

print("\n" + "=" * 60)
print("INSERTING DEFAULT STRATEGIES")
print("=" * 60)

# Insert Rise Cycle Detection Strategy
rcd_strategy = {
    "strategy_id": "RCD-001",
    "strategy_name": "Rise Cycle Detection",
    "strategy_code": "RCD",
    "description": "Identify and trade intraday rise cycles. Buy at cycle start, sell at decline detection.",
    "strategy_type": "intraday",
    "asset_types": ["stocks", "crypto", "etfs"],
    "timeframes": ["1min", "5min", "hourly"],
    "parameters": json.dumps({
        "ma_period": 5,
        "confirm_bars": 3,
        "exit_bars": 2,
        "stop_loss_pct": 2.0,
        "take_profit_pct": 5.0,
        "min_volume_ratio": 1.0,
        "rsi_threshold": 50
    }),
    "entry_rules": json.dumps({
        "conditions": [
            "price > sma_5",
            "rsi > 50",
            "volume_ratio > 1.0",
            "3 consecutive higher closes"
        ]
    }),
    "exit_rules": json.dumps({
        "conditions": [
            "price < sma_5",
            "2 consecutive lower closes",
            "stop_loss: -2%",
            "take_profit: +5%"
        ]
    }),
    "data_sources": ["warehouse", "live"],
    "is_active": True,
    "is_paper_trading": True,
    "is_live_trading": False,
    "created_by": "system"
}

# Insert Sector Momentum Strategy
smr_strategy = {
    "strategy_id": "SMR-001",
    "strategy_name": "Sector Momentum Rotation",
    "strategy_code": "SMR",
    "description": "Identify hottest sectors weekly, then top movers within those sectors.",
    "strategy_type": "swing",
    "asset_types": ["stocks", "etfs"],
    "timeframes": ["weekly", "daily"],
    "parameters": json.dumps({
        "top_sectors": 3,
        "stocks_per_sector": 10,
        "min_rsi": 50,
        "max_rsi": 70,
        "min_volume_ratio": 1.5,
        "stop_loss_pct": 5.0,
        "take_profit_pct": 15.0
    }),
    "entry_rules": json.dumps({
        "conditions": [
            "sector in top 3 momentum",
            "stock in top 10 of sector",
            "rsi between 50-70",
            "volume > 1.5x average"
        ]
    }),
    "exit_rules": json.dumps({
        "conditions": [
            "sector drops out of top 5",
            "stock drops out of sector top 20",
            "rsi > 80",
            "stop_loss: -5%"
        ]
    }),
    "data_sources": ["warehouse"],
    "is_active": True,
    "is_paper_trading": True,
    "is_live_trading": False,
    "created_by": "system"
}

# Insert Multi-Timeframe Strategy
mtc_strategy = {
    "strategy_id": "MTC-001",
    "strategy_name": "Multi-Timeframe Confirmation",
    "strategy_code": "MTC",
    "description": "Align weekly, daily, and hourly trends for high-probability entries.",
    "strategy_type": "swing",
    "asset_types": ["stocks", "crypto", "etfs", "forex"],
    "timeframes": ["weekly", "daily", "hourly"],
    "parameters": json.dumps({
        "weekly_sma": 50,
        "daily_sma": 20,
        "hourly_sma": 20,
        "min_adx": 25,
        "rsi_oversold": 30,
        "min_confluence_score": 3,
        "stop_loss_pct": 3.0
    }),
    "entry_rules": json.dumps({
        "conditions": [
            "weekly: price > SMA50, RSI > 50, MACD > signal",
            "daily: price > SMA20, RSI > 50, ADX > 25",
            "hourly: RSI crosses above 30 OR price crosses SMA20",
            "confluence score >= 3"
        ]
    }),
    "exit_rules": json.dumps({
        "conditions": [
            "weekly trend reverses",
            "daily RSI > 80",
            "stop_loss: -3%"
        ]
    }),
    "data_sources": ["warehouse", "live"],
    "is_active": True,
    "is_paper_trading": True,
    "is_live_trading": False,
    "created_by": "system"
}

# Insert strategies into table
from datetime import datetime

strategies = [rcd_strategy, smr_strategy, mtc_strategy]
table_id = f"{PROJECT_ID}.{DATASET_ID}.trading_strategies"

for strat in strategies:
    strat["created_at"] = datetime.utcnow().isoformat()
    strat["updated_at"] = datetime.utcnow().isoformat()

try:
    errors = client.insert_rows_json(table_id, strategies)
    if errors:
        print(f"  Errors inserting strategies: {errors}")
    else:
        print(f"  Inserted {len(strategies)} default strategies:")
        for s in strategies:
            print(f"    - {s['strategy_code']}: {s['strategy_name']}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("ALL TABLES CREATED SUCCESSFULLY")
print("=" * 60)
print("""
Tables created:
  1. trading_strategies     - Strategy definitions with parameters
  2. strategy_signals       - Buy/sell signals (partitioned by date)
  3. paper_trades           - Simulated trade records
  4. strategy_backtests     - Backtest results and metrics
  5. strategy_daily_summary - Daily performance summaries
  6. sector_momentum_rankings - Weekly sector rankings
  7. rise_cycles            - Detailed cycle data for Rise Cycle strategy

Default strategies inserted:
  - RCD-001: Rise Cycle Detection (intraday)
  - SMR-001: Sector Momentum Rotation (swing)
  - MTC-001: Multi-Timeframe Confirmation (swing)

Data Sources:
  - warehouse: Historical data from BigQuery (weekly, daily, hourly tables)
  - live: Near real-time data from TwelveData API (5min, 1min intervals)
""")
