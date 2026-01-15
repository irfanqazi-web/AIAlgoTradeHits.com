"""
Complete Rise Cycle Enhancement
Adds: Sector Sentiment, Political/Trump News, Market Regime, Sector Momentum,
      Multi-Day Confirmation, Day-of-Week Optimization
"""

from google.cloud import bigquery
from datetime import datetime
import requests

client = bigquery.Client(project='aialgotradehits')

print("=" * 70)
print("COMPLETE RISE CYCLE ENHANCEMENT")
print("=" * 70)
print(f"Started: {datetime.now()}")

# ============================================================================
# STEP 1: Create Sector Sentiment Tables
# ============================================================================
print("\n" + "=" * 70)
print("STEP 1: Creating Sector & Industry Sentiment Tables")
print("-" * 70)

# Sector mapping for our stocks
SECTOR_MAPPING = {
    'AAPL': {'sector': 'Technology', 'industry': 'Consumer Electronics', 'sector_etf': 'XLK'},
    'MSFT': {'sector': 'Technology', 'industry': 'Software', 'sector_etf': 'XLK'},
    'GOOGL': {'sector': 'Technology', 'industry': 'Internet Services', 'sector_etf': 'XLK'},
    'NVDA': {'sector': 'Technology', 'industry': 'Semiconductors', 'sector_etf': 'SMH'},
    'AMD': {'sector': 'Technology', 'industry': 'Semiconductors', 'sector_etf': 'SMH'},
    'AVGO': {'sector': 'Technology', 'industry': 'Semiconductors', 'sector_etf': 'SMH'},
    'INTC': {'sector': 'Technology', 'industry': 'Semiconductors', 'sector_etf': 'SMH'},
    'LMT': {'sector': 'Industrials', 'industry': 'Defense', 'sector_etf': 'XLI'},
    'RTX': {'sector': 'Industrials', 'industry': 'Defense', 'sector_etf': 'XLI'},
    'HON': {'sector': 'Industrials', 'industry': 'Diversified', 'sector_etf': 'XLI'},
    'CAT': {'sector': 'Industrials', 'industry': 'Machinery', 'sector_etf': 'XLI'},
    'JPM': {'sector': 'Financials', 'industry': 'Banking', 'sector_etf': 'XLF'},
    'V': {'sector': 'Financials', 'industry': 'Payments', 'sector_etf': 'XLF'},
}

# Create sector sentiment table
sector_sentiment_ddl = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.sector_sentiment` (
    date DATE,
    sector STRING,
    industry STRING,
    sentiment_score FLOAT64,  -- -1 to 1 scale
    sentiment_label STRING,   -- BULLISH, NEUTRAL, BEARISH
    news_volume INT64,        -- Number of news articles
    positive_mentions INT64,
    negative_mentions INT64,
    trump_impact_score FLOAT64,  -- Impact from Trump/political news
    tariff_risk_score FLOAT64,   -- Trade/tariff risk
    regulatory_risk_score FLOAT64,
    sector_momentum_5d FLOAT64,  -- 5-day sector ETF return
    sector_momentum_20d FLOAT64, -- 20-day sector ETF return
    updated_at TIMESTAMP
)
PARTITION BY date
"""

print("Creating sector_sentiment table...")
try:
    client.query(sector_sentiment_ddl).result()
    print("  sector_sentiment table created")
except Exception as e:
    print(f"  Table may already exist: {e}")

# Create political/news sentiment table
political_sentiment_ddl = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.political_sentiment` (
    date DATE,
    headline STRING,
    source STRING,
    sentiment_score FLOAT64,
    impact_sectors ARRAY<STRING>,  -- Affected sectors
    trump_related BOOL,
    tariff_related BOOL,
    fed_related BOOL,
    china_related BOOL,
    market_impact STRING,  -- POSITIVE, NEGATIVE, NEUTRAL
    confidence FLOAT64,
    created_at TIMESTAMP
)
PARTITION BY date
"""

print("Creating political_sentiment table...")
try:
    client.query(political_sentiment_ddl).result()
    print("  political_sentiment table created")
except Exception as e:
    print(f"  Table may already exist: {e}")

# ============================================================================
# STEP 2: Create Market Regime Detection
# ============================================================================
print("\n" + "=" * 70)
print("STEP 2: Creating Market Regime Detection")
print("-" * 70)

# Get SPY data for market regime
market_regime_query = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.market_regime` AS
WITH spy_data AS (
    SELECT
        DATE(datetime) as date,
        close,
        AVG(close) OVER (ORDER BY datetime ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as sma_50,
        AVG(close) OVER (ORDER BY datetime ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) as sma_200,
        STDDEV(close) OVER (ORDER BY datetime ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as volatility_20d,
        (close - LAG(close, 5) OVER (ORDER BY datetime)) / NULLIF(LAG(close, 5) OVER (ORDER BY datetime), 0) * 100 as return_5d,
        (close - LAG(close, 20) OVER (ORDER BY datetime)) / NULLIF(LAG(close, 20) OVER (ORDER BY datetime), 0) * 100 as return_20d
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE symbol = 'AAPL'  -- Using AAPL as proxy since we may not have SPY
      AND datetime >= '2023-01-01'
),
regime_calc AS (
    SELECT
        date,
        close,
        sma_50,
        sma_200,
        volatility_20d,
        return_5d,
        return_20d,
        CASE
            WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_BULL'
            WHEN close > sma_50 AND close > sma_200 THEN 'BULL'
            WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_BEAR'
            WHEN close < sma_50 AND close < sma_200 THEN 'BEAR'
            ELSE 'NEUTRAL'
        END as market_regime,
        CASE
            WHEN volatility_20d / close < 0.01 THEN 'LOW_VOL'
            WHEN volatility_20d / close < 0.02 THEN 'NORMAL_VOL'
            ELSE 'HIGH_VOL'
        END as volatility_regime
    FROM spy_data
)
SELECT * FROM regime_calc
WHERE date IS NOT NULL
"""

print("Creating market regime table...")
client.query(market_regime_query).result()
print("  Market regime table created")

# Check market regime distribution
regime_check = """
SELECT market_regime, volatility_regime, COUNT(*) as days
FROM `aialgotradehits.ml_models.market_regime`
WHERE date >= '2024-01-01'
GROUP BY market_regime, volatility_regime
ORDER BY days DESC
"""
print("\nMarket Regime Distribution (2024+):")
for row in client.query(regime_check).result():
    print(f"  {row.market_regime} / {row.volatility_regime}: {row.days} days")

# ============================================================================
# STEP 3: Calculate Sector Momentum
# ============================================================================
print("\n" + "=" * 70)
print("STEP 3: Calculating Sector Momentum")
print("-" * 70)

sector_momentum_query = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.sector_momentum` AS
WITH sector_returns AS (
    SELECT
        DATE(datetime) as date,
        symbol,
        close,
        (close - LAG(close, 5) OVER (PARTITION BY symbol ORDER BY datetime)) /
            NULLIF(LAG(close, 5) OVER (PARTITION BY symbol ORDER BY datetime), 0) * 100 as return_5d,
        (close - LAG(close, 20) OVER (PARTITION BY symbol ORDER BY datetime)) /
            NULLIF(LAG(close, 20) OVER (PARTITION BY symbol ORDER BY datetime), 0) * 100 as return_20d
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE symbol IN ('AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'AVGO', 'INTC', 'LMT', 'RTX', 'HON', 'CAT', 'JPM', 'V')
      AND datetime >= '2023-01-01'
),
sector_avg AS (
    SELECT
        date,
        -- Technology sector average
        AVG(CASE WHEN symbol IN ('AAPL', 'MSFT', 'GOOGL') THEN return_5d END) as tech_return_5d,
        AVG(CASE WHEN symbol IN ('AAPL', 'MSFT', 'GOOGL') THEN return_20d END) as tech_return_20d,
        -- Semiconductor average
        AVG(CASE WHEN symbol IN ('NVDA', 'AMD', 'AVGO', 'INTC') THEN return_5d END) as semi_return_5d,
        AVG(CASE WHEN symbol IN ('NVDA', 'AMD', 'AVGO', 'INTC') THEN return_20d END) as semi_return_20d,
        -- Industrials/Defense average
        AVG(CASE WHEN symbol IN ('LMT', 'RTX', 'HON', 'CAT') THEN return_5d END) as industrial_return_5d,
        AVG(CASE WHEN symbol IN ('LMT', 'RTX', 'HON', 'CAT') THEN return_20d END) as industrial_return_20d,
        -- Financials average
        AVG(CASE WHEN symbol IN ('JPM', 'V') THEN return_5d END) as financial_return_5d,
        AVG(CASE WHEN symbol IN ('JPM', 'V') THEN return_20d END) as financial_return_20d
    FROM sector_returns
    GROUP BY date
)
SELECT
    s.date,
    s.symbol,
    s.close,
    s.return_5d as stock_return_5d,
    s.return_20d as stock_return_20d,
    -- Relative strength vs sector
    CASE
        WHEN s.symbol IN ('AAPL', 'MSFT', 'GOOGL') THEN s.return_5d - a.tech_return_5d
        WHEN s.symbol IN ('NVDA', 'AMD', 'AVGO', 'INTC') THEN s.return_5d - a.semi_return_5d
        WHEN s.symbol IN ('LMT', 'RTX', 'HON', 'CAT') THEN s.return_5d - a.industrial_return_5d
        WHEN s.symbol IN ('JPM', 'V') THEN s.return_5d - a.financial_return_5d
    END as relative_strength_5d,
    -- Sector momentum
    CASE
        WHEN s.symbol IN ('AAPL', 'MSFT', 'GOOGL') THEN a.tech_return_5d
        WHEN s.symbol IN ('NVDA', 'AMD', 'AVGO', 'INTC') THEN a.semi_return_5d
        WHEN s.symbol IN ('LMT', 'RTX', 'HON', 'CAT') THEN a.industrial_return_5d
        WHEN s.symbol IN ('JPM', 'V') THEN a.financial_return_5d
    END as sector_momentum_5d,
    -- Sector label
    CASE
        WHEN s.symbol IN ('AAPL', 'MSFT', 'GOOGL') THEN 'Technology'
        WHEN s.symbol IN ('NVDA', 'AMD', 'AVGO', 'INTC') THEN 'Semiconductors'
        WHEN s.symbol IN ('LMT', 'RTX', 'HON', 'CAT') THEN 'Industrials'
        WHEN s.symbol IN ('JPM', 'V') THEN 'Financials'
    END as sector
FROM sector_returns s
JOIN sector_avg a ON s.date = a.date
"""

print("Creating sector momentum table...")
client.query(sector_momentum_query).result()
print("  Sector momentum table created")

# ============================================================================
# STEP 4: Create Enhanced Rise Cycle Features with All Factors
# ============================================================================
print("\n" + "=" * 70)
print("STEP 4: Creating Enhanced Rise Cycle Features")
print("-" * 70)

enhanced_features_query = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.rise_cycle_enhanced` AS
WITH base_features AS (
    SELECT
        f.*,
        -- Day of week (1=Sunday, 7=Saturday)
        EXTRACT(DAYOFWEEK FROM f.datetime) as day_of_week,
        -- Multi-day confirmation
        LAG(rise_cycle_score) OVER (PARTITION BY f.symbol ORDER BY f.datetime) as prev_day_score,
        LAG(rise_cycle_score, 2) OVER (PARTITION BY f.symbol ORDER BY f.datetime) as prev_2day_score,
        LAG(ema_bullish) OVER (PARTITION BY f.symbol ORDER BY f.datetime) as prev_ema_bullish,
        LAG(direction_target) OVER (PARTITION BY f.symbol ORDER BY f.datetime) as prev_actual_direction
    FROM `aialgotradehits.ml_models.rise_cycle_features` f
),
with_market AS (
    SELECT
        b.*,
        m.market_regime,
        m.volatility_regime,
        m.return_5d as market_return_5d,
        m.return_20d as market_return_20d
    FROM base_features b
    LEFT JOIN `aialgotradehits.ml_models.market_regime` m
        ON DATE(b.datetime) = m.date
),
with_sector AS (
    SELECT
        w.*,
        s.sector,
        s.sector_momentum_5d,
        s.relative_strength_5d,
        s.stock_return_5d
    FROM with_market w
    LEFT JOIN `aialgotradehits.ml_models.sector_momentum` s
        ON DATE(w.datetime) = s.date AND w.symbol = s.symbol
)
SELECT
    symbol,
    datetime,
    close,
    direction_target,

    -- Original rise cycle indicators
    rise_cycle_score,
    rsi,
    macd_histogram,
    adx,
    momentum,
    ema_bullish,
    above_sma50,
    above_sma200,
    volume_ratio,

    -- Day of week (Tuesday-Thursday historically better)
    day_of_week,
    CASE WHEN day_of_week IN (3, 4, 5) THEN 1 ELSE 0 END as optimal_day,  -- Tue, Wed, Thu

    -- Multi-day confirmation
    prev_day_score,
    prev_2day_score,
    prev_ema_bullish,
    CASE WHEN rise_cycle_score >= 5 AND prev_day_score >= 4 THEN 1 ELSE 0 END as multi_day_confirmed,
    CASE WHEN ema_bullish = 1 AND prev_ema_bullish = 1 THEN 1 ELSE 0 END as ema_streak,

    -- Market regime
    market_regime,
    volatility_regime,
    market_return_5d,
    CASE WHEN market_regime IN ('STRONG_BULL', 'BULL') THEN 1 ELSE 0 END as bull_market,
    CASE WHEN volatility_regime = 'LOW_VOL' THEN 1 ELSE 0 END as low_volatility,

    -- Sector momentum
    sector,
    sector_momentum_5d,
    relative_strength_5d,
    CASE WHEN sector_momentum_5d > 0 THEN 1 ELSE 0 END as sector_bullish,
    CASE WHEN relative_strength_5d > 0 THEN 1 ELSE 0 END as outperforming_sector,

    -- Combined enhanced score (0-20)
    rise_cycle_score +
    (CASE WHEN day_of_week IN (3, 4, 5) THEN 1 ELSE 0 END) +
    (CASE WHEN rise_cycle_score >= 5 AND prev_day_score >= 4 THEN 2 ELSE 0 END) +
    (CASE WHEN market_regime IN ('STRONG_BULL', 'BULL') THEN 2 ELSE 0 END) +
    (CASE WHEN volatility_regime = 'LOW_VOL' THEN 1 ELSE 0 END) +
    (CASE WHEN sector_momentum_5d > 0 THEN 2 ELSE 0 END) +
    (CASE WHEN relative_strength_5d > 0 THEN 2 ELSE 0 END) as enhanced_score

FROM with_sector
WHERE datetime >= '2024-01-01'
"""

print("Creating enhanced rise cycle features...")
client.query(enhanced_features_query).result()

# Count and verify
count_result = list(client.query("""
    SELECT COUNT(*) as total,
           SUM(direction_target) as ups,
           ROUND(AVG(enhanced_score), 2) as avg_enhanced_score
    FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
""").result())[0]
print(f"  Enhanced features created: {count_result.total:,} records")
print(f"  Average enhanced score: {count_result.avg_enhanced_score}")

# ============================================================================
# STEP 5: Analyze Enhanced Score Effectiveness
# ============================================================================
print("\n" + "=" * 70)
print("STEP 5: Analyzing Enhanced Score Effectiveness")
print("-" * 70)

# Enhanced score analysis
enhanced_analysis = """
SELECT
    enhanced_score,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
GROUP BY enhanced_score
ORDER BY enhanced_score
"""

print("\nEnhanced Score Effectiveness:")
print(f"{'Score':<8} {'Total':>10} {'UPs':>10} {'UP %':>10}")
print("-" * 45)
for row in client.query(enhanced_analysis).result():
    marker = " ***" if row.up_pct and row.up_pct > 25 else ""
    print(f"{row.enhanced_score:<8} {row.total:>10,} {row.ups:>10,} {row.up_pct:>9.1f}%{marker}")

# Analyze by factor combinations
factor_analysis = """
SELECT
    'Bull Market + Score 5+' as factor,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
WHERE bull_market = 1 AND rise_cycle_score >= 5

UNION ALL

SELECT
    'Optimal Day + Score 5+' as factor,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
WHERE optimal_day = 1 AND rise_cycle_score >= 5

UNION ALL

SELECT
    'Multi-Day Confirmed' as factor,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
WHERE multi_day_confirmed = 1

UNION ALL

SELECT
    'Sector Bullish + Score 5+' as factor,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
WHERE sector_bullish = 1 AND rise_cycle_score >= 5

UNION ALL

SELECT
    'Outperforming Sector + Score 5+' as factor,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
WHERE outperforming_sector = 1 AND rise_cycle_score >= 5

UNION ALL

SELECT
    'All Factors Aligned' as factor,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
WHERE bull_market = 1
  AND sector_bullish = 1
  AND multi_day_confirmed = 1
  AND rise_cycle_score >= 5

ORDER BY up_pct DESC
"""

print("\n\nFactor Combination Analysis:")
print(f"{'Factor':<30} {'Total':>10} {'UPs':>10} {'UP %':>10}")
print("-" * 65)
for row in client.query(factor_analysis).result():
    if row.up_pct:
        print(f"{row.factor:<30} {row.total:>10,} {row.ups:>10,} {row.up_pct:>9.1f}%")

# ============================================================================
# STEP 6: Create Final Enhanced Signal View
# ============================================================================
print("\n" + "=" * 70)
print("STEP 6: Creating Final Enhanced Signal View")
print("-" * 70)

final_view = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_rise_cycle_enhanced_signals` AS
WITH ranked AS (
    SELECT
        symbol,
        DATE(datetime) as signal_date,
        close as current_price,
        rise_cycle_score,
        enhanced_score,
        rsi,
        adx,
        volume_ratio,
        day_of_week,
        optimal_day,
        multi_day_confirmed,
        ema_streak,
        market_regime,
        bull_market,
        sector,
        sector_momentum_5d,
        sector_bullish,
        outperforming_sector,
        relative_strength_5d,
        ema_bullish,
        above_sma50,
        above_sma200,
        -- Enhanced signal classification
        CASE
            -- ULTRA signals: All factors aligned
            WHEN enhanced_score >= 15 AND bull_market = 1 AND sector_bullish = 1 THEN 'ULTRA_BUY'
            WHEN enhanced_score >= 14 AND multi_day_confirmed = 1 AND sector_bullish = 1 THEN 'ULTRA_BUY'
            -- STRONG signals: Most factors aligned
            WHEN enhanced_score >= 12 AND bull_market = 1 THEN 'STRONG_BUY'
            WHEN enhanced_score >= 11 AND sector_bullish = 1 AND outperforming_sector = 1 THEN 'STRONG_BUY'
            -- BUY signals: Good alignment
            WHEN enhanced_score >= 10 THEN 'BUY'
            WHEN rise_cycle_score >= 5 AND sector_bullish = 1 THEN 'BUY'
            -- WEAK signals
            WHEN enhanced_score >= 8 AND ema_bullish = 1 THEN 'WEAK_BUY'
            ELSE 'WATCH'
        END as signal,
        -- Confidence based on factor alignment
        CASE
            WHEN enhanced_score >= 15 THEN 'VERY_HIGH'
            WHEN enhanced_score >= 12 THEN 'HIGH'
            WHEN enhanced_score >= 10 THEN 'MEDIUM'
            ELSE 'LOW'
        END as confidence,
        ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY enhanced_score DESC) as rn
    FROM `aialgotradehits.ml_models.rise_cycle_enhanced`
    WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
)
SELECT
    symbol,
    signal_date,
    current_price,
    rise_cycle_score as base_score,
    enhanced_score,
    signal,
    confidence,
    rsi,
    adx,
    volume_ratio,
    -- Factor flags
    CASE WHEN optimal_day = 1 THEN 'Yes' ELSE 'No' END as optimal_day,
    CASE WHEN multi_day_confirmed = 1 THEN 'Yes' ELSE 'No' END as multi_day_confirmed,
    market_regime,
    CASE WHEN bull_market = 1 THEN 'Yes' ELSE 'No' END as bull_market,
    sector,
    ROUND(sector_momentum_5d, 2) as sector_momentum_5d,
    CASE WHEN sector_bullish = 1 THEN 'Yes' ELSE 'No' END as sector_bullish,
    CASE WHEN outperforming_sector = 1 THEN 'Yes' ELSE 'No' END as outperforming_sector,
    ROUND(relative_strength_5d, 2) as relative_strength,
    ema_bullish,
    above_sma50,
    above_sma200
FROM ranked
WHERE rn = 1
ORDER BY signal_date DESC, enhanced_score DESC
"""

client.query(final_view).result()
print("  Enhanced signal view created!")

# Show current signals
print("\nCurrent Enhanced Signals (Last 7 Days):")
print("-" * 100)
signals = list(client.query("""
    SELECT * FROM `aialgotradehits.ml_models.v_rise_cycle_enhanced_signals`
    WHERE signal IN ('ULTRA_BUY', 'STRONG_BUY', 'BUY')
      AND signal_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    ORDER BY enhanced_score DESC, signal_date DESC
    LIMIT 15
""").result())

if signals:
    print(f"{'Date':<12} {'Symbol':<6} {'Price':>8} {'Base':>5} {'Enh':>5} {'Signal':<12} {'Sector':<14} {'SecMom':>7} {'Regime':<12}")
    print("-" * 100)
    for s in signals:
        sec_mom = f"{s.sector_momentum_5d:>6.1f}%" if s.sector_momentum_5d else "N/A"
        print(f"{str(s.signal_date):<12} {s.symbol:<6} {s.current_price:>8.2f} {s.base_score:>5} {s.enhanced_score:>5} {s.signal:<12} {s.sector:<14} {sec_mom:>7} {s.market_regime:<12}")
else:
    print("No high-confidence signals in last 7 days")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("ENHANCEMENT SUMMARY")
print("=" * 70)
print("""
New Factors Added:
1. Market Regime: STRONG_BULL, BULL, NEUTRAL, BEAR, STRONG_BEAR
2. Volatility Regime: LOW_VOL, NORMAL_VOL, HIGH_VOL
3. Sector Momentum: 5-day sector return
4. Relative Strength: Stock vs sector performance
5. Multi-Day Confirmation: 2 consecutive bullish days
6. Day of Week: Tuesday-Thursday optimization
7. EMA Streak: Consecutive EMA bullish days

Enhanced Score (0-20) = Base Score + Factor Bonuses:
- Optimal Day (Tue-Thu): +1
- Multi-Day Confirmed: +2
- Bull Market: +2
- Low Volatility: +1
- Sector Bullish: +2
- Outperforming Sector: +2

Signal Rules:
- ULTRA_BUY: Enhanced >= 15 with bull market and sector bullish
- STRONG_BUY: Enhanced >= 12 with bull market
- BUY: Enhanced >= 10 or (Base >= 5 with sector bullish)
- WEAK_BUY: Enhanced >= 8 with EMA bullish
""")

print(f"\nCompleted: {datetime.now()}")
print("=" * 70)
