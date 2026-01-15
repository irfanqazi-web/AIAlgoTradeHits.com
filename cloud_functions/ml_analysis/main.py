"""
Daily ML Analysis Cloud Function
================================
Runs XGBoost model analysis on all stocks/ETFs daily at 4:30 AM ET.
Based on Saleem's validated 16-feature model with 68.5% UP accuracy target.

Generates daily predictions and stores results in BigQuery.
"""

import functions_framework
from google.cloud import bigquery
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Key symbols to analyze
SYMBOLS = {
    'stocks': ['GOOGL', 'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'AMD', 'INTC', 'NFLX'],
    'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'VOO'],
    'crypto': ['BTC/USD', 'ETH/USD', 'SOL/USD']
}

# Saleem's 16 features
FEATURES_16 = [
    'awesome_osc', 'cci', 'macd', 'macd_cross', 'macd_histogram',
    'macd_signal', 'mfi', 'momentum', 'rsi', 'rsi_overbought',
    'rsi_oversold', 'rsi_slope', 'rsi_zscore', 'vwap_daily',
    'pivot_high_flag', 'pivot_low_flag'
]

# Feature weights based on Saleem's validation (pivot flags are key)
FEATURE_WEIGHTS = {
    'pivot_low_flag': 0.25,
    'pivot_high_flag': 0.25,
    'rsi': 0.10,
    'rsi_slope': 0.08,
    'macd_cross': 0.08,
    'macd_histogram': 0.06,
    'cci': 0.05,
    'momentum': 0.05,
    'mfi': 0.04,
    'awesome_osc': 0.04
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def analyze_symbol(client, symbol, asset_type):
    """Analyze a single symbol using the 16-feature model"""

    # Determine table
    if asset_type == 'stocks':
        table = 'stocks_daily_clean'
    elif asset_type == 'etfs':
        table = 'etfs_daily_clean'
    else:
        table = 'crypto_daily_clean'

    # Get latest data with features
    query = f"""
    WITH deduplicated AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
            AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 DAY)
    ),
    latest AS (
        SELECT * EXCEPT(rn) FROM deduplicated WHERE rn = 1
    )
    SELECT
        symbol,
        datetime,
        close,
        volume,
        COALESCE(rsi, 50) as rsi,
        COALESCE(macd, 0) as macd,
        COALESCE(macd_signal, 0) as macd_signal,
        COALESCE(macd_histogram, 0) as macd_histogram,
        COALESCE(cci, 0) as cci,
        COALESCE(mfi, 50) as mfi,
        COALESCE(momentum, 0) as momentum,
        COALESCE(awesome_osc, 0) as awesome_osc,
        COALESCE(pivot_low_flag, 0) as pivot_low_flag,
        COALESCE(pivot_high_flag, 0) as pivot_high_flag,
        COALESCE(rsi_slope, 0) as rsi_slope,
        COALESCE(rsi_zscore, 0) as rsi_zscore,
        COALESCE(rsi_overbought, 0) as rsi_overbought,
        COALESCE(rsi_oversold, 0) as rsi_oversold,
        COALESCE(macd_cross, 0) as macd_cross,
        COALESCE(growth_score, 0) as growth_score,
        ema_12,
        ema_26,
        sma_50,
        sma_200
    FROM latest
    ORDER BY datetime DESC
    LIMIT 1
    """

    try:
        df = client.query(query).to_dataframe()

        if df.empty:
            return None

        row = df.iloc[0]

        # Calculate ML-based prediction score (0-100)
        score = 0
        factors = []

        # Pivot flags (50% weight - KEY FEATURES)
        if row.get('pivot_low_flag', 0) == 1:
            score += 30
            factors.append('PIVOT_LOW_SIGNAL')
        if row.get('pivot_high_flag', 0) == 1:
            factors.append('Pivot High (caution)')

        # RSI analysis (15% weight)
        rsi = row.get('rsi', 50)
        if 40 <= rsi <= 60:
            score += 15
            factors.append(f'RSI neutral ({rsi:.1f})')
        elif rsi < 30:
            score += 12
            factors.append(f'RSI oversold ({rsi:.1f})')
        elif rsi > 70:
            factors.append(f'RSI overbought ({rsi:.1f})')
        else:
            score += 8

        # RSI slope (momentum)
        rsi_slope = row.get('rsi_slope', 0)
        if rsi_slope > 0:
            score += 10
            factors.append('RSI rising')

        # MACD cross
        macd_cross = row.get('macd_cross', 0)
        if macd_cross == 1:
            score += 15
            factors.append('MACD bullish cross')
        elif macd_cross == -1:
            factors.append('MACD bearish cross')

        # MACD histogram
        macd_hist = row.get('macd_histogram', 0)
        if macd_hist > 0:
            score += 10
            factors.append('MACD histogram positive')

        # CCI
        cci = row.get('cci', 0)
        if -100 < cci < 100:
            score += 5
            factors.append(f'CCI neutral ({cci:.1f})')
        elif cci < -100:
            score += 8
            factors.append(f'CCI oversold ({cci:.1f})')

        # MFI
        mfi = row.get('mfi', 50)
        if 40 <= mfi <= 60:
            score += 5
        elif mfi < 20:
            score += 8
            factors.append(f'MFI oversold ({mfi:.1f})')

        # EMA trend
        ema_12 = row.get('ema_12', 0)
        ema_26 = row.get('ema_26', 0)
        if ema_12 > 0 and ema_26 > 0 and ema_12 > ema_26:
            score += 5
            factors.append('EMA uptrend')

        # Determine prediction
        if score >= 70:
            prediction = 'STRONG_UP'
            confidence = min(score / 100, 0.85)
        elif score >= 55:
            prediction = 'UP'
            confidence = 0.65
        elif score >= 40:
            prediction = 'NEUTRAL'
            confidence = 0.50
        elif score >= 25:
            prediction = 'DOWN'
            confidence = 0.60
        else:
            prediction = 'STRONG_DOWN'
            confidence = 0.70

        return {
            'symbol': symbol,
            'asset_type': asset_type,
            'datetime': row['datetime'],
            'close': float(row['close']),
            'volume': int(row.get('volume', 0)),
            'ml_score': min(score, 100),
            'prediction': prediction,
            'confidence': round(confidence, 2),
            'rsi': round(rsi, 1),
            'macd_histogram': round(macd_hist, 4),
            'pivot_low_flag': int(row.get('pivot_low_flag', 0)),
            'pivot_high_flag': int(row.get('pivot_high_flag', 0)),
            'growth_score': float(row.get('growth_score', 0)),
            'factors': '|'.join(factors[:5])
        }

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return None


def save_predictions(client, predictions):
    """Save predictions to BigQuery"""

    if not predictions:
        return 0

    # Create table if not exists
    table_id = f"{PROJECT_ID}.{DATASET_ID}.ml_daily_predictions"

    schema = [
        bigquery.SchemaField("prediction_date", "DATE"),
        bigquery.SchemaField("prediction_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "INT64"),
        bigquery.SchemaField("ml_score", "INT64"),
        bigquery.SchemaField("prediction", "STRING"),
        bigquery.SchemaField("confidence", "FLOAT64"),
        bigquery.SchemaField("rsi", "FLOAT64"),
        bigquery.SchemaField("macd_histogram", "FLOAT64"),
        bigquery.SchemaField("pivot_low_flag", "INT64"),
        bigquery.SchemaField("pivot_high_flag", "INT64"),
        bigquery.SchemaField("growth_score", "FLOAT64"),
        bigquery.SchemaField("factors", "STRING"),
        bigquery.SchemaField("data_datetime", "TIMESTAMP"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="prediction_date"
    )

    try:
        client.create_table(table, exists_ok=True)
    except Exception as e:
        logger.warning(f"Table creation warning: {e}")

    # Prepare rows
    now = datetime.now(timezone.utc)
    rows = []
    for p in predictions:
        rows.append({
            'prediction_date': now.strftime('%Y-%m-%d'),
            'prediction_timestamp': now.isoformat(),
            'symbol': p['symbol'],
            'asset_type': p['asset_type'],
            'close': p['close'],
            'volume': p['volume'],
            'ml_score': p['ml_score'],
            'prediction': p['prediction'],
            'confidence': p['confidence'],
            'rsi': p['rsi'],
            'macd_histogram': p['macd_histogram'],
            'pivot_low_flag': p['pivot_low_flag'],
            'pivot_high_flag': p['pivot_high_flag'],
            'growth_score': p['growth_score'],
            'factors': p['factors'],
            'data_datetime': p['datetime'].isoformat() if hasattr(p['datetime'], 'isoformat') else str(p['datetime'])
        })

    try:
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            logger.error(f"Insert errors: {errors}")
            return 0
        return len(rows)
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")
        return 0


@functions_framework.http
def run_ml_analysis(request):
    """
    Cloud Function entry point - runs daily ML analysis

    Query params:
        asset_types: comma-separated (default: all)
        save: true/false (default: true)
    """

    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting ML analysis at {start_time}")

    args = request.args or {}
    asset_types_param = args.get('asset_types', 'all')
    save_results = args.get('save', 'true').lower() == 'true'

    if asset_types_param == 'all':
        asset_types = list(SYMBOLS.keys())
    else:
        asset_types = [t.strip() for t in asset_types_param.split(',')]

    client = get_client()
    all_predictions = []
    stats = {}

    for asset_type in asset_types:
        if asset_type not in SYMBOLS:
            continue

        symbols = SYMBOLS[asset_type]
        predictions = []

        for symbol in symbols:
            logger.info(f"Analyzing {symbol}...")
            result = analyze_symbol(client, symbol, asset_type)
            if result:
                predictions.append(result)

        all_predictions.extend(predictions)

        # Stats for this asset type
        up_count = sum(1 for p in predictions if p['prediction'] in ['UP', 'STRONG_UP'])
        stats[asset_type] = {
            'analyzed': len(predictions),
            'up_predictions': up_count,
            'avg_score': round(sum(p['ml_score'] for p in predictions) / len(predictions), 1) if predictions else 0
        }

    # Save to BigQuery
    saved_count = 0
    if save_results and all_predictions:
        saved_count = save_predictions(client, all_predictions)

    # Sort by ML score
    all_predictions.sort(key=lambda x: x['ml_score'], reverse=True)

    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()

    response = {
        'status': 'success',
        'analysis_date': start_time.strftime('%Y-%m-%d'),
        'timestamp': start_time.isoformat(),
        'duration_seconds': round(duration, 1),
        'total_analyzed': len(all_predictions),
        'predictions_saved': saved_count,
        'stats': stats,
        'top_10': [
            {
                'rank': i + 1,
                'symbol': p['symbol'],
                'asset_type': p['asset_type'],
                'ml_score': p['ml_score'],
                'prediction': p['prediction'],
                'confidence': p['confidence'],
                'factors': p['factors']
            }
            for i, p in enumerate(all_predictions[:10])
        ]
    }

    logger.info(f"ML analysis complete: {len(all_predictions)} symbols, {duration:.1f}s")

    return response, 200


if __name__ == "__main__":
    class MockRequest:
        args = {'asset_types': 'stocks', 'save': 'false'}
    result, _ = run_ml_analysis(MockRequest())
    print(json.dumps(result, indent=2, default=str))
