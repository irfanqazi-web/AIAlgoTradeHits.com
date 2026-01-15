#!/usr/bin/env python3
"""Fix the download endpoint in main.py"""

import re

main_py_path = 'C:/1AITrading/Trading/cloud_function_api/main.py'

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the download endpoint function using regex
pattern = r"(@app\.route\('/api/stocks/reconciliation/<symbol>/download'.*?def download_stock_reconciliation\(symbol\):.*?return Response\(str\(e\), mimetype='text/plain', status=500\))"

match = re.search(pattern, content, re.DOTALL)

if match:
    old_code = match.group(1)
    print(f"Found endpoint at position {match.start()}")

    new_code = '''@app.route('/api/stocks/reconciliation/<symbol>/download', methods=['GET'])
def download_stock_reconciliation(symbol):
    """Download complete stock data as CSV with all 97 fields in schema order"""
    try:
        import csv
        from io import StringIO
        import math
        from datetime import datetime as dt

        # Define column order matching the schema design (97 fields)
        SCHEMA_COLUMN_ORDER = [
            'datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume',
            'previous_close', 'change', 'percent_change', 'high_low', 'pct_high_low',
            'week_52_high', 'week_52_low', 'average_volume', 'rsi', 'macd',
            'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci',
            'williams_r', 'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12',
            'ema_20', 'ema_26', 'ema_50', 'ema_200', 'kama', 'bollinger_upper',
            'bollinger_middle', 'bollinger_lower', 'bb_width', 'adx', 'plus_di',
            'minus_di', 'atr', 'trix', 'roc', 'obv', 'pvo', 'ppo', 'ultimate_osc',
            'awesome_osc', 'log_return', 'return_2w', 'return_4w',
            'close_vs_sma20_pct', 'close_vs_sma50_pct', 'close_vs_sma200_pct',
            'rsi_slope', 'rsi_zscore', 'rsi_overbought', 'rsi_oversold',
            'macd_cross', 'ema20_slope', 'ema50_slope', 'atr_zscore', 'atr_slope',
            'volume_zscore', 'volume_ratio', 'pivot_high_flag', 'pivot_low_flag',
            'dist_to_pivot_high', 'dist_to_pivot_low', 'trend_regime', 'vol_regime',
            'regime_confidence', 'mfi', 'cmf', 'ichimoku_tenkan', 'ichimoku_kijun',
            'ichimoku_senkou_a', 'ichimoku_senkou_b', 'ichimoku_chikou',
            'vwap_daily', 'vwap_weekly', 'volume_profile_poc', 'volume_profile_vah',
            'volume_profile_val', 'name', 'sector', 'industry', 'asset_type',
            'exchange', 'mic_code', 'country', 'currency', 'type', 'timestamp',
            'data_source', 'created_at', 'updated_at'
        ]

        # Decimal columns to round to 2 places
        DECIMAL_COLUMNS = {
            'open', 'high', 'low', 'close', 'previous_close', 'change', 'percent_change',
            'high_low', 'pct_high_low', 'week_52_high', 'week_52_low', 'rsi', 'macd',
            'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'cci', 'williams_r',
            'momentum', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_20', 'ema_26',
            'ema_50', 'ema_200', 'kama', 'bollinger_upper', 'bollinger_middle',
            'bollinger_lower', 'bb_width', 'adx', 'plus_di', 'minus_di', 'atr', 'trix',
            'roc', 'pvo', 'ppo', 'ultimate_osc', 'awesome_osc', 'log_return',
            'return_2w', 'return_4w', 'close_vs_sma20_pct', 'close_vs_sma50_pct',
            'close_vs_sma200_pct', 'rsi_slope', 'rsi_zscore', 'ema20_slope',
            'ema50_slope', 'atr_zscore', 'atr_slope', 'volume_zscore', 'volume_ratio',
            'dist_to_pivot_high', 'dist_to_pivot_low', 'regime_confidence', 'mfi', 'cmf',
            'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b',
            'ichimoku_chikou', 'vwap_daily', 'vwap_weekly', 'volume_profile_poc',
            'volume_profile_vah', 'volume_profile_val'
        }

        # Query all data for symbol (NO LIMIT - full download, latest first)
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        """

        query_job = client.query(query)
        results = list(query_job.result())

        if not results:
            return Response("No data found", mimetype='text/plain', status=404)

        # Get available columns from data
        available_cols = set(dict(results[0]).keys())

        # Use schema order, only including columns that exist
        columns = [col for col in SCHEMA_COLUMN_ORDER if col in available_cols]

        # Add any extra columns not in schema order at the end
        extra_cols = [col for col in available_cols if col not in SCHEMA_COLUMN_ORDER]
        columns.extend(sorted(extra_cols))

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)

        for row in results:
            row_dict = dict(row)
            row_data = []
            for col in columns:
                val = row_dict.get(col)
                if val is None:
                    row_data.append('')
                elif hasattr(val, 'isoformat'):
                    row_data.append(val.isoformat())
                elif col == 'timestamp' and isinstance(val, (int, float)):
                    row_data.append(dt.utcfromtimestamp(val).strftime('%Y-%m-%dT%H:%M:%S'))
                elif isinstance(val, float):
                    if math.isnan(val) or math.isinf(val):
                        row_data.append('')
                    elif col in DECIMAL_COLUMNS:
                        row_data.append(round(val, 2))
                    else:
                        row_data.append(val)
                else:
                    row_data.append(val)
            writer.writerow(row_data)

        csv_content = output.getvalue()

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={symbol}_97_fields_complete.csv'}
        )

    except Exception as e:
        logger.error(f"Error downloading stock data: {str(e)}")
        return Response(str(e), mimetype='text/plain', status=500)'''

    content = content.replace(old_code, new_code)

    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: Updated download endpoint")
else:
    print("ERROR: Could not find the download endpoint")
