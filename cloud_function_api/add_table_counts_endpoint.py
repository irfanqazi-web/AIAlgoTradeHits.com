"""
Add table counts endpoint to API
"""

endpoint_code = '''
@app.route('/api/admin/table-counts', methods=['GET'])
def get_table_counts():
    """Get row counts and sizes for all BigQuery tables"""
    try:
        # Query to get table information from INFORMATION_SCHEMA
        query = f"""
        SELECT
            table_name,
            CASE
                WHEN table_name LIKE '%stock%' OR table_name LIKE '%Stock%' THEN 'stocks'
                WHEN table_name LIKE '%crypto%' OR table_name LIKE '%Crypto%' THEN 'crypto'
                WHEN table_name LIKE '%forex%' OR table_name LIKE '%Forex%' THEN 'forex'
                WHEN table_name LIKE '%etf%' OR table_name LIKE '%ETF%' THEN 'etfs'
                WHEN table_name LIKE '%indic%' OR table_name LIKE '%Indic%' THEN 'indices'
                WHEN table_name LIKE '%commodit%' OR table_name LIKE '%Commodit%' THEN 'commodities'
                WHEN table_name LIKE '%fundamental%' THEN 'fundamentals'
                WHEN table_name LIKE '%analyst%' THEN 'analyst'
                WHEN table_name LIKE '%earning%' THEN 'corporate_actions'
                WHEN table_name LIKE '%dividend%' THEN 'corporate_actions'
                WHEN table_name LIKE '%split%' THEN 'corporate_actions'
                WHEN table_name LIKE '%ipo%' THEN 'corporate_actions'
                ELSE 'other'
            END as category,
            row_count,
            ROUND(size_bytes / 1024 / 1024, 2) as size_mb,
            TIMESTAMP_MILLIS(CAST(creation_time AS INT64)) as created_at
        FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
        ORDER BY row_count DESC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        tables = []
        for row in results:
            tables.append({
                'table_name': row.table_name,
                'category': row.category,
                'row_count': int(row.row_count) if row.row_count else 0,
                'size_mb': float(row.size_mb) if row.size_mb else 0.0,
                'created_at': row.created_at.isoformat() if row.created_at else None
            })

        logger.info(f"Fetched {len(tables)} table counts")

        return jsonify({
            'success': True,
            'tables': tables,
            'count': len(tables)
        })

    except Exception as e:
        logger.error(f"Error fetching table counts: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'tables': [],
            'count': 0
        }), 500
'''

print("Add this endpoint to cloud_function_api/main.py:")
print("="*80)
print(endpoint_code)
print("="*80)
