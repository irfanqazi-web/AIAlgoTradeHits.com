"""
Datetime Utilities for AIAlgoTradeHits
Central module for all datetime conversions to ensure consistency
"""
from datetime import datetime, timezone
import pandas as pd


def get_utc_now():
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


def get_utc_now_str():
    """Get current UTC time as ISO string for BigQuery"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def to_bigquery_datetime(dt):
    """Convert datetime to BigQuery-compatible string"""
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, pd.Timestamp):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return str(dt)


def to_bigquery_date(dt):
    """Convert datetime to BigQuery DATE string"""
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, str):
        return dt[:10] if len(dt) >= 10 else dt
    if isinstance(dt, pd.Timestamp):
        return dt.strftime('%Y-%m-%d')
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d')
    return str(dt)[:10]


def to_bigquery_timestamp(dt):
    """Convert datetime to BigQuery TIMESTAMP string"""
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, pd.Timestamp):
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return str(dt)


def prepare_df_for_bigquery(df):
    """Prepare DataFrame datetime columns for BigQuery upload"""
    df = df.copy()

    # Convert all datetime columns to string format
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]' or 'datetime' in str(df[col].dtype).lower():
            df[col] = df[col].apply(to_bigquery_datetime)
        elif col in ['datetime', 'date', 'created_at', 'updated_at', 'timestamp']:
            df[col] = df[col].apply(to_bigquery_datetime)

    return df


# Standard timezone for the project
PROJECT_TIMEZONE = 'America/New_York'
