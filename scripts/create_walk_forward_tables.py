"""
Create Walk-Forward Validation Tables in BigQuery
Tables: walk_forward_runs, model_versions
"""

from google.cloud import bigquery
from datetime import datetime

def create_tables():
    """Create walk-forward validation tables"""

    client = bigquery.Client(project='aialgotradehits')
    dataset_id = 'ml_models'

    print("=" * 60)
    print("CREATING WALK-FORWARD VALIDATION TABLES")
    print("=" * 60)

    # Table 1: walk_forward_runs
    walk_forward_runs_schema = [
        bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("run_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("symbols", "STRING"),  # Comma-separated list
        bigquery.SchemaField("asset_class", "STRING"),  # Equity, FX, Crypto, Commodities
        bigquery.SchemaField("train_start", "DATE"),
        bigquery.SchemaField("train_end", "DATE"),
        bigquery.SchemaField("test_start", "DATE"),
        bigquery.SchemaField("test_end", "DATE"),
        bigquery.SchemaField("validation_window_days", "INT64"),
        bigquery.SchemaField("walk_forward_days", "INT64"),
        bigquery.SchemaField("retrain_frequency", "STRING"),  # daily, weekly, monthly
        bigquery.SchemaField("features_mode", "STRING"),  # default_16, advanced_97
        bigquery.SchemaField("features_used", "STRING"),  # JSON list of features
        bigquery.SchemaField("model_type", "STRING"),  # xgboost, lightgbm, etc.
        bigquery.SchemaField("confidence_threshold", "FLOAT64"),
        bigquery.SchemaField("total_predictions", "INT64"),
        bigquery.SchemaField("correct_predictions", "INT64"),
        bigquery.SchemaField("overall_accuracy", "FLOAT64"),
        bigquery.SchemaField("up_predictions", "INT64"),
        bigquery.SchemaField("up_correct", "INT64"),
        bigquery.SchemaField("up_accuracy", "FLOAT64"),
        bigquery.SchemaField("down_predictions", "INT64"),
        bigquery.SchemaField("down_correct", "INT64"),
        bigquery.SchemaField("down_accuracy", "FLOAT64"),
        bigquery.SchemaField("high_conf_predictions", "INT64"),
        bigquery.SchemaField("high_conf_correct", "INT64"),
        bigquery.SchemaField("high_conf_accuracy", "FLOAT64"),
        bigquery.SchemaField("sharpe_ratio", "FLOAT64"),
        bigquery.SchemaField("max_drawdown", "FLOAT64"),
        bigquery.SchemaField("total_return", "FLOAT64"),
        bigquery.SchemaField("status", "STRING"),  # pending, running, completed, failed, cancelled
        bigquery.SchemaField("progress_pct", "FLOAT64"),
        bigquery.SchemaField("current_day", "INT64"),
        bigquery.SchemaField("error_message", "STRING"),
        bigquery.SchemaField("started_at", "TIMESTAMP"),
        bigquery.SchemaField("completed_at", "TIMESTAMP"),
        bigquery.SchemaField("model_version_id", "STRING"),
    ]

    table_id = f"{client.project}.{dataset_id}.walk_forward_runs"
    table = bigquery.Table(table_id, schema=walk_forward_runs_schema)

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"\n[1] Created table: {table_id}")
        print(f"    Schema: {len(walk_forward_runs_schema)} columns")
    except Exception as e:
        print(f"    Error creating walk_forward_runs: {e}")

    # Table 2: model_versions
    model_versions_schema = [
        bigquery.SchemaField("version_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("model_name", "STRING"),
        bigquery.SchemaField("model_type", "STRING"),  # xgboost, sector_xgboost, etc.
        bigquery.SchemaField("sector", "STRING"),  # For sector-specific models
        bigquery.SchemaField("asset_class", "STRING"),
        bigquery.SchemaField("model_path", "STRING"),  # GCS path if stored
        bigquery.SchemaField("bigquery_model_name", "STRING"),  # BigQuery ML model name
        bigquery.SchemaField("features_used", "STRING"),  # JSON list
        bigquery.SchemaField("features_mode", "STRING"),  # default_16, advanced_97
        bigquery.SchemaField("hyperparameters", "STRING"),  # JSON
        bigquery.SchemaField("train_start", "DATE"),
        bigquery.SchemaField("train_end", "DATE"),
        bigquery.SchemaField("train_samples", "INT64"),
        bigquery.SchemaField("validation_accuracy", "FLOAT64"),
        bigquery.SchemaField("test_accuracy", "FLOAT64"),
        bigquery.SchemaField("precision_up", "FLOAT64"),
        bigquery.SchemaField("recall_up", "FLOAT64"),
        bigquery.SchemaField("f1_score", "FLOAT64"),
        bigquery.SchemaField("auc_roc", "FLOAT64"),
        bigquery.SchemaField("log_loss", "FLOAT64"),
        bigquery.SchemaField("feature_importance", "STRING"),  # JSON
        bigquery.SchemaField("is_active", "BOOL"),
        bigquery.SchemaField("is_production", "BOOL"),
        bigquery.SchemaField("replaced_by", "STRING"),  # version_id of replacement
        bigquery.SchemaField("notes", "STRING"),
    ]

    table_id = f"{client.project}.{dataset_id}.model_versions"
    table = bigquery.Table(table_id, schema=model_versions_schema)

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"\n[2] Created table: {table_id}")
        print(f"    Schema: {len(model_versions_schema)} columns")
    except Exception as e:
        print(f"    Error creating model_versions: {e}")

    # Table 3: walk_forward_daily_results (detailed daily predictions)
    daily_results_schema = [
        bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("prediction_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("predicted_direction", "STRING"),  # UP, DOWN
        bigquery.SchemaField("actual_direction", "STRING"),
        bigquery.SchemaField("confidence", "FLOAT64"),
        bigquery.SchemaField("probability_up", "FLOAT64"),
        bigquery.SchemaField("probability_down", "FLOAT64"),
        bigquery.SchemaField("is_correct", "BOOL"),
        bigquery.SchemaField("open_price", "FLOAT64"),
        bigquery.SchemaField("close_price", "FLOAT64"),
        bigquery.SchemaField("actual_return", "FLOAT64"),
        bigquery.SchemaField("cumulative_return", "FLOAT64"),
        bigquery.SchemaField("model_version_id", "STRING"),
        bigquery.SchemaField("retrained", "BOOL"),  # Was model retrained on this day?
    ]

    table_id = f"{client.project}.{dataset_id}.walk_forward_daily_results"
    table = bigquery.Table(table_id, schema=daily_results_schema)

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"\n[3] Created table: {table_id}")
        print(f"    Schema: {len(daily_results_schema)} columns")
    except Exception as e:
        print(f"    Error creating walk_forward_daily_results: {e}")

    # Table 4: walk_forward_equity_curve
    equity_curve_schema = [
        bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("trade_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("day_number", "INT64"),
        bigquery.SchemaField("equity_value", "FLOAT64"),  # Starting at 10000
        bigquery.SchemaField("daily_return", "FLOAT64"),
        bigquery.SchemaField("cumulative_return", "FLOAT64"),
        bigquery.SchemaField("rolling_accuracy_30d", "FLOAT64"),
        bigquery.SchemaField("rolling_sharpe_30d", "FLOAT64"),
        bigquery.SchemaField("drawdown", "FLOAT64"),
        bigquery.SchemaField("max_drawdown_to_date", "FLOAT64"),
        bigquery.SchemaField("win_rate_to_date", "FLOAT64"),
        bigquery.SchemaField("trades_to_date", "INT64"),
    ]

    table_id = f"{client.project}.{dataset_id}.walk_forward_equity_curve"
    table = bigquery.Table(table_id, schema=equity_curve_schema)

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"\n[4] Created table: {table_id}")
        print(f"    Schema: {len(equity_curve_schema)} columns")
    except Exception as e:
        print(f"    Error creating walk_forward_equity_curve: {e}")

    print("\n" + "=" * 60)
    print("TABLE CREATION COMPLETE")
    print("=" * 60)

    # Verify tables exist
    print("\nVerifying tables...")
    tables = list(client.list_tables(f"{client.project}.{dataset_id}"))
    wf_tables = [t.table_id for t in tables if 'walk_forward' in t.table_id or 'model_versions' in t.table_id]

    print(f"\nWalk-Forward tables in {dataset_id}:")
    for t in sorted(wf_tables):
        print(f"  - {t}")

    return True

if __name__ == "__main__":
    create_tables()
