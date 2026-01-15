# Trading Strategies Framework
## AIAlgoTradeHits - Automated Strategy Engine

**Created: December 5, 2025**

---

## Executive Summary

This framework provides a systematic approach to:
1. **Define** trading strategies with configurable parameters
2. **Detect** signals using real-time and historical data
3. **Backtest** strategies against historical data
4. **Paper Trade** simulations without real money
5. **Analyze** performance with AI (Claude/Gemini)

---

## Part 1: Registered Strategies

### Strategy 1: Rise Cycle Detection (RCD)

**Concept**: Identify intraday rise cycles and trade them automatically.

```
RISE CYCLE DETECTION ALGORITHM
==============================

1. DETECTION PHASE:
   - Monitor price movement in 1-min or 5-min intervals
   - Identify "rise start" when:
     * Price crosses above short-term MA (5-period)
     * Volume increases above average
     * RSI starts moving up from < 50

2. ENTRY SIGNAL:
   - BUY when rise cycle confirmed (3 consecutive higher closes)
   - Record entry price, time, volume

3. EXIT SIGNAL:
   - SELL when decline detected:
     * Price drops below 5-period MA
     * OR 2 consecutive lower closes
     * OR RSI crosses below 70 (overbought exit)
     * OR stop-loss triggered (configurable %)

4. CYCLE METRICS:
   - Cycle duration (minutes)
   - Gain % = (exit_price - entry_price) / entry_price * 100
   - Volume during cycle
   - Number of cycles per day
```

**Parameters**:
| Parameter | Default | Description |
|-----------|---------|-------------|
| `ma_period` | 5 | Moving average period for trend |
| `confirm_bars` | 3 | Bars to confirm rise cycle |
| `exit_bars` | 2 | Consecutive down bars to exit |
| `stop_loss_pct` | 2.0 | Stop loss percentage |
| `take_profit_pct` | 5.0 | Optional take profit |
| `timeframe` | 5min | Data timeframe |

---

### Strategy 2: Sector Momentum Rotation (SMR)

**Concept**: Find the hottest sector, then the top movers within it.

```
SECTOR MOMENTUM ALGORITHM
=========================

1. WEEKLY SECTOR RANKING:
   - Calculate average weekly change % for each sector
   - Rank sectors by momentum (1 = highest)
   - Identify top 3 momentum sectors

2. STOCK SELECTION:
   - Within top sectors, rank stocks by:
     * Weekly price change %
     * Volume increase vs 20-day average
     * RSI momentum (rising RSI)

3. ENTRY CRITERIA:
   - Stock in top 3 momentum sector
   - Stock in top 10 within that sector
   - RSI between 50-70 (strong but not overbought)
   - Volume > 1.5x average

4. EXIT CRITERIA:
   - Sector drops out of top 5
   - Stock drops out of sector top 20
   - RSI > 80 (take profit)
   - Stop loss: 5%
```

---

### Strategy 3: Multi-Timeframe Confirmation (MTC)

**Concept**: Align weekly, daily, and hourly trends for high-probability entries.

```
MULTI-TIMEFRAME ALGORITHM
=========================

1. WEEKLY TREND:
   - Bullish if: Price > SMA50, RSI > 50, MACD > Signal

2. DAILY TREND:
   - Bullish if: Price > SMA20, RSI > 50, ADX > 25

3. HOURLY TRIGGER:
   - Entry when hourly RSI crosses above 30 (oversold bounce)
   - OR price crosses above hourly SMA20

4. CONFLUENCE SCORE:
   - Weekly bullish: +1
   - Daily bullish: +1
   - Hourly trigger: +1
   - Volume confirmation: +1
   - ENTER when score >= 3
```

---

## Part 2: Database Schema

### 2.1 Strategy Definitions Table

```sql
CREATE TABLE `cryptobot-462709.crypto_trading_data.trading_strategies` (
    strategy_id STRING NOT NULL,
    strategy_name STRING NOT NULL,
    strategy_code STRING NOT NULL,  -- 'RCD', 'SMR', 'MTC', etc.
    description STRING,

    -- Strategy Type
    strategy_type STRING,  -- 'intraday', 'swing', 'position'
    asset_types ARRAY<STRING>,  -- ['stocks', 'crypto', 'etfs']
    timeframes ARRAY<STRING>,  -- ['5min', 'hourly', 'daily']

    -- Parameters (JSON)
    parameters JSON,  -- {"ma_period": 5, "stop_loss_pct": 2.0, ...}

    -- Entry/Exit Rules (JSON)
    entry_rules JSON,
    exit_rules JSON,

    -- Status
    is_active BOOL DEFAULT TRUE,
    is_paper_trading BOOL DEFAULT TRUE,
    is_live_trading BOOL DEFAULT FALSE,

    -- Metadata
    created_by STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### 2.2 Strategy Signals Table

```sql
CREATE TABLE `cryptobot-462709.crypto_trading_data.strategy_signals` (
    signal_id STRING NOT NULL,
    strategy_id STRING NOT NULL,

    -- Asset Info
    symbol STRING NOT NULL,
    asset_type STRING,  -- 'stock', 'crypto', etc.

    -- Signal Details
    signal_type STRING NOT NULL,  -- 'BUY', 'SELL', 'HOLD'
    signal_strength FLOAT64,  -- 0.0 to 1.0
    confidence_score FLOAT64,

    -- Price Data at Signal
    signal_price FLOAT64,
    signal_datetime TIMESTAMP NOT NULL,

    -- Indicators at Signal
    rsi FLOAT64,
    macd FLOAT64,
    volume INT64,
    volume_ratio FLOAT64,  -- vs average

    -- Cycle Info (for Rise Cycle strategy)
    cycle_number INT64,
    cycle_type STRING,  -- 'rise_start', 'rise_end', 'decline_start'

    -- Sector Info (for Sector Momentum strategy)
    sector STRING,
    sector_rank INT64,
    stock_sector_rank INT64,

    -- AI Analysis
    ai_reasoning STRING,

    -- Execution Status
    is_executed BOOL DEFAULT FALSE,
    execution_type STRING,  -- 'paper', 'live'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(signal_datetime)
CLUSTER BY strategy_id, symbol;
```

### 2.3 Paper Trades Table

```sql
CREATE TABLE `cryptobot-462709.crypto_trading_data.paper_trades` (
    trade_id STRING NOT NULL,
    strategy_id STRING NOT NULL,
    signal_id STRING,  -- Reference to signal that triggered

    -- Asset
    symbol STRING NOT NULL,
    asset_type STRING,

    -- Trade Details
    trade_type STRING NOT NULL,  -- 'BUY', 'SELL'
    quantity FLOAT64,
    entry_price FLOAT64,
    exit_price FLOAT64,

    -- Timing
    entry_datetime TIMESTAMP,
    exit_datetime TIMESTAMP,
    hold_duration_minutes INT64,

    -- Financials
    position_size FLOAT64,  -- Dollar amount
    gross_pnl FLOAT64,
    commission FLOAT64 DEFAULT 0,
    net_pnl FLOAT64,
    pnl_percent FLOAT64,

    -- Cycle Metrics (Rise Cycle strategy)
    cycle_number INT64,
    cycle_gain_pct FLOAT64,

    -- Status
    status STRING,  -- 'open', 'closed', 'stopped_out', 'take_profit'
    exit_reason STRING,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(entry_datetime)
CLUSTER BY strategy_id, symbol;
```

### 2.4 Strategy Backtests Table

```sql
CREATE TABLE `cryptobot-462709.crypto_trading_data.strategy_backtests` (
    backtest_id STRING NOT NULL,
    strategy_id STRING NOT NULL,

    -- Backtest Period
    start_date DATE,
    end_date DATE,
    symbols_tested ARRAY<STRING>,

    -- Parameters Used
    parameters JSON,

    -- Results Summary
    total_trades INT64,
    winning_trades INT64,
    losing_trades INT64,
    win_rate FLOAT64,

    -- Financial Results
    starting_capital FLOAT64,
    ending_capital FLOAT64,
    total_return_pct FLOAT64,
    max_drawdown_pct FLOAT64,
    sharpe_ratio FLOAT64,

    -- Trade Stats
    avg_win_pct FLOAT64,
    avg_loss_pct FLOAT64,
    largest_win FLOAT64,
    largest_loss FLOAT64,
    avg_hold_time_minutes FLOAT64,

    -- Risk Metrics
    profit_factor FLOAT64,  -- gross profit / gross loss
    recovery_factor FLOAT64,

    -- AI Analysis
    ai_summary STRING,
    ai_recommendations STRING,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### 2.5 Daily Strategy Summary Table

```sql
CREATE TABLE `cryptobot-462709.crypto_trading_data.strategy_daily_summary` (
    summary_id STRING NOT NULL,
    strategy_id STRING NOT NULL,
    trade_date DATE NOT NULL,

    -- Daily Metrics
    trades_count INT64,
    cycles_detected INT64,
    winning_cycles INT64,

    -- PnL
    gross_pnl FLOAT64,
    net_pnl FLOAT64,
    best_trade_pnl FLOAT64,
    worst_trade_pnl FLOAT64,

    -- Symbols Traded
    symbols_traded ARRAY<STRING>,
    top_performer STRING,
    top_performer_pnl FLOAT64,

    -- Market Context
    market_condition STRING,  -- 'bullish', 'bearish', 'choppy'
    vix_level FLOAT64,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY trade_date
CLUSTER BY strategy_id;
```

---

## Part 3: Rise Cycle Detection Implementation

### 3.1 Algorithm Pseudocode

```python
def detect_rise_cycles(symbol, date, timeframe='5min'):
    """
    Detect all rise cycles for a symbol on a given date

    Returns: List of cycles with entry/exit points and gains
    """

    # Get intraday data
    data = get_intraday_data(symbol, date, timeframe)

    # Calculate indicators
    data['sma5'] = data['close'].rolling(5).mean()
    data['rsi'] = calculate_rsi(data['close'], 14)
    data['vol_avg'] = data['volume'].rolling(20).mean()
    data['vol_ratio'] = data['volume'] / data['vol_avg']

    cycles = []
    in_cycle = False
    cycle_start = None
    consecutive_up = 0
    consecutive_down = 0

    for i, row in data.iterrows():
        if not in_cycle:
            # Look for rise cycle start
            if (row['close'] > row['sma5'] and
                row['rsi'] > 50 and
                row['vol_ratio'] > 1.0):
                consecutive_up += 1
                if consecutive_up >= 3:  # Confirmed rise
                    in_cycle = True
                    cycle_start = {
                        'entry_time': row['datetime'],
                        'entry_price': row['close'],
                        'entry_rsi': row['rsi'],
                        'entry_volume': row['volume']
                    }
                    consecutive_up = 0
            else:
                consecutive_up = 0
        else:
            # In a cycle - look for exit
            if (row['close'] < row['sma5'] or
                row['close'] < cycle_start['entry_price'] * 0.98):  # 2% stop
                consecutive_down += 1
                if consecutive_down >= 2:  # Confirmed decline
                    cycle = {
                        **cycle_start,
                        'exit_time': row['datetime'],
                        'exit_price': row['close'],
                        'exit_rsi': row['rsi'],
                        'duration_minutes': (row['datetime'] - cycle_start['entry_time']).minutes,
                        'gain_pct': (row['close'] - cycle_start['entry_price']) / cycle_start['entry_price'] * 100
                    }
                    cycles.append(cycle)
                    in_cycle = False
                    consecutive_down = 0
            else:
                consecutive_down = 0

    return cycles


def calculate_daily_potential(symbol, date):
    """
    Calculate how much you would have made trading all rise cycles
    """
    cycles = detect_rise_cycles(symbol, date)

    starting_capital = 10000
    current_capital = starting_capital

    for cycle in cycles:
        trade_amount = current_capital  # All-in each cycle
        gain = trade_amount * (cycle['gain_pct'] / 100)
        current_capital += gain

    return {
        'symbol': symbol,
        'date': date,
        'cycles_count': len(cycles),
        'profitable_cycles': len([c for c in cycles if c['gain_pct'] > 0]),
        'starting_capital': starting_capital,
        'ending_capital': current_capital,
        'total_return_pct': (current_capital - starting_capital) / starting_capital * 100,
        'cycles': cycles
    }
```

### 3.2 Example Output

```json
{
  "symbol": "NVDA",
  "date": "2025-12-05",
  "cycles_count": 4,
  "profitable_cycles": 3,
  "starting_capital": 10000,
  "ending_capital": 10847.50,
  "total_return_pct": 8.475,
  "cycles": [
    {
      "cycle_number": 1,
      "entry_time": "09:35:00",
      "entry_price": 142.50,
      "exit_time": "10:15:00",
      "exit_price": 145.20,
      "duration_minutes": 40,
      "gain_pct": 1.89
    },
    {
      "cycle_number": 2,
      "entry_time": "11:05:00",
      "entry_price": 144.80,
      "exit_time": "11:45:00",
      "exit_price": 147.90,
      "duration_minutes": 40,
      "gain_pct": 2.14
    },
    {
      "cycle_number": 3,
      "entry_time": "13:20:00",
      "entry_price": 146.50,
      "exit_time": "13:40:00",
      "exit_price": 145.10,
      "duration_minutes": 20,
      "gain_pct": -0.96
    },
    {
      "cycle_number": 4,
      "entry_time": "14:30:00",
      "entry_price": 145.80,
      "exit_time": "15:30:00",
      "exit_price": 153.60,
      "duration_minutes": 60,
      "gain_pct": 5.35
    }
  ],
  "ai_analysis": "NVDA showed 4 distinct rise cycles today. Best cycle was #4 with 5.35% gain during afternoon momentum. The losing cycle #3 was cut short by stop-loss, limiting damage. Overall strategy would have generated 8.47% return on $10K capital."
}
```

---

## Part 4: API Endpoints

### 4.1 Strategy Management

```
GET  /api/strategies                    # List all strategies
GET  /api/strategies/{id}               # Get strategy details
POST /api/strategies                    # Create new strategy
PUT  /api/strategies/{id}               # Update strategy
DELETE /api/strategies/{id}             # Delete strategy
```

### 4.2 Signal Detection

```
GET  /api/strategies/{id}/signals       # Get recent signals
POST /api/strategies/{id}/scan          # Scan for new signals
GET  /api/strategies/{id}/scan/{symbol} # Scan specific symbol
```

### 4.3 Backtesting

```
POST /api/strategies/{id}/backtest      # Run backtest
GET  /api/backtests/{id}                # Get backtest results
GET  /api/strategies/{id}/backtests     # List all backtests
```

### 4.4 Rise Cycle Specific

```
GET  /api/rise-cycles/{symbol}/{date}   # Get cycles for symbol/date
POST /api/rise-cycles/simulate          # Simulate trading cycles
GET  /api/rise-cycles/daily-summary     # Daily summary across stocks
```

### 4.5 Paper Trading

```
GET  /api/paper-trades                  # List paper trades
POST /api/paper-trades                  # Create paper trade
GET  /api/paper-trades/summary          # Portfolio summary
GET  /api/paper-trades/{strategy_id}    # Trades for strategy
```

---

## Part 5: Frontend Components

### 5.1 Strategy Dashboard

```
/strategies
├── Strategy List (cards with performance)
├── Create New Strategy (wizard)
├── Strategy Detail View
│   ├── Parameters Panel
│   ├── Recent Signals Table
│   ├── Performance Chart
│   └── Backtest History
├── Rise Cycle Analyzer
│   ├── Symbol Selector
│   ├── Date Picker
│   ├── Cycle Visualization
│   └── "What If" Calculator
└── Paper Trading Portfolio
    ├── Open Positions
    ├── Closed Trades
    └── P&L Summary
```

### 5.2 Rise Cycle Visualization

```
┌─────────────────────────────────────────────────────────────┐
│  NVDA Rise Cycles - December 5, 2025                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  $153 ─┐                                          ┌───●     │
│        │                                         /          │
│  $150 ─┤                         ●──┐          /            │
│        │                        /    \        /             │
│  $147 ─┤      ●────●           /      \      /              │
│        │     /      \         /        \    /               │
│  $144 ─┤    /        \       /          \  /                │
│        │   /          \     /            ●                  │
│  $141 ─┤──●            \   /                                │
│        │                ●─●                                 │
│  $138 ─┴────┬────┬────┬────┬────┬────┬────┬────┬────┬─────  │
│        9:30  10   11   12   13   14   15   16               │
│                                                              │
│  Legend: ● Entry  ● Exit  ── Rise Cycle  ── Decline         │
├─────────────────────────────────────────────────────────────┤
│  CYCLE SUMMARY                                               │
│  ┌────────┬──────────┬──────────┬──────────┬────────┐       │
│  │ Cycle  │ Entry    │ Exit     │ Duration │ Gain % │       │
│  ├────────┼──────────┼──────────┼──────────┼────────┤       │
│  │ #1     │ $142.50  │ $145.20  │ 40 min   │ +1.89% │       │
│  │ #2     │ $144.80  │ $147.90  │ 40 min   │ +2.14% │       │
│  │ #3     │ $146.50  │ $145.10  │ 20 min   │ -0.96% │       │
│  │ #4     │ $145.80  │ $153.60  │ 60 min   │ +5.35% │       │
│  └────────┴──────────┴──────────┴──────────┴────────┘       │
│                                                              │
│  If you traded $10,000:  TOTAL RETURN: +$847.50 (+8.47%)    │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 6: Implementation Phases

### Phase 1: Database Setup
- [ ] Create all strategy tables in BigQuery
- [ ] Insert Rise Cycle Detection as first strategy
- [ ] Insert Sector Momentum as second strategy

### Phase 2: Algorithm Implementation
- [ ] Build rise cycle detection function
- [ ] Build sector momentum ranking function
- [ ] Create signal generation logic

### Phase 3: API Development
- [ ] Add strategy endpoints to trading API
- [ ] Implement backtest engine
- [ ] Add paper trading logic

### Phase 4: Frontend
- [ ] Create StrategyDashboard.jsx
- [ ] Create RiseCycleAnalyzer.jsx
- [ ] Create PaperTradingPortfolio.jsx
- [ ] Add strategy page to navigation

### Phase 5: AI Integration
- [ ] Connect Gemini for cycle analysis
- [ ] Generate AI insights for each cycle
- [ ] Create AI-powered strategy recommendations

---

## Part 7: Sector/Industry Enhancement

To support the Sector Momentum strategy, add these fields to weekly tables:

```sql
-- Add to weekly_stocks_all
ALTER TABLE `cryptobot-462709.crypto_trading_data.weekly_stocks_all`
ADD COLUMN sector STRING,
ADD COLUMN industry STRING,
ADD COLUMN market_cap FLOAT64,
ADD COLUMN market_cap_category STRING;  -- 'mega', 'large', 'mid', 'small', 'micro'

-- Create sector momentum view
CREATE OR REPLACE VIEW `cryptobot-462709.crypto_trading_data.v_sector_momentum` AS
SELECT
    sector,
    COUNT(DISTINCT symbol) as stock_count,
    AVG(week_change_pct) as avg_change_pct,
    SUM(volume) as total_volume,
    RANK() OVER (ORDER BY AVG(week_change_pct) DESC) as momentum_rank
FROM `cryptobot-462709.crypto_trading_data.weekly_stocks_all` w
JOIN `cryptobot-462709.crypto_trading_data.stocks_master_list` m
  ON w.symbol = m.symbol
WHERE w.week_start = (SELECT MAX(week_start) FROM weekly_stocks_all)
GROUP BY sector
ORDER BY avg_change_pct DESC;
```

---

*Document Version: 1.0*
*Created by: Claude Code for AIAlgoTradeHits*
