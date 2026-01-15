-- Migrate and consolidate data using BigQuery SQL (fastest approach)
-- Handles all data type conversions and basic calculations in the database

INSERT INTO `aialgotradehits.crypto_trading_data.stocks_daily_clean`
(datetime, symbol, open, high, low, close, previous_close, volume,
 average_volume, change, percent_change, high_low, pct_high_low, week_52_high, week_52_low,
 name, sector, industry, asset_type, exchange, mic_code, country, currency, type,
 timestamp, data_source, created_at, updated_at)

WITH consolidated AS (
    -- Union all 3 source tables
    SELECT
        d.datetime,
        d.symbol,
        d.open,
        d.high,
        d.low,
        d.close,
        CAST(d.volume AS INT64) as volume,
        COALESCE(m.name, d.name) as name,
        COALESCE(m.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, 'US') as country,
        COALESCE(m.currency, d.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        1 as priority
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily` d
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON d.symbol = m.symbol

    UNION ALL

    SELECT
        s.datetime,
        s.symbol,
        s.open,
        s.high,
        s.low,
        s.close,
        SAFE_CAST(s.volume AS INT64) as volume,
        COALESCE(m.name, s.name) as name,
        COALESCE(m.exchange, s.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, 'US') as country,
        COALESCE(m.currency, s.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        2 as priority
    FROM `aialgotradehits.crypto_trading_data.stocks_unified_daily` s
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON s.symbol = m.symbol

    UNION ALL

    SELECT
        h.datetime,
        h.symbol,
        h.open,
        h.high,
        h.low,
        h.close,
        SAFE_CAST(h.volume AS INT64) as volume,
        COALESCE(m.name, h.name) as name,
        COALESCE(m.exchange, h.exchange, 'UNKNOWN') as exchange,
        COALESCE(m.mic_code, 'UNKNOWN') as mic_code,
        COALESCE(m.sector, 'UNKNOWN') as sector,
        COALESCE(m.industry, 'UNKNOWN') as industry,
        COALESCE(m.asset_type, h.asset_type, 'Common Stock') as asset_type,
        COALESCE(m.country, h.country, 'US') as country,
        COALESCE(m.currency, h.currency, 'USD') as currency,
        COALESCE(m.type, 'Common Stock') as type,
        3 as priority
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_historical_daily` h
    LEFT JOIN `aialgotradehits.crypto_trading_data.v2_stocks_master` m
        ON h.symbol = m.symbol
),

deduplicated AS (
    -- Keep only one row per symbol+datetime (prioritize v2_stocks_daily)
    SELECT * EXCEPT(row_num, priority)
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY symbol, datetime
                ORDER BY priority
            ) as row_num
        FROM consolidated
    )
    WHERE row_num = 1
),

with_calcs AS (
    -- Add calculated fields (window functions for moving calculations)
    SELECT
        *,
        LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) as previous_close,
        AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as average_volume_float,
        MAX(high) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) as week_52_high,
        MIN(low) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) as week_52_low
    FROM deduplicated
    WHERE mic_code IN ('XNAS', 'XNGS', 'XNCM', 'XNMS', 'XNYS', 'ARCX', 'XASE', 'BATS', 'CBOE', 'XCBO')
        AND open > 0
        AND high > 0
        AND low > 0
        AND close > 0
        AND volume > 0
)

SELECT
    datetime,
    symbol,
    open,
    high,
    low,
    close,
    previous_close,
    volume,
    CAST(average_volume_float AS INT64) as average_volume,
    close - previous_close as change,
    SAFE_DIVIDE((close - previous_close), previous_close) * 100 as percent_change,
    high - low as high_low,
    SAFE_DIVIDE((high - low), low) * 100 as pct_high_low,
    week_52_high,
    week_52_low,
    -- Indicators (NULL for now)
    CAST(NULL AS FLOAT64) as rsi,
    CAST(NULL AS FLOAT64) as macd,
    CAST(NULL AS FLOAT64) as macd_signal,
    CAST(NULL AS FLOAT64) as macd_histogram,
    CAST(NULL AS FLOAT64) as stoch_k,
    CAST(NULL AS FLOAT64) as stoch_d,
    CAST(NULL AS FLOAT64) as cci,
    CAST(NULL AS FLOAT64) as williams_r,
    CAST(NULL AS FLOAT64) as momentum,
    CAST(NULL AS FLOAT64) as sma_20,
    CAST(NULL AS FLOAT64) as sma_50,
    CAST(NULL AS FLOAT64) as sma_200,
    CAST(NULL AS FLOAT64) as ema_12,
    CAST(NULL AS FLOAT64) as ema_20,
    CAST(NULL AS FLOAT64) as ema_26,
    CAST(NULL AS FLOAT64) as ema_50,
    CAST(NULL AS FLOAT64) as ema_200,
    CAST(NULL AS FLOAT64) as kama,
    CAST(NULL AS FLOAT64) as bollinger_upper,
    CAST(NULL AS FLOAT64) as bollinger_middle,
    CAST(NULL AS FLOAT64) as bollinger_lower,
    CAST(NULL AS FLOAT64) as bb_width,
    CAST(NULL AS FLOAT64) as adx,
    CAST(NULL AS FLOAT64) as plus_di,
    CAST(NULL AS FLOAT64) as minus_di,
    CAST(NULL AS FLOAT64) as atr,
    CAST(NULL AS FLOAT64) as trix,
    CAST(NULL AS FLOAT64) as roc,
    CAST(NULL AS FLOAT64) as obv,
    CAST(NULL AS FLOAT64) as pvo,
    CAST(NULL AS FLOAT64) as ppo,
    CAST(NULL AS FLOAT64) as ultimate_osc,
    CAST(NULL AS FLOAT64) as awesome_osc,
    CAST(NULL AS FLOAT64) as log_return,
    CAST(NULL AS FLOAT64) as return_2w,
    CAST(NULL AS FLOAT64) as return_4w,
    CAST(NULL AS FLOAT64) as close_vs_sma20_pct,
    CAST(NULL AS FLOAT64) as close_vs_sma50_pct,
    CAST(NULL AS FLOAT64) as close_vs_sma200_pct,
    CAST(NULL AS FLOAT64) as rsi_slope,
    CAST(NULL AS FLOAT64) as rsi_zscore,
    CAST(NULL AS INT64) as rsi_overbought,
    CAST(NULL AS INT64) as rsi_oversold,
    CAST(NULL AS INT64) as macd_cross,
    CAST(NULL AS FLOAT64) as ema20_slope,
    CAST(NULL AS FLOAT64) as ema50_slope,
    CAST(NULL AS FLOAT64) as atr_zscore,
    CAST(NULL AS FLOAT64) as atr_slope,
    CAST(NULL AS FLOAT64) as volume_zscore,
    CAST(NULL AS FLOAT64) as volume_ratio,
    CAST(NULL AS INT64) as pivot_high_flag,
    CAST(NULL AS INT64) as pivot_low_flag,
    CAST(NULL AS FLOAT64) as dist_to_pivot_high,
    CAST(NULL AS FLOAT64) as dist_to_pivot_low,
    CAST(NULL AS INT64) as trend_regime,
    CAST(NULL AS INT64) as vol_regime,
    CAST(NULL AS FLOAT64) as regime_confidence,
    -- Metadata
    name,
    sector,
    industry,
    asset_type,
    exchange,
    mic_code,
    country,
    currency,
    type,
    -- System
    UNIX_SECONDS(datetime) as timestamp,
    'TwelveData' as data_source,
    CURRENT_TIMESTAMP() as created_at,
    CURRENT_TIMESTAMP() as updated_at
FROM with_calcs
ORDER BY symbol, datetime;
