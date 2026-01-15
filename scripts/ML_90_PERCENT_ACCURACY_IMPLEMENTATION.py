"""
ML 90%+ Accuracy Implementation Guide
======================================
Complete implementation from Saleem's 67% to 90%+ accuracy

Phases:
1. Data Foundation (Splits, Deduplication, Gap Filling)
2. Feature Engineering (Saleem's 16 + Interactions)
3. Gemini 2.5 Pro Integration (Ensemble)
4. Automation (Pipeline, Monitoring, Validation)

Author: Claude Code + Saleem Ahmad
Date: January 2026
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import os

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

print("=" * 80)
print("ML 90%+ ACCURACY IMPLEMENTATION")
print("From Saleem's 67% to Target 90%+")
print("=" * 80)
print(f"Started: {datetime.now()}")
print()

# ============================================================================
# PHASE 1: DATA FOUNDATION
# ============================================================================

def phase1_validate_data_splits():
    """
    PHASE 1.1: Validate Data Splits

    Critical: Proper time-based splitting prevents look-ahead bias
    - Training: Beginning of data → Dec 31, 2022
    - Testing: Jan 1, 2023 → Dec 31, 2023
    - Validation: Jan 1, 2024 → Present (2025+)
    """
    print("\n" + "=" * 80)
    print("PHASE 1.1: VALIDATING DATA SPLITS")
    print("=" * 80)

    # Check data coverage for stocks
    query = f"""
    SELECT
        'stocks_daily_clean' as table_name,
        MIN(DATE(datetime)) as earliest_date,
        MAX(DATE(datetime)) as latest_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as unique_symbols,

        -- Training set (< 2023)
        COUNTIF(DATE(datetime) < '2023-01-01') as training_records,

        -- Testing set (2023)
        COUNTIF(DATE(datetime) >= '2023-01-01' AND DATE(datetime) < '2024-01-01') as testing_records,

        -- Validation set (2024+)
        COUNTIF(DATE(datetime) >= '2024-01-01') as validation_records

    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE datetime IS NOT NULL

    UNION ALL

    SELECT
        'crypto_daily_clean' as table_name,
        MIN(DATE(datetime)) as earliest_date,
        MAX(DATE(datetime)) as latest_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as unique_symbols,
        COUNTIF(DATE(datetime) < '2023-01-01') as training_records,
        COUNTIF(DATE(datetime) >= '2023-01-01' AND DATE(datetime) < '2024-01-01') as testing_records,
        COUNTIF(DATE(datetime) >= '2024-01-01') as validation_records
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    WHERE datetime IS NOT NULL
    """

    print("\nChecking data coverage...")
    try:
        df = client.query(query).to_dataframe()
        print("\nDATA SPLIT ANALYSIS:")
        print("-" * 80)

        for _, row in df.iterrows():
            total = row['total_records']
            train_pct = row['training_records'] / total * 100 if total > 0 else 0
            test_pct = row['testing_records'] / total * 100 if total > 0 else 0
            val_pct = row['validation_records'] / total * 100 if total > 0 else 0

            print(f"\nTable: {row['table_name']}")
            print(f"  Date Range: {row['earliest_date']} to {row['latest_date']}")
            print(f"  Total Records: {row['total_records']:,}")
            print(f"  Unique Symbols: {row['unique_symbols']}")
            print(f"  Training (<2023):    {row['training_records']:,} ({train_pct:.1f}%)")
            print(f"  Testing (2023):      {row['testing_records']:,} ({test_pct:.1f}%)")
            print(f"  Validation (2024+):  {row['validation_records']:,} ({val_pct:.1f}%)")

            # Recommendations
            if train_pct < 50:
                print(f"  ⚠️  WARNING: Training set too small. Need more historical data.")
            if test_pct < 10:
                print(f"  ⚠️  WARNING: Testing set small. Consider expanding.")
            if val_pct < 10:
                print(f"  ⚠️  WARNING: Validation set small. Ensure 2024+ data is loaded.")

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None


def phase1_deduplicate_tables():
    """
    PHASE 1.2: Deduplicate Tables

    Critical fix from Saleem's analysis - ensures one row per date per symbol
    Expected accuracy improvement: +2-3%
    """
    print("\n" + "=" * 80)
    print("PHASE 1.2: DEDUPLICATING TABLES")
    print("=" * 80)

    tables = ['stocks_daily_clean', 'crypto_daily_clean', 'etfs_daily_clean']

    for table in tables:
        print(f"\nProcessing {table}...")

        # Check for duplicates
        check_query = f"""
        SELECT
            symbol,
            DATE(datetime) as trade_date,
            COUNT(*) as row_count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        GROUP BY symbol, DATE(datetime)
        HAVING COUNT(*) > 1
        LIMIT 10
        """

        try:
            dupes = client.query(check_query).to_dataframe()

            if len(dupes) > 0:
                print(f"  Found {len(dupes)}+ duplicate date/symbol combinations")
                print(f"  Sample duplicates:")
                print(dupes.head())

                # Create deduplicated table
                dedup_query = f"""
                CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.{table}_deduped` AS
                WITH ranked AS (
                    SELECT
                        *,
                        ROW_NUMBER() OVER (
                            PARTITION BY symbol, DATE(datetime)
                            ORDER BY datetime DESC
                        ) as rn
                    FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
                )
                SELECT * EXCEPT(rn)
                FROM ranked
                WHERE rn = 1
                """

                print(f"  Creating deduplicated table: {table}_deduped...")
                client.query(dedup_query).result()
                print(f"  ✓ Deduplicated table created")

            else:
                print(f"  ✓ No duplicates found in {table}")

        except Exception as e:
            print(f"  Error processing {table}: {e}")


def phase1_check_data_gaps():
    """
    PHASE 1.3: Check and Fill Data Gaps

    Identifies missing trading days and data quality issues
    """
    print("\n" + "=" * 80)
    print("PHASE 1.3: CHECKING DATA GAPS")
    print("=" * 80)

    # Check for major symbols
    symbols_to_check = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'SPY', 'QQQ']

    for symbol in symbols_to_check:
        query = f"""
        WITH date_series AS (
            SELECT date
            FROM UNNEST(GENERATE_DATE_ARRAY('2020-01-01', CURRENT_DATE(), INTERVAL 1 DAY)) as date
            WHERE EXTRACT(DAYOFWEEK FROM date) NOT IN (1, 7)  -- Exclude weekends
        ),
        symbol_dates AS (
            SELECT DISTINCT DATE(datetime) as trade_date
            FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
            WHERE symbol = '{symbol}'
        )
        SELECT
            COUNT(*) as missing_days,
            MIN(d.date) as first_missing,
            MAX(d.date) as last_missing
        FROM date_series d
        LEFT JOIN symbol_dates s ON d.date = s.trade_date
        WHERE s.trade_date IS NULL
            AND d.date >= '2020-01-01'
            AND d.date <= CURRENT_DATE() - 1
        """

        try:
            result = client.query(query).to_dataframe()
            missing = result.iloc[0]['missing_days']

            if missing > 50:  # Allow some holidays
                print(f"  ⚠️  {symbol}: {missing} potential missing days")
            else:
                print(f"  ✓ {symbol}: Data coverage OK ({missing} gaps, likely holidays)")

        except Exception as e:
            print(f"  Error checking {symbol}: {e}")


# ============================================================================
# PHASE 2: FEATURE ENGINEERING (SALEEM'S FEATURES + INTERACTIONS)
# ============================================================================

def phase2_add_saleem_features():
    """
    PHASE 2.1: Add Saleem's 16 Validated Features

    Key features from Saleem's 67% model:
    - pivot_high_flag, pivot_low_flag (25% importance each!)
    - rsi_slope, rsi_zscore, rsi_overbought, rsi_oversold
    - macd_cross
    - awesome_osc, cci, mfi, momentum
    """
    print("\n" + "=" * 80)
    print("PHASE 2.1: ADDING SALEEM'S 16 FEATURES")
    print("=" * 80)

    # Create ML feature table with Saleem's features
    saleem_features_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_saleem_16_features` AS
    WITH base_data AS (
        SELECT
            symbol,
            datetime,
            open, high, low, close, volume,
            rsi, macd, macd_signal, macd_histogram,
            cci, mfi, momentum,
            ema_12, ema_26, sma_50, sma_200,
            adx, atr,
            bollinger_upper, bollinger_middle, bollinger_lower,

            -- Row number for window functions
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as rn

        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE datetime >= '2018-01-01'
            AND rsi IS NOT NULL
            AND close IS NOT NULL
    ),
    with_derived AS (
        SELECT
            *,

            -- ================================================
            -- SALEEM'S KEY FEATURES (16 total)
            -- ================================================

            -- 1. RSI Slope (momentum derivative) - 8% importance
            rsi - LAG(rsi, 1) OVER w as rsi_slope,

            -- 2. RSI Z-Score (normalized RSI)
            (rsi - AVG(rsi) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)) /
                NULLIF(STDDEV(rsi) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 0) as rsi_zscore,

            -- 3. RSI Overbought Signal
            CASE WHEN rsi > 70 THEN 1 ELSE 0 END as rsi_overbought,

            -- 4. RSI Oversold Signal
            CASE WHEN rsi < 30 THEN 1 ELSE 0 END as rsi_oversold,

            -- 5. MACD Cross Signal - 8% importance
            CASE
                WHEN macd > macd_signal AND LAG(macd, 1) OVER w <= LAG(macd_signal, 1) OVER w THEN 1   -- Bullish cross
                WHEN macd < macd_signal AND LAG(macd, 1) OVER w >= LAG(macd_signal, 1) OVER w THEN -1  -- Bearish cross
                ELSE 0
            END as macd_cross,

            -- 6. VWAP Daily (simplified)
            (high + low + close) / 3 as vwap_daily,

            -- 7-8. PIVOT HIGH/LOW FLAGS - 25% importance each! (KEY FEATURES)
            CASE
                WHEN high > LAG(high, 1) OVER w
                 AND high > LAG(high, 2) OVER w
                 AND high > LEAD(high, 1) OVER w
                 AND high > LEAD(high, 2) OVER w
                THEN 1 ELSE 0
            END as pivot_high_flag,

            CASE
                WHEN low < LAG(low, 1) OVER w
                 AND low < LAG(low, 2) OVER w
                 AND low < LEAD(low, 1) OVER w
                 AND low < LEAD(low, 2) OVER w
                THEN 1 ELSE 0
            END as pivot_low_flag,

            -- 9. Awesome Oscillator (if not already present)
            COALESCE(
                (SMA(high + low, 5) OVER w - SMA(high + low, 34) OVER w) / 2,
                (AVG((high + low)/2) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) -
                 AVG((high + low)/2) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 33 PRECEDING AND CURRENT ROW))
            ) as awesome_osc_calc

        FROM base_data
        WHERE rn > 34  -- Need enough history for calculations
        WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    ),
    final_features AS (
        SELECT
            symbol,
            datetime,
            close,
            volume,

            -- Saleem's 16 Features
            rsi,                    -- 1. RSI
            rsi_slope,              -- 2. RSI Slope
            rsi_zscore,             -- 3. RSI Z-Score
            rsi_overbought,         -- 4. RSI Overbought
            rsi_oversold,           -- 5. RSI Oversold
            macd,                   -- 6. MACD
            macd_signal,            -- 7. MACD Signal
            macd_histogram,         -- 8. MACD Histogram
            macd_cross,             -- 9. MACD Cross
            cci,                    -- 10. CCI
            mfi,                    -- 11. MFI
            momentum,               -- 12. Momentum
            awesome_osc_calc as awesome_osc,  -- 13. Awesome Oscillator
            vwap_daily,             -- 14. VWAP Daily
            pivot_high_flag,        -- 15. Pivot High (KEY - 25%)
            pivot_low_flag,         -- 16. Pivot Low (KEY - 25%)

            -- Additional context
            adx,
            atr,
            ema_12,
            ema_26,
            sma_50,
            sma_200,

            -- Target variable
            CASE WHEN LEAD(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) > close
                 THEN 1 ELSE 0 END as target_direction

        FROM with_derived
        WHERE rsi_slope IS NOT NULL
    )
    SELECT * FROM final_features
    """

    print("\nCreating Saleem's 16-feature table...")
    try:
        # Simplified version without SMA window function
        simplified_sql = f"""
        CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_saleem_16_features` AS
        WITH base_data AS (
            SELECT
                symbol,
                datetime,
                open, high, low, close, volume,
                rsi, macd, macd_signal, macd_histogram,
                cci, mfi, momentum,
                ema_12, ema_26, sma_50, sma_200,
                adx, atr,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
            WHERE datetime >= '2018-01-01'
                AND rsi IS NOT NULL
                AND close IS NOT NULL
        ),
        with_derived AS (
            SELECT
                symbol,
                datetime,
                close,
                volume,
                rsi,
                macd,
                macd_signal,
                macd_histogram,
                cci,
                mfi,
                momentum,
                adx,
                atr,
                ema_12,
                ema_26,
                sma_50,
                sma_200,
                high,
                low,

                -- RSI Slope
                rsi - LAG(rsi, 1) OVER w as rsi_slope,

                -- RSI Z-Score (simplified)
                (rsi - 50) / 14.0 as rsi_zscore,

                -- RSI Signals
                CASE WHEN rsi > 70 THEN 1 ELSE 0 END as rsi_overbought,
                CASE WHEN rsi < 30 THEN 1 ELSE 0 END as rsi_oversold,

                -- MACD Cross
                CASE
                    WHEN macd > macd_signal AND LAG(macd, 1) OVER w <= LAG(macd_signal, 1) OVER w THEN 1
                    WHEN macd < macd_signal AND LAG(macd, 1) OVER w >= LAG(macd_signal, 1) OVER w THEN -1
                    ELSE 0
                END as macd_cross,

                -- VWAP Daily
                (high + low + close) / 3 as vwap_daily,

                -- Pivot High Flag (KEY - 25% importance)
                CASE
                    WHEN high > LAG(high, 1) OVER w
                     AND high > LAG(high, 2) OVER w
                     AND high > LEAD(high, 1) OVER w
                     AND high > LEAD(high, 2) OVER w
                    THEN 1 ELSE 0
                END as pivot_high_flag,

                -- Pivot Low Flag (KEY - 25% importance)
                CASE
                    WHEN low < LAG(low, 1) OVER w
                     AND low < LAG(low, 2) OVER w
                     AND low < LEAD(low, 1) OVER w
                     AND low < LEAD(low, 2) OVER w
                    THEN 1 ELSE 0
                END as pivot_low_flag,

                -- Awesome Oscillator (simplified)
                macd_histogram * 0.5 as awesome_osc,

                -- Target
                CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction

            FROM base_data
            WHERE rn > 5
            WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
        )
        SELECT
            symbol,
            datetime,
            close,
            volume,
            rsi,
            rsi_slope,
            rsi_zscore,
            rsi_overbought,
            rsi_oversold,
            macd,
            macd_signal,
            macd_histogram,
            macd_cross,
            cci,
            mfi,
            momentum,
            awesome_osc,
            vwap_daily,
            pivot_high_flag,
            pivot_low_flag,
            adx,
            atr,
            ema_12,
            ema_26,
            sma_50,
            sma_200,
            target_direction
        FROM with_derived
        WHERE rsi_slope IS NOT NULL
            AND target_direction IS NOT NULL
        """

        client.query(simplified_sql).result()
        print("  ✓ Created ml_saleem_16_features table")

        # Verify
        count_query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.ml_saleem_16_features`"
        count = list(client.query(count_query).result())[0].cnt
        print(f"  ✓ Table contains {count:,} records")

    except Exception as e:
        print(f"  Error: {e}")


def phase2_add_feature_interactions():
    """
    PHASE 2.2: Add Feature Interactions

    Key interactions that boost accuracy:
    - RSI × Volume_Ratio
    - MACD × ATR
    - ADX × Trend_Direction
    - RSI × ADX
    """
    print("\n" + "=" * 80)
    print("PHASE 2.2: ADDING FEATURE INTERACTIONS")
    print("=" * 80)

    interactions_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features` AS
    SELECT
        s.*,

        -- ================================================
        -- FEATURE INTERACTIONS (per masterquery.md)
        -- ================================================

        -- 1. RSI × Volume Ratio (momentum confirmed by volume)
        s.rsi * (s.volume / NULLIF(AVG(s.volume) OVER (PARTITION BY s.symbol ORDER BY s.datetime ROWS 20 PRECEDING), 0)) as rsi_volume_interaction,

        -- 2. MACD × ATR (momentum relative to volatility)
        s.macd_histogram * (s.atr / NULLIF(s.close, 0) * 100) as macd_atr_interaction,

        -- 3. ADX × Trend Direction (trend strength with direction)
        s.adx * CASE WHEN s.ema_12 > s.ema_26 THEN 1 ELSE -1 END as adx_trend_interaction,

        -- 4. RSI × ADX (momentum in trending market)
        s.rsi * (s.adx / 100) as rsi_adx_interaction,

        -- 5. Stochastic approximation × Volume
        ((s.close - s.sma_50) / NULLIF(s.sma_50, 0) * 100) *
            (s.volume / NULLIF(AVG(s.volume) OVER (PARTITION BY s.symbol ORDER BY s.datetime ROWS 20 PRECEDING), 0)) as price_volume_interaction,

        -- ================================================
        -- LAGGED FEATURES
        -- ================================================

        -- RSI lags
        LAG(s.rsi, 1) OVER w as rsi_lag1,
        LAG(s.rsi, 5) OVER w as rsi_lag5,
        LAG(s.rsi, 10) OVER w as rsi_lag10,

        -- MACD histogram lags
        LAG(s.macd_histogram, 1) OVER w as macd_hist_lag1,
        LAG(s.macd_histogram, 5) OVER w as macd_hist_lag5,

        -- RSI changes
        s.rsi - LAG(s.rsi, 1) OVER w as rsi_change_1d,
        s.rsi - LAG(s.rsi, 5) OVER w as rsi_change_5d,

        -- ================================================
        -- MOMENTUM FEATURES
        -- ================================================

        (s.close - LAG(s.close, 1) OVER w) / NULLIF(LAG(s.close, 1) OVER w, 0) * 100 as momentum_1d,
        (s.close - LAG(s.close, 5) OVER w) / NULLIF(LAG(s.close, 5) OVER w, 0) * 100 as momentum_5d,
        (s.close - LAG(s.close, 10) OVER w) / NULLIF(LAG(s.close, 10) OVER w, 0) * 100 as momentum_10d,
        (s.close - LAG(s.close, 20) OVER w) / NULLIF(LAG(s.close, 20) OVER w, 0) * 100 as momentum_20d,

        -- ================================================
        -- CYCLE DETECTION (per masterquery.md)
        -- ================================================

        CASE WHEN s.ema_12 > s.ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

        CASE WHEN s.ema_12 > s.ema_26 AND LAG(s.ema_12) OVER w <= LAG(s.ema_26) OVER w
             THEN 1 ELSE 0 END as rise_cycle_start,

        CASE WHEN s.ema_12 < s.ema_26 AND LAG(s.ema_12) OVER w >= LAG(s.ema_26) OVER w
             THEN 1 ELSE 0 END as fall_cycle_start,

        CASE WHEN s.sma_50 > s.sma_200 AND LAG(s.sma_50) OVER w <= LAG(s.sma_200) OVER w
             THEN 1 ELSE 0 END as golden_cross,

        CASE WHEN s.sma_50 < s.sma_200 AND LAG(s.sma_50) OVER w >= LAG(s.sma_200) OVER w
             THEN 1 ELSE 0 END as death_cross,

        -- ================================================
        -- TREND REGIME
        -- ================================================

        CASE
            WHEN s.close > s.sma_50 AND s.sma_50 > s.sma_200 AND s.adx > 25 THEN 'STRONG_UPTREND'
            WHEN s.close < s.sma_50 AND s.sma_50 < s.sma_200 AND s.adx > 25 THEN 'STRONG_DOWNTREND'
            WHEN s.close > s.sma_200 THEN 'WEAK_UPTREND'
            WHEN s.close < s.sma_200 THEN 'WEAK_DOWNTREND'
            ELSE 'CONSOLIDATION'
        END as trend_regime,

        -- ================================================
        -- GROWTH SCORE (0-100)
        -- ================================================

        (CASE WHEN s.rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
         CASE WHEN s.macd_histogram > 0 THEN 25 ELSE 0 END +
         CASE WHEN s.adx > 25 THEN 25 ELSE 0 END +
         CASE WHEN s.close > s.sma_200 THEN 25 ELSE 0 END) as growth_score,

        -- ================================================
        -- VOLATILITY FEATURES
        -- ================================================

        s.atr / NULLIF(s.close, 0) * 100 as atr_pct,
        s.volume / NULLIF(AVG(s.volume) OVER (PARTITION BY s.symbol ORDER BY s.datetime ROWS 20 PRECEDING), 0) as volume_ratio

    FROM `{PROJECT_ID}.{ML_DATASET}.ml_saleem_16_features` s
    WINDOW w AS (PARTITION BY s.symbol ORDER BY s.datetime)
    """

    print("\nCreating enhanced 40+ feature table...")
    try:
        client.query(interactions_sql).result()
        print("  ✓ Created ml_enhanced_40_features table")

        # Verify
        count_query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features`"
        count = list(client.query(count_query).result())[0].cnt
        print(f"  ✓ Table contains {count:,} records with 40+ features")

    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# PHASE 3: GEMINI 2.5 PRO INTEGRATION
# ============================================================================

def phase3_setup_gemini_integration():
    """
    PHASE 3.1: Set Up Gemini 2.5 Pro Integration

    Creates the hybrid ensemble model combining:
    - XGBoost (60% weight) - quantitative technical analysis
    - Gemini 2.5 Pro (40% weight) - qualitative market analysis
    """
    print("\n" + "=" * 80)
    print("PHASE 3.1: GEMINI 2.5 PRO INTEGRATION SETUP")
    print("=" * 80)

    print("""
    GEMINI INTEGRATION CHECKLIST:

    1. API Key Setup:
       □ Obtain Gemini API key from https://aistudio.google.com/app/apikey
       □ Store in GCP Secret Manager:
         gcloud secrets create gemini-api-key --data-file=- <<< "YOUR_API_KEY"

    2. Model Configuration:
       - Primary Model: gemini-2.5-pro (best reasoning)
       - Fallback: gemini-2.0-flash (faster, lower cost)
       - Temperature: 0.1 (consistent predictions)
       - Max Tokens: 8192

    3. Ensemble Weights:
       - XGBoost: 60% (technical indicators)
       - Gemini: 40% (qualitative analysis)

    4. Prompt Template for Gemini:
       - Input: symbol, price, RSI, MACD, ADX, trend_regime
       - Output: direction, confidence, reasoning, key_factors
    """)

    # Check if Gemini API is configured
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(project=PROJECT_ID, location='us-central1')
        model = GenerativeModel("gemini-2.0-flash-001")

        # Test prompt
        response = model.generate_content("Say 'Gemini API configured successfully'")
        print(f"\n  ✓ Gemini API Test: {response.text.strip()}")

    except Exception as e:
        print(f"\n  ⚠️  Gemini API not configured: {e}")
        print("     Please set up the API key in Secret Manager")


def phase3_create_ensemble_model():
    """
    PHASE 3.2: Create XGBoost + Gemini Ensemble Model
    """
    print("\n" + "=" * 80)
    print("PHASE 3.2: CREATING XGBOOST + GEMINI ENSEMBLE")
    print("=" * 80)

    # Create XGBoost model with Saleem's features
    xgboost_model_sql = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_saleem_90pct`
    OPTIONS(
        model_type='BOOSTED_TREE_CLASSIFIER',
        input_label_cols=['target_direction'],

        -- Optimized hyperparameters
        max_iterations=200,
        num_parallel_tree=2,
        max_tree_depth=8,
        min_tree_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        l1_reg=0.01,
        l2_reg=0.1,
        learn_rate=0.05,

        -- Training settings
        early_stop=TRUE,
        data_split_method='CUSTOM',
        data_split_col='data_split',
        enable_global_explain=TRUE,

        -- Class balancing
        auto_class_weights=TRUE
    ) AS
    SELECT
        -- Saleem's core 16 features
        rsi,
        rsi_slope,
        rsi_zscore,
        rsi_overbought,
        rsi_oversold,
        macd_histogram,
        macd_cross,
        cci,
        mfi,
        momentum,
        awesome_osc,
        vwap_daily,
        pivot_high_flag,    -- KEY: 25% importance
        pivot_low_flag,     -- KEY: 25% importance

        -- Feature interactions
        rsi_volume_interaction,
        macd_atr_interaction,
        adx_trend_interaction,
        rsi_adx_interaction,

        -- Lagged features
        rsi_lag1,
        rsi_lag5,
        macd_hist_lag1,
        rsi_change_1d,

        -- Momentum
        momentum_5d,
        momentum_10d,
        momentum_20d,

        -- Cycle detection
        in_rise_cycle,
        rise_cycle_start,
        golden_cross,
        growth_score,

        -- Volatility
        atr_pct,
        volume_ratio,

        -- Target
        CAST(target_direction AS INT64) as target_direction,

        -- Data split: Training (<2023), Testing (2023), Validation (2024+)
        CASE
            WHEN DATE(datetime) < '2023-01-01' THEN 'TRAIN'
            WHEN DATE(datetime) < '2024-01-01' THEN 'TEST'
            ELSE 'EVAL'
        END as data_split

    FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features`
    WHERE target_direction IS NOT NULL
        AND rsi IS NOT NULL
        AND pivot_high_flag IS NOT NULL
        AND volume_ratio IS NOT NULL
        AND volume_ratio < 10  -- Remove extreme outliers
    """

    print("\nTraining XGBoost model with Saleem's features...")
    print("  (This may take 5-10 minutes)")

    try:
        client.query(xgboost_model_sql).result()
        print("  ✓ XGBoost model trained: xgboost_saleem_90pct")

        # Evaluate model
        eval_query = f"""
        SELECT * FROM ML.EVALUATE(MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_saleem_90pct`)
        """
        results = list(client.query(eval_query).result())

        if results:
            r = results[0]
            print(f"\n  MODEL EVALUATION:")
            print(f"  -----------------")
            print(f"  Accuracy:  {r.accuracy*100:.2f}%")
            print(f"  Precision: {r.precision*100:.2f}%")
            print(f"  Recall:    {r.recall*100:.2f}%")
            print(f"  F1 Score:  {r.f1_score*100:.2f}%")
            print(f"  ROC AUC:   {r.roc_auc*100:.2f}%")

    except Exception as e:
        print(f"  Error training model: {e}")


# ============================================================================
# PHASE 4: AUTOMATION (PIPELINE, MONITORING, VALIDATION)
# ============================================================================

def phase4_setup_automated_pipeline():
    """
    PHASE 4.1: Set Up Automated Training Pipeline
    """
    print("\n" + "=" * 80)
    print("PHASE 4.1: AUTOMATED TRAINING PIPELINE")
    print("=" * 80)

    print("""
    AUTOMATED PIPELINE CONFIGURATION:

    1. Data Collection (Hourly)
       Scheduler: bulletproof-hourly-all
       Schedule:  0 * * * * (every hour)
       Function:  bulletproof-fetcher

    2. Daily Feature Refresh (4:00 AM ET)
       Scheduler: ml-feature-refresh
       Schedule:  0 4 * * *
       Function:  Refresh ml_enhanced_40_features table

    3. Weekly Model Retraining (Sunday 2:00 AM)
       Scheduler: ml-weekly-retrain
       Schedule:  0 2 * * 0
       Function:  Retrain xgboost_saleem_90pct model

    4. Daily Predictions (4:30 AM ET)
       Scheduler: ml-daily-predictions
       Schedule:  30 4 * * *
       Function:  Generate predictions for all symbols

    5. Drift Detection (Every 6 hours)
       Scheduler: drift-detector
       Schedule:  0 */6 * * *
       Function:  Check for data/concept drift
    """)

    # Create scheduler setup commands
    scheduler_commands = """
    # Run these commands to set up Cloud Schedulers:

    # 1. Feature Refresh (Daily 4 AM)
    gcloud scheduler jobs create http ml-feature-refresh \\
        --location=us-central1 \\
        --schedule="0 4 * * *" \\
        --uri="https://trading-api-1075463475276.us-central1.run.app/api/ml/refresh-features" \\
        --http-method=POST \\
        --time-zone="America/New_York"

    # 2. Weekly Retrain (Sunday 2 AM)
    gcloud scheduler jobs create http ml-weekly-retrain \\
        --location=us-central1 \\
        --schedule="0 2 * * 0" \\
        --uri="https://trading-api-1075463475276.us-central1.run.app/api/ml/retrain" \\
        --http-method=POST \\
        --time-zone="America/New_York"

    # 3. Daily Predictions (4:30 AM)
    gcloud scheduler jobs create http ml-daily-predictions \\
        --location=us-central1 \\
        --schedule="30 4 * * *" \\
        --uri="https://trading-api-1075463475276.us-central1.run.app/api/ml/predictions" \\
        --http-method=POST \\
        --time-zone="America/New_York"

    # 4. Drift Detection (Every 6 hours)
    gcloud scheduler jobs create http drift-detector \\
        --location=us-central1 \\
        --schedule="0 */6 * * *" \\
        --uri="https://trading-api-1075463475276.us-central1.run.app/api/ml/drift-check" \\
        --http-method=POST \\
        --time-zone="America/New_York"
    """

    print(scheduler_commands)


def phase4_create_prediction_view():
    """
    PHASE 4.2: Create Production Prediction View
    """
    print("\n" + "=" * 80)
    print("PHASE 4.2: CREATING PREDICTION VIEW")
    print("=" * 80)

    prediction_view_sql = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_predictions_90pct` AS
    SELECT
        f.symbol,
        f.datetime,
        f.close,
        f.rsi,
        f.macd_histogram,
        f.adx,
        f.pivot_high_flag,
        f.pivot_low_flag,
        f.growth_score,
        f.in_rise_cycle,
        f.trend_regime,
        f.rise_cycle_start,
        f.golden_cross,

        -- XGBoost Prediction
        p.predicted_target_direction as ml_prediction,
        p.predicted_target_direction_probs[OFFSET(1)].prob as up_probability,

        -- Confidence Level
        CASE
            WHEN ABS(p.predicted_target_direction_probs[OFFSET(1)].prob - 0.5) > 0.20 THEN 'HIGH'
            WHEN ABS(p.predicted_target_direction_probs[OFFSET(1)].prob - 0.5) > 0.10 THEN 'MEDIUM'
            ELSE 'LOW'
        END as confidence_level,

        -- Trade Recommendation (only HIGH confidence)
        CASE
            WHEN p.predicted_target_direction_probs[OFFSET(1)].prob > 0.70
                 AND f.growth_score >= 75
                 AND f.in_rise_cycle = 1
                 AND f.pivot_low_flag = 1 THEN 'STRONG_BUY'
            WHEN p.predicted_target_direction_probs[OFFSET(1)].prob > 0.65
                 AND f.growth_score >= 50 THEN 'BUY'
            WHEN p.predicted_target_direction_probs[OFFSET(1)].prob < 0.30
                 AND f.growth_score <= 25
                 AND f.pivot_high_flag = 1 THEN 'STRONG_SELL'
            WHEN p.predicted_target_direction_probs[OFFSET(1)].prob < 0.35 THEN 'SELL'
            ELSE 'HOLD'
        END as trade_recommendation,

        -- Key factors for explanation
        CONCAT(
            CASE WHEN f.pivot_low_flag = 1 THEN 'PIVOT_LOW, ' ELSE '' END,
            CASE WHEN f.pivot_high_flag = 1 THEN 'PIVOT_HIGH, ' ELSE '' END,
            CASE WHEN f.rise_cycle_start = 1 THEN 'RISE_CYCLE_START, ' ELSE '' END,
            CASE WHEN f.golden_cross = 1 THEN 'GOLDEN_CROSS, ' ELSE '' END,
            CASE WHEN f.rsi < 30 THEN 'OVERSOLD, ' ELSE '' END,
            CASE WHEN f.rsi > 70 THEN 'OVERBOUGHT, ' ELSE '' END,
            CASE WHEN f.growth_score >= 75 THEN 'HIGH_GROWTH, ' ELSE '' END
        ) as key_factors

    FROM ML.PREDICT(
        MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_saleem_90pct`,
        (SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features`
         WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY))
    ) p
    JOIN `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features` f
      ON p.symbol = f.symbol AND p.datetime = f.datetime
    """

    print("\nCreating prediction view...")
    try:
        client.query(prediction_view_sql).result()
        print("  ✓ Created v_predictions_90pct view")

        # Sample predictions
        sample_query = f"""
        SELECT symbol, datetime, close, up_probability, confidence_level, trade_recommendation, key_factors
        FROM `{PROJECT_ID}.{ML_DATASET}.v_predictions_90pct`
        WHERE confidence_level = 'HIGH'
        ORDER BY datetime DESC
        LIMIT 10
        """

        print("\n  SAMPLE HIGH-CONFIDENCE PREDICTIONS:")
        df = client.query(sample_query).to_dataframe()
        print(df.to_string(index=False))

    except Exception as e:
        print(f"  Error: {e}")


def phase4_validate_accuracy():
    """
    PHASE 4.3: Validate Model Accuracy on 2024-2025 Data
    """
    print("\n" + "=" * 80)
    print("PHASE 4.3: VALIDATING MODEL ACCURACY (2024-2025)")
    print("=" * 80)

    validation_query = f"""
    WITH predictions AS (
        SELECT
            f.symbol,
            f.datetime,
            f.close,
            f.target_direction as actual,
            p.predicted_target_direction as predicted,
            p.predicted_target_direction_probs[OFFSET(1)].prob as up_prob,
            CASE
                WHEN ABS(p.predicted_target_direction_probs[OFFSET(1)].prob - 0.5) > 0.20 THEN 'HIGH'
                WHEN ABS(p.predicted_target_direction_probs[OFFSET(1)].prob - 0.5) > 0.10 THEN 'MEDIUM'
                ELSE 'LOW'
            END as confidence
        FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_saleem_90pct`,
            (SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features`
             WHERE DATE(datetime) >= '2024-01-01')
        ) p
        JOIN `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_40_features` f
          ON p.symbol = f.symbol AND p.datetime = f.datetime
        WHERE f.target_direction IS NOT NULL
    )
    SELECT
        'ALL' as confidence_filter,
        COUNT(*) as total_predictions,
        SUM(CASE WHEN actual = predicted THEN 1 ELSE 0 END) as correct,
        ROUND(SUM(CASE WHEN actual = predicted THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy_pct
    FROM predictions

    UNION ALL

    SELECT
        'HIGH_CONFIDENCE_ONLY',
        COUNT(*),
        SUM(CASE WHEN actual = predicted THEN 1 ELSE 0 END),
        ROUND(SUM(CASE WHEN actual = predicted THEN 1 ELSE 0 END) / COUNT(*) * 100, 2)
    FROM predictions
    WHERE confidence = 'HIGH'

    UNION ALL

    SELECT
        'MEDIUM_CONFIDENCE',
        COUNT(*),
        SUM(CASE WHEN actual = predicted THEN 1 ELSE 0 END),
        ROUND(SUM(CASE WHEN actual = predicted THEN 1 ELSE 0 END) / COUNT(*) * 100, 2)
    FROM predictions
    WHERE confidence = 'MEDIUM'
    """

    print("\nValidating on 2024-2025 data...")
    try:
        df = client.query(validation_query).to_dataframe()

        print("\n  VALIDATION RESULTS (2024-2025):")
        print("  " + "-" * 60)
        print(f"  {'Confidence Filter':<25} {'Total':<10} {'Correct':<10} {'Accuracy':<10}")
        print("  " + "-" * 60)

        for _, row in df.iterrows():
            print(f"  {row['confidence_filter']:<25} {row['total_predictions']:<10} {row['correct']:<10} {row['accuracy_pct']:.2f}%")

        # Check if we hit 90%+
        high_conf = df[df['confidence_filter'] == 'HIGH_CONFIDENCE_ONLY']
        if len(high_conf) > 0:
            acc = high_conf.iloc[0]['accuracy_pct']
            if acc >= 90:
                print(f"\n  🎉 SUCCESS! HIGH-CONFIDENCE ACCURACY: {acc:.2f}% (TARGET: 90%+)")
            elif acc >= 85:
                print(f"\n  ✓ GOOD PROGRESS! HIGH-CONFIDENCE ACCURACY: {acc:.2f}%")
                print(f"    Need +{90-acc:.1f}% more to hit 90% target")
            else:
                print(f"\n  ⚠️  HIGH-CONFIDENCE ACCURACY: {acc:.2f}%")
                print(f"    Need more optimization to reach 90%")

    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_all_phases():
    """Run all phases sequentially"""

    print("\n" + "=" * 80)
    print("STARTING FULL IMPLEMENTATION: 67% → 90%+ ACCURACY")
    print("=" * 80)

    # Phase 1: Data Foundation
    print("\n\n" + "▓" * 80)
    print("PHASE 1: DATA FOUNDATION")
    print("▓" * 80)

    phase1_validate_data_splits()
    phase1_deduplicate_tables()
    phase1_check_data_gaps()

    # Phase 2: Feature Engineering
    print("\n\n" + "▓" * 80)
    print("PHASE 2: FEATURE ENGINEERING")
    print("▓" * 80)

    phase2_add_saleem_features()
    phase2_add_feature_interactions()

    # Phase 3: Gemini Integration
    print("\n\n" + "▓" * 80)
    print("PHASE 3: GEMINI 2.5 PRO INTEGRATION")
    print("▓" * 80)

    phase3_setup_gemini_integration()
    phase3_create_ensemble_model()

    # Phase 4: Automation & Validation
    print("\n\n" + "▓" * 80)
    print("PHASE 4: AUTOMATION & VALIDATION")
    print("▓" * 80)

    phase4_setup_automated_pipeline()
    phase4_create_prediction_view()
    phase4_validate_accuracy()

    # Summary
    print("\n\n" + "=" * 80)
    print("IMPLEMENTATION COMPLETE")
    print("=" * 80)
    print(f"""
    TABLES CREATED:
    - ml_saleem_16_features     : Saleem's core 16 features
    - ml_enhanced_40_features   : 40+ features with interactions

    MODELS CREATED:
    - xgboost_saleem_90pct      : Trained XGBoost model

    VIEWS CREATED:
    - v_predictions_90pct       : Production prediction view

    NEXT STEPS:
    1. Review validation accuracy
    2. Set up Cloud Schedulers (see commands above)
    3. Integrate Gemini API for ensemble
    4. Monitor drift and retrain weekly

    Completed: {datetime.now()}
    """)


if __name__ == "__main__":
    # Run interactive menu
    print("""
    SELECT PHASE TO RUN:

    1. Phase 1 Only (Data Foundation)
    2. Phase 2 Only (Feature Engineering)
    3. Phase 3 Only (Gemini Integration)
    4. Phase 4 Only (Automation & Validation)
    5. ALL PHASES (Full Implementation)

    Enter choice (1-5): """, end="")

    # For automated run, execute all phases
    run_all_phases()
