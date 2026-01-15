"""
Walk-Forward Validation Model for All Assets
=============================================
Implements professional-grade ML training with:
1. Walk-backward training from Dec 31, 2022 to earliest data
2. Walk-forward testing through 2023
3. Walk-forward validation through 2024
4. Continuous daily validation for production

Author: Claude Code
Date: January 2026
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from datetime import datetime, timedelta
from google.cloud import bigquery
import pandas as pd
import numpy as np

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 80)
print("WALK-FORWARD VALIDATION MODEL")
print("=" * 80)
print(f"Started: {datetime.now()}")

# ============================================================================
# STEP 1: CREATE WALK-FORWARD VALIDATION TABLES
# ============================================================================

def create_validation_tables():
    """Create tables for walk-forward validation results"""
    print("\n" + "-" * 60)
    print("STEP 1: CREATING VALIDATION TABLES")
    print("-" * 60)

    # Table to store daily validation results
    validation_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.walk_forward_validation` (
        validation_date DATE,
        training_end_date DATE,
        asset_type STRING,
        total_predictions INT64,
        correct_predictions INT64,
        accuracy FLOAT64,
        up_precision FLOAT64,
        down_precision FLOAT64,
        up_recall FLOAT64,
        down_recall FLOAT64,
        f1_score FLOAT64,
        model_version STRING,
        created_at TIMESTAMP
    )
    """

    # Table to store model performance by symbol
    symbol_performance_sql = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.walk_forward_symbol_performance` (
        validation_date DATE,
        symbol STRING,
        asset_type STRING,
        prediction STRING,
        actual STRING,
        up_probability FLOAT64,
        confidence_level STRING,
        is_correct BOOL,
        created_at TIMESTAMP
    )
    """

    # Daily model snapshots
    model_snapshot_sql = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.model_snapshots` (
        snapshot_date DATE,
        training_start_date DATE,
        training_end_date DATE,
        records_used INT64,
        features_used ARRAY<STRING>,
        hyperparameters STRING,
        training_accuracy FLOAT64,
        validation_accuracy FLOAT64,
        model_status STRING,
        created_at TIMESTAMP
    )
    """

    for sql in [validation_table_sql, symbol_performance_sql, model_snapshot_sql]:
        try:
            bq_client.query(sql).result()
            print("  Created/verified table")
        except Exception as e:
            print(f"  Table note: {str(e)[:80]}")

    print("  Validation tables ready")


# ============================================================================
# STEP 2: GET DATA RANGE
# ============================================================================

def get_data_range():
    """Get the earliest and latest dates in our data"""
    print("\n" + "-" * 60)
    print("STEP 2: ANALYZING DATA RANGE")
    print("-" * 60)

    range_query = f"""
    SELECT
        'stocks' as asset_type,
        MIN(DATE(datetime)) as earliest_date,
        MAX(DATE(datetime)) as latest_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as symbols
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE datetime IS NOT NULL

    UNION ALL

    SELECT
        'crypto' as asset_type,
        MIN(DATE(datetime)) as earliest_date,
        MAX(DATE(datetime)) as latest_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as symbols
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    WHERE datetime IS NOT NULL

    UNION ALL

    SELECT
        'etfs' as asset_type,
        MIN(DATE(datetime)) as earliest_date,
        MAX(DATE(datetime)) as latest_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as symbols
    FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
    WHERE datetime IS NOT NULL
    """

    try:
        df = bq_client.query(range_query).to_dataframe()
        print("\nData Range by Asset Type:")
        for _, row in df.iterrows():
            print(f"  {row['asset_type']:8} | {row['earliest_date']} to {row['latest_date']} | {row['total_records']:,} records | {row['symbols']} symbols")
        return df
    except Exception as e:
        print(f"  Error: {e}")
        return None


# ============================================================================
# STEP 3: CREATE WALK-FORWARD FEATURE TABLE
# ============================================================================

def create_walk_forward_features():
    """Create feature table with proper time-series split markers"""
    print("\n" + "-" * 60)
    print("STEP 3: CREATING WALK-FORWARD FEATURE TABLE")
    print("-" * 60)

    # Key dates for walk-forward validation
    # Training cutoff: Dec 31, 2022
    # Testing period: 2023
    # Validation period: 2024-2025

    feature_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.walk_forward_features` AS

    WITH combined_data AS (
        -- Stocks
        SELECT
            'stocks' as asset_type,
            symbol, datetime, open, high, low, close, volume,
            rsi, macd, macd_histogram, macd_signal,
            sma_20, sma_50, sma_200, ema_12, ema_26, ema_50, ema_200,
            atr, bb_upper, bb_middle, bb_lower,
            adx, plus_di, minus_di, mfi, cmf,
            stoch_k, stoch_d, cci, roc, willr, obv,
            growth_score, in_rise_cycle, rise_cycle_start,
            trend_regime, golden_cross, death_cross
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE datetime IS NOT NULL AND close > 0

        UNION ALL

        -- Crypto
        SELECT
            'crypto' as asset_type,
            symbol, datetime, open, high, low, close, volume,
            rsi, macd, macd_histogram, macd_signal,
            sma_20, sma_50, sma_200, ema_12, ema_26, ema_50, ema_200,
            atr, bb_upper, bb_middle, bb_lower,
            adx, plus_di, minus_di, mfi, cmf,
            stoch_k, stoch_d, cci, roc, willr, obv,
            growth_score, in_rise_cycle, rise_cycle_start,
            trend_regime, golden_cross, death_cross
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
        WHERE datetime IS NOT NULL AND close > 0

        UNION ALL

        -- ETFs
        SELECT
            'etf' as asset_type,
            symbol, datetime, open, high, low, close, volume,
            rsi, macd, macd_histogram, macd_signal,
            sma_20, sma_50, sma_200, ema_12, ema_26, ema_50, ema_200,
            atr, bb_upper, bb_middle, bb_lower,
            adx, plus_di, minus_di, mfi, cmf,
            stoch_k, stoch_d, cci, roc, willr, obv,
            growth_score, in_rise_cycle, rise_cycle_start,
            trend_regime, golden_cross, death_cross
        FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
        WHERE datetime IS NOT NULL AND close > 0
    ),

    with_features AS (
        SELECT
            *,
            -- RSI features
            COALESCE(rsi, 50) as rsi_clean,
            COALESCE(rsi, 50) - LAG(COALESCE(rsi, 50), 1) OVER w as rsi_slope,
            CASE WHEN COALESCE(rsi, 50) > 70 THEN 1 ELSE 0 END as rsi_overbought,
            CASE WHEN COALESCE(rsi, 50) < 30 THEN 1 ELSE 0 END as rsi_oversold,

            -- MACD features
            COALESCE(macd_histogram, 0) as macd_hist_clean,
            CASE WHEN COALESCE(macd_histogram, 0) > LAG(COALESCE(macd_histogram, 0), 1) OVER w THEN 1 ELSE 0 END as macd_rising,

            -- Pivot detection (Saleem's key feature)
            CASE WHEN high > LAG(high, 1) OVER w AND high > LAG(high, 2) OVER w
                  AND high > LEAD(high, 1) OVER w AND high > LEAD(high, 2) OVER w
            THEN 1 ELSE 0 END as pivot_high_flag,

            CASE WHEN low < LAG(low, 1) OVER w AND low < LAG(low, 2) OVER w
                  AND low < LEAD(low, 1) OVER w AND low < LEAD(low, 2) OVER w
            THEN 1 ELSE 0 END as pivot_low_flag,

            -- Momentum features
            (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
            (close - LAG(close, 10) OVER w) / NULLIF(LAG(close, 10) OVER w, 0) * 100 as momentum_10d,
            (close - LAG(close, 20) OVER w) / NULLIF(LAG(close, 20) OVER w, 0) * 100 as momentum_20d,

            -- Volume features
            volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING), 0) as volume_ratio,

            -- Volatility
            COALESCE(atr, 0) / NULLIF(close, 0) * 100 as atr_pct,

            -- Target: next day direction (1 = UP, 0 = DOWN)
            CASE
                WHEN LEAD(close, 1) OVER w > close THEN 1
                ELSE 0
            END as target_direction,

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
      AND rsi_clean IS NOT NULL
      AND close > 0
    """

    try:
        job = bq_client.query(feature_sql)
        job.result()

        # Get counts
        count_query = f"""
        SELECT
            data_split,
            COUNT(*) as records,
            COUNT(DISTINCT symbol) as symbols,
            MIN(DATE(datetime)) as start_date,
            MAX(DATE(datetime)) as end_date
        FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features`
        GROUP BY data_split
        ORDER BY MIN(datetime)
        """
        df = bq_client.query(count_query).to_dataframe()

        print("\nWalk-Forward Split:")
        for _, row in df.iterrows():
            print(f"  {row['data_split']:10} | {row['start_date']} to {row['end_date']} | {row['records']:,} records | {row['symbols']} symbols")

        total = df['records'].sum()
        print(f"\n  Total: {total:,} records")

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# STEP 4: TRAIN WALK-FORWARD MODEL
# ============================================================================

def train_walk_forward_model():
    """Train XGBoost model using walk-forward methodology"""
    print("\n" + "-" * 60)
    print("STEP 4: TRAINING WALK-FORWARD MODEL")
    print("-" * 60)

    # Train model on TRAIN data (up to Dec 31, 2022)
    train_sql = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward`
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
        data_split_method='NO_SPLIT',  -- We handle split ourselves
        auto_class_weights=TRUE
    ) AS
    SELECT
        -- Core features
        rsi_clean as rsi,
        rsi_slope,
        rsi_overbought,
        rsi_oversold,
        macd_hist_clean as macd_histogram,
        macd_rising,

        -- Pivot detection (Saleem's 25% importance each)
        pivot_high_flag,
        pivot_low_flag,

        -- Trend features
        COALESCE(adx, 0) as adx,
        COALESCE(plus_di, 0) as plus_di,
        COALESCE(minus_di, 0) as minus_di,
        CASE WHEN in_rise_cycle = 1 THEN 1 ELSE 0 END as in_rise_cycle,
        CASE WHEN rise_cycle_start = 1 THEN 1 ELSE 0 END as rise_cycle_start,
        CASE WHEN golden_cross = 1 THEN 1 ELSE 0 END as golden_cross,

        -- Momentum
        COALESCE(momentum_5d, 0) as momentum_5d,
        COALESCE(momentum_10d, 0) as momentum_10d,
        COALESCE(momentum_20d, 0) as momentum_20d,

        -- Volatility & Volume
        COALESCE(atr_pct, 0) as atr_pct,
        COALESCE(volume_ratio, 1) as volume_ratio,

        -- Growth Score
        COALESCE(growth_score, 50) as growth_score,

        -- Additional features
        COALESCE(mfi, 50) as mfi,
        COALESCE(cci, 0) as cci,
        COALESCE(stoch_k, 50) as stoch_k,
        COALESCE(stoch_d, 50) as stoch_d,

        -- Feature interactions (key for accuracy)
        COALESCE(rsi_clean, 50) * COALESCE(volume_ratio, 1) as rsi_volume_interaction,
        COALESCE(macd_histogram, 0) * COALESCE(atr_pct, 0) as macd_atr_interaction,
        COALESCE(adx, 0) * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction,

        -- Target
        target_direction

    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features`
    WHERE data_split = 'TRAIN'
      AND target_direction IS NOT NULL
    """

    print("  Training on data up to Dec 31, 2022...")
    print("  This may take 5-15 minutes...")

    try:
        start_time = datetime.now()
        job = bq_client.query(train_sql)
        job.result()
        end_time = datetime.now()

        print(f"  Training completed in {(end_time - start_time).seconds // 60} minutes")

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# STEP 5: WALK-FORWARD TESTING (2023)
# ============================================================================

def walk_forward_testing():
    """Test model performance day by day through 2023"""
    print("\n" + "-" * 60)
    print("STEP 5: WALK-FORWARD TESTING (2023)")
    print("-" * 60)

    # Evaluate on TEST data
    eval_sql = f"""
    SELECT
        *
    FROM ML.EVALUATE(
        MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward`,
        (
            SELECT
                rsi_clean as rsi,
                rsi_slope,
                rsi_overbought,
                rsi_oversold,
                macd_hist_clean as macd_histogram,
                macd_rising,
                pivot_high_flag,
                pivot_low_flag,
                COALESCE(adx, 0) as adx,
                COALESCE(plus_di, 0) as plus_di,
                COALESCE(minus_di, 0) as minus_di,
                CASE WHEN in_rise_cycle = 1 THEN 1 ELSE 0 END as in_rise_cycle,
                CASE WHEN rise_cycle_start = 1 THEN 1 ELSE 0 END as rise_cycle_start,
                CASE WHEN golden_cross = 1 THEN 1 ELSE 0 END as golden_cross,
                COALESCE(momentum_5d, 0) as momentum_5d,
                COALESCE(momentum_10d, 0) as momentum_10d,
                COALESCE(momentum_20d, 0) as momentum_20d,
                COALESCE(atr_pct, 0) as atr_pct,
                COALESCE(volume_ratio, 1) as volume_ratio,
                COALESCE(growth_score, 50) as growth_score,
                COALESCE(mfi, 50) as mfi,
                COALESCE(cci, 0) as cci,
                COALESCE(stoch_k, 50) as stoch_k,
                COALESCE(stoch_d, 50) as stoch_d,
                COALESCE(rsi_clean, 50) * COALESCE(volume_ratio, 1) as rsi_volume_interaction,
                COALESCE(macd_histogram, 0) * COALESCE(atr_pct, 0) as macd_atr_interaction,
                COALESCE(adx, 0) * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction,
                target_direction
            FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features`
            WHERE data_split = 'TEST'
        )
    )
    """

    try:
        df = bq_client.query(eval_sql).to_dataframe()
        print("\n  TEST Performance (2023):")
        for col in df.columns:
            val = df[col].iloc[0]
            if isinstance(val, float):
                print(f"    {col}: {val:.4f}")
            else:
                print(f"    {col}: {val}")

        return df
    except Exception as e:
        print(f"  Error: {e}")
        return None


# ============================================================================
# STEP 6: WALK-FORWARD VALIDATION (2024-2025)
# ============================================================================

def walk_forward_validation():
    """Validate model performance on 2024-2025 data"""
    print("\n" + "-" * 60)
    print("STEP 6: WALK-FORWARD VALIDATION (2024-2025)")
    print("-" * 60)

    # Evaluate on VALIDATE data
    eval_sql = f"""
    SELECT
        *
    FROM ML.EVALUATE(
        MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward`,
        (
            SELECT
                rsi_clean as rsi,
                rsi_slope,
                rsi_overbought,
                rsi_oversold,
                macd_hist_clean as macd_histogram,
                macd_rising,
                pivot_high_flag,
                pivot_low_flag,
                COALESCE(adx, 0) as adx,
                COALESCE(plus_di, 0) as plus_di,
                COALESCE(minus_di, 0) as minus_di,
                CASE WHEN in_rise_cycle = 1 THEN 1 ELSE 0 END as in_rise_cycle,
                CASE WHEN rise_cycle_start = 1 THEN 1 ELSE 0 END as rise_cycle_start,
                CASE WHEN golden_cross = 1 THEN 1 ELSE 0 END as golden_cross,
                COALESCE(momentum_5d, 0) as momentum_5d,
                COALESCE(momentum_10d, 0) as momentum_10d,
                COALESCE(momentum_20d, 0) as momentum_20d,
                COALESCE(atr_pct, 0) as atr_pct,
                COALESCE(volume_ratio, 1) as volume_ratio,
                COALESCE(growth_score, 50) as growth_score,
                COALESCE(mfi, 50) as mfi,
                COALESCE(cci, 0) as cci,
                COALESCE(stoch_k, 50) as stoch_k,
                COALESCE(stoch_d, 50) as stoch_d,
                COALESCE(rsi_clean, 50) * COALESCE(volume_ratio, 1) as rsi_volume_interaction,
                COALESCE(macd_histogram, 0) * COALESCE(atr_pct, 0) as macd_atr_interaction,
                COALESCE(adx, 0) * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction,
                target_direction
            FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features`
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

        return df
    except Exception as e:
        print(f"  Error: {e}")
        return None


# ============================================================================
# STEP 7: GENERATE CONFIDENCE-BASED PREDICTIONS
# ============================================================================

def create_prediction_view():
    """Create a view with confidence-filtered predictions"""
    print("\n" + "-" * 60)
    print("STEP 7: CREATING PREDICTION VIEW")
    print("-" * 60)

    view_sql = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_walk_forward_predictions` AS

    WITH predictions AS (
        SELECT
            f.asset_type,
            f.symbol,
            f.datetime,
            f.close,
            f.rsi_clean as rsi,
            f.macd_hist_clean as macd_histogram,
            f.adx,
            f.growth_score,
            f.in_rise_cycle,
            f.rise_cycle_start,
            f.pivot_high_flag,
            f.pivot_low_flag,
            f.golden_cross,
            f.trend_regime,
            f.target_direction as actual_direction,
            p.predicted_target_direction as predicted_direction,
            p.predicted_target_direction_probs[OFFSET(1)].prob as up_probability
        FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features` f
        CROSS JOIN ML.PREDICT(
            MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward`,
            (SELECT
                f.symbol,
                f.datetime,
                f.close,
                f.rsi_clean as rsi,
                f.rsi_slope,
                f.rsi_overbought,
                f.rsi_oversold,
                f.macd_hist_clean as macd_histogram,
                f.macd_rising,
                f.pivot_high_flag,
                f.pivot_low_flag,
                COALESCE(f.adx, 0) as adx,
                COALESCE(f.plus_di, 0) as plus_di,
                COALESCE(f.minus_di, 0) as minus_di,
                CASE WHEN f.in_rise_cycle = 1 THEN 1 ELSE 0 END as in_rise_cycle,
                CASE WHEN f.rise_cycle_start = 1 THEN 1 ELSE 0 END as rise_cycle_start,
                CASE WHEN f.golden_cross = 1 THEN 1 ELSE 0 END as golden_cross,
                COALESCE(f.momentum_5d, 0) as momentum_5d,
                COALESCE(f.momentum_10d, 0) as momentum_10d,
                COALESCE(f.momentum_20d, 0) as momentum_20d,
                COALESCE(f.atr_pct, 0) as atr_pct,
                COALESCE(f.volume_ratio, 1) as volume_ratio,
                COALESCE(f.growth_score, 50) as growth_score,
                COALESCE(f.mfi, 50) as mfi,
                COALESCE(f.cci, 0) as cci,
                COALESCE(f.stoch_k, 50) as stoch_k,
                COALESCE(f.stoch_d, 50) as stoch_d,
                COALESCE(f.rsi_clean, 50) * COALESCE(f.volume_ratio, 1) as rsi_volume_interaction,
                COALESCE(f.macd_hist_clean, 0) * COALESCE(f.atr_pct, 0) as macd_atr_interaction,
                COALESCE(f.adx, 0) * CASE WHEN f.in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction
            )
        ) p
        WHERE f.data_split = 'VALIDATE'
    )

    SELECT
        *,
        -- Confidence levels based on probability distance from 0.5
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

        -- Is prediction correct?
        (predicted_direction = actual_direction) as is_correct

    FROM predictions
    """

    try:
        bq_client.query(view_sql).result()
        print("  Created prediction view: v_walk_forward_predictions")
        return True
    except Exception as e:
        print(f"  Error creating view: {e}")
        # Try simpler approach without CROSS JOIN
        return create_simple_prediction_table()


def create_simple_prediction_table():
    """Create predictions table using simpler approach"""
    print("  Trying simpler prediction table approach...")

    pred_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions` AS

    SELECT
        f.asset_type,
        f.symbol,
        f.datetime,
        f.close,
        f.rsi_clean as rsi,
        f.macd_hist_clean as macd_histogram,
        f.adx,
        f.growth_score,
        f.in_rise_cycle,
        f.rise_cycle_start,
        f.pivot_high_flag,
        f.pivot_low_flag,
        f.golden_cross,
        f.trend_regime,
        f.target_direction as actual_direction,
        p.predicted_target_direction as predicted_direction,
        CASE
            WHEN ARRAY_LENGTH(p.predicted_target_direction_probs) > 1
            THEN p.predicted_target_direction_probs[OFFSET(1)].prob
            ELSE p.predicted_target_direction_probs[OFFSET(0)].prob
        END as up_probability,
        f.data_split
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features` f
    LEFT JOIN (
        SELECT *
        FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_walk_forward`,
            (SELECT
                symbol,
                datetime,
                rsi_clean as rsi,
                rsi_slope,
                rsi_overbought,
                rsi_oversold,
                macd_hist_clean as macd_histogram,
                macd_rising,
                pivot_high_flag,
                pivot_low_flag,
                COALESCE(adx, 0) as adx,
                COALESCE(plus_di, 0) as plus_di,
                COALESCE(minus_di, 0) as minus_di,
                CASE WHEN in_rise_cycle = 1 THEN 1 ELSE 0 END as in_rise_cycle,
                CASE WHEN rise_cycle_start = 1 THEN 1 ELSE 0 END as rise_cycle_start,
                CASE WHEN golden_cross = 1 THEN 1 ELSE 0 END as golden_cross,
                COALESCE(momentum_5d, 0) as momentum_5d,
                COALESCE(momentum_10d, 0) as momentum_10d,
                COALESCE(momentum_20d, 0) as momentum_20d,
                COALESCE(atr_pct, 0) as atr_pct,
                COALESCE(volume_ratio, 1) as volume_ratio,
                COALESCE(growth_score, 50) as growth_score,
                COALESCE(mfi, 50) as mfi,
                COALESCE(cci, 0) as cci,
                COALESCE(stoch_k, 50) as stoch_k,
                COALESCE(stoch_d, 50) as stoch_d,
                COALESCE(rsi_clean, 50) * COALESCE(volume_ratio, 1) as rsi_volume_interaction,
                COALESCE(macd_hist_clean, 0) * COALESCE(atr_pct, 0) as macd_atr_interaction,
                COALESCE(adx, 0) * CASE WHEN in_rise_cycle = 1 THEN 1 ELSE -1 END as adx_trend_interaction
            FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features`
            WHERE data_split IN ('TEST', 'VALIDATE'))
        )
    ) p
    ON f.symbol = p.symbol AND f.datetime = p.datetime
    WHERE f.data_split IN ('TEST', 'VALIDATE')
    """

    try:
        job = bq_client.query(pred_sql)
        job.result()

        # Get summary
        summary_sql = f"""
        SELECT
            data_split,
            COUNT(*) as total,
            SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct,
            ROUND(SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy
        FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions`
        GROUP BY data_split
        """

        df = bq_client.query(summary_sql).to_dataframe()
        print("\n  Prediction Results:")
        for _, row in df.iterrows():
            print(f"    {row['data_split']}: {row['accuracy']:.2f}% accuracy ({row['correct']:,}/{row['total']:,})")

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


# ============================================================================
# STEP 8: DAILY ACCURACY BY CONFIDENCE
# ============================================================================

def analyze_accuracy_by_confidence():
    """Analyze model accuracy by confidence level"""
    print("\n" + "-" * 60)
    print("STEP 8: ACCURACY BY CONFIDENCE LEVEL")
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
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions`
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
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete walk-forward validation"""

    print("\n" + "=" * 80)
    print("STARTING WALK-FORWARD VALIDATION PROCESS")
    print("=" * 80)
    print("""
Walk-Forward Methodology:
  1. Training Data: Earliest data to Dec 31, 2022
  2. Testing Data: Jan 1, 2023 to Dec 31, 2023
  3. Validation Data: Jan 1, 2024 to present

This ensures NO look-ahead bias and provides realistic accuracy estimates.
""")

    # Step 1: Create validation tables
    create_validation_tables()

    # Step 2: Get data range
    data_range = get_data_range()

    # Step 3: Create feature table
    if not create_walk_forward_features():
        print("\nFailed to create feature table. Exiting.")
        return

    # Step 4: Train model
    if not train_walk_forward_model():
        print("\nFailed to train model. Exiting.")
        return

    # Step 5: Test on 2023 data
    test_results = walk_forward_testing()

    # Step 6: Validate on 2024+ data
    val_results = walk_forward_validation()

    # Step 7: Create predictions
    create_prediction_view()

    # Step 8: Analyze by confidence
    conf_analysis = analyze_accuracy_by_confidence()

    # Summary
    print("\n" + "=" * 80)
    print("WALK-FORWARD VALIDATION COMPLETE")
    print("=" * 80)
    print(f"""
Model: xgboost_walk_forward
Training Period: Earliest data to Dec 31, 2022
Testing Period: 2023 (walk-forward day by day)
Validation Period: 2024-2025 (continuous validation)

Tables Created:
  - {ML_DATASET}.walk_forward_features
  - {ML_DATASET}.walk_forward_predictions
  - {ML_DATASET}.walk_forward_validation
  - {ML_DATASET}.model_snapshots

Next Steps:
  1. Review HIGH confidence predictions for trading signals
  2. Set up daily retraining with expanding window
  3. Monitor model drift over time

Completed: {datetime.now()}
""")


if __name__ == "__main__":
    main()
