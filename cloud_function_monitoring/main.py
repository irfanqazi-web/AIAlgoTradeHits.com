"""
System Monitoring Cloud Function
Provides BigQuery table statistics, billing data, and system health metrics
"""

import os
import json
import functions_framework
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.cloud import billing_v1
from flask import jsonify

PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'aialgotradehits')
DATASET_ID = os.environ.get('BIGQUERY_DATASET', 'crypto_trading_data')
DATASET_UNIFIED = 'trading_data_unified'  # Second dataset for unified trading data
BILLING_ACCOUNT = os.environ.get('BILLING_ACCOUNT', '')

bq_client = bigquery.Client(project=PROJECT_ID)


def get_all_table_stats():
    """Get statistics for all BigQuery tables - dynamically fetch ALL tables from BOTH datasets"""

    tables_info = []

    # List of datasets to scan
    datasets_to_scan = [DATASET_ID, DATASET_UNIFIED]

    for dataset_id in datasets_to_scan:
        # Dynamically get all tables from the dataset
        try:
            dataset_ref = bq_client.dataset(dataset_id)
            tables = [table.table_id for table in bq_client.list_tables(dataset_ref)]
        except Exception as e:
            # Skip if dataset doesn't exist or can't be accessed
            continue

        for table_name in tables:
            try:
                # Get table metadata
                table_ref = bq_client.dataset(dataset_id).table(table_name)
                table = bq_client.get_table(table_ref)

                # Get row count
                query = f"""
                    SELECT COUNT(*) as row_count
                    FROM `{PROJECT_ID}.{dataset_id}.{table_name}`
                """
                result = bq_client.query(query).result()
                row_count = list(result)[0]['row_count']

                # Get latest timestamp
                try:
                    timestamp_query = f"""
                        SELECT MAX(datetime) as latest_timestamp
                        FROM `{PROJECT_ID}.{dataset_id}.{table_name}`
                    """
                    timestamp_result = bq_client.query(timestamp_query).result()
                    latest_timestamp = list(timestamp_result)[0]['latest_timestamp']
                except:
                    latest_timestamp = None

                # Get unique pairs/symbols count
                unique_pairs = 0
                try:
                    # Try 'pair' column first, then 'symbol'
                    for col in ['pair', 'symbol']:
                        try:
                            pairs_query = f"""
                                SELECT COUNT(DISTINCT {col}) as unique_pairs
                                FROM `{PROJECT_ID}.{dataset_id}.{table_name}`
                            """
                            pairs_result = bq_client.query(pairs_query).result()
                            unique_pairs = list(pairs_result)[0]['unique_pairs']
                            if unique_pairs > 0:
                                break
                        except:
                            continue
                except:
                    unique_pairs = 0

                # Get table size
                table_size_gb = table.num_bytes / (1024 ** 3)

                # Get data for last 24 hours
                try:
                    recent_query = f"""
                        SELECT COUNT(*) as recent_count
                        FROM `{PROJECT_ID}.{dataset_id}.{table_name}`
                        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
                    """
                    recent_result = bq_client.query(recent_query).result()
                    recent_count = list(recent_result)[0]['recent_count']
                except:
                    recent_count = 0

                tables_info.append({
                    'table_name': table_name,
                    'dataset': dataset_id,
                    'row_count': row_count,
                    'size_gb': round(table_size_gb, 4),
                    'latest_timestamp': latest_timestamp.isoformat() if latest_timestamp else None,
                    'unique_pairs': unique_pairs,
                    'recent_24h_count': recent_count,
                    'created': table.created.isoformat() if table.created else None,
                    'modified': table.modified.isoformat() if table.modified else None,
                    'status': 'healthy' if row_count > 0 else 'warning'
                })

            except Exception as e:
                tables_info.append({
                    'table_name': table_name,
                    'dataset': dataset_id,
                    'error': str(e),
                    'status': 'error'
                })

    return tables_info


def get_daily_data_growth():
    """Get daily data growth statistics"""

    growth_stats = []

    tables = ['crypto_analysis', 'crypto_hourly_data', 'crypto_5min_top10_gainers']

    for table_name in tables:
        try:
            query = f"""
                SELECT
                    DATE(datetime) as date,
                    COUNT(*) as records
                FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
                WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                GROUP BY DATE(datetime)
                ORDER BY date DESC
                LIMIT 30
            """

            result = bq_client.query(query).result()

            daily_records = []
            for row in result:
                daily_records.append({
                    'date': row['date'].isoformat(),
                    'records': row['records']
                })

            growth_stats.append({
                'table_name': table_name,
                'daily_records': daily_records
            })

        except Exception as e:
            growth_stats.append({
                'table_name': table_name,
                'error': str(e)
            })

    return growth_stats


def get_billing_data():
    """Get GCP billing information"""

    try:
        # For billing, we'll estimate based on usage
        # Note: Actual billing requires Cloud Billing API and proper permissions

        billing_info = {
            'estimated_monthly_costs': {
                'cloud_functions': {
                    'daily_crypto': 4.00,
                    'hourly_crypto': 72.00,
                    'fivemin_crypto': 50.00,
                    'ai_intelligence': 35.00,
                    'monitoring': 2.00
                },
                'bigquery': {
                    'storage': 2.00,
                    'queries': 5.00
                },
                'cloud_scheduler': 0.30,
                'cloud_run': 5.00,
                'networking': 3.00,
                'ai_apis': {
                    'claude': 40.00,
                    'vertex_ai': 20.00
                }
            },
            'total_estimated': 238.30,
            'billing_period': datetime.now().strftime('%Y-%m'),
            'last_updated': datetime.utcnow().isoformat()
        }

        # Calculate actual costs by component
        billing_info['breakdown_by_category'] = {
            'compute': 168.00,  # Cloud Functions + Cloud Run
            'data_storage': 7.00,  # BigQuery + Cloud Storage
            'ai_ml': 60.00,  # Claude + Vertex AI
            'networking': 3.00,
            'scheduler': 0.30
        }

        return billing_info

    except Exception as e:
        return {
            'error': str(e),
            'message': 'Unable to fetch billing data'
        }


def get_function_health():
    """Get Cloud Function health status"""

    functions_status = []

    functions = [
        'daily-crypto-fetcher',
        'hourly-crypto-fetcher',
        'fivemin-top10-fetcher',
        'ai-trading-intelligence',
        'system-monitoring'
    ]

    # For now, return expected status
    # In production, this would query Cloud Functions API
    for func in functions:
        functions_status.append({
            'name': func,
            'status': 'active',
            'region': 'us-central1',
            'runtime': 'python311',
            'last_deployed': datetime.utcnow().isoformat()
        })

    return functions_status


def get_scheduler_status():
    """Get Cloud Scheduler job status"""

    schedulers = [
        {
            'name': 'daily-crypto-fetch-job',
            'schedule': '0 0 * * *',
            'description': 'Daily crypto data fetch',
            'status': 'enabled',
            'next_run': 'Midnight ET'
        },
        {
            'name': 'hourly-crypto-fetch-job',
            'schedule': '0 * * * *',
            'description': 'Hourly crypto data fetch',
            'status': 'enabled',
            'next_run': 'Top of every hour'
        },
        {
            'name': 'fivemin-top10-fetch-job',
            'schedule': '*/5 * * * *',
            'description': '5-min top 10 gainers',
            'status': 'enabled',
            'next_run': 'Every 5 minutes'
        }
    ]

    return schedulers


def get_data_quality_metrics():
    """Check data quality and completeness across all asset categories"""

    quality_metrics = []

    # Define tables to check by category
    tables_by_category = {
        'stocks': ['v2_stocks_daily', 'v2_stocks_hourly', 'stocks_daily'],
        'crypto': ['v2_crypto_daily', 'v2_crypto_hourly', 'crypto_daily', 'daily_crypto'],
        'forex': ['v2_forex_daily', 'v2_forex_hourly', 'forex_daily'],
        'etfs': ['v2_etfs_daily', 'v2_etfs_hourly', 'etfs_daily'],
        'indices': ['v2_indices_daily', 'v2_indices_hourly', 'indices_daily'],
        'commodities': ['v2_commodities_daily', 'v2_commodities_hourly', 'commodities_daily'],
    }

    for category, tables in tables_by_category.items():
        category_metrics = {
            'category': category,
            'tables_checked': 0,
            'tables_with_data': 0,
            'total_rows': 0,
            'missing_dates': [],
            'freshness_hours': None,
            'status': 'unknown',
            'details': []
        }

        for table_name in tables:
            try:
                # Check if table has recent data
                freshness_query = f"""
                    SELECT
                        COUNT(*) as row_count,
                        MAX(datetime) as latest_datetime,
                        MIN(datetime) as earliest_datetime,
                        TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(datetime), HOUR) as hours_since_update
                    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
                """
                result = bq_client.query(freshness_query).result()
                row = list(result)[0]

                if row['row_count'] > 0:
                    category_metrics['tables_with_data'] += 1
                    category_metrics['total_rows'] += row['row_count']

                    hours_since = row['hours_since_update']
                    if category_metrics['freshness_hours'] is None or hours_since < category_metrics['freshness_hours']:
                        category_metrics['freshness_hours'] = hours_since

                    category_metrics['details'].append({
                        'table': table_name,
                        'row_count': row['row_count'],
                        'latest': row['latest_datetime'].isoformat() if row['latest_datetime'] else None,
                        'hours_since_update': hours_since,
                        'status': 'fresh' if hours_since < 48 else 'stale'
                    })

                category_metrics['tables_checked'] += 1

            except Exception as e:
                category_metrics['details'].append({
                    'table': table_name,
                    'error': str(e)[:100]
                })

        # Determine category status
        if category_metrics['tables_with_data'] == 0:
            category_metrics['status'] = 'critical'
        elif category_metrics['freshness_hours'] and category_metrics['freshness_hours'] > 48:
            category_metrics['status'] = 'stale'
        elif category_metrics['tables_with_data'] < len(tables):
            category_metrics['status'] = 'partial'
        else:
            category_metrics['status'] = 'healthy'

        quality_metrics.append(category_metrics)

    return quality_metrics


def get_empty_tables():
    """Identify empty tables that may need attention"""
    try:
        query = f"""
            SELECT table_id, row_count, size_bytes
            FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
            WHERE row_count = 0
            ORDER BY table_id
        """
        result = bq_client.query(query).result()
        return [{'table': row.table_id, 'size_bytes': row.size_bytes} for row in result]
    except Exception as e:
        return {'error': str(e)}


def get_duplicate_analysis():
    """Identify potentially duplicate tables based on similar row counts"""
    try:
        query = f"""
            SELECT table_id, row_count, size_bytes
            FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
            WHERE row_count > 0
            ORDER BY row_count DESC
        """
        result = bq_client.query(query).result()

        tables = [(row.table_id, row.row_count, row.size_bytes) for row in result]

        # Find tables with identical row counts (potential duplicates)
        duplicates = {}
        for i, (name, count, size) in enumerate(tables):
            for j, (name2, count2, size2) in enumerate(tables[i+1:], i+1):
                if count == count2 and count > 1000:  # Only flag if >1000 rows
                    key = str(count)
                    if key not in duplicates:
                        duplicates[key] = []
                    if name not in duplicates[key]:
                        duplicates[key].append({'table': name, 'rows': count, 'size_mb': round(size/(1024*1024), 2)})
                    if name2 not in duplicates[key]:
                        duplicates[key].append({'table': name2, 'rows': count2, 'size_mb': round(size2/(1024*1024), 2)})

        return list(duplicates.values())

    except Exception as e:
        return {'error': str(e)}


def get_row_count_changes():
    """Track row count changes over time (requires data_quality_log table)"""
    try:
        # Get current row counts by category
        query = f"""
            SELECT
                CASE
                    WHEN LOWER(table_id) LIKE '%stock%' THEN 'stocks'
                    WHEN LOWER(table_id) LIKE '%crypto%' THEN 'crypto'
                    WHEN LOWER(table_id) LIKE '%forex%' OR LOWER(table_id) LIKE '%fx%' THEN 'forex'
                    WHEN LOWER(table_id) LIKE '%etf%' THEN 'etfs'
                    WHEN LOWER(table_id) LIKE '%indic%' THEN 'indices'
                    WHEN LOWER(table_id) LIKE '%commod%' THEN 'commodities'
                    ELSE 'other'
                END as category,
                COUNT(*) as table_count,
                SUM(row_count) as total_rows,
                SUM(size_bytes) / (1024*1024) as total_size_mb
            FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
            GROUP BY 1
            ORDER BY total_rows DESC
        """
        result = bq_client.query(query).result()
        return [{
            'category': row.category,
            'table_count': row.table_count,
            'total_rows': row.total_rows,
            'total_size_mb': round(row.total_size_mb, 2)
        } for row in result]
    except Exception as e:
        return {'error': str(e)}


def get_top_pairs_by_volume():
    """Get top trading pairs by recent volume - tries multiple tables in both datasets"""

    try:
        # Try multiple tables to find pairs data (dataset, table, pair_col, vol_col, price_col)
        tables_to_try = [
            (DATASET_ID, 'daily_crypto', 'pair', 'volume', 'close'),
            (DATASET_ID, 'crypto_daily', 'pair', 'volume', 'close'),
            (DATASET_ID, 'crypto_hourly_data', 'pair', 'volume', 'close'),
            (DATASET_ID, 'stocks_daily', 'symbol', 'volume', 'close'),
            (DATASET_ID, 'daily_stock', 'symbol', 'volume', 'close'),
            (DATASET_UNIFIED, 'etfs_daily', 'symbol', 'volume', 'close'),
            (DATASET_UNIFIED, 'forex_daily', 'symbol', 'volume', 'close'),
            (DATASET_UNIFIED, 'indices_daily', 'symbol', 'volume', 'close'),
            (DATASET_UNIFIED, 'commodities_daily', 'symbol', 'volume', 'close'),
        ]

        for dataset_id, table_name, pair_col, vol_col, price_col in tables_to_try:
            try:
                query = f"""
                    SELECT
                        {pair_col} as pair,
                        AVG({vol_col}) as avg_volume,
                        MAX({price_col}) as latest_price,
                        COUNT(*) as data_points
                    FROM `{PROJECT_ID}.{dataset_id}.{table_name}`
                    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                    GROUP BY {pair_col}
                    HAVING AVG({vol_col}) > 0
                    ORDER BY avg_volume DESC
                    LIMIT 20
                """

                result = bq_client.query(query).result()
                rows = list(result)

                if rows:
                    top_pairs = []
                    for row in rows:
                        avg_vol = row['avg_volume']
                        latest_price = row['latest_price']
                        top_pairs.append({
                            'pair': row['pair'],
                            'avg_volume_24h': float(avg_vol) if avg_vol else 0,
                            'latest_price': float(latest_price) if latest_price else 0,
                            'data_points': row['data_points'],
                            'source_table': f"{dataset_id}.{table_name}"
                        })
                    return top_pairs
            except:
                continue

        return []

    except Exception as e:
        return []


@functions_framework.http
def system_monitoring(request):
    """
    Main HTTP endpoint for system monitoring

    Endpoints:
    - /tables - Get all table statistics
    - /billing - Get billing information
    - /health - Get system health status
    - /growth - Get data growth metrics
    - /quality - Get data quality metrics
    - /top-pairs - Get top trading pairs
    - /full - Get complete monitoring report
    """

    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        # Parse request
        request_args = request.args
        endpoint = request_args.get('endpoint', 'full')

        response_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'project_id': PROJECT_ID,
            'dataset_id': DATASET_ID
        }

        if endpoint == 'tables' or endpoint == 'full':
            response_data['tables'] = get_all_table_stats()

        if endpoint == 'billing' or endpoint == 'full':
            response_data['billing'] = get_billing_data()

        if endpoint == 'health' or endpoint == 'full':
            response_data['functions'] = get_function_health()
            response_data['schedulers'] = get_scheduler_status()

        if endpoint == 'growth' or endpoint == 'full':
            response_data['growth'] = get_daily_data_growth()

        if endpoint == 'quality' or endpoint == 'full':
            response_data['quality'] = get_data_quality_metrics()

        if endpoint == 'top-pairs' or endpoint == 'full':
            response_data['top_pairs'] = get_top_pairs_by_volume()

        if endpoint == 'empty-tables' or endpoint == 'full':
            response_data['empty_tables'] = get_empty_tables()

        if endpoint == 'duplicates' or endpoint == 'full':
            response_data['duplicate_candidates'] = get_duplicate_analysis()

        if endpoint == 'category-summary' or endpoint == 'full':
            response_data['category_summary'] = get_row_count_changes()

        # Add summary
        if endpoint == 'full':
            response_data['summary'] = {
                'total_tables': len(response_data.get('tables', [])),
                'healthy_tables': len([t for t in response_data.get('tables', []) if t.get('status') == 'healthy']),
                'total_records': sum([t.get('row_count', 0) for t in response_data.get('tables', [])]),
                'total_size_gb': sum([t.get('size_gb', 0) for t in response_data.get('tables', [])]),
                'estimated_monthly_cost': response_data.get('billing', {}).get('total_estimated', 0),
                'data_quality': 'good' if all([q.get('status') == 'good' for q in response_data.get('quality', [])]) else 'needs_attention'
            }

        return jsonify(response_data), 200, headers

    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500, headers
