"""
Paper Trading System Setup
Creates BigQuery tables and initializes paper trading infrastructure
"""
from google.cloud import bigquery
from datetime import datetime
import uuid

client = bigquery.Client(project='aialgotradehits')

print("=" * 60)
print("PAPER TRADING SYSTEM SETUP")
print("=" * 60)
print(f"Started: {datetime.now()}")
print()

# Step 1: Create paper trading tables
print("Step 1: Creating paper trading tables...")

# Portfolios table
portfolios_query = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.paper_portfolios` (
    portfolio_id STRING NOT NULL,
    name STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    initial_capital FLOAT64 DEFAULT 100000,
    current_cash FLOAT64,
    current_value FLOAT64,
    total_pnl FLOAT64 DEFAULT 0,
    total_pnl_pct FLOAT64 DEFAULT 0,
    total_trades INT64 DEFAULT 0,
    winning_trades INT64 DEFAULT 0,
    losing_trades INT64 DEFAULT 0,
    win_rate FLOAT64 DEFAULT 0,
    strategy STRING,
    is_active BOOL DEFAULT TRUE,
    last_updated TIMESTAMP
)
"""
try:
    client.query(portfolios_query).result()
    print("  - paper_portfolios table created")
except Exception as e:
    print(f"  - paper_portfolios: {e}")

# Positions table
positions_query = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.paper_positions` (
    position_id STRING NOT NULL,
    portfolio_id STRING NOT NULL,
    symbol STRING NOT NULL,
    side STRING,  -- LONG or SHORT
    quantity FLOAT64,
    entry_price FLOAT64,
    entry_date TIMESTAMP,
    current_price FLOAT64,
    unrealized_pnl FLOAT64,
    unrealized_pnl_pct FLOAT64,
    stop_loss FLOAT64,
    take_profit FLOAT64,
    ml_signal STRING,
    ml_confidence FLOAT64,
    is_open BOOL DEFAULT TRUE,
    last_updated TIMESTAMP
)
"""
try:
    client.query(positions_query).result()
    print("  - paper_positions table created")
except Exception as e:
    print(f"  - paper_positions: {e}")

# Trades table
trades_query = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.paper_trades` (
    trade_id STRING NOT NULL,
    portfolio_id STRING NOT NULL,
    position_id STRING,
    symbol STRING NOT NULL,
    side STRING,  -- BUY or SELL
    action STRING,  -- OPEN or CLOSE
    quantity FLOAT64,
    price FLOAT64,
    value FLOAT64,
    commission FLOAT64 DEFAULT 0,
    trade_date TIMESTAMP,
    ml_signal STRING,
    ml_confidence FLOAT64,
    ml_predicted_direction STRING,
    actual_direction STRING,
    was_correct BOOL,
    pnl FLOAT64,
    pnl_pct FLOAT64,
    notes STRING
)
"""
try:
    client.query(trades_query).result()
    print("  - paper_trades table created")
except Exception as e:
    print(f"  - paper_trades: {e}")

# Daily performance table
performance_query = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.paper_daily_performance` (
    portfolio_id STRING NOT NULL,
    date DATE NOT NULL,
    starting_value FLOAT64,
    ending_value FLOAT64,
    daily_pnl FLOAT64,
    daily_pnl_pct FLOAT64,
    cumulative_pnl FLOAT64,
    cumulative_pnl_pct FLOAT64,
    open_positions INT64,
    trades_executed INT64,
    winning_trades INT64,
    losing_trades INT64,
    max_drawdown FLOAT64,
    sharpe_ratio FLOAT64
)
"""
try:
    client.query(performance_query).result()
    print("  - paper_daily_performance table created")
except Exception as e:
    print(f"  - paper_daily_performance: {e}")

# Step 2: Create default portfolio
print("\nStep 2: Creating default ML trading portfolio...")

portfolio_id = str(uuid.uuid4())[:8]
insert_portfolio = f"""
INSERT INTO `aialgotradehits.ml_models.paper_portfolios`
(portfolio_id, name, initial_capital, current_cash, current_value, strategy, last_updated)
VALUES
('{portfolio_id}', 'ML Signal Portfolio', 100000, 100000, 100000, 'ml_ensemble', CURRENT_TIMESTAMP())
"""
try:
    client.query(insert_portfolio).result()
    print(f"  Portfolio created: {portfolio_id}")
    print(f"  Initial capital: $100,000")
except Exception as e:
    print(f"  Portfolio creation: {e}")

# Step 3: Create paper trading view for signals
print("\nStep 3: Creating ML signal to trade view...")

signal_view_query = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_paper_trading_signals` AS
WITH latest_predictions AS (
    SELECT
        symbol,
        DATE(datetime) as signal_date,
        close as current_price,
        predicted_direction_target as predicted_direction,
        predicted_direction_target_probs[OFFSET(1)].prob as prob_up,
        predicted_direction_target_probs[OFFSET(0)].prob as prob_down,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
    FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.ensemble_daily_xgboost`,
        (SELECT symbol, datetime, close,
                rsi, macd, macd_histogram, mfi, cci, adx, momentum,
                price_sma50_ratio, price_sma200_ratio, daily_volatility
         FROM `aialgotradehits.ml_models.ensemble_daily_features`
         WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)))
)
SELECT
    symbol,
    signal_date,
    current_price,
    predicted_direction,
    prob_up,
    prob_down,
    CASE
        WHEN predicted_direction = 1 AND prob_up >= 0.65 THEN 'STRONG_BUY'
        WHEN predicted_direction = 1 AND prob_up >= 0.55 THEN 'BUY'
        WHEN predicted_direction = 0 AND prob_down >= 0.65 THEN 'STRONG_SELL'
        WHEN predicted_direction = 0 AND prob_down >= 0.55 THEN 'SELL'
        ELSE 'HOLD'
    END as trading_signal,
    GREATEST(prob_up, prob_down) as confidence,
    CASE
        WHEN GREATEST(prob_up, prob_down) >= 0.65 THEN 'HIGH'
        WHEN GREATEST(prob_up, prob_down) >= 0.55 THEN 'MEDIUM'
        ELSE 'LOW'
    END as confidence_level
FROM latest_predictions
WHERE rn = 1
"""
try:
    client.query(signal_view_query).result()
    print("  Signal view created")
except Exception as e:
    print(f"  Signal view: {e}")

# Step 4: Create trade execution procedure
print("\nStep 4: Creating trade execution function...")

# Get current signals for paper trading
print("\nStep 5: Current ML Trading Signals...")

signals_query = """
SELECT *
FROM `aialgotradehits.ml_models.v_paper_trading_signals`
WHERE trading_signal IN ('STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL')
ORDER BY confidence DESC
LIMIT 20
"""
try:
    result = client.query(signals_query).result()
    signals = list(result)
    print(f"\n  Found {len(signals)} actionable signals:")
    for s in signals:
        print(f"    {s.symbol}: {s.trading_signal} @ ${s.current_price:.2f} ({s.confidence*100:.1f}% conf)")
except Exception as e:
    print(f"  Signals query error: {e}")

# Step 6: Execute sample trades based on signals
print("\nStep 6: Executing sample paper trades...")

# Get the portfolio ID we just created
portfolio_query = """
SELECT portfolio_id, current_cash
FROM `aialgotradehits.ml_models.paper_portfolios`
WHERE is_active = TRUE
ORDER BY created_at DESC
LIMIT 1
"""
try:
    portfolio = list(client.query(portfolio_query).result())[0]
    active_portfolio_id = portfolio.portfolio_id
    current_cash = portfolio.current_cash
    print(f"  Using portfolio: {active_portfolio_id}")
    print(f"  Available cash: ${current_cash:,.2f}")

    # Execute trades for top signals
    position_size = 10000  # $10,000 per position

    for signal in signals[:5]:  # Top 5 signals
        if signal.trading_signal in ('STRONG_BUY', 'BUY'):
            side = 'LONG'
            action = 'BUY'
        else:
            side = 'SHORT'
            action = 'SELL'

        quantity = round(position_size / signal.current_price, 2)
        trade_id = str(uuid.uuid4())[:8]
        position_id = str(uuid.uuid4())[:8]

        # Insert trade
        trade_insert = f"""
        INSERT INTO `aialgotradehits.ml_models.paper_trades`
        (trade_id, portfolio_id, position_id, symbol, side, action, quantity, price, value,
         trade_date, ml_signal, ml_confidence, ml_predicted_direction)
        VALUES
        ('{trade_id}', '{active_portfolio_id}', '{position_id}', '{signal.symbol}',
         '{action}', 'OPEN', {quantity}, {signal.current_price}, {quantity * signal.current_price},
         CURRENT_TIMESTAMP(), '{signal.trading_signal}', {signal.confidence},
         '{"UP" if signal.predicted_direction == 1 else "DOWN"}')
        """
        client.query(trade_insert).result()

        # Insert position
        position_insert = f"""
        INSERT INTO `aialgotradehits.ml_models.paper_positions`
        (position_id, portfolio_id, symbol, side, quantity, entry_price, entry_date,
         current_price, unrealized_pnl, ml_signal, ml_confidence, is_open, last_updated)
        VALUES
        ('{position_id}', '{active_portfolio_id}', '{signal.symbol}', '{side}',
         {quantity}, {signal.current_price}, CURRENT_TIMESTAMP(),
         {signal.current_price}, 0, '{signal.trading_signal}', {signal.confidence},
         TRUE, CURRENT_TIMESTAMP())
        """
        client.query(position_insert).result()

        print(f"    {action} {quantity} {signal.symbol} @ ${signal.current_price:.2f} = ${quantity * signal.current_price:,.2f}")

except Exception as e:
    print(f"  Trade execution error: {e}")

# Step 7: Update portfolio summary
print("\nStep 7: Updating portfolio summary...")

update_portfolio = f"""
UPDATE `aialgotradehits.ml_models.paper_portfolios`
SET
    current_cash = initial_capital - (
        SELECT COALESCE(SUM(value), 0)
        FROM `aialgotradehits.ml_models.paper_trades`
        WHERE portfolio_id = '{active_portfolio_id}' AND action = 'OPEN'
    ),
    total_trades = (
        SELECT COUNT(*)
        FROM `aialgotradehits.ml_models.paper_trades`
        WHERE portfolio_id = '{active_portfolio_id}'
    ),
    last_updated = CURRENT_TIMESTAMP()
WHERE portfolio_id = '{active_portfolio_id}'
"""
try:
    client.query(update_portfolio).result()
    print("  Portfolio updated")
except Exception as e:
    print(f"  Portfolio update error: {e}")

# Final summary
print("\n" + "=" * 60)
print("PAPER TRADING SETUP COMPLETE")
print("=" * 60)

summary_query = f"""
SELECT
    p.portfolio_id,
    p.name,
    p.initial_capital,
    p.current_cash,
    COUNT(DISTINCT pos.position_id) as open_positions,
    COALESCE(SUM(t.value), 0) as total_invested
FROM `aialgotradehits.ml_models.paper_portfolios` p
LEFT JOIN `aialgotradehits.ml_models.paper_positions` pos ON p.portfolio_id = pos.portfolio_id AND pos.is_open = TRUE
LEFT JOIN `aialgotradehits.ml_models.paper_trades` t ON p.portfolio_id = t.portfolio_id AND t.action = 'OPEN'
WHERE p.portfolio_id = '{active_portfolio_id}'
GROUP BY p.portfolio_id, p.name, p.initial_capital, p.current_cash
"""
try:
    summary = list(client.query(summary_query).result())[0]
    print(f"\nPortfolio: {summary.name}")
    print(f"  Portfolio ID: {summary.portfolio_id}")
    print(f"  Initial Capital: ${summary.initial_capital:,.2f}")
    print(f"  Cash Available: ${summary.current_cash:,.2f}")
    print(f"  Total Invested: ${summary.total_invested:,.2f}")
    print(f"  Open Positions: {summary.open_positions}")
except Exception as e:
    print(f"Summary error: {e}")

print(f"\nCompleted: {datetime.now()}")
