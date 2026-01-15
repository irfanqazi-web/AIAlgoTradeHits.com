"""
Walk-Forward Validation Model v2 - All Assets
==============================================
Uses only common columns across stocks, crypto, and ETFs

Author: Claude Code
Date: January 2026
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import datetime
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 80)
print("WALK-FORWARD VALIDATION MODEL v2 - ALL ASSETS")
print("=" * 80)
print(f"Started: {datetime.now()}")

# ============================================================================
# STEP 1: CREATE FEATURE TABLE WITH ONLY COMMON COLUMNS
# ============================================================================

def create_feature_table():
    """Create unified feature table using only common columns"""
    print("\n" + "-" * 60)
    print("STEP 1: CREATING UNIFIED FEATURE TABLE")
    print("-" * 60)

    # Using ONLY columns that exist in all 3 tables
    feature_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2` AS

    WITH combined_data AS (
        -- Stocks
        SELECT
            'stocks' as asset_type,
            symbol, datetime, open, high, low, close, volume,
            rsi, macd, macd_histogram, macd_signal,
            sma_20, sma_50, sma_200, ema_12, ema_20, ema_26, ema_50, ema_200,
            atr, adx, plus_di, minus_di, mfi, cmf,
            stoch_k, stoch_d, cci, roc, obv, volume_ratio,
            bollinger_lower
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE datetime IS NOT NULL AND close > 0

        UNION ALL

        -- Crypto
        SELECT
            'crypto' as asset_type,
            symbol, datetime, open, high, low, close, volume,
            rsi, macd, macd_histogram, macd_signal,
            sma_20, sma_50, sma_200, ema_12, ema_20, ema_26, ema_50, ema_200,
            atr, adx, plus_di, minus_di, mfi, cmf,
            stoch_k, stoch_d, cci, roc, obv, volume_ratio,
            bollinger_lower
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
        WHERE datetime IS NOT NULL AND close > 0

        UNION ALL

        -- ETFs
        SELECT
            'etf' as asset_type,
            symbol, datetime, open, high, low, close, volume,
            rsi, macd, macd_histogram, macd_signal,
            sma_20, sma_50, sma_200, ema_12, ema_20, ema_26, ema_50, ema_200,
            atr, adx, plus_di, minus_di, mfi, cmf,
            stoch_k, stoch_d, cci, roc, obv, volume_ratio,
            bollinger_lower
        FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
        WHERE datetime IS NOT NULL AND close > 0
    ),

    with_features AS (
        SELECT
            asset_type, symbol, datetime, open, high, low, close, volume,

            -- Core indicators (cleaned)
            COALESCE(rsi, 50) as rsi,
            COALESCE(macd_histogram, 0) as macd_histogram,
            COALESCE(adx, 0) as adx,
            COALESCE(plus_di, 0) as plus_di,
            COALESCE(minus_di, 0) as minus_di,
            COALESCE(mfi, 50) as mfi,
            COALESCE(cci, 0) as cci,
            COALESCE(stoch_k, 50) as stoch_k,
            COALESCE(stoch_d, 50) as stoch_d,
            COALESCE(roc, 0) as roc,
            COALESCE(atr, 0) as atr,
            CASE
                WHEN volume_ratio IS NULL OR IS_NAN(volume_ratio) OR IS_INF(volume_ratio)
                THEN 1.0
                ELSE volume_ratio
            END as volume_ratio_clean,

            -- EMA trend indicators
            COALESCE(ema_12, close) as ema_12,
            COALESCE(ema_26, close) as ema_26,
            COALESCE(ema_50, close) as ema_50,
            COALESCE(ema_200, close) as ema_200,
            COALESCE(sma_50, close) as sma_50,
            COALESCE(sma_200, close) as sma_200,

            -- RSI features (derived)
            COALESCE(rsi, 50) - LAG(COALESCE(rsi, 50), 1) OVER w as rsi_slope,
            CASE WHEN COALESCE(rsi, 50) > 70 THEN 1 ELSE 0 END as rsi_overbought,
            CASE WHEN COALESCE(rsi, 50) < 30 THEN 1 ELSE 0 END as rsi_oversold,

            -- MACD features
            CASE WHEN COALESCE(macd_histogram, 0) > LAG(COALESCE(macd_histogram, 0), 1) OVER w THEN 1 ELSE 0 END as macd_rising,
            CASE WHEN COALESCE(macd_histogram, 0) > 0 AND LAG(COALESCE(macd_histogram, 0), 1) OVER w <= 0 THEN 1 ELSE 0 END as macd_cross_up,

            -- Pivot detection (Saleem's key feature - 25% importance each)
            CASE WHEN high > LAG(high, 1) OVER w AND high > LAG(high, 2) OVER w
                  AND high > LEAD(high, 1) OVER w AND high > LEAD(high, 2) OVER w
            THEN 1 ELSE 0 END as pivot_high_flag,

            CASE WHEN low < LAG(low, 1) OVER w AND low < LAG(low, 2) OVER w
                  AND low < LEAD(low, 1) OVER w AND low < LEAD(low, 2) OVER w
            THEN 1 ELSE 0 END as pivot_low_flag,

            -- EMA Cycle Detection (calculated from raw EMAs)
            CASE WHEN COALESCE(ema_12, close) > COALESCE(ema_26, close) THEN 1 ELSE 0 END as in_rise_cycle,
            CASE WHEN COALESCE(ema_12, close) > COALESCE(ema_26, close)
                  AND LAG(COALESCE(ema_12, close), 1) OVER w <= LAG(COALESCE(ema_26, close), 1) OVER w
            THEN 1 ELSE 0 END as rise_cycle_start,

            -- Golden/Death Cross
            CASE WHEN COALESCE(sma_50, close) > COALESCE(sma_200, close)
                  AND LAG(COALESCE(sma_50, close), 1) OVER w <= LAG(COALESCE(sma_200, close), 1) OVER w
            THEN 1 ELSE 0 END as golden_cross,

            CASE WHEN COALESCE(sma_50, close) < COALESCE(sma_200, close)
                  AND LAG(COALESCE(sma_50, close), 1) OVER w >= LAG(COALESCE(sma_200, close), 1) OVER w
            THEN 1 ELSE 0 END as death_cross,

            -- Growth Score (calculated per masterquery.md spec)
            (CASE WHEN COALESCE(rsi, 50) BETWEEN 50 AND 70 THEN 25 ELSE 0 END) +
            (CASE WHEN COALESCE(macd_histogram, 0) > 0 THEN 25 ELSE 0 END) +
            (CASE WHEN COALESCE(adx, 0) > 25 THEN 25 ELSE 0 END) +
            (CASE WHEN close > COALESCE(sma_200, close * 0.9) THEN 25 ELSE 0 END) as growth_score,

            -- Trend Regime (calculated)
            CASE
                WHEN close > COALESCE(sma_50, close) AND COALESCE(sma_50, close) > COALESCE(sma_200, close) AND COALESCE(adx, 0) > 25 THEN 'STRONG_UPTREND'
                WHEN close > COALESCE(sma_50, close) AND close > COALESCE(sma_200, close) THEN 'WEAK_UPTREND'
                WHEN close < COALESCE(sma_50, close) AND COALESCE(sma_50, close) < COALESCE(sma_200, close) AND COALESCE(adx, 0) > 25 THEN 'STRONG_DOWNTREND'
                WHEN close < COALESCE(sma_50, close) AND close < COALESCE(sma_200, close) THEN 'WEAK_DOWNTREND'
                ELSE 'CONSOLIDATION'
            END as trend_regime,

            -- Momentum features
            (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
            (close - LAG(close, 10) OVER w) / NULLIF(LAG(close, 10) OVER w, 0) * 100 as momentum_10d,
            (close - LAG(close, 20) OVER w) / NULLIF(LAG(close, 20) OVER w, 0) * 100 as momentum_20d,

            -- Volatility
            COALESCE(atr, 0) / NULLIF(close, 0) * 100 as atr_pct,

            -- Target: next day direction (1 = UP, 0 = DOWN)
            CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction,

            -- Walk-forward split markers
            CASE
                WHEN DATE(datetime) <= '2022-12-31' THEN 'TRAIN'
                WHEN DATE(datetime) <= '2023-12-31' THEN 'TEST'
                ELSE 'VALIDATE'
            END as data_split

        FROM combined_data
        WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    )

    SELECT * FROM with_features
    WHERE target_direction IS NOT NULL
      AND rsi IS NOT NULL
      AND close > 0
    """

    try:
        print("  Creating feature table (this may take 2-3 minutes)...")
        job = bq_client.query(feature_sql)
        job.result()

        # Get counts
        count_query = f"""
        SELECT
            data_split,
            COUNT(*) as records,
            COUNT(DISTINCT symbol) as symbols,
            COUNT(DISTINCT asset_type) as asset_types,
            MIN(DATE(datetime)) as start_date,
            MAX(DATE(datetime)) as end_date
        FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2`
        GROUP BY data_split
        ORDER BY MIN(datetime)
        """
        df = bq_client.query(count_query).to_dataframe()

        print("\n  Walk-Forward Data Splits:")
        for _, row in df.iterrows():
            print(f"    {row['data_split']:10} | {row['start_date']} to {row['end_date']} | {row['records']:,} records | {row['symbols']} symbols")

        total = df['records'].sum()
        print(f"\n    Total: {total:,} records across all assets")

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# STEP 2: TRAIN XGBOOST MODEL
# ============================================================================

def train_model():
    """Train XGBoost classifier using walk-forward methodology"""
    print("\n" + "-" * 60)
    print("STEP 2: TRAINING XGBOOST MODEL")
    print("-" * 60)

    train_sql = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward_v2`
    OPTIONS(
        model_type='BOOSTED_TREE_CLASSIFIER',
        input_label_cols=['target_direction'],
        max_iterations=200,
        num_parallel_tree=2,
        max_tree_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        learn_rate=0.05,
        early_stop=TRUE,
        data_split_method='NO_SPLIT',
        auto_class_weights=TRUE
    ) AS
    SELECT
        -- RSI features
        rsi,
        COALESCE(rsi_slope, 0) as rsi_slope,
        rsi_overbought,
        rsi_oversold,

        -- MACD features
        macd_histogram,
        macd_rising,
        macd_cross_up,

        -- Pivot detection (KEY - Saleem's 25% importance each)
        pivot_high_flag,
        pivot_low_flag,

        -- Trend indicators
        adx,
        plus_di,
        minus_di,
        in_rise_cycle,
        rise_cycle_start,
        golden_cross,
        death_cross,

        -- Momentum features
        COALESCE(momentum_5d, 0) as momentum_5d,
        COALESCE(momentum_10d, 0) as momentum_10d,
        COALESCE(momentum_20d, 0) as momentum_20d,

        -- Volatility & Volume
        COALESCE(atr_pct, 0) as atr_pct,
        COALESCE(volume_ratio_clean, 1) as volume_ratio,

        -- Oscillators
        mfi,
        cci,
        stoch_k,
        stoch_d,
        roc,

        -- Growth Score
        growth_score,

        -- Feature interactions (proven to improve accuracy)
        rsi * COALESCE(volume_ratio_clean, 1) as rsi_volume_interaction,
        macd_histogram * COALESCE(atr_pct, 0) as macd_atr_interaction,
        adx * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction,

        -- Target
        target_direction

    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2`
    WHERE data_split = 'TRAIN'
      AND target_direction IS NOT NULL
    """

    print("  Training on data up to Dec 31, 2022...")
    print("  This may take 10-15 minutes for 6M+ records...")

    try:
        start_time = datetime.now()
        job = bq_client.query(train_sql)
        job.result()
        elapsed = (datetime.now() - start_time).seconds

        print(f"  Training completed in {elapsed // 60}m {elapsed % 60}s")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# STEP 3: EVALUATE ON TEST DATA (2023)
# ============================================================================

def evaluate_test():
    """Evaluate model on 2023 test data"""
    print("\n" + "-" * 60)
    print("STEP 3: EVALUATING ON TEST DATA (2023)")
    print("-" * 60)

    eval_sql = f"""
    SELECT *
    FROM ML.EVALUATE(
        MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward_v2`,
        (
            SELECT
                rsi, COALESCE(rsi_slope, 0) as rsi_slope, rsi_overbought, rsi_oversold,
                macd_histogram, macd_rising, macd_cross_up,
                pivot_high_flag, pivot_low_flag,
                adx, plus_di, minus_di, in_rise_cycle, rise_cycle_start, golden_cross, death_cross,
                COALESCE(momentum_5d, 0) as momentum_5d, COALESCE(momentum_10d, 0) as momentum_10d,
                COALESCE(momentum_20d, 0) as momentum_20d,
                COALESCE(atr_pct, 0) as atr_pct, volume_ratio_clean as volume_ratio,
                mfi, cci, stoch_k, stoch_d, roc, growth_score,
                rsi * COALESCE(volume_ratio_clean, 1) as rsi_volume_interaction,
                macd_histogram * COALESCE(atr_pct, 0) as macd_atr_interaction,
                adx * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction,
                target_direction
            FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2`
            WHERE data_split = 'TEST'
        )
    )
    """

    try:
        df = bq_client.query(eval_sql).to_dataframe()
        print("\n  TEST Performance (2023 - Walk Forward):")
        for col in df.columns:
            val = df[col].iloc[0]
            if isinstance(val, float):
                print(f"    {col}: {val:.4f}")
            else:
                print(f"    {col}: {val}")

        accuracy = df['accuracy'].iloc[0] if 'accuracy' in df.columns else 0
        return accuracy
    except Exception as e:
        print(f"  Error: {e}")
        return 0


# ============================================================================
# STEP 4: EVALUATE ON VALIDATION DATA (2024-2025)
# ============================================================================

def evaluate_validation():
    """Evaluate model on 2024-2025 validation data"""
    print("\n" + "-" * 60)
    print("STEP 4: EVALUATING ON VALIDATION DATA (2024-2025)")
    print("-" * 60)

    eval_sql = f"""
    SELECT *
    FROM ML.EVALUATE(
        MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward_v2`,
        (
            SELECT
                rsi, COALESCE(rsi_slope, 0) as rsi_slope, rsi_overbought, rsi_oversold,
                macd_histogram, macd_rising, macd_cross_up,
                pivot_high_flag, pivot_low_flag,
                adx, plus_di, minus_di, in_rise_cycle, rise_cycle_start, golden_cross, death_cross,
                COALESCE(momentum_5d, 0) as momentum_5d, COALESCE(momentum_10d, 0) as momentum_10d,
                COALESCE(momentum_20d, 0) as momentum_20d,
                COALESCE(atr_pct, 0) as atr_pct, volume_ratio_clean as volume_ratio,
                mfi, cci, stoch_k, stoch_d, roc, growth_score,
                rsi * COALESCE(volume_ratio_clean, 1) as rsi_volume_interaction,
                macd_histogram * COALESCE(atr_pct, 0) as macd_atr_interaction,
                adx * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction,
                target_direction
            FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2`
            WHERE data_split = 'VALIDATE'
        )
    )
    """

    try:
        df = bq_client.query(eval_sql).to_dataframe()
        print("\n  VALIDATION Performance (2024-2025):")
        for col in df.columns:
            val = df[col].iloc[0]
            if isinstance(val, float):
                print(f"    {col}: {val:.4f}")
            else:
                print(f"    {col}: {val}")

        accuracy = df['accuracy'].iloc[0] if 'accuracy' in df.columns else 0
        return accuracy
    except Exception as e:
        print(f"  Error: {e}")
        return 0


# ============================================================================
# STEP 5: CREATE PREDICTIONS TABLE
# ============================================================================

def create_predictions():
    """Generate predictions for test and validation periods"""
    print("\n" + "-" * 60)
    print("STEP 5: GENERATING PREDICTIONS")
    print("-" * 60)

    pred_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2` AS

    SELECT
        f.asset_type,
        f.symbol,
        f.datetime,
        f.close,
        f.rsi,
        f.macd_histogram,
        f.adx,
        f.growth_score,
        f.in_rise_cycle,
        f.rise_cycle_start,
        f.pivot_high_flag,
        f.pivot_low_flag,
        f.golden_cross,
        f.trend_regime,
        f.target_direction as actual_direction,
        f.data_split,
        p.predicted_target_direction as predicted_direction,
        CASE
            WHEN ARRAY_LENGTH(p.predicted_target_direction_probs) > 1
            THEN p.predicted_target_direction_probs[OFFSET(1)].prob
            ELSE p.predicted_target_direction_probs[OFFSET(0)].prob
        END as up_probability
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2` f
    LEFT JOIN (
        SELECT *
        FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward_v2`,
            (SELECT
                symbol, datetime,
                rsi, COALESCE(rsi_slope, 0) as rsi_slope, rsi_overbought, rsi_oversold,
                macd_histogram, macd_rising, macd_cross_up,
                pivot_high_flag, pivot_low_flag,
                adx, plus_di, minus_di, in_rise_cycle, rise_cycle_start, golden_cross, death_cross,
                COALESCE(momentum_5d, 0) as momentum_5d, COALESCE(momentum_10d, 0) as momentum_10d,
                COALESCE(momentum_20d, 0) as momentum_20d,
                COALESCE(atr_pct, 0) as atr_pct, volume_ratio_clean as volume_ratio,
                mfi, cci, stoch_k, stoch_d, roc, growth_score,
                rsi * COALESCE(volume_ratio_clean, 1) as rsi_volume_interaction,
                macd_histogram * COALESCE(atr_pct, 0) as macd_atr_interaction,
                adx * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction
            FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_v2`
            WHERE data_split IN ('TEST', 'VALIDATE'))
        )
    ) p
    ON f.symbol = p.symbol AND f.datetime = p.datetime
    WHERE f.data_split IN ('TEST', 'VALIDATE')
    """

    try:
        print("  Generating predictions for 2023-2025...")
        job = bq_client.query(pred_sql)
        job.result()

        # Summary
        summary_sql = f"""
        SELECT
            data_split,
            asset_type,
            COUNT(*) as total,
            SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct,
            ROUND(SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy
        FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
        GROUP BY data_split, asset_type
        ORDER BY data_split, asset_type
        """

        df = bq_client.query(summary_sql).to_dataframe()
        print("\n  Accuracy by Split and Asset Type:")
        for split in df['data_split'].unique():
            print(f"\n  {split}:")
            split_df = df[df['data_split'] == split]
            for _, row in split_df.iterrows():
                print(f"    {row['asset_type']:8} | {row['accuracy']:6.2f}% | {row['correct']:,}/{row['total']:,}")

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# STEP 6: ANALYZE CONFIDENCE LEVELS
# ============================================================================

def analyze_confidence():
    """Analyze accuracy by confidence level"""
    print("\n" + "-" * 60)
    print("STEP 6: ACCURACY BY CONFIDENCE LEVEL")
    print("-" * 60)

    conf_sql = f"""
    SELECT
        data_split,
        CASE
            WHEN up_probability >= 0.65 OR up_probability <= 0.35 THEN 'HIGH'
            WHEN up_probability >= 0.55 OR up_probability <= 0.45 THEN 'MEDIUM'
            ELSE 'LOW'
        END as confidence_level,
        COUNT(*) as predictions,
        SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct,
        ROUND(SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    GROUP BY 1, 2
    ORDER BY 1, 2
    """

    try:
        df = bq_client.query(conf_sql).to_dataframe()
        print("\n  Accuracy by Confidence Level:")
        for split in df['data_split'].unique():
            print(f"\n  {split}:")
            split_df = df[df['data_split'] == split]
            for _, row in split_df.iterrows():
                print(f"    {row['confidence_level']:8} | {row['accuracy']:6.2f}% | {row['correct']:,}/{row['predictions']:,} predictions")

        return df
    except Exception as e:
        print(f"  Error: {e}")
        return None


# ============================================================================
# STEP 7: CREATE PRODUCTION VIEW
# ============================================================================

def create_production_view():
    """Create view for production trading signals"""
    print("\n" + "-" * 60)
    print("STEP 7: CREATING PRODUCTION VIEW")
    print("-" * 60)

    view_sql = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_walk_forward_signals_v2` AS

    SELECT
        asset_type,
        symbol,
        datetime,
        close as price,
        rsi,
        macd_histogram,
        adx,
        growth_score,
        in_rise_cycle,
        rise_cycle_start,
        pivot_high_flag,
        pivot_low_flag,
        golden_cross,
        trend_regime,
        predicted_direction,
        up_probability,
        ROUND(up_probability * 100, 1) as up_probability_pct,

        -- Confidence level
        CASE
            WHEN up_probability >= 0.65 OR up_probability <= 0.35 THEN 'HIGH'
            WHEN up_probability >= 0.55 OR up_probability <= 0.45 THEN 'MEDIUM'
            ELSE 'LOW'
        END as confidence_level,

        -- Trade recommendation
        CASE
            WHEN up_probability >= 0.70 AND growth_score >= 75 AND in_rise_cycle = 1 THEN 'STRONG_BUY'
            WHEN up_probability >= 0.60 AND growth_score >= 50 THEN 'BUY'
            WHEN up_probability <= 0.30 AND growth_score <= 25 THEN 'STRONG_SELL'
            WHEN up_probability <= 0.40 AND growth_score <= 50 THEN 'SELL'
            ELSE 'HOLD'
        END as trade_recommendation,

        -- Key factors
        CONCAT(
            CASE WHEN rsi < 30 THEN 'Oversold, ' WHEN rsi > 70 THEN 'Overbought, ' ELSE '' END,
            CASE WHEN rise_cycle_start = 1 THEN 'Rise Cycle Start, ' ELSE '' END,
            CASE WHEN pivot_low_flag = 1 THEN 'Pivot Low, ' ELSE '' END,
            CASE WHEN pivot_high_flag = 1 THEN 'Pivot High, ' ELSE '' END,
            CASE WHEN golden_cross = 1 THEN 'Golden Cross, ' ELSE '' END,
            trend_regime
        ) as key_factors

    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
    """

    try:
        bq_client.query(view_sql).result()
        print("  Created: v_walk_forward_signals_v2")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run complete walk-forward validation"""

    print("\n" + "=" * 80)
    print("STARTING WALK-FORWARD VALIDATION")
    print("=" * 80)
    print("""
Methodology:
  - Training: Earliest data to Dec 31, 2022 (walk backward)
  - Testing: Jan 1, 2023 to Dec 31, 2023 (walk forward day by day)
  - Validation: Jan 1, 2024 to present (continuous validation)

Asset Types: Stocks, Crypto, ETFs
Features: 28 features including Saleem's pivot detection
""")

    # Step 1: Create features
    if not create_feature_table():
        return

    # Step 2: Train model
    if not train_model():
        return

    # Step 3: Test on 2023
    test_acc = evaluate_test()

    # Step 4: Validate on 2024-2025
    val_acc = evaluate_validation()

    # Step 5: Create predictions
    create_predictions()

    # Step 6: Analyze confidence
    analyze_confidence()

    # Step 7: Create production view
    create_production_view()

    # Summary
    print("\n" + "=" * 80)
    print("WALK-FORWARD VALIDATION COMPLETE")
    print("=" * 80)
    print(f"""
MODEL: xgboost_walk_forward_v2
TRAINING: Earliest data to Dec 31, 2022
TESTING (2023): {test_acc*100:.2f}% accuracy
VALIDATION (2024-2025): {val_acc*100:.2f}% accuracy

TABLES CREATED:
  - {ML_DATASET}.walk_forward_features_v2
  - {ML_DATASET}.walk_forward_predictions_v2
  - {ML_DATASET}.v_walk_forward_signals_v2

QUERY FOR HIGH CONFIDENCE SIGNALS:
  SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.v_walk_forward_signals_v2`
  WHERE confidence_level = 'HIGH'
    AND trade_recommendation IN ('BUY', 'STRONG_BUY')
  ORDER BY datetime DESC
  LIMIT 50;

Completed: {datetime.now()}
""")


if __name__ == "__main__":
    main()
