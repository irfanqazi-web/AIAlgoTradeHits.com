-- ============================================
-- BIGQUERY SQL TEMPLATES FOR AIALGOTRADEHITS
-- NL2SQL Pattern Recognition & Growth Scoring
-- Version: 1.0 | December 2025
-- ============================================

-- ============================================
-- 1. RISE/FALL CYCLE DETECTION QUERIES
-- ============================================

-- 1.1 Daily Screening: Find cryptos with most rise/fall cycles
CREATE OR REPLACE VIEW `aialgotradehits.crypto_trading_data.v_cycle_screening` AS
SELECT 
    pair,
    date,
    close,
    open,
    volume,
    (close - open) / open * 100 as daily_change_pct,
    rsi_14,
    macd_histogram,
    adx,
    sma_9,
    sma_21,
    -- Current cycle status
    CASE WHEN sma_9 > sma_21 THEN 'RISE' ELSE 'FALL' END as current_cycle,
    -- Cycle transition signals
    CASE 
        WHEN sma_9 > sma_21 AND LAG(sma_9) OVER w <= LAG(sma_21) OVER w 
        THEN 'RISE_CYCLE_START'
        WHEN sma_9 < sma_21 AND LAG(sma_9) OVER w >= LAG(sma_21) OVER w 
        THEN 'FALL_CYCLE_START'
        ELSE 'CONTINUING'
    END as cycle_signal,
    -- Cycle duration (days in current cycle)
    SUM(CASE WHEN sma_9 > sma_21 THEN 1 ELSE 0 END) OVER (
        PARTITION BY pair ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
    ) as rise_days_30d,
    -- Growth score (0-100)
    (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score
FROM `aialgotradehits.crypto_trading_data.crypto_analysis`
WINDOW w AS (PARTITION BY pair ORDER BY date);


-- 1.2 Hourly Timing: Detect exact hour of cycle transitions
CREATE OR REPLACE VIEW `aialgotradehits.crypto_trading_data.v_hourly_cycle_timing` AS
SELECT 
    pair,
    datetime,
    close,
    volume,
    rsi_14,
    sma_9,
    sma_21,
    -- Cycle transition detection
    CASE 
        WHEN sma_9 > sma_21 AND LAG(sma_9) OVER w <= LAG(sma_21) OVER w 
        THEN 'BUY_SIGNAL'
        WHEN sma_9 < sma_21 AND LAG(sma_9) OVER w >= LAG(sma_21) OVER w 
        THEN 'SELL_SIGNAL'
        ELSE 'HOLD'
    END as trade_signal,
    -- Signal strength
    ABS(sma_9 - sma_21) / close * 100 as signal_strength,
    -- Volume confirmation
    CASE WHEN volume > LAG(volume) OVER w * 1.5 THEN TRUE ELSE FALSE END as volume_confirmed
FROM `aialgotradehits.crypto_trading_data.crypto_hourly_data`
WINDOW w AS (PARTITION BY pair ORDER BY datetime);


-- 1.3 5-Minute Execution: Real-time trade signals
CREATE OR REPLACE VIEW `aialgotradehits.crypto_trading_data.v_5min_trade_signals` AS
SELECT 
    pair,
    datetime,
    close,
    volume,
    rsi_14,
    macd_histogram,
    adx,
    sma_9,
    sma_21,
    -- Trade action with multiple conditions
    CASE 
        WHEN sma_9 > sma_21 
            AND rsi_14 > 50 
            AND rsi_14 < 70
            AND macd_histogram > 0
            AND volume > LAG(volume) OVER w
        THEN 'STRONG_BUY'
        WHEN sma_9 > sma_21 AND rsi_14 > 50 
        THEN 'BUY'
        WHEN sma_9 < sma_21 AND rsi_14 < 50
        THEN 'SELL'
        WHEN rsi_14 > 75
        THEN 'TAKE_PROFIT'
        WHEN rsi_14 < 25
        THEN 'STOP_LOSS_RISK'
        ELSE 'HOLD'
    END as trade_action,
    -- Confidence level (0-100)
    (CASE WHEN sma_9 > sma_21 THEN 20 ELSE 0 END +
     CASE WHEN rsi_14 BETWEEN 40 AND 60 THEN 20 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 20 ELSE 0 END +
     CASE WHEN adx > 25 THEN 20 ELSE 0 END +
     CASE WHEN volume > LAG(volume) OVER w THEN 20 ELSE 0 END) as confidence_level
FROM `aialgotradehits.crypto_trading_data.crypto_5min_top10_gainers`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
WINDOW w AS (PARTITION BY pair ORDER BY datetime);


-- ============================================
-- 2. GOLDEN CROSS / DEATH CROSS DETECTION
-- ============================================

-- 2.1 Daily Golden/Death Cross Scanner
CREATE OR REPLACE VIEW `aialgotradehits.crypto_trading_data.v_ma_crossovers` AS
SELECT 
    pair,
    date,
    close,
    sma_50,
    sma_200,
    volume,
    -- Current MA relationship
    CASE WHEN sma_50 > sma_200 THEN 'BULLISH' ELSE 'BEARISH' END as ma_trend,
    -- Crossover detection
    CASE 
        WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w 
        THEN 'GOLDEN_CROSS'
        WHEN sma_50 < sma_200 AND LAG(sma_50) OVER w >= LAG(sma_200) OVER w 
        THEN 'DEATH_CROSS'
        ELSE NULL
    END as crossover_signal,
    -- Distance between MAs (trend strength indicator)
    (sma_50 - sma_200) / sma_200 * 100 as ma_spread_pct,
    -- Days since last crossover
    DATE_DIFF(date, 
        LAST_VALUE(CASE 
            WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w THEN date
            WHEN sma_50 < sma_200 AND LAG(sma_50) OVER w >= LAG(sma_200) OVER w THEN date
        END IGNORE NULLS) OVER w2, DAY
    ) as days_since_crossover
FROM `aialgotradehits.crypto_trading_data.crypto_analysis`
WINDOW 
    w AS (PARTITION BY pair ORDER BY date),
    w2 AS (PARTITION BY pair ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW);


-- ============================================
-- 3. PATTERN RECOGNITION SQL TEMPLATES
-- ============================================

-- 3.1 Enhanced Training Features Table with Pattern Flags
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.training_features_enhanced` AS
SELECT 
    *,
    -- Momentum Features
    (close - LAG(close, 1) OVER w) / NULLIF(LAG(close, 1) OVER w, 0) * 100 as momentum_1d,
    (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
    (close - LAG(close, 20) OVER w) / NULLIF(LAG(close, 20) OVER w, 0) * 100 as momentum_20d,
    
    -- Rise Cycle Features
    CASE WHEN sma_9 > sma_21 THEN 1 ELSE 0 END as in_rise_cycle,
    CASE WHEN sma_9 > sma_21 AND LAG(sma_9) OVER w <= LAG(sma_21) OVER w THEN 1 ELSE 0 END as rise_cycle_start,
    CASE WHEN sma_9 < sma_21 AND LAG(sma_9) OVER w >= LAG(sma_21) OVER w THEN 1 ELSE 0 END as fall_cycle_start,
    
    -- Trend Regime
    CASE 
        WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
        WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_DOWNTREND'
        WHEN close > sma_200 THEN 'WEAK_UPTREND'
        WHEN close < sma_200 THEN 'WEAK_DOWNTREND'
        ELSE 'CONSOLIDATION' 
    END as trend_regime,
    
    -- Growth Pattern Score (0-100)
    (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,
     
    -- Volatility Features
    atr / close * 100 as atr_pct,
    (bb_upper - bb_lower) / close * 100 as bb_width_pct,
    (close - bb_lower) / NULLIF(bb_upper - bb_lower, 0) as bb_position,
    
    -- Volume Features
    volume / NULLIF(AVG(volume) OVER (PARTITION BY pair ORDER BY date ROWS 20 PRECEDING), 0) as volume_ratio,
    
    -- Swing Detection (for pattern recognition)
    CASE WHEN high > LAG(high) OVER w AND high > LEAD(high) OVER w THEN 1 ELSE 0 END as is_swing_high,
    CASE WHEN low < LAG(low) OVER w AND low < LEAD(low) OVER w THEN 1 ELSE 0 END as is_swing_low,
    
    -- Higher Highs / Lower Lows
    CASE WHEN high > MAX(high) OVER (PARTITION BY pair ORDER BY date ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) 
         THEN 1 ELSE 0 END as higher_high,
    CASE WHEN low < MIN(low) OVER (PARTITION BY pair ORDER BY date ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) 
         THEN 1 ELSE 0 END as lower_low,
         
    -- Target Variable (next day direction)
    CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction,
    (LEAD(close, 1) OVER w - close) / close * 100 as target_return_pct
    
FROM `aialgotradehits.crypto_trading_data.crypto_analysis`
WINDOW w AS (PARTITION BY pair ORDER BY date);


-- 3.2 Pattern Detection Query Template
-- (Use this with NL2SQL when user asks for patterns)
SELECT 
    symbol,
    date,
    close,
    rsi_14,
    adx,
    -- Pattern flags (populated by separate detection process)
    pattern_head_shoulders,
    pattern_double_top,
    pattern_double_bottom,
    pattern_ascending_triangle,
    pattern_descending_triangle,
    pattern_bull_flag,
    pattern_falling_wedge,
    pattern_confidence,
    -- Trading implication
    CASE 
        WHEN pattern_double_bottom OR pattern_inverse_head_shoulders 
            OR pattern_ascending_triangle OR pattern_falling_wedge
        THEN 'BULLISH'
        WHEN pattern_double_top OR pattern_head_shoulders 
            OR pattern_descending_triangle OR pattern_rising_wedge
        THEN 'BEARISH'
        ELSE 'NEUTRAL'
    END as pattern_bias,
    -- Combined signal
    CASE 
        WHEN pattern_double_bottom AND rsi_14 < 40 AND adx > 20 THEN 'STRONG_BUY'
        WHEN pattern_ascending_triangle AND rsi_14 BETWEEN 40 AND 60 THEN 'BUY'
        WHEN pattern_double_top AND rsi_14 > 60 THEN 'SELL'
        ELSE 'WATCH'
    END as combined_signal
FROM `aialgotradehits.crypto_trading_data.stock_analysis`
WHERE DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND pattern_confidence >= 0.7
ORDER BY pattern_confidence DESC, date DESC;


-- ============================================
-- 4. NL2SQL EXAMPLE QUERIES
-- ============================================

-- 4.1 "Show me oversold cryptos with high volume"
SELECT 
    pair,
    date,
    close,
    rsi_14,
    volume,
    macd_histogram,
    CASE WHEN sma_9 > sma_21 THEN 'RISE' ELSE 'FALL' END as cycle
FROM `aialgotradehits.crypto_trading_data.crypto_analysis`
WHERE DATE(date) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    AND rsi_14 < 30
    AND volume > (SELECT AVG(volume) * 1.5 FROM `aialgotradehits.crypto_trading_data.crypto_analysis`)
ORDER BY rsi_14 ASC
LIMIT 20;


-- 4.2 "Cryptos starting a rise cycle"
SELECT 
    pair,
    date,
    close,
    sma_9,
    sma_21,
    rsi_14,
    volume,
    'RISE_CYCLE_START' as signal
FROM `aialgotradehits.crypto_trading_data.crypto_analysis` t1
WHERE DATE(date) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    AND sma_9 > sma_21
    AND (
        SELECT sma_9 <= sma_21 
        FROM `aialgotradehits.crypto_trading_data.crypto_analysis` t2 
        WHERE t2.pair = t1.pair 
        AND t2.date = DATE_SUB(t1.date, INTERVAL 1 DAY)
    )
ORDER BY (sma_9 - sma_21) / sma_21 DESC
LIMIT 20;


-- 4.3 "Top 10 stocks with ascending triangle pattern"
SELECT 
    symbol,
    date,
    close,
    pattern_ascending_triangle,
    pattern_confidence,
    rsi_14,
    adx,
    volume,
    'BULLISH_CONTINUATION' as pattern_implication
FROM `aialgotradehits.crypto_trading_data.stock_analysis`
WHERE DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    AND pattern_ascending_triangle = TRUE
    AND pattern_confidence >= 0.7
ORDER BY pattern_confidence DESC, date DESC
LIMIT 10;


-- 4.4 "Golden cross stocks this week"
WITH crossover_detection AS (
    SELECT 
        symbol,
        date,
        close,
        sma_50,
        sma_200,
        volume,
        CASE 
            WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w 
            THEN TRUE ELSE FALSE 
        END as golden_cross
    FROM `aialgotradehits.crypto_trading_data.stock_analysis`
    WHERE DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    WINDOW w AS (PARTITION BY symbol ORDER BY date)
)
SELECT 
    symbol,
    date as golden_cross_date,
    close,
    sma_50,
    sma_200,
    volume,
    (sma_50 - sma_200) / sma_200 * 100 as ma_spread_pct
FROM crossover_detection
WHERE golden_cross = TRUE
ORDER BY date DESC;


-- 4.5 "High growth momentum stocks with strong trend"
SELECT 
    symbol,
    date,
    close,
    rsi_14,
    macd_histogram,
    adx,
    sma_200,
    -- Calculate growth score
    (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,
    -- Trend classification
    CASE 
        WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
        ELSE 'MODERATE'
    END as trend_status
FROM `aialgotradehits.crypto_trading_data.stock_analysis`
WHERE DATE(date) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    AND adx > 25  -- Strong trend
    AND rsi_14 BETWEEN 50 AND 70  -- Bullish but not overbought
    AND macd_histogram > 0  -- Bullish MACD
    AND close > sma_200  -- Above long-term MA
ORDER BY 
    (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_200 THEN 25 ELSE 0 END) DESC
LIMIT 20;


-- ============================================
-- 5. BIGQUERY ML MODEL TRAINING
-- ============================================

-- 5.1 Create Direction Prediction Model
CREATE OR REPLACE MODEL `aialgotradehits.ml_models.direction_predictor_v1`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['target_direction'],
    max_iterations=100,
    early_stop=TRUE,
    data_split_method='AUTO_SPLIT',
    enable_global_explain=TRUE
) AS
SELECT 
    rsi_14,
    macd_histogram,
    adx,
    bb_position,
    volume_ratio,
    in_rise_cycle,
    momentum_5d,
    atr_pct,
    growth_score,
    target_direction
FROM `aialgotradehits.ml_models.training_features_enhanced`
WHERE target_direction IS NOT NULL
    AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 YEAR);


-- 5.2 Make Predictions
SELECT 
    pair,
    date,
    close,
    predicted_target_direction as predicted_direction,
    predicted_target_direction_probs[OFFSET(1)].prob as up_probability,
    growth_score,
    CASE 
        WHEN predicted_target_direction_probs[OFFSET(1)].prob > 0.65 THEN 'STRONG_BUY'
        WHEN predicted_target_direction_probs[OFFSET(1)].prob > 0.55 THEN 'BUY'
        WHEN predicted_target_direction_probs[OFFSET(1)].prob < 0.35 THEN 'SELL'
        ELSE 'HOLD'
    END as trade_recommendation
FROM ML.PREDICT(
    MODEL `aialgotradehits.ml_models.direction_predictor_v1`,
    (SELECT * FROM `aialgotradehits.ml_models.training_features_enhanced`
     WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
)
ORDER BY predicted_target_direction_probs[OFFSET(1)].prob DESC
LIMIT 20;


-- ============================================
-- 6. STORED PROCEDURES FOR NL2SQL
-- ============================================

-- 6.1 Procedure: Get Rise Cycle Candidates
CREATE OR REPLACE PROCEDURE `aialgotradehits.procedures.get_rise_cycle_candidates`(
    IN market_type STRING,
    IN min_rsi FLOAT64,
    IN max_rsi FLOAT64,
    IN min_adx FLOAT64,
    IN result_limit INT64
)
BEGIN
    DECLARE table_name STRING;
    DECLARE symbol_field STRING;
    
    IF market_type = 'crypto' THEN
        SET table_name = 'crypto_analysis';
        SET symbol_field = 'pair';
    ELSE
        SET table_name = 'stock_analysis';
        SET symbol_field = 'symbol';
    END IF;
    
    EXECUTE IMMEDIATE FORMAT("""
        SELECT 
            %s as symbol,
            date,
            close,
            sma_9,
            sma_21,
            rsi_14,
            adx,
            volume,
            CASE 
                WHEN sma_9 > sma_21 AND LAG(sma_9) OVER w <= LAG(sma_21) OVER w 
                THEN 'RISE_CYCLE_START'
                WHEN sma_9 > sma_21 THEN 'RISE_CYCLE'
                ELSE 'FALL_CYCLE'
            END as cycle_status
        FROM `aialgotradehits.crypto_trading_data.%s`
        WHERE DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            AND rsi_14 BETWEEN %f AND %f
            AND adx >= %f
        WINDOW w AS (PARTITION BY %s ORDER BY date)
        ORDER BY date DESC
        LIMIT %d
    """, symbol_field, table_name, min_rsi, max_rsi, min_adx, symbol_field, result_limit);
END;


-- Example call:
-- CALL `aialgotradehits.procedures.get_rise_cycle_candidates`('crypto', 30.0, 70.0, 20.0, 20);
