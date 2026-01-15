"""
Rise Cycle Prediction Improvement V2
Additional features and refined signal criteria to improve UP prediction accuracy
"""

from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client(project='aialgotradehits')

print("=" * 70)
print("RISE CYCLE IMPROVEMENT V2")
print("=" * 70)
print(f"Started: {datetime.now()}")

# Symbols to analyze
symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'AVGO', 'INTC',
           'LMT', 'RTX', 'HON', 'CAT', 'JPM', 'V']
symbol_str = "','".join(symbols)

# ============================================================================
# PHASE 1: Analyze Current Rise Cycle Score Performance by Additional Factors
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 1: Analyzing Additional Predictive Factors")
print("-" * 70)

# Analyze RSI ranges within each score
rsi_analysis = """
WITH scored_data AS (
    SELECT
        rise_cycle_score,
        rsi,
        direction_target,
        CASE
            WHEN rsi < 40 THEN 'Oversold (<40)'
            WHEN rsi BETWEEN 40 AND 50 THEN 'Neutral-Low (40-50)'
            WHEN rsi BETWEEN 50 AND 60 THEN 'Neutral-High (50-60)'
            WHEN rsi BETWEEN 60 AND 70 THEN 'Strong (60-70)'
            ELSE 'Overbought (>70)'
        END as rsi_range
    FROM `aialgotradehits.ml_models.rise_cycle_features`
    WHERE DATE(datetime) BETWEEN '2024-01-01' AND '2025-12-31'
      AND rise_cycle_score >= 4
)
SELECT
    rise_cycle_score,
    rsi_range,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM scored_data
GROUP BY rise_cycle_score, rsi_range
ORDER BY rise_cycle_score DESC, up_pct DESC
"""

print("\nUP Accuracy by Score + RSI Range:")
print(f"{'Score':<6} {'RSI Range':<20} {'Total':>8} {'UPs':>8} {'UP %':>8}")
print("-" * 55)
for row in client.query(rsi_analysis).result():
    print(f"{row.rise_cycle_score:<6} {row.rsi_range:<20} {row.total:>8} {row.ups:>8} {row.up_pct:>7.1f}%")

# Analyze ADX (trend strength) impact
adx_analysis = """
WITH scored_data AS (
    SELECT
        rise_cycle_score,
        adx,
        direction_target,
        CASE
            WHEN adx < 20 THEN 'Weak Trend (<20)'
            WHEN adx BETWEEN 20 AND 30 THEN 'Moderate (20-30)'
            WHEN adx BETWEEN 30 AND 40 THEN 'Strong (30-40)'
            ELSE 'Very Strong (>40)'
        END as adx_range
    FROM `aialgotradehits.ml_models.rise_cycle_features`
    WHERE DATE(datetime) BETWEEN '2024-01-01' AND '2025-12-31'
      AND rise_cycle_score >= 4
)
SELECT
    adx_range,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM scored_data
GROUP BY adx_range
ORDER BY up_pct DESC
"""

print("\n\nUP Accuracy by ADX Range (Score >= 4):")
print(f"{'ADX Range':<20} {'Total':>10} {'UPs':>10} {'UP %':>10}")
print("-" * 55)
for row in client.query(adx_analysis).result():
    print(f"{row.adx_range:<20} {row.total:>10} {row.ups:>10} {row.up_pct:>9.1f}%")

# Analyze volume ratio impact
volume_analysis = """
WITH scored_data AS (
    SELECT
        rise_cycle_score,
        volume_ratio,
        direction_target,
        CASE
            WHEN volume_ratio < 0.8 THEN 'Low Vol (<0.8)'
            WHEN volume_ratio BETWEEN 0.8 AND 1.0 THEN 'Normal (0.8-1.0)'
            WHEN volume_ratio BETWEEN 1.0 AND 1.5 THEN 'Above Avg (1.0-1.5)'
            ELSE 'High Vol (>1.5)'
        END as vol_range
    FROM `aialgotradehits.ml_models.rise_cycle_features`
    WHERE DATE(datetime) BETWEEN '2024-01-01' AND '2025-12-31'
      AND rise_cycle_score >= 4
      AND volume_ratio IS NOT NULL
)
SELECT
    vol_range,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM scored_data
GROUP BY vol_range
ORDER BY up_pct DESC
"""

print("\n\nUP Accuracy by Volume Ratio (Score >= 4):")
print(f"{'Volume Range':<20} {'Total':>10} {'UPs':>10} {'UP %':>10}")
print("-" * 55)
for row in client.query(volume_analysis).result():
    print(f"{row.vol_range:<20} {row.total:>10} {row.ups:>10} {row.up_pct:>9.1f}%")

# ============================================================================
# PHASE 2: Create Enhanced Rise Cycle Features
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 2: Creating Enhanced Rise Cycle Features")
print("-" * 70)

enhanced_features_query = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.rise_cycle_features_v2` AS
WITH base_data AS (
    SELECT
        symbol, datetime, close, open, high, low, volume,
        rsi, macd, macd_histogram, mfi, cci, adx, momentum,
        sma_20, sma_50, sma_200, atr, ema_12, ema_26,
        CASE WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 1 ELSE 0 END as direction_target
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE symbol IN ('{symbol_str}')
      AND datetime >= '2023-01-01'
      AND rsi IS NOT NULL AND macd IS NOT NULL AND ema_12 IS NOT NULL
),
with_lags AS (
    SELECT *,
        -- Previous values
        LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close,
        LAG(close, 2) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close_2,
        LAG(close, 3) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close_3,
        LAG(close, 5) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close_5,
        LAG(rsi) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi,
        LAG(rsi, 2) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi_2,
        LAG(rsi, 3) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi_3,
        LAG(rsi, 5) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi_5,
        LAG(macd_histogram) OVER (PARTITION BY symbol ORDER BY datetime) as prev_macd_hist,
        LAG(macd_histogram, 2) OVER (PARTITION BY symbol ORDER BY datetime) as prev_macd_hist_2,
        LAG(ema_12) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_12,
        LAG(ema_26) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_26,
        LAG(momentum) OVER (PARTITION BY symbol ORDER BY datetime) as prev_momentum,
        LAG(cci) OVER (PARTITION BY symbol ORDER BY datetime) as prev_cci,
        LAG(adx) OVER (PARTITION BY symbol ORDER BY datetime) as prev_adx,
        LAG(volume) OVER (PARTITION BY symbol ORDER BY datetime) as prev_volume,
        -- Rolling calculations
        AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as avg_volume_20,
        MAX(high) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as max_high_20,
        MIN(low) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as min_low_20,
        STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as stddev_10,
        AVG(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) as avg_close_5
    FROM base_data WHERE direction_target IS NOT NULL
),
with_up_flags AS (
    SELECT *,
        CASE WHEN close > prev_close THEN 1 ELSE 0 END as is_up_day,
        CASE WHEN prev_close > prev_close_2 THEN 1 ELSE 0 END as prev_up_day,
        CASE WHEN prev_close_2 > prev_close_3 THEN 1 ELSE 0 END as prev_up_day_2
    FROM with_lags
),
with_streaks AS (
    SELECT *,
        is_up_day + prev_up_day + prev_up_day_2 as up_streak_3
    FROM with_up_flags
)
SELECT
    symbol, datetime, close, direction_target,
    rsi, macd, macd_histogram, mfi, cci, adx, momentum,

    -- ORIGINAL RISE CYCLE INDICATORS
    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as ema_bullish,
    CASE WHEN ema_12 > ema_26 AND prev_ema_12 <= prev_ema_26 THEN 1 ELSE 0 END as ema_cross_up,
    rsi - prev_rsi_3 as rsi_momentum_3d,
    CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END as rsi_sweet_spot,
    CASE WHEN macd_histogram > 0 AND prev_macd_hist <= 0 THEN 1 ELSE 0 END as macd_turning_bullish,
    macd_histogram - prev_macd_hist as macd_hist_change,
    CASE WHEN close > sma_20 THEN 1 ELSE 0 END as above_sma20,
    CASE WHEN close > sma_50 THEN 1 ELSE 0 END as above_sma50,
    CASE WHEN close > sma_200 THEN 1 ELSE 0 END as above_sma200,
    CASE WHEN adx > 25 THEN 1 ELSE 0 END as strong_trend,
    CASE WHEN mfi BETWEEN 30 AND 70 THEN 1 ELSE 0 END as mfi_healthy,
    CASE WHEN momentum > 0 THEN 1 ELSE 0 END as positive_momentum,
    volume / NULLIF(avg_volume_20, 0) as volume_ratio,
    (close - low) / NULLIF(high - low, 0) as daily_range_position,
    close / NULLIF(max_high_20, 0) as price_vs_20d_high,

    -- NEW ENHANCED FEATURES

    -- 1. Multi-day momentum confirmation
    CASE WHEN rsi > prev_rsi AND prev_rsi > prev_rsi_2 THEN 1 ELSE 0 END as rsi_rising_3d,
    CASE WHEN macd_histogram > prev_macd_hist AND prev_macd_hist > prev_macd_hist_2 THEN 1 ELSE 0 END as macd_hist_rising_3d,

    -- 2. Price momentum slope
    (close - prev_close_3) / NULLIF(prev_close_3, 0) * 100 as price_momentum_3d_pct,

    -- 3. RSI acceleration (rate of change)
    (rsi - prev_rsi) - (prev_rsi - prev_rsi_2) as rsi_acceleration,

    -- 4. Trend strength improving
    CASE WHEN adx > prev_adx THEN 1 ELSE 0 END as adx_rising,

    -- 5. Volume surge with price confirmation
    CASE WHEN volume > avg_volume_20 * 1.2 AND close > prev_close THEN 1 ELSE 0 END as volume_breakout,

    -- 6. Price distance from 20-day SMA (proxy for BB position)
    (close - sma_20) / NULLIF(sma_20, 0) * 100 as price_vs_sma20_pct,

    -- 7. Price vs recent average (above avg = bullish)
    CASE WHEN close > avg_close_5 THEN 1 ELSE 0 END as above_recent_avg,

    -- 8. Consecutive up days streak
    up_streak_3,

    -- 9. Near 20-day high (breakout zone)
    CASE WHEN close > max_high_20 * 0.98 THEN 1 ELSE 0 END as near_20d_high,

    -- 10. Candle body bullish (close > open)
    CASE WHEN close > open THEN 1 ELSE 0 END as bullish_candle,

    -- 11. Volatility (ATR-based)
    atr / NULLIF(close, 0) * 100 as atr_pct,

    -- 12. RSI in optimal buy zone (45-60 for trending up)
    CASE WHEN rsi BETWEEN 45 AND 60 THEN 1 ELSE 0 END as rsi_optimal_buy,

    -- 13. ADX in sweet spot (25-40 = strong but not exhausted trend)
    CASE WHEN adx BETWEEN 25 AND 40 THEN 1 ELSE 0 END as adx_sweet_spot,

    -- 14. MFI momentum
    CASE WHEN mfi > 50 AND mfi < 80 THEN 1 ELSE 0 END as mfi_buying_pressure,

    -- 15. CCI positive momentum
    CASE WHEN cci > 0 AND cci < 150 THEN 1 ELSE 0 END as cci_bullish_zone,

    -- ORIGINAL Rise Cycle Score (0-10)
    (CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END) +
    (CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END) +
    (CASE WHEN macd_histogram > 0 THEN 1 ELSE 0 END) +
    (CASE WHEN close > sma_50 THEN 1 ELSE 0 END) +
    (CASE WHEN close > sma_200 THEN 1 ELSE 0 END) +
    (CASE WHEN adx > 25 THEN 1 ELSE 0 END) +
    (CASE WHEN mfi BETWEEN 30 AND 70 THEN 1 ELSE 0 END) +
    (CASE WHEN momentum > 0 THEN 1 ELSE 0 END) +
    (CASE WHEN macd_histogram > prev_macd_hist THEN 1 ELSE 0 END) +
    (CASE WHEN rsi > prev_rsi THEN 1 ELSE 0 END) as rise_cycle_score,

    -- NEW Enhanced Score V2 (0-15) - More confirmation required
    (CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END) +
    (CASE WHEN rsi BETWEEN 45 AND 60 THEN 2 WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END) +
    (CASE WHEN macd_histogram > 0 AND macd_histogram > prev_macd_hist THEN 2 WHEN macd_histogram > 0 THEN 1 ELSE 0 END) +
    (CASE WHEN close > sma_50 AND close > sma_200 THEN 2 WHEN close > sma_50 THEN 1 ELSE 0 END) +
    (CASE WHEN adx BETWEEN 25 AND 40 THEN 2 WHEN adx > 25 THEN 1 ELSE 0 END) +
    (CASE WHEN volume > avg_volume_20 AND close > prev_close THEN 2 ELSE 0 END) +
    (CASE WHEN rsi > prev_rsi AND prev_rsi > prev_rsi_2 THEN 2 WHEN rsi > prev_rsi THEN 1 ELSE 0 END) +
    (CASE WHEN close > open THEN 1 ELSE 0 END) as rise_cycle_score_v2

FROM with_streaks
"""

print("Creating enhanced features table...")
client.query(enhanced_features_query).result()

# Count records
count_result = list(client.query("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN direction_target = 1 THEN 1 ELSE 0 END) as up_count,
           ROUND(AVG(rise_cycle_score), 2) as avg_v1_score,
           ROUND(AVG(rise_cycle_score_v2), 2) as avg_v2_score
    FROM `aialgotradehits.ml_models.rise_cycle_features_v2`
""").result())[0]
print(f"Enhanced features table created: {count_result.total:,} records")
print(f"UP days: {count_result.up_count:,} ({count_result.up_count/count_result.total*100:.1f}%)")
print(f"Average V1 score: {count_result.avg_v1_score}")
print(f"Average V2 score: {count_result.avg_v2_score}")

# ============================================================================
# PHASE 3: Compare V1 vs V2 Score Effectiveness
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 3: Comparing V1 vs V2 Score Effectiveness")
print("-" * 70)

# V2 Score analysis
v2_analysis = """
SELECT
    rise_cycle_score_v2 as score,
    COUNT(*) as total,
    SUM(direction_target) as ups,
    ROUND(AVG(CAST(direction_target AS FLOAT64)) * 100, 1) as up_pct
FROM `aialgotradehits.ml_models.rise_cycle_features_v2`
WHERE DATE(datetime) BETWEEN '2024-01-01' AND '2025-12-31'
GROUP BY rise_cycle_score_v2
ORDER BY rise_cycle_score_v2
"""

print("\nV2 Score Effectiveness (2024-2025 Data):")
print(f"{'V2 Score':<10} {'Total':>10} {'UP Count':>10} {'UP %':>10}")
print("-" * 45)
for row in client.query(v2_analysis).result():
    print(f"{row.score:<10} {row.total:>10,} {row.ups:>10,} {row.up_pct:>9.1f}%")

# ============================================================================
# PHASE 4: Create Optimized Signal Criteria
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 4: Testing Optimized Signal Combinations")
print("-" * 70)

# Test various signal combinations
combo_test = """
WITH signals AS (
    SELECT
        direction_target as actual,
        rise_cycle_score,
        rise_cycle_score_v2,
        ema_bullish,
        rsi_optimal_buy,
        adx_sweet_spot,
        macd_hist_rising_3d,
        rsi_rising_3d,
        volume_breakout,
        bullish_candle,
        above_sma50,
        above_sma200
    FROM `aialgotradehits.ml_models.rise_cycle_features_v2`
    WHERE DATE(datetime) BETWEEN '2024-01-01' AND '2025-12-31'
)
SELECT
    'V2 Score >= 10' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 10

UNION ALL

SELECT
    'V2 Score >= 11' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 11

UNION ALL

SELECT
    'V2 Score >= 12' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 12

UNION ALL

SELECT
    'V2>=10 + RSI_rising_3d' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 10 AND rsi_rising_3d = 1

UNION ALL

SELECT
    'V2>=10 + Vol_breakout' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 10 AND volume_breakout = 1

UNION ALL

SELECT
    'V2>=10 + MACD_rising_3d' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 10 AND macd_hist_rising_3d = 1

UNION ALL

SELECT
    'V2>=10 + ADX_sweet + RSI_opt' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score_v2 >= 10 AND adx_sweet_spot = 1 AND rsi_optimal_buy = 1

UNION ALL

SELECT
    'V1>=5 + V2>=10 + RSI_rising' as criteria,
    COUNT(*) as signals,
    SUM(actual) as ups,
    ROUND(AVG(CAST(actual AS FLOAT64)) * 100, 1) as up_pct
FROM signals WHERE rise_cycle_score >= 5 AND rise_cycle_score_v2 >= 10 AND rsi_rising_3d = 1

ORDER BY up_pct DESC
"""

print("\nSignal Combination Analysis:")
print(f"{'Criteria':<30} {'Signals':>10} {'UPs':>10} {'UP %':>10}")
print("-" * 65)
for row in client.query(combo_test).result():
    print(f"{row.criteria:<30} {row.signals:>10,} {row.ups:>10,} {row.up_pct:>9.1f}%")

# ============================================================================
# PHASE 5: Create Enhanced Signal View
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 5: Creating Enhanced Signal View")
print("-" * 70)

enhanced_view = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_rise_cycle_signals_v2` AS
WITH ranked_signals AS (
    SELECT
        symbol,
        DATE(datetime) as signal_date,
        close as current_price,
        rsi,
        macd_histogram,
        adx,
        momentum,
        rise_cycle_score,
        rise_cycle_score_v2,
        ema_bullish,
        rsi_optimal_buy,
        rsi_rising_3d,
        macd_hist_rising_3d,
        adx_sweet_spot,
        volume_breakout,
        above_sma50,
        above_sma200,
        volume_ratio,
        -- Enhanced signal logic
        CASE
            WHEN rise_cycle_score_v2 >= 12 THEN 'STRONG_BUY'
            WHEN rise_cycle_score_v2 >= 10 AND rsi_rising_3d = 1 THEN 'STRONG_BUY'
            WHEN rise_cycle_score_v2 >= 10 AND volume_breakout = 1 THEN 'STRONG_BUY'
            WHEN rise_cycle_score_v2 >= 10 THEN 'BUY'
            WHEN rise_cycle_score_v2 >= 8 AND ema_bullish = 1 THEN 'WEAK_BUY'
            ELSE 'WATCH'
        END as signal_v2,
        -- Expected UP probability based on V2 score
        CASE
            WHEN rise_cycle_score_v2 >= 12 THEN 30.0
            WHEN rise_cycle_score_v2 >= 11 THEN 25.0
            WHEN rise_cycle_score_v2 >= 10 THEN 22.0
            WHEN rise_cycle_score_v2 >= 9 THEN 18.0
            WHEN rise_cycle_score_v2 >= 8 THEN 15.0
            ELSE 10.0
        END as expected_up_pct,
        ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY rise_cycle_score_v2 DESC) as rn
    FROM `aialgotradehits.ml_models.rise_cycle_features_v2`
    WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
)
SELECT
    symbol,
    signal_date,
    current_price,
    rise_cycle_score as v1_score,
    rise_cycle_score_v2 as v2_score,
    signal_v2 as signal,
    expected_up_pct,
    CASE
        WHEN expected_up_pct >= 25 THEN 'VERY_HIGH'
        WHEN expected_up_pct >= 20 THEN 'HIGH'
        WHEN expected_up_pct >= 15 THEN 'MEDIUM'
        ELSE 'LOW'
    END as confidence,
    rsi,
    adx,
    volume_ratio,
    ema_bullish,
    rsi_rising_3d,
    macd_hist_rising_3d,
    volume_breakout,
    above_sma50,
    above_sma200
FROM ranked_signals
WHERE rn = 1
ORDER BY signal_date DESC, rise_cycle_score_v2 DESC
"""

client.query(enhanced_view).result()
print("Enhanced signal view v2 created!")

# Get current V2 signals
print("\nCurrent Enhanced Signals (V2):")
print("-" * 90)
signals = list(client.query("""
    SELECT * FROM `aialgotradehits.ml_models.v_rise_cycle_signals_v2`
    WHERE signal IN ('STRONG_BUY', 'BUY')
      AND signal_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    ORDER BY v2_score DESC, signal_date DESC
    LIMIT 20
""").result())

print(f"{'Date':<12} {'Symbol':<8} {'Price':>10} {'V1':>4} {'V2':>4} {'Signal':<12} {'Exp UP%':>8} {'RSI':>6}")
print("-" * 80)
for s in signals:
    print(f"{str(s.signal_date):<12} {s.symbol:<8} {s.current_price:>10.2f} {s.v1_score:>4} {s.v2_score:>4} {s.signal:<12} {s.expected_up_pct:>7.1f}% {s.rsi:>6.1f}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("RISE CYCLE IMPROVEMENT V2 - SUMMARY")
print("=" * 70)
print("""
Enhanced Features Added:
- RSI rising for 3 consecutive days
- MACD histogram rising for 3 consecutive days
- RSI acceleration (2nd derivative)
- ADX sweet spot (25-40)
- Volume breakout confirmation
- Bollinger Band position
- Multi-day price momentum
- Consecutive up day streaks

New V2 Score (0-15):
- Weighted scoring with bonus for confirmations
- Higher scores = more indicators aligned
- RSI optimal zone (45-60) gets extra weight
- MACD rising histogram gets extra weight
- Volume confirmation adds 2 points

Signal Rules V2:
- STRONG_BUY: V2 >= 12 OR (V2 >= 10 + RSI rising) OR (V2 >= 10 + volume breakout)
- BUY: V2 >= 10
- WEAK_BUY: V2 >= 8 + EMA bullish
""")

print(f"\nCompleted: {datetime.now()}")
print("=" * 70)
