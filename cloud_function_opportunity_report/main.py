"""
Daily Opportunity Report Generator
==================================

Analyzes ALL assets (Stocks, Crypto, ETFs, Forex, Indices, Commodities)
and generates a ranked opportunity report stored in BigQuery.

Runs daily via Cloud Scheduler at market close (4:30 PM ET)

Based on validated ML model:
- 68.5% UP accuracy
- Key features: pivot_low_flag, pivot_high_flag, Growth Score, EMA cycles
"""

import functions_framework
from google.cloud import bigquery
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Asset type configurations
ASSET_CONFIGS = {
    'stocks': {
        'daily_table': 'stocks_daily_clean',
        'hourly_table': 'stocks_hourly_clean',
        'display_name': 'Stocks'
    },
    'crypto': {
        'daily_table': 'crypto_daily_clean',
        'hourly_table': 'crypto_hourly_clean',
        'display_name': 'Crypto'
    },
    'etfs': {
        'daily_table': 'etfs_daily_clean',
        'hourly_table': 'etfs_hourly_clean',
        'display_name': 'ETFs'
    },
    'forex': {
        'daily_table': 'forex_daily_clean',
        'hourly_table': 'forex_hourly_clean',
        'display_name': 'Forex'
    },
    'indices': {
        'daily_table': 'v2_indices_daily',
        'hourly_table': 'v2_indices_hourly',
        'display_name': 'Indices'
    },
    'commodities': {
        'daily_table': 'v2_commodities_daily',
        'hourly_table': 'v2_commodities_hourly',
        'display_name': 'Commodities'
    }
}

def get_bigquery_client():
    """Get BigQuery client"""
    return bigquery.Client(project=PROJECT_ID)


def calculate_opportunity_score(row: Dict) -> Dict:
    """
    Calculate opportunity score based on validated ML model features

    Scoring (0-100):
    - Growth Score component: 40 points max
    - EMA Cycle: 20 points max
    - RSI positioning: 15 points max
    - MACD momentum: 10 points max
    - Pivot signals: 10 points max
    - Trend alignment: 5 points max
    """
    score = 0
    factors = []

    # 1. Growth Score (40 points) - Most important per validation
    growth_score = float(row.get('growth_score') or 0)
    if growth_score >= 75:
        score += 40
        factors.append('Growth Score EXCELLENT (75+)')
    elif growth_score >= 50:
        score += 25
        factors.append('Growth Score GOOD (50-74)')
    elif growth_score >= 25:
        score += 10
        factors.append('Growth Score FAIR (25-49)')

    # 2. EMA Cycle (20 points)
    ema_12 = float(row.get('ema_12') or 0)
    ema_26 = float(row.get('ema_26') or 0)
    in_rise_cycle = ema_12 > ema_26 if ema_12 > 0 and ema_26 > 0 else False

    if in_rise_cycle:
        score += 20
        factors.append('EMA Rise Cycle ACTIVE')

    # 3. RSI Sweet Spot (15 points)
    rsi = float(row.get('rsi') or row.get('rsi_14') or 50)
    if 40 <= rsi <= 65:
        score += 15
        factors.append(f'RSI Sweet Spot ({rsi:.1f})')
    elif rsi < 30:
        score += 12
        factors.append(f'RSI Oversold ({rsi:.1f})')
    elif rsi > 70:
        score -= 5
        factors.append(f'RSI Overbought ({rsi:.1f})')

    # 4. MACD Momentum (10 points)
    macd_hist = float(row.get('macd_histogram') or row.get('macd_hist') or 0)
    if macd_hist > 0:
        score += 10
        factors.append('MACD Bullish')
    elif macd_hist < 0:
        factors.append('MACD Bearish')

    # 5. Pivot Signals (10 points) - KEY FEATURE per validation
    pivot_low = int(row.get('pivot_low_flag') or 0)
    pivot_high = int(row.get('pivot_high_flag') or 0)

    if pivot_low == 1:
        score += 10
        factors.append('PIVOT LOW Signal!')
    if pivot_high == 1:
        factors.append('Pivot High (caution)')

    # 6. Trend Alignment (5 points)
    close = float(row.get('close') or 0)
    sma_200 = float(row.get('sma_200') or 0)
    sma_50 = float(row.get('sma_50') or 0)

    if close > 0 and sma_200 > 0 and close > sma_200:
        score += 3
        factors.append('Above 200 SMA')
    if close > 0 and sma_50 > 0 and close > sma_50:
        score += 2
        factors.append('Above 50 SMA')

    # Determine recommendation
    if score >= 80:
        recommendation = 'STRONG_BUY'
    elif score >= 60:
        recommendation = 'BUY'
    elif score >= 40:
        recommendation = 'HOLD'
    elif score >= 20:
        recommendation = 'SELL'
    else:
        recommendation = 'STRONG_SELL'

    # Calculate confidence
    confidence = min(len([f for f in factors if 'EXCELLENT' in f or 'ACTIVE' in f or 'Signal' in f]) / 3.0, 1.0)

    return {
        'opportunity_score': min(max(score, 0), 100),
        'recommendation': recommendation,
        'confidence': round(confidence, 2),
        'factors': factors,
        'in_rise_cycle': in_rise_cycle,
        'growth_score': growth_score,
        'rsi': rsi,
        'macd_histogram': macd_hist,
        'pivot_low': pivot_low == 1,
        'pivot_high': pivot_high == 1
    }


def analyze_asset_type(client: bigquery.Client, asset_type: str, config: Dict) -> List[Dict]:
    """Analyze all symbols for an asset type"""

    daily_table = config['daily_table']

    query = f"""
    WITH latest_data AS (
        SELECT
            symbol,
            datetime,
            close,
            open,
            high,
            low,
            volume,
            rsi,
            rsi_14,
            macd,
            macd_signal,
            macd_histogram,
            macd_hist,
            ema_12,
            ema_26,
            sma_20,
            sma_50,
            sma_200,
            growth_score,
            sentiment_score,
            pivot_low_flag,
            pivot_high_flag,
            adx,
            atr,
            mfi,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{daily_table}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    )
    SELECT * FROM latest_data WHERE rn = 1
    """

    try:
        df = client.query(query).to_dataframe()

        if df.empty:
            logger.warning(f"No data found for {asset_type}")
            return []

        results = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            analysis = calculate_opportunity_score(row_dict)

            # Calculate daily change
            close = float(row_dict.get('close') or 0)
            open_price = float(row_dict.get('open') or close)
            daily_change = ((close - open_price) / open_price * 100) if open_price > 0 else 0

            results.append({
                'symbol': row_dict['symbol'],
                'asset_type': asset_type,
                'close': close,
                'daily_change_pct': round(daily_change, 2),
                'volume': int(row_dict.get('volume') or 0),
                'opportunity_score': analysis['opportunity_score'],
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence'],
                'growth_score': analysis['growth_score'],
                'rsi': round(analysis['rsi'], 1),
                'in_rise_cycle': analysis['in_rise_cycle'],
                'pivot_low_signal': analysis['pivot_low'],
                'pivot_high_signal': analysis['pivot_high'],
                'macd_histogram': round(analysis['macd_histogram'], 4),
                'factors': '|'.join(analysis['factors'][:5]),  # Top 5 factors
                'datetime': row_dict['datetime'],
                'sma_50': float(row_dict.get('sma_50') or 0),
                'sma_200': float(row_dict.get('sma_200') or 0),
                'adx': float(row_dict.get('adx') or 0),
                'sentiment_score': float(row_dict.get('sentiment_score') or 0)
            })

        return results

    except Exception as e:
        logger.error(f"Error analyzing {asset_type}: {e}")
        return []


def create_opportunity_table(client: bigquery.Client):
    """Create the opportunity report table if it doesn't exist"""

    schema = [
        bigquery.SchemaField("report_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("report_timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("daily_change_pct", "FLOAT64"),
        bigquery.SchemaField("volume", "INT64"),
        bigquery.SchemaField("opportunity_score", "INT64"),
        bigquery.SchemaField("rank_in_type", "INT64"),
        bigquery.SchemaField("rank_overall", "INT64"),
        bigquery.SchemaField("recommendation", "STRING"),
        bigquery.SchemaField("confidence", "FLOAT64"),
        bigquery.SchemaField("growth_score", "FLOAT64"),
        bigquery.SchemaField("rsi", "FLOAT64"),
        bigquery.SchemaField("in_rise_cycle", "BOOLEAN"),
        bigquery.SchemaField("pivot_low_signal", "BOOLEAN"),
        bigquery.SchemaField("pivot_high_signal", "BOOLEAN"),
        bigquery.SchemaField("macd_histogram", "FLOAT64"),
        bigquery.SchemaField("factors", "STRING"),
        bigquery.SchemaField("sma_50", "FLOAT64"),
        bigquery.SchemaField("sma_200", "FLOAT64"),
        bigquery.SchemaField("adx", "FLOAT64"),
        bigquery.SchemaField("sentiment_score", "FLOAT64"),
        bigquery.SchemaField("data_datetime", "TIMESTAMP"),
    ]

    table_id = f"{PROJECT_ID}.{DATASET_ID}.daily_opportunity_report"

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="report_date"
    )

    try:
        client.create_table(table, exists_ok=True)
        logger.info(f"Table {table_id} ready")
    except Exception as e:
        logger.error(f"Error creating table: {e}")


def save_opportunity_report(client: bigquery.Client, all_results: List[Dict], report_date: datetime):
    """Save opportunity report to BigQuery"""

    if not all_results:
        logger.warning("No results to save")
        return 0

    # Sort by opportunity score (highest first)
    all_results.sort(key=lambda x: x['opportunity_score'], reverse=True)

    # Add overall rank
    for i, result in enumerate(all_results):
        result['rank_overall'] = i + 1

    # Add rank within asset type
    asset_ranks = {}
    for result in all_results:
        asset_type = result['asset_type']
        if asset_type not in asset_ranks:
            asset_ranks[asset_type] = 0
        asset_ranks[asset_type] += 1
        result['rank_in_type'] = asset_ranks[asset_type]

    # Prepare rows for BigQuery
    rows = []
    for result in all_results:
        rows.append({
            'report_date': report_date.strftime('%Y-%m-%d'),
            'report_timestamp': datetime.now(timezone.utc).isoformat(),
            'symbol': result['symbol'],
            'asset_type': result['asset_type'],
            'close': result['close'],
            'daily_change_pct': result['daily_change_pct'],
            'volume': result['volume'],
            'opportunity_score': result['opportunity_score'],
            'rank_in_type': result['rank_in_type'],
            'rank_overall': result['rank_overall'],
            'recommendation': result['recommendation'],
            'confidence': result['confidence'],
            'growth_score': result['growth_score'],
            'rsi': result['rsi'],
            'in_rise_cycle': result['in_rise_cycle'],
            'pivot_low_signal': result['pivot_low_signal'],
            'pivot_high_signal': result['pivot_high_signal'],
            'macd_histogram': result['macd_histogram'],
            'factors': result['factors'],
            'sma_50': result['sma_50'],
            'sma_200': result['sma_200'],
            'adx': result['adx'],
            'sentiment_score': result['sentiment_score'],
            'data_datetime': result['datetime'].isoformat() if hasattr(result['datetime'], 'isoformat') else str(result['datetime'])
        })

    # Upload to BigQuery
    table_id = f"{PROJECT_ID}.{DATASET_ID}.daily_opportunity_report"

    try:
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            logger.error(f"BigQuery insert errors: {errors}")
            return 0

        logger.info(f"Saved {len(rows)} opportunity records")
        return len(rows)

    except Exception as e:
        logger.error(f"Error saving to BigQuery: {e}")
        return 0


def generate_summary(all_results: List[Dict]) -> Dict:
    """Generate summary statistics for the report"""

    if not all_results:
        return {}

    df = pd.DataFrame(all_results)

    summary = {
        'total_assets_analyzed': len(df),
        'strong_buy_count': len(df[df['recommendation'] == 'STRONG_BUY']),
        'buy_count': len(df[df['recommendation'] == 'BUY']),
        'hold_count': len(df[df['recommendation'] == 'HOLD']),
        'sell_count': len(df[df['recommendation'] == 'SELL']),
        'strong_sell_count': len(df[df['recommendation'] == 'STRONG_SELL']),
        'avg_opportunity_score': round(df['opportunity_score'].mean(), 1),
        'rise_cycle_count': len(df[df['in_rise_cycle'] == True]),
        'pivot_low_count': len(df[df['pivot_low_signal'] == True]),
        'by_asset_type': {}
    }

    for asset_type in df['asset_type'].unique():
        asset_df = df[df['asset_type'] == asset_type]
        summary['by_asset_type'][asset_type] = {
            'count': len(asset_df),
            'strong_buy': len(asset_df[asset_df['recommendation'] == 'STRONG_BUY']),
            'buy': len(asset_df[asset_df['recommendation'] == 'BUY']),
            'avg_score': round(asset_df['opportunity_score'].mean(), 1),
            'top_symbol': asset_df.iloc[0]['symbol'] if len(asset_df) > 0 else None,
            'top_score': int(asset_df.iloc[0]['opportunity_score']) if len(asset_df) > 0 else 0
        }

    # Top 10 overall
    summary['top_10_overall'] = [
        {
            'rank': i + 1,
            'symbol': r['symbol'],
            'asset_type': r['asset_type'],
            'score': r['opportunity_score'],
            'recommendation': r['recommendation']
        }
        for i, r in enumerate(all_results[:10])
    ]

    return summary


@functions_framework.http
def generate_opportunity_report(request):
    """
    Cloud Function entry point - generates daily opportunity report

    Query params:
        asset_types: comma-separated list (default: all)
        save: true/false - whether to save to BigQuery (default: true)
    """

    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting Opportunity Report generation at {start_time}")

    # Parse parameters
    request_json = request.get_json(silent=True) or {}
    args = request.args

    asset_types_param = args.get('asset_types') or request_json.get('asset_types') or 'all'
    save_to_bq = (args.get('save') or request_json.get('save') or 'true').lower() == 'true'

    # Determine asset types to analyze
    if asset_types_param == 'all':
        asset_types = list(ASSET_CONFIGS.keys())
    else:
        asset_types = [t.strip() for t in asset_types_param.split(',')]

    logger.info(f"Analyzing asset types: {asset_types}")

    client = get_bigquery_client()

    # Create table if needed
    if save_to_bq:
        create_opportunity_table(client)

    # Analyze all asset types
    all_results = []
    analysis_stats = {}

    for asset_type in asset_types:
        if asset_type not in ASSET_CONFIGS:
            logger.warning(f"Unknown asset type: {asset_type}")
            continue

        config = ASSET_CONFIGS[asset_type]
        logger.info(f"Analyzing {config['display_name']}...")

        results = analyze_asset_type(client, asset_type, config)
        all_results.extend(results)

        analysis_stats[asset_type] = {
            'count': len(results),
            'strong_buy': len([r for r in results if r['recommendation'] == 'STRONG_BUY']),
            'buy': len([r for r in results if r['recommendation'] == 'BUY'])
        }

        logger.info(f"  {asset_type}: {len(results)} symbols analyzed")

    # Sort all results by opportunity score
    all_results.sort(key=lambda x: x['opportunity_score'], reverse=True)

    # Generate summary
    summary = generate_summary(all_results)

    # Save to BigQuery
    saved_count = 0
    if save_to_bq and all_results:
        saved_count = save_opportunity_report(client, all_results, start_time)

    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()

    response = {
        'status': 'success',
        'report_date': start_time.strftime('%Y-%m-%d'),
        'report_timestamp': start_time.isoformat(),
        'duration_seconds': round(duration, 1),
        'total_assets_analyzed': len(all_results),
        'records_saved': saved_count,
        'analysis_stats': analysis_stats,
        'summary': summary,
        'top_10': [
            {
                'rank': i + 1,
                'symbol': r['symbol'],
                'asset_type': r['asset_type'],
                'opportunity_score': r['opportunity_score'],
                'recommendation': r['recommendation'],
                'growth_score': r['growth_score'],
                'rsi': r['rsi'],
                'in_rise_cycle': r['in_rise_cycle'],
                'factors': r['factors']
            }
            for i, r in enumerate(all_results[:10])
        ]
    }

    logger.info(f"Report complete: {len(all_results)} assets, {saved_count} saved, {duration:.1f}s")

    return response, 200


# For local testing
if __name__ == "__main__":
    class MockRequest:
        args = {'asset_types': 'stocks,crypto', 'save': 'false'}
        def get_json(self, silent=False):
            return None

    result, status = generate_opportunity_report(MockRequest())
    print(json.dumps(result, indent=2, default=str))
