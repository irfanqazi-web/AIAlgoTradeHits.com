"""
Create Timeseries Insights Datasets for AIAlgoTradeHits.com
Based on: gcp-timeseries-bigquery-implementation.html

This script creates Timeseries Insights datasets using the exported GCS data
for anomaly detection and forecasting on stock/crypto data.
"""

from google.cloud import aiplatform
from google.protobuf import duration_pb2
import json
from datetime import datetime

# Configuration
PROJECT_ID = 'aialgotradehits'
LOCATION = 'us-central1'
GCS_BUCKET = 'aialgotradehits-timeseries'

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=LOCATION)


def create_stock_timeseries_dataset():
    """Create Timeseries Insights dataset for stock data"""

    dataset_name = "stock_price_timeseries"

    # Dataset configuration for stocks
    dataset_config = {
        "display_name": dataset_name,
        "metadata_schema_uri": "gs://google-cloud-aiplatform/schema/dataset/metadata/time_series_1.0.0.yaml",
        "metadata": {
            "input_config": {
                "gcs_source": {
                    "uri": f"gs://{GCS_BUCKET}/events/stocks/*.json.gz"
                }
            },
            "time_series_identifier_column": "symbol",
            "time_column": "eventTime",
            "target_column": "close",
            "forecast_horizon": 5,  # 5 day forecast
            "data_granularity_unit": "day",
            "data_granularity_count": 1
        }
    }

    print(f"Creating stock timeseries dataset: {dataset_name}")
    print(f"  Source: gs://{GCS_BUCKET}/events/stocks/")
    print(f"  Forecast horizon: 5 days")

    try:
        # Create the dataset
        dataset = aiplatform.TimeSeriesDataset.create(
            display_name=dataset_name,
            gcs_source=[f"gs://{GCS_BUCKET}/events/stocks/*.json.gz"],
            import_schema_uri="gs://google-cloud-aiplatform/schema/dataset/ioformat/time_series_io_format_1.0.0.yaml"
        )
        print(f"  Created dataset: {dataset.resource_name}")
        return dataset
    except Exception as e:
        print(f"  Error creating dataset: {e}")
        # Try alternative approach using BigQuery directly
        print("  Attempting BigQuery-based approach...")
        return create_bigquery_timeseries_view('stocks')


def create_crypto_timeseries_dataset():
    """Create Timeseries Insights dataset for crypto data"""

    dataset_name = "crypto_price_timeseries"

    print(f"Creating crypto timeseries dataset: {dataset_name}")
    print(f"  Source: gs://{GCS_BUCKET}/events/crypto/")
    print(f"  Forecast horizon: 5 days")

    try:
        dataset = aiplatform.TimeSeriesDataset.create(
            display_name=dataset_name,
            gcs_source=[f"gs://{GCS_BUCKET}/events/crypto/*.json.gz"],
            import_schema_uri="gs://google-cloud-aiplatform/schema/dataset/ioformat/time_series_io_format_1.0.0.yaml"
        )
        print(f"  Created dataset: {dataset.resource_name}")
        return dataset
    except Exception as e:
        print(f"  Error creating dataset: {e}")
        print("  Attempting BigQuery-based approach...")
        return create_bigquery_timeseries_view('crypto')


def create_bigquery_timeseries_view(asset_type: str):
    """Create BigQuery views optimized for Timeseries analysis"""

    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)

    table_name = f"{asset_type}_daily_clean"
    view_name = f"{asset_type}_timeseries_view"

    # Create a view with proper timeseries format
    view_query = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.crypto_trading_data.{view_name}` AS
    SELECT
        symbol,
        datetime as timestamp,
        CAST(open AS FLOAT64) as open,
        CAST(high AS FLOAT64) as high,
        CAST(low AS FLOAT64) as low,
        CAST(close AS FLOAT64) as close,
        CAST(volume AS FLOAT64) as volume,
        CAST(rsi AS FLOAT64) as rsi,
        CAST(macd AS FLOAT64) as macd,
        CAST(adx AS FLOAT64) as adx,
        CAST(atr AS FLOAT64) as atr,
        CAST(sma_20 AS FLOAT64) as sma_20,
        CAST(sma_50 AS FLOAT64) as sma_50,
        CAST(sma_200 AS FLOAT64) as sma_200,
        CAST(bollinger_upper AS FLOAT64) as bollinger_upper,
        CAST(bollinger_lower AS FLOAT64) as bollinger_lower,
        CAST(buy_pressure_pct AS FLOAT64) as buy_pressure_pct,
        CAST(sell_pressure_pct AS FLOAT64) as sell_pressure_pct,
        COALESCE(trend_regime, 0) as trend_regime,
        COALESCE(cycle_type, 0) as cycle_type,
        CAST(cycle_pnl_pct AS FLOAT64) as cycle_pnl_pct,
        -- Derived features for ML
        CAST((close - open) / NULLIF(open, 0) * 100 AS FLOAT64) as daily_return_pct,
        CAST((high - low) / NULLIF(low, 0) * 100 AS FLOAT64) as daily_range_pct,
        LAG(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close,
        LAG(close, 5) OVER (PARTITION BY symbol ORDER BY datetime) as close_5d_ago,
        LAG(close, 20) OVER (PARTITION BY symbol ORDER BY datetime) as close_20d_ago,
        -- Future targets for supervised learning
        LEAD(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) as next_day_close,
        LEAD(close, 5) OVER (PARTITION BY symbol ORDER BY datetime) as close_in_5d
    FROM `{PROJECT_ID}.crypto_trading_data.{table_name}`
    WHERE datetime IS NOT NULL
      AND close IS NOT NULL
      AND close > 0
    ORDER BY symbol, datetime
    """

    print(f"Creating BigQuery timeseries view: {view_name}")

    try:
        job = client.query(view_query)
        job.result()
        print(f"  Created view: {PROJECT_ID}.crypto_trading_data.{view_name}")
        return view_name
    except Exception as e:
        print(f"  Error creating view: {e}")
        return None


def create_anomaly_detection_config():
    """Create configuration for anomaly detection on price data"""

    config = {
        "name": "price_anomaly_detector",
        "description": "Detect unusual price movements in stocks and crypto",
        "metrics": [
            {
                "name": "price_spike",
                "description": "Detect sudden price spikes",
                "aggregation": "DELTA_PERCENT",
                "threshold_high": 5.0,  # 5% spike
                "threshold_low": -5.0   # 5% drop
            },
            {
                "name": "volume_surge",
                "description": "Detect unusual volume",
                "aggregation": "RATIO_TO_AVERAGE",
                "threshold_high": 3.0,  # 3x average volume
                "window_size": 20
            },
            {
                "name": "rsi_extreme",
                "description": "Detect extreme RSI values",
                "aggregation": "VALUE",
                "threshold_high": 80,
                "threshold_low": 20
            },
            {
                "name": "bollinger_breakout",
                "description": "Detect Bollinger Band breakouts",
                "aggregation": "CUSTOM",
                "condition": "close > bollinger_upper OR close < bollinger_lower"
            }
        ],
        "alert_settings": {
            "email_notification": True,
            "severity_levels": ["CRITICAL", "WARNING", "INFO"],
            "cooldown_minutes": 60
        }
    }

    config_path = f"gs://{GCS_BUCKET}/config/anomaly_detection_config.json"

    print(f"Anomaly detection configuration:")
    print(json.dumps(config, indent=2))

    # Save config to local file
    with open('anomaly_detection_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\nConfig saved to: anomaly_detection_config.json")
    return config


def create_forecasting_config():
    """Create configuration for price forecasting"""

    config = {
        "name": "price_forecaster",
        "description": "Forecast future prices for stocks and crypto",
        "model_type": "AutoML_Tabular_Forecasting",
        "features": {
            "target_column": "close",
            "time_column": "timestamp",
            "time_series_identifier": "symbol",
            "feature_columns": [
                "open", "high", "low", "volume",
                "rsi", "macd", "adx", "atr",
                "sma_20", "sma_50", "sma_200",
                "bollinger_upper", "bollinger_lower",
                "buy_pressure_pct", "sell_pressure_pct",
                "trend_regime", "cycle_type"
            ],
            "available_at_forecast": [
                "sma_20", "sma_50", "sma_200",
                "trend_regime"
            ]
        },
        "training_options": {
            "forecast_horizon": 5,
            "context_window": 30,
            "data_granularity_unit": "day",
            "budget_milli_node_hours": 1000,
            "optimization_objective": "minimize-rmse"
        },
        "evaluation_metrics": [
            "RMSE", "MAE", "MAPE", "R2"
        ]
    }

    print(f"Forecasting configuration:")
    print(json.dumps(config, indent=2))

    with open('forecasting_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\nConfig saved to: forecasting_config.json")
    return config


def setup_vertex_ai_training_pipeline():
    """Create Vertex AI training pipeline for timeseries forecasting"""

    from google.cloud import aiplatform

    pipeline_config = {
        "display_name": "trading_forecast_pipeline",
        "stages": [
            {
                "name": "data_prep",
                "type": "BigQueryExportOp",
                "config": {
                    "project": PROJECT_ID,
                    "dataset": "crypto_trading_data",
                    "table": "stocks_timeseries_view"
                }
            },
            {
                "name": "feature_engineering",
                "type": "DataTransformOp",
                "config": {
                    "transformations": [
                        "fill_missing_values",
                        "normalize_features",
                        "create_lag_features"
                    ]
                }
            },
            {
                "name": "model_training",
                "type": "AutoMLForecastingTrainOp",
                "config": {
                    "target_column": "close",
                    "time_column": "timestamp",
                    "forecast_horizon": 5,
                    "optimization_objective": "minimize-rmse"
                }
            },
            {
                "name": "model_evaluation",
                "type": "ModelEvaluationOp",
                "config": {
                    "metrics": ["rmse", "mae", "mape"]
                }
            },
            {
                "name": "model_deployment",
                "type": "ModelDeployOp",
                "config": {
                    "endpoint_name": "trading_forecast_endpoint",
                    "machine_type": "n1-standard-4"
                }
            }
        ]
    }

    print("Vertex AI Training Pipeline Configuration:")
    print(json.dumps(pipeline_config, indent=2))

    with open('vertex_pipeline_config.json', 'w') as f:
        json.dump(pipeline_config, f, indent=2)

    print(f"\nPipeline config saved to: vertex_pipeline_config.json")
    return pipeline_config


def main():
    """Main function to create all Timeseries Insights datasets"""

    print("=" * 80)
    print("CREATING TIMESERIES INSIGHTS DATASETS FOR AIALGOTRADEHITS.COM")
    print("=" * 80)
    print(f"Started: {datetime.now()}")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"GCS Bucket: gs://{GCS_BUCKET}/")

    # Create BigQuery views for timeseries analysis
    print("\n--- CREATING BIGQUERY TIMESERIES VIEWS ---")
    stock_view = create_bigquery_timeseries_view('stocks')
    crypto_view = create_bigquery_timeseries_view('crypto')

    # Create anomaly detection configuration
    print("\n--- CONFIGURING ANOMALY DETECTION ---")
    anomaly_config = create_anomaly_detection_config()

    # Create forecasting configuration
    print("\n--- CONFIGURING PRICE FORECASTING ---")
    forecast_config = create_forecasting_config()

    # Create Vertex AI pipeline configuration
    print("\n--- SETTING UP VERTEX AI PIPELINE ---")
    pipeline_config = setup_vertex_ai_training_pipeline()

    # Summary
    print("\n" + "=" * 80)
    print("SETUP SUMMARY")
    print("=" * 80)
    print(f"Stock timeseries view: {stock_view}")
    print(f"Crypto timeseries view: {crypto_view}")
    print("\nConfiguration files created:")
    print("  - anomaly_detection_config.json")
    print("  - forecasting_config.json")
    print("  - vertex_pipeline_config.json")
    print("\nNext steps:")
    print("  1. Upload configs to GCS: gsutil cp *.json gs://aialgotradehits-timeseries/config/")
    print("  2. Create Vertex AI dataset from BigQuery views")
    print("  3. Train AutoML forecasting model")
    print("  4. Deploy model endpoint for predictions")
    print(f"\nCompleted: {datetime.now()}")


if __name__ == "__main__":
    main()
