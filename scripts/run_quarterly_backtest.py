"""
Quarterly Backtest - 2-Year Walk-Forward Validation
Tests ML model performance across 8 quarters (Q1 2024 - Q4 2025)
"""
from google.cloud import bigquery
from datetime import datetime, timedelta
import json

client = bigquery.Client(project='aialgotradehits')

print("=" * 70)
print("QUARTERLY BACKTEST - 2-YEAR WALK-FORWARD VALIDATION")
print("=" * 70)
print(f"Started: {datetime.now()}")
print()

# Configuration
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'AVGO', 'INTC',
           'LMT', 'RTX', 'HON', 'CAT', 'JPM', 'V']

# Define quarters for backtest
QUARTERS = [
    {'name': 'Q1_2024', 'train_start': '2023-01-01', 'train_end': '2023-12-31', 'test_start': '2024-01-01', 'test_end': '2024-03-31'},
    {'name': 'Q2_2024', 'train_start': '2023-04-01', 'train_end': '2024-03-31', 'test_start': '2024-04-01', 'test_end': '2024-06-30'},
    {'name': 'Q3_2024', 'train_start': '2023-07-01', 'train_end': '2024-06-30', 'test_start': '2024-07-01', 'test_end': '2024-09-30'},
    {'name': 'Q4_2024', 'train_start': '2023-10-01', 'train_end': '2024-09-30', 'test_start': '2024-10-01', 'test_end': '2024-12-31'},
    {'name': 'Q1_2025', 'train_start': '2024-01-01', 'train_end': '2024-12-31', 'test_start': '2025-01-01', 'test_end': '2025-03-31'},
    {'name': 'Q2_2025', 'train_start': '2024-04-01', 'train_end': '2025-03-31', 'test_start': '2025-04-01', 'test_end': '2025-06-30'},
    {'name': 'Q3_2025', 'train_start': '2024-07-01', 'train_end': '2025-06-30', 'test_start': '2025-07-01', 'test_end': '2025-09-30'},
    {'name': 'Q4_2025', 'train_start': '2024-10-01', 'train_end': '2025-09-30', 'test_start': '2025-10-01', 'test_end': '2025-12-31'},
]

symbol_str = "','".join(SYMBOLS)

# Step 1: Create backtest results table
print("Step 1: Creating backtest results table...")

create_table_query = """
CREATE TABLE IF NOT EXISTS `aialgotradehits.ml_models.quarterly_backtest_results` (
    backtest_id STRING,
    quarter STRING,
    train_start DATE,
    train_end DATE,
    test_start DATE,
    test_end DATE,
    symbols STRING,
    total_predictions INT64,
    correct_predictions INT64,
    accuracy FLOAT64,
    up_predictions INT64,
    up_correct INT64,
    up_accuracy FLOAT64,
    down_predictions INT64,
    down_correct INT64,
    down_accuracy FLOAT64,
    avg_confidence FLOAT64,
    high_conf_predictions INT64,
    high_conf_correct INT64,
    high_conf_accuracy FLOAT64,
    simulated_return FLOAT64,
    sharpe_ratio FLOAT64,
    max_drawdown FLOAT64,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""
try:
    client.query(create_table_query).result()
    print("  Backtest results table ready")
except Exception as e:
    print(f"  Table creation: {e}")

# Step 2: Create features table for backtest
print("\nStep 2: Creating comprehensive features table...")

features_query = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.backtest_features` AS
SELECT
    symbol,
    datetime,
    close,
    rsi,
    macd,
    macd_histogram,
    mfi,
    cci,
    adx,
    momentum,
    sma_20,
    sma_50,
    sma_200,
    atr,
    volume,
    -- Derived features
    close / NULLIF(sma_50, 0) as price_sma50_ratio,
    close / NULLIF(sma_200, 0) as price_sma200_ratio,
    STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as volatility_20d,
    (rsi - 50) / 14 as rsi_zscore,
    CASE WHEN macd > LAG(macd) OVER (PARTITION BY symbol ORDER BY datetime) THEN 1 ELSE 0 END as macd_rising,
    -- Direction target
    CASE
        WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 1
        ELSE 0
    END as direction_target
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol IN ('{symbol_str}')
  AND datetime >= '2023-01-01'
  AND rsi IS NOT NULL
  AND macd IS NOT NULL
"""

try:
    client.query(features_query).result()

    # Count records
    count_result = list(client.query("""
        SELECT COUNT(*) as total, COUNT(DISTINCT symbol) as symbols,
               MIN(DATE(datetime)) as min_date, MAX(DATE(datetime)) as max_date
        FROM `aialgotradehits.ml_models.backtest_features`
    """).result())[0]
    print(f"  Features table created: {count_result.total:,} records")
    print(f"  Date range: {count_result.min_date} to {count_result.max_date}")
    print(f"  Symbols: {count_result.symbols}")
except Exception as e:
    print(f"  Features creation error: {e}")

# Step 3: Run quarterly backtest
print("\nStep 3: Running quarterly backtest...")
print("-" * 70)

backtest_id = datetime.now().strftime("%Y%m%d_%H%M%S")
results = []

for quarter in QUARTERS:
    print(f"\n{quarter['name']}: Train {quarter['train_start']} to {quarter['train_end']}")
    print(f"         Test {quarter['test_start']} to {quarter['test_end']}")

    # Train model for this quarter
    model_name = f"backtest_{quarter['name'].lower()}"

    train_model_query = f"""
    CREATE OR REPLACE MODEL `aialgotradehits.ml_models.{model_name}`
    OPTIONS(
        model_type = 'BOOSTED_TREE_CLASSIFIER',
        input_label_cols = ['direction_target'],
        max_iterations = 30,
        learn_rate = 0.1,
        early_stop = TRUE,
        data_split_method = 'NO_SPLIT'
    ) AS
    SELECT
        rsi, macd, macd_histogram, mfi, cci, adx, momentum,
        price_sma50_ratio, price_sma200_ratio, volatility_20d,
        rsi_zscore, macd_rising,
        direction_target
    FROM `aialgotradehits.ml_models.backtest_features`
    WHERE DATE(datetime) >= '{quarter['train_start']}'
      AND DATE(datetime) <= '{quarter['train_end']}'
      AND direction_target IS NOT NULL
    """

    try:
        client.query(train_model_query).result()
        print(f"  Model trained: {model_name}")
    except Exception as e:
        print(f"  Training error: {e}")
        continue

    # Evaluate on test period
    eval_query = f"""
    WITH predictions AS (
        SELECT
            symbol,
            DATE(datetime) as pred_date,
            close,
            direction_target as actual,
            predicted_direction_target as predicted,
            predicted_direction_target_probs[OFFSET(1)].prob as prob_up
        FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.{model_name}`,
            (SELECT symbol, datetime, close,
                    rsi, macd, macd_histogram, mfi, cci, adx, momentum,
                    price_sma50_ratio, price_sma200_ratio, volatility_20d,
                    rsi_zscore, macd_rising, direction_target
             FROM `aialgotradehits.ml_models.backtest_features`
             WHERE DATE(datetime) >= '{quarter['test_start']}'
               AND DATE(datetime) <= '{quarter['test_end']}'
               AND direction_target IS NOT NULL))
    )
    SELECT
        COUNT(*) as total_predictions,
        SUM(CASE WHEN predicted = actual THEN 1 ELSE 0 END) as correct,
        ROUND(AVG(CASE WHEN predicted = actual THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy,
        SUM(CASE WHEN actual = 1 THEN 1 ELSE 0 END) as up_actual,
        SUM(CASE WHEN predicted = 1 AND actual = 1 THEN 1 ELSE 0 END) as up_correct,
        SUM(CASE WHEN actual = 0 THEN 1 ELSE 0 END) as down_actual,
        SUM(CASE WHEN predicted = 0 AND actual = 0 THEN 1 ELSE 0 END) as down_correct,
        ROUND(AVG(prob_up), 3) as avg_prob,
        SUM(CASE WHEN prob_up >= 0.6 OR prob_up <= 0.4 THEN 1 ELSE 0 END) as high_conf,
        SUM(CASE WHEN (prob_up >= 0.6 AND actual = 1) OR (prob_up <= 0.4 AND actual = 0) THEN 1 ELSE 0 END) as high_conf_correct
    FROM predictions
    """

    try:
        eval_result = list(client.query(eval_query).result())[0]

        if eval_result.total_predictions and eval_result.total_predictions > 0:
            up_accuracy = (eval_result.up_correct / eval_result.up_actual * 100) if eval_result.up_actual > 0 else 0
            down_accuracy = (eval_result.down_correct / eval_result.down_actual * 100) if eval_result.down_actual > 0 else 0
            high_conf_accuracy = (eval_result.high_conf_correct / eval_result.high_conf * 100) if eval_result.high_conf > 0 else 0

            result = {
                'quarter': quarter['name'],
                'train_start': quarter['train_start'],
                'train_end': quarter['train_end'],
                'test_start': quarter['test_start'],
                'test_end': quarter['test_end'],
                'total_predictions': eval_result.total_predictions,
                'correct': eval_result.correct,
                'accuracy': eval_result.accuracy,
                'up_accuracy': round(up_accuracy, 2),
                'down_accuracy': round(down_accuracy, 2),
                'high_conf': eval_result.high_conf,
                'high_conf_accuracy': round(high_conf_accuracy, 2)
            }
            results.append(result)

            print(f"  Results: {eval_result.total_predictions} predictions, {eval_result.accuracy}% accuracy")
            print(f"    UP: {up_accuracy:.1f}%, DOWN: {down_accuracy:.1f}%, High Conf: {high_conf_accuracy:.1f}%")

            # Save to BigQuery
            insert_query = f"""
            INSERT INTO `aialgotradehits.ml_models.quarterly_backtest_results`
            (backtest_id, quarter, train_start, train_end, test_start, test_end, symbols,
             total_predictions, correct_predictions, accuracy,
             up_predictions, up_correct, up_accuracy,
             down_predictions, down_correct, down_accuracy,
             high_conf_predictions, high_conf_correct, high_conf_accuracy)
            VALUES
            ('{backtest_id}', '{quarter["name"]}',
             DATE('{quarter["train_start"]}'), DATE('{quarter["train_end"]}'),
             DATE('{quarter["test_start"]}'), DATE('{quarter["test_end"]}'),
             '{",".join(SYMBOLS)}',
             {eval_result.total_predictions}, {eval_result.correct}, {eval_result.accuracy},
             {eval_result.up_actual}, {eval_result.up_correct}, {up_accuracy},
             {eval_result.down_actual}, {eval_result.down_correct}, {down_accuracy},
             {eval_result.high_conf}, {eval_result.high_conf_correct}, {high_conf_accuracy})
            """
            client.query(insert_query).result()
        else:
            print(f"  No predictions for this quarter")

    except Exception as e:
        print(f"  Evaluation error: {e}")

# Step 4: Generate summary
print("\n" + "=" * 70)
print("QUARTERLY BACKTEST SUMMARY")
print("=" * 70)

if results:
    total_preds = sum(r['total_predictions'] for r in results)
    total_correct = sum(r['correct'] for r in results)
    overall_accuracy = total_correct / total_preds * 100 if total_preds > 0 else 0

    print(f"\nOverall Results:")
    print(f"  Total Predictions: {total_preds:,}")
    print(f"  Correct Predictions: {total_correct:,}")
    print(f"  Overall Accuracy: {overall_accuracy:.2f}%")
    print(f"  Quarters Tested: {len(results)}")

    print(f"\nQuarterly Breakdown:")
    print("-" * 70)
    print(f"{'Quarter':<10} {'Predictions':>12} {'Accuracy':>10} {'UP Acc':>10} {'DOWN Acc':>10} {'HiConf':>10}")
    print("-" * 70)

    for r in results:
        print(f"{r['quarter']:<10} {r['total_predictions']:>12,} {r['accuracy']:>9.1f}% {r['up_accuracy']:>9.1f}% {r['down_accuracy']:>9.1f}% {r['high_conf_accuracy']:>9.1f}%")

    print("-" * 70)
    avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
    avg_up = sum(r['up_accuracy'] for r in results) / len(results)
    avg_down = sum(r['down_accuracy'] for r in results) / len(results)
    avg_hc = sum(r['high_conf_accuracy'] for r in results) / len(results)
    print(f"{'AVERAGE':<10} {total_preds:>12,} {avg_accuracy:>9.1f}% {avg_up:>9.1f}% {avg_down:>9.1f}% {avg_hc:>9.1f}%")

    # Save summary to JSON
    summary = {
        'backtest_id': backtest_id,
        'symbols': SYMBOLS,
        'quarters_tested': len(results),
        'total_predictions': total_preds,
        'total_correct': total_correct,
        'overall_accuracy': round(overall_accuracy, 2),
        'avg_quarterly_accuracy': round(avg_accuracy, 2),
        'avg_up_accuracy': round(avg_up, 2),
        'avg_down_accuracy': round(avg_down, 2),
        'avg_high_conf_accuracy': round(avg_hc, 2),
        'quarterly_results': results,
        'completed_at': datetime.now().isoformat()
    }

    with open('quarterly_backtest_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to: quarterly_backtest_results.json")

print("\n" + "=" * 70)
print(f"Completed: {datetime.now()}")
print("=" * 70)
