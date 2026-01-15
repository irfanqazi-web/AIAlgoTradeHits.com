"""
Reliable ML Training Cloud Run Service
- 60-minute timeout for long-running validations
- Checkpoint/resume for interrupted runs
- Symbol-by-symbol processing with progress saving
- Automatic result finalization
"""

import os
from flask import Flask, request, jsonify
from google.cloud import bigquery
from datetime import datetime, timedelta
import uuid
import json
import traceback

app = Flask(__name__)
client = bigquery.Client(project='aialgotradehits')

# Feature configurations
ESSENTIAL_FEATURES = [
    'rsi', 'macd', 'macd_histogram', 'momentum',
    'mfi', 'cci', 'rsi_zscore', 'macd_cross'
]

DEFAULT_FEATURES = [
    'pivot_low_flag', 'pivot_high_flag', 'rsi', 'rsi_slope', 'rsi_zscore',
    'rsi_overbought', 'rsi_oversold', 'macd', 'macd_signal', 'macd_histogram',
    'macd_cross', 'momentum', 'mfi', 'cci', 'awesome_osc', 'vwap_daily'
]

RETRAIN_INTERVALS = {
    'daily': 1,
    'weekly': 5,
    'monthly': 21,
    'quarterly': 63
}


def update_run_status(run_id, status, progress_pct=None, current_day=None,
                      error_message=None, overall_accuracy=None, total_return=None):
    """Update run status in BigQuery"""
    updates = [f"status = '{status}'"]
    if progress_pct is not None:
        updates.append(f"progress_pct = {progress_pct}")
    if current_day is not None:
        updates.append(f"current_day = {current_day}")
    if error_message:
        updates.append(f"error_message = '{error_message}'")
    if overall_accuracy is not None:
        updates.append(f"overall_accuracy = {overall_accuracy}")
    if total_return is not None:
        updates.append(f"total_return = {total_return}")
    if status == 'completed':
        updates.append("completed_at = CURRENT_TIMESTAMP()")

    query = f"""
    UPDATE `aialgotradehits.ml_models.walk_forward_runs`
    SET {', '.join(updates)}
    WHERE run_id = '{run_id}'
    """
    try:
        client.query(query).result()
    except Exception as e:
        print(f"Error updating status: {e}")


def save_checkpoint(run_id, symbol, last_date, predictions_saved):
    """Save checkpoint for resume capability"""
    query = f"""
    MERGE `aialgotradehits.ml_models.validation_checkpoints` T
    USING (SELECT '{run_id}' as run_id, '{symbol}' as symbol) S
    ON T.run_id = S.run_id AND T.symbol = S.symbol
    WHEN MATCHED THEN
        UPDATE SET last_date = '{last_date}', predictions_saved = {predictions_saved}, updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (run_id, symbol, last_date, predictions_saved, updated_at)
        VALUES ('{run_id}', '{symbol}', '{last_date}', {predictions_saved}, CURRENT_TIMESTAMP())
    """
    try:
        client.query(query).result()
    except Exception as e:
        print(f"Checkpoint save error: {e}")


def get_checkpoint(run_id, symbol):
    """Get checkpoint for resume"""
    query = f"""
    SELECT last_date, predictions_saved
    FROM `aialgotradehits.ml_models.validation_checkpoints`
    WHERE run_id = '{run_id}' AND symbol = '{symbol}'
    """
    try:
        result = client.query(query).result()
        rows = list(result)
        if rows:
            return rows[0].last_date, rows[0].predictions_saved
    except:
        pass
    return None, 0


def check_cached_model(symbol, train_end_date, features_mode):
    """Check if a cached model exists"""
    query = f"""
    SELECT model_name
    FROM `aialgotradehits.ml_models.model_cache`
    WHERE symbol = '{symbol}'
      AND train_end_date = '{train_end_date}'
      AND features_mode = '{features_mode}'
      AND created_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    ORDER BY created_at DESC
    LIMIT 1
    """
    try:
        result = client.query(query).result()
        rows = list(result)
        if rows:
            return rows[0].model_name
    except:
        pass
    return None


def train_model(symbol, train_end_date, features, run_id, features_mode):
    """Train XGBoost model with caching"""
    # Check cache first
    cached = check_cached_model(symbol, train_end_date, features_mode)
    if cached:
        print(f"  Using cached model for {symbol}: {cached}")
        return cached

    unique_suffix = run_id[:8] if run_id else str(uuid.uuid4())[:8]
    model_name = f"wf_model_{symbol.lower()}_{train_end_date.replace('-', '')}_{unique_suffix}"
    feature_cols = ', '.join(features)

    train_query = f"""
    CREATE OR REPLACE MODEL `aialgotradehits.ml_models.{model_name}`
    OPTIONS(
        model_type='BOOSTED_TREE_CLASSIFIER',
        input_label_cols=['direction_target'],
        max_iterations=20,
        early_stop=TRUE,
        data_split_method='NO_SPLIT'
    ) AS
    SELECT {feature_cols}, direction_target
    FROM `aialgotradehits.ml_models.walk_forward_features_16_mat`
    WHERE symbol = '{symbol}'
      AND trade_date < '{train_end_date}'
      AND trade_date >= DATE_SUB(DATE('{train_end_date}'), INTERVAL 365 DAY)
    """

    try:
        print(f"  Training model for {symbol}...")
        client.query(train_query).result()

        # Cache the model
        cache_query = f"""
        INSERT INTO `aialgotradehits.ml_models.model_cache`
        (symbol, train_end_date, features_mode, model_name, created_at)
        VALUES ('{symbol}', '{train_end_date}', '{features_mode}', '{model_name}', CURRENT_TIMESTAMP())
        """
        client.query(cache_query).result()

        return model_name
    except Exception as e:
        print(f"  Model training error for {symbol}: {e}")
        return None


def batch_predict(model_name, symbol, start_date, end_date, features):
    """Make batch predictions for a date range"""
    feature_cols = ', '.join(features)

    query = f"""
    WITH predictions AS (
        SELECT
            symbol,
            trade_date,
            close,
            LEAD(close, 1) OVER (ORDER BY trade_date) as next_close,
            predicted_direction_target as predicted_direction,
            predicted_direction_target_probs as predicted_probs
        FROM ML.PREDICT(
            MODEL `aialgotradehits.ml_models.{model_name}`,
            (
                SELECT {feature_cols}, symbol, trade_date, close
                FROM `aialgotradehits.ml_models.walk_forward_features_16_mat`
                WHERE symbol = '{symbol}'
                  AND trade_date >= '{start_date}'
                  AND trade_date <= '{end_date}'
            )
        )
    )
    SELECT * FROM predictions WHERE next_close IS NOT NULL ORDER BY trade_date
    """

    try:
        result = client.query(query).result()
        predictions = []
        for row in result:
            prob_up = 0.5
            if row.predicted_probs:
                for prob in row.predicted_probs:
                    if prob['label'] == 1:
                        prob_up = prob['prob']
                        break

            predictions.append({
                'symbol': row.symbol,
                'date': str(row.trade_date),
                'close': row.close,
                'next_close': row.next_close,
                'predicted': row.predicted_direction,
                'probability_up': prob_up,
                'probability_down': 1 - prob_up
            })
        return predictions
    except Exception as e:
        print(f"Prediction error: {e}")
        return []


def save_daily_results(run_id, predictions):
    """Save daily prediction results to BigQuery"""
    if not predictions:
        return

    values = []
    for pred in predictions:
        actual = 1 if pred['next_close'] > pred['close'] else 0
        is_correct = pred['predicted'] == actual
        confidence = max(pred['probability_up'], pred['probability_down'])
        actual_return = (pred['next_close'] - pred['close']) / pred['close'] if pred['close'] > 0 else 0

        # predicted_direction and actual_direction are STRING columns
        values.append(f"""
            ('{run_id}', '{pred['symbol']}', DATE('{pred['date']}'),
             {pred['close']}, '{pred['predicted']}', '{actual}',
             {is_correct}, {confidence}, {pred['probability_up']}, {pred['probability_down']}, {actual_return})
        """)

    query = f"""
    INSERT INTO `aialgotradehits.ml_models.walk_forward_daily_results`
    (run_id, symbol, prediction_date, close_price,
     predicted_direction, actual_direction, is_correct, confidence,
     probability_up, probability_down, actual_return)
    VALUES {','.join(values)}
    """

    try:
        client.query(query).result()
    except Exception as e:
        print(f"Error saving results: {e}")


def finalize_run(run_id):
    """Calculate final metrics and update run status"""
    query = f"""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
        SUM(CASE WHEN predicted_direction = '1' AND is_correct THEN 1 ELSE 0 END) as up_correct,
        SUM(CASE WHEN predicted_direction = '1' THEN 1 ELSE 0 END) as up_total,
        SUM(CASE WHEN predicted_direction = '0' AND is_correct THEN 1 ELSE 0 END) as down_correct,
        SUM(CASE WHEN predicted_direction = '0' THEN 1 ELSE 0 END) as down_total
    FROM `aialgotradehits.ml_models.walk_forward_daily_results`
    WHERE run_id = '{run_id}'
    """

    result = client.query(query).result()
    row = list(result)[0]

    if row.total > 0:
        accuracy = row.correct / row.total
        # Simple return calculation
        total_return = (row.correct - (row.total - row.correct)) / row.total * 0.01

        update_run_status(
            run_id, 'completed',
            progress_pct=100.0,
            overall_accuracy=accuracy,
            total_return=total_return
        )

        return {
            'overall_accuracy': accuracy,
            'total_predictions': row.total,
            'correct_predictions': row.correct,
            'up_accuracy': row.up_correct / row.up_total if row.up_total > 0 else 0,
            'down_accuracy': row.down_correct / row.down_total if row.down_total > 0 else 0
        }

    return None


def run_validation(config):
    """Execute walk-forward validation with checkpointing"""
    run_id = config['run_id']
    symbols = config['symbols'].split(',') if isinstance(config['symbols'], str) else config['symbols']
    test_start = config['test_start']
    walk_forward_days = config.get('walk_forward_days', 252)
    retrain_frequency = config.get('retrain_frequency', 'monthly')
    features_mode = config.get('features_mode', 'essential_8')

    # Select features
    if features_mode == 'essential_8':
        features = ESSENTIAL_FEATURES
    else:
        features = DEFAULT_FEATURES

    retrain_interval = RETRAIN_INTERVALS.get(retrain_frequency, 21)

    print(f"\n{'='*60}")
    print(f"RELIABLE ML VALIDATION")
    print(f"{'='*60}")
    print(f"Run ID: {run_id}")
    print(f"Symbols: {symbols}")
    print(f"Days: {walk_forward_days}")
    print(f"Retrain: {retrain_frequency} (every {retrain_interval} days)")
    print(f"Features: {features_mode} ({len(features)} features)")

    # Get trading dates
    dates_query = f"""
    SELECT DISTINCT trade_date
    FROM `aialgotradehits.ml_models.walk_forward_features_16_mat`
    WHERE symbol = '{symbols[0]}'
      AND trade_date >= '{test_start}'
    ORDER BY trade_date
    LIMIT {walk_forward_days}
    """

    result = client.query(dates_query).result()
    trading_dates = [row.trade_date for row in result]

    if not trading_dates:
        update_run_status(run_id, 'failed', error_message='No trading dates found')
        return {'error': 'No trading dates found'}

    print(f"Trading dates: {len(trading_dates)}")

    total_symbols = len(symbols)

    # Process each symbol with checkpointing
    for symbol_idx, symbol in enumerate(symbols):
        print(f"\n--- Processing {symbol} ({symbol_idx + 1}/{total_symbols}) ---")

        # Check for checkpoint
        last_date, predictions_saved = get_checkpoint(run_id, symbol)
        start_idx = 0

        if last_date:
            print(f"  Resuming from checkpoint: {last_date}")
            for i, d in enumerate(trading_dates):
                if str(d) > str(last_date):
                    start_idx = i
                    break

        # Process in batches
        batch_start_idx = start_idx
        while batch_start_idx < len(trading_dates):
            batch_end_idx = min(batch_start_idx + retrain_interval, len(trading_dates))
            batch_start_date = trading_dates[batch_start_idx]
            batch_end_date = trading_dates[batch_end_idx - 1]

            # Calculate overall progress
            symbol_progress = batch_end_idx / len(trading_dates)
            overall_progress = ((symbol_idx + symbol_progress) / total_symbols) * 100

            update_run_status(run_id, 'running', overall_progress, batch_end_idx)
            print(f"  Batch {batch_start_idx + 1}-{batch_end_idx}/{len(trading_dates)} ({overall_progress:.1f}%)")

            # Train model
            train_end = (batch_start_date - timedelta(days=1)).strftime('%Y-%m-%d')
            model_name = train_model(symbol, train_end, features, run_id, features_mode)

            if not model_name:
                print(f"  Skipping {symbol} - model training failed")
                break

            # Batch predict
            predictions = batch_predict(
                model_name, symbol,
                str(batch_start_date), str(batch_end_date),
                features
            )

            if predictions:
                save_daily_results(run_id, predictions)
                save_checkpoint(run_id, symbol, str(batch_end_date), predictions_saved + len(predictions))
                predictions_saved += len(predictions)
                print(f"  Saved {len(predictions)} predictions")

            batch_start_idx = batch_end_idx

    # Finalize
    print(f"\n--- Finalizing run {run_id} ---")
    metrics = finalize_run(run_id)

    if metrics:
        print(f"Overall Accuracy: {metrics['overall_accuracy']:.1%}")
        print(f"Total Predictions: {metrics['total_predictions']}")

    return {
        'run_id': run_id,
        'status': 'completed',
        **metrics
    } if metrics else {'run_id': run_id, 'status': 'completed'}


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_request():
    """HTTP endpoint"""
    if request.method == 'OPTIONS':
        return '', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = dict(request.args)

        action = data.get('action', 'run')

        if action == 'status':
            run_id = data.get('run_id')
            if not run_id:
                return jsonify({'error': 'run_id required'}), 400, headers

            query = f"""
            SELECT * FROM `aialgotradehits.ml_models.walk_forward_runs`
            WHERE run_id = '{run_id}'
            """
            result = client.query(query).result()
            rows = list(result)
            if rows:
                row = rows[0]
                return jsonify({
                    'run_id': row.run_id,
                    'status': row.status,
                    'progress_pct': row.progress_pct,
                    'overall_accuracy': row.overall_accuracy,
                    'total_return': row.total_return
                }), 200, headers
            return jsonify({'error': 'Run not found'}), 404, headers

        elif action == 'list':
            query = """
            SELECT run_id, run_timestamp, symbols, status, progress_pct,
                   overall_accuracy, total_return
            FROM `aialgotradehits.ml_models.walk_forward_runs`
            ORDER BY run_timestamp DESC
            LIMIT 50
            """
            result = client.query(query).result()
            runs = [{
                'run_id': row.run_id,
                'timestamp': str(row.run_timestamp),
                'symbols': row.symbols,
                'status': row.status,
                'progress_pct': row.progress_pct,
                'overall_accuracy': row.overall_accuracy
            } for row in result]
            return jsonify({'runs': runs}), 200, headers

        elif action == 'resume':
            run_id = data.get('run_id')
            if not run_id:
                return jsonify({'error': 'run_id required'}), 400, headers

            # Get existing run config
            query = f"""
            SELECT symbols, test_start, walk_forward_days, retrain_frequency, features_mode
            FROM `aialgotradehits.ml_models.walk_forward_runs`
            WHERE run_id = '{run_id}'
            """
            result = client.query(query).result()
            rows = list(result)
            if not rows:
                return jsonify({'error': 'Run not found'}), 404, headers

            row = rows[0]
            config = {
                'run_id': run_id,
                'symbols': row.symbols,
                'test_start': str(row.test_start),
                'walk_forward_days': row.walk_forward_days,
                'retrain_frequency': row.retrain_frequency,
                'features_mode': row.features_mode
            }

            result = run_validation(config)
            return jsonify(result), 200, headers

        elif action == 'run':
            run_id = str(uuid.uuid4())[:8]
            symbols_input = data.get('symbols', 'AAPL')
            if isinstance(symbols_input, list):
                symbols = ','.join(symbols_input)
            else:
                symbols = symbols_input

            test_start = data.get('test_start', '2024-01-01')
            walk_forward_days = int(data.get('walk_forward_days', 252))
            retrain_frequency = data.get('retrain_frequency', 'monthly')
            features_mode = data.get('features_mode', 'essential_8')

            # Create run record
            insert_query = f"""
            INSERT INTO `aialgotradehits.ml_models.walk_forward_runs`
            (run_id, run_timestamp, symbols, test_start, walk_forward_days,
             retrain_frequency, features_mode, status, progress_pct, started_at)
            VALUES
            ('{run_id}', CURRENT_TIMESTAMP(), '{symbols}', DATE('{test_start}'),
             {walk_forward_days}, '{retrain_frequency}', '{features_mode}',
             'running', 0, CURRENT_TIMESTAMP())
            """
            client.query(insert_query).result()

            config = {
                'run_id': run_id,
                'symbols': symbols,
                'test_start': test_start,
                'walk_forward_days': walk_forward_days,
                'retrain_frequency': retrain_frequency,
                'features_mode': features_mode
            }

            result = run_validation(config)
            return jsonify(result), 200, headers

        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400, headers

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500, headers


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
