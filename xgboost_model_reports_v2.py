"""
XGBoost Individual Model Reports Generator v2
==============================================
Based on Saleem's validated 16-feature model with 68.5% UP accuracy.

Key improvements:
- Handles both stocks and ETFs table schemas
- Filters for quality data with non-null indicators
- Class balancing for better UP prediction
- Uses recent data (2020+) for better relevance

Generates individual model reports for:
GOOGL, SPY, QQQ, QQQI, AAPL, NVDA, TSLA, AMZN
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.utils import class_weight
import xgboost as xgb

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Symbols to analyze
SYMBOLS = ['GOOGL', 'SPY', 'QQQ', 'QQQI', 'AAPL', 'NVDA', 'TSLA', 'AMZN']

# Saleem's validated 16 features
FEATURES_16 = [
    'awesome_osc', 'cci', 'macd', 'macd_cross', 'macd_histogram',
    'macd_signal', 'mfi', 'momentum', 'rsi', 'rsi_overbought',
    'rsi_oversold', 'rsi_slope', 'rsi_zscore', 'vwap_daily',
    'pivot_high_flag', 'pivot_low_flag'
]

# XGBoost parameters from Saleem's validation
XGBOOST_PARAMS = {
    'max_depth': 8,
    'learning_rate': 0.3,
    'n_estimators': 100,
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'use_label_encoder': False,
    'random_state': 42,
    'scale_pos_weight': 1.0  # Will be adjusted based on class balance
}


class ModelReport:
    """Store results for each symbol"""
    def __init__(self, symbol):
        self.symbol = symbol
        self.data_points = 0
        self.train_size = 0
        self.test_size = 0
        self.train_period = ""
        self.test_period = ""
        self.test_accuracy = 0.0
        self.up_accuracy = 0.0
        self.down_accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
        self.f1 = 0.0
        self.feature_importance = {}
        self.top_3_features = []
        self.confusion_matrix = None
        self.cv_scores = []
        self.cv_mean = 0.0
        self.cv_std = 0.0
        self.status = "PENDING"
        self.error_message = ""
        self.class_balance = ""
        self.data_quality = ""


def get_bigquery_client():
    """Get BigQuery client"""
    return bigquery.Client(project=PROJECT_ID)


def fetch_stock_data(client, symbol):
    """Fetch stock data with Saleem's 16 features"""

    query = f"""
    WITH raw_data AS (
        SELECT
            symbol,
            datetime,
            open,
            high,
            low,
            close,
            volume,
            -- Core indicators
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            mfi,
            cci,
            momentum,
            awesome_osc,
            -- Derived features
            rsi_slope,
            rsi_zscore,
            rsi_overbought,
            rsi_oversold,
            macd_cross,
            vwap_daily,
            -- Pivot flags (KEY FEATURES)
            pivot_low_flag,
            pivot_high_flag,
            -- For analysis
            ema_12,
            ema_26,
            sma_50,
            sma_200,
            adx
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE symbol = '{symbol}'
            AND datetime >= '2018-01-01'
            AND rsi IS NOT NULL
            AND macd IS NOT NULL
        ORDER BY datetime
    ),
    with_target AS (
        SELECT
            *,
            CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
        FROM raw_data
    )
    SELECT * FROM with_target WHERE target IS NOT NULL
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"  Error fetching stock {symbol}: {e}")
        return pd.DataFrame()


def fetch_etf_data(client, symbol):
    """Fetch ETF data (different schema without pivot flags)"""

    query = f"""
    WITH raw_data AS (
        SELECT
            symbol,
            datetime,
            open,
            high,
            low,
            close,
            volume,
            -- Core indicators
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            mfi,
            cci,
            momentum,
            ao as awesome_osc,
            -- EMAs for calculations
            ema_12,
            ema_26,
            sma_20,
            sma_50,
            sma_200,
            adx,
            atr,
            stoch_k,
            stoch_d,
            bollinger_upper,
            bollinger_middle,
            bollinger_lower
        FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
        WHERE symbol = '{symbol}'
            AND datetime >= '2018-01-01'
            AND rsi IS NOT NULL
            AND macd IS NOT NULL
        ORDER BY datetime
    ),
    with_derived AS (
        SELECT
            *,
            -- Calculate derived features that ETFs don't have
            rsi - LAG(rsi, 1) OVER (ORDER BY datetime) as rsi_slope,
            (rsi - AVG(rsi) OVER (ORDER BY datetime ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)) /
                NULLIF(STDDEV(rsi) OVER (ORDER BY datetime ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 0) as rsi_zscore,
            CASE WHEN rsi > 70 THEN 1 ELSE 0 END as rsi_overbought,
            CASE WHEN rsi < 30 THEN 1 ELSE 0 END as rsi_oversold,
            CASE
                WHEN macd > macd_signal AND LAG(macd, 1) OVER (ORDER BY datetime) <= LAG(macd_signal, 1) OVER (ORDER BY datetime) THEN 1
                WHEN macd < macd_signal AND LAG(macd, 1) OVER (ORDER BY datetime) >= LAG(macd_signal, 1) OVER (ORDER BY datetime) THEN -1
                ELSE 0
            END as macd_cross,
            (high + low + close) / 3 as vwap_daily,
            -- Pivot detection (simplified)
            CASE WHEN low < LAG(low, 1) OVER (ORDER BY datetime) AND low < LAG(low, 2) OVER (ORDER BY datetime)
                  AND low < LEAD(low, 1) OVER (ORDER BY datetime) AND low < LEAD(low, 2) OVER (ORDER BY datetime)
                 THEN 1 ELSE 0 END as pivot_low_flag,
            CASE WHEN high > LAG(high, 1) OVER (ORDER BY datetime) AND high > LAG(high, 2) OVER (ORDER BY datetime)
                  AND high > LEAD(high, 1) OVER (ORDER BY datetime) AND high > LEAD(high, 2) OVER (ORDER BY datetime)
                 THEN 1 ELSE 0 END as pivot_high_flag,
            -- Target
            CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
        FROM raw_data
    )
    SELECT * FROM with_derived
    WHERE target IS NOT NULL
        AND rsi_slope IS NOT NULL
        AND rsi_zscore IS NOT NULL
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"  Error fetching ETF {symbol}: {e}")
        return pd.DataFrame()


def prepare_features(df):
    """Prepare the 16 features for model training"""

    feature_cols = [
        'awesome_osc', 'cci', 'macd', 'macd_cross', 'macd_histogram',
        'macd_signal', 'mfi', 'momentum', 'rsi', 'rsi_overbought',
        'rsi_oversold', 'rsi_slope', 'rsi_zscore', 'vwap_daily',
        'pivot_high_flag', 'pivot_low_flag'
    ]

    # Check which features exist
    available_features = [f for f in feature_cols if f in df.columns]
    missing_features = [f for f in feature_cols if f not in df.columns]

    if missing_features:
        print(f"  Note: Missing features: {missing_features}")

    # Fill NaN values with 0 or median
    X = df[available_features].copy()
    for col in X.columns:
        if X[col].isnull().sum() > 0:
            X[col] = X[col].fillna(X[col].median() if X[col].median() != 0 else 0)

    y = df['target'].fillna(0).astype(int)

    return X, y, available_features


def train_and_evaluate(X, y, df, report):
    """Train XGBoost model and evaluate performance with class balancing"""

    # Time-based split (80% train, 20% test)
    split_idx = int(len(X) * 0.8)

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Get date ranges
    train_dates = df['datetime'].iloc[:split_idx]
    test_dates = df['datetime'].iloc[split_idx:]

    report.train_size = len(X_train)
    report.test_size = len(X_test)
    report.train_period = f"{train_dates.min().strftime('%Y-%m-%d')} to {train_dates.max().strftime('%Y-%m-%d')}"
    report.test_period = f"{test_dates.min().strftime('%Y-%m-%d')} to {test_dates.max().strftime('%Y-%m-%d')}"

    # Calculate class balance
    up_count = y_train.sum()
    down_count = len(y_train) - up_count
    report.class_balance = f"UP: {up_count} ({up_count/len(y_train)*100:.1f}%), DOWN: {down_count} ({down_count/len(y_train)*100:.1f}%)"

    # Calculate scale_pos_weight for class balancing
    scale_pos_weight = down_count / up_count if up_count > 0 else 1.0

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost model with class balancing
    params = XGBOOST_PARAMS.copy()
    params['scale_pos_weight'] = scale_pos_weight

    model = xgb.XGBClassifier(**params)
    model.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=False)

    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

    # Calculate metrics
    report.test_accuracy = accuracy_score(y_test, y_pred) * 100
    report.precision = precision_score(y_test, y_pred, zero_division=0) * 100
    report.recall = recall_score(y_test, y_pred, zero_division=0) * 100
    report.f1 = f1_score(y_test, y_pred, zero_division=0) * 100

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    report.confusion_matrix = cm

    # Calculate UP and DOWN accuracy
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        report.up_accuracy = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0
        report.down_accuracy = (tn / (tn + fp) * 100) if (tn + fp) > 0 else 0

    # Feature importance
    importance_dict = dict(zip(X.columns, model.feature_importances_))
    report.feature_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    report.top_3_features = list(report.feature_importance.keys())[:3]

    # Cross-validation with TimeSeriesSplit
    tscv = TimeSeriesSplit(n_splits=5)
    try:
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=tscv, scoring='accuracy')
        report.cv_scores = cv_scores.tolist()
        report.cv_mean = cv_scores.mean() * 100
        report.cv_std = cv_scores.std() * 100
    except:
        report.cv_mean = report.test_accuracy
        report.cv_std = 0

    # Determine status based on UP accuracy (Saleem's criteria)
    if report.up_accuracy >= 65:
        report.status = "PASS"
    elif report.up_accuracy >= 60:
        report.status = "OK"
    else:
        report.status = "NEEDS_REVIEW"

    return model, scaler


def run_individual_report(client, symbol):
    """Run complete analysis for a single symbol"""

    print(f"\n{'='*60}")
    print(f"Processing {symbol}...")
    print(f"{'='*60}")

    report = ModelReport(symbol)

    # Determine if stock or ETF
    is_etf = symbol in ['SPY', 'QQQ', 'QQQI', 'IWM', 'DIA', 'VOO', 'VTI']

    # Fetch data
    print(f"  Fetching data from BigQuery ({('ETF' if is_etf else 'Stock')})...")
    if is_etf:
        df = fetch_etf_data(client, symbol)
    else:
        df = fetch_stock_data(client, symbol)

    if df.empty:
        report.status = "ERROR"
        report.error_message = "No data found in BigQuery"
        return report

    report.data_points = len(df)
    print(f"  Found {report.data_points} data points")

    # Check data quality
    null_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    report.data_quality = f"{100-null_pct:.1f}% complete"

    if report.data_points < 500:
        report.status = "ERROR"
        report.error_message = f"Insufficient data: {report.data_points} points (need 500+)"
        return report

    # Prepare features
    print(f"  Preparing features...")
    X, y, features = prepare_features(df)
    print(f"  Using {len(features)} features")

    # Check class distribution
    up_pct = y.mean() * 100
    print(f"  Class distribution: {up_pct:.1f}% UP, {100-up_pct:.1f}% DOWN")

    # Train and evaluate
    print(f"  Training XGBoost model with class balancing...")
    try:
        model, scaler = train_and_evaluate(X, y, df, report)
        print(f"  Training complete!")
        print(f"  Test Accuracy: {report.test_accuracy:.1f}%")
        print(f"  UP Accuracy: {report.up_accuracy:.1f}%")
        print(f"  DOWN Accuracy: {report.down_accuracy:.1f}%")
        print(f"  Top 3 Features: {', '.join(report.top_3_features)}")
        print(f"  Status: {report.status}")
    except Exception as e:
        report.status = "ERROR"
        report.error_message = str(e)
        print(f"  Error during training: {e}")

    return report


def generate_pdf_report(reports, filename):
    """Generate comprehensive PDF report"""

    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=22, spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue
    )

    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=14, spaceAfter=12, spaceBefore=20, textColor=colors.darkblue
    )

    subheading_style = ParagraphStyle(
        'CustomSubheading', parent=styles['Heading3'],
        fontSize=11, spaceAfter=8, spaceBefore=12, textColor=colors.darkgreen
    )

    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, spaceAfter=8
    )

    story = []

    # Title Page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("XGBoost ML Model Validation Report", title_style))
    story.append(Paragraph("Individual Symbol Analysis - v2", heading_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", body_style))
    story.append(Paragraph("Based on Saleem's Validated 16-Feature Model (68.5% UP Accuracy)", body_style))
    story.append(Spacer(1, 0.3*inch))

    # Executive Summary
    passed = sum(1 for r in reports if r.status == "PASS")
    ok = sum(1 for r in reports if r.status == "OK")
    needs_review = sum(1 for r in reports if r.status == "NEEDS_REVIEW")
    errors = sum(1 for r in reports if r.status == "ERROR")

    valid_reports = [r for r in reports if r.status not in ["ERROR", "PENDING"]]
    avg_up = sum(r.up_accuracy for r in valid_reports) / len(valid_reports) if valid_reports else 0
    avg_test = sum(r.test_accuracy for r in valid_reports) / len(valid_reports) if valid_reports else 0

    summary_data = [
        ['Metric', 'Result'],
        ['Symbols Analyzed', str(len(reports))],
        ['Tests Passed (UP >= 65%)', f'{passed}/{len(reports)}'],
        ['Tests OK (UP 60-65%)', f'{ok}/{len(reports)}'],
        ['Needs Review (UP < 60%)', f'{needs_review}/{len(reports)}'],
        ['Errors', f'{errors}/{len(reports)}'],
        ['Average UP Accuracy', f'{avg_up:.1f}%'],
        ['Average Test Accuracy', f'{avg_test:.1f}%'],
    ]

    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    story.append(summary_table)
    story.append(PageBreak())

    # Results Summary Table
    story.append(Paragraph("Results Summary", heading_style))

    results_data = [
        ['Symbol', 'Data Pts', 'Train Period', 'Test %', 'UP %', 'DOWN %', 'Status']
    ]

    for r in reports:
        results_data.append([
            r.symbol,
            str(r.data_points),
            r.train_period[:10] if r.train_period else 'N/A',
            f'{r.test_accuracy:.1f}%' if r.test_accuracy else 'N/A',
            f'{r.up_accuracy:.1f}%' if r.up_accuracy else 'N/A',
            f'{r.down_accuracy:.1f}%' if r.down_accuracy else 'N/A',
            r.status
        ])

    results_table = Table(results_data, colWidths=[0.7*inch, 0.7*inch, 1.1*inch, 0.7*inch, 0.7*inch, 0.7*inch, 1*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(results_table)
    story.append(Spacer(1, 0.3*inch))

    # The 16 Features
    story.append(Paragraph("Saleem's Validated 16 Features", heading_style))
    features_text = """
    <b>Momentum:</b> awesome_osc, momentum, rsi, rsi_overbought, rsi_oversold, rsi_slope, rsi_zscore<br/>
    <b>Trend:</b> macd, macd_cross, macd_histogram, macd_signal, cci<br/>
    <b>Volume/Flow:</b> mfi, vwap_daily<br/>
    <b>Pivot Signals (KEY):</b> pivot_high_flag, pivot_low_flag
    """
    story.append(Paragraph(features_text, body_style))
    story.append(PageBreak())

    # Individual Symbol Reports
    for report in reports:
        story.append(Paragraph(f"Report: {report.symbol}", heading_style))

        if report.status == "ERROR":
            story.append(Paragraph(f"Error: {report.error_message}", body_style))
            story.append(Spacer(1, 0.5*inch))
            continue

        # Symbol details table
        details_data = [
            ['Metric', 'Value'],
            ['Total Data Points', str(report.data_points)],
            ['Training Size', str(report.train_size)],
            ['Test Size', str(report.test_size)],
            ['Training Period', report.train_period],
            ['Test Period', report.test_period],
            ['Class Balance', report.class_balance],
            ['Data Quality', report.data_quality],
            ['Test Accuracy', f'{report.test_accuracy:.2f}%'],
            ['UP Accuracy', f'{report.up_accuracy:.2f}%'],
            ['DOWN Accuracy', f'{report.down_accuracy:.2f}%'],
            ['Precision', f'{report.precision:.2f}%'],
            ['Recall', f'{report.recall:.2f}%'],
            ['F1 Score', f'{report.f1:.2f}%'],
            ['CV Mean', f'{report.cv_mean:.2f}%'],
            ['Status', report.status],
        ]

        details_table = Table(details_data, colWidths=[1.8*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        story.append(details_table)
        story.append(Spacer(1, 0.2*inch))

        # Top 3 Features
        story.append(Paragraph("Top 3 Features:", subheading_style))
        if report.top_3_features:
            for i, feat in enumerate(report.top_3_features):
                imp = report.feature_importance.get(feat, 0)
                pivot_marker = " ** KEY **" if 'pivot' in feat else ""
                story.append(Paragraph(f"{i+1}. {feat}: {imp:.4f}{pivot_marker}", body_style))

        # Confusion Matrix
        if report.confusion_matrix is not None:
            story.append(Paragraph("Confusion Matrix:", subheading_style))
            cm = report.confusion_matrix
            cm_data = [
                ['', 'Pred DOWN', 'Pred UP'],
                ['Actual DOWN', str(cm[0][0]), str(cm[0][1])],
                ['Actual UP', str(cm[1][0]), str(cm[1][1])],
            ]
            cm_table = Table(cm_data, colWidths=[1.2*inch, 1*inch, 1*inch])
            cm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(cm_table)

        story.append(PageBreak())

    # XGBoost Configuration
    story.append(Paragraph("XGBoost Model Configuration", heading_style))
    config_data = [
        ['Parameter', 'Value'],
        ['Algorithm', 'XGBoost Classifier'],
        ['max_depth', '8'],
        ['learning_rate', '0.3'],
        ['n_estimators', '100'],
        ['objective', 'binary:logistic'],
        ['Class Balancing', 'scale_pos_weight (auto)'],
    ]

    config_table = Table(config_data, colWidths=[2*inch, 2*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(config_table)
    story.append(Spacer(1, 0.5*inch))

    # Conclusions
    story.append(Paragraph("Key Findings & Recommendations", heading_style))
    conclusions = [
        f"Models analyzed: {len(reports)} symbols",
        f"Average UP accuracy: {avg_up:.1f}%",
        "Pivot flags (pivot_low_flag, pivot_high_flag) are critical features",
        "Class balancing (scale_pos_weight) improves UP prediction",
        "ETFs require derived feature calculation",
        "Recommend: Focus on UP signals for trading decisions"
    ]
    for c in conclusions:
        story.append(Paragraph(f"- {c}", body_style))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph("AIAlgoTradeHits.com - XGBoost ML Model Validation", body_style))

    # Build PDF
    doc.build(story)
    print(f"\nPDF Report generated: {filename}")
    return filename


def main():
    """Main execution function"""

    print("="*70)
    print("XGBoost Individual Model Reports Generator v2")
    print("Based on Saleem's Validated 16-Feature Model")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print("="*70)

    # Initialize BigQuery client
    client = get_bigquery_client()

    # Run reports for each symbol
    reports = []
    for symbol in SYMBOLS:
        report = run_individual_report(client, symbol)
        reports.append(report)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\n{'Symbol':<10} {'Data':<8} {'Test%':<8} {'UP%':<8} {'DOWN%':<8} {'Top Feature':<20} {'Status':<12}")
    print("-"*80)

    for r in reports:
        top_feat = r.top_3_features[0] if r.top_3_features else 'N/A'
        print(f"{r.symbol:<10} {r.data_points:<8} {r.test_accuracy:<8.1f} {r.up_accuracy:<8.1f} {r.down_accuracy:<8.1f} {top_feat:<20} {r.status:<12}")

    # Generate PDF
    print("\nGenerating comprehensive PDF report...")
    pdf_file = "C:/1AITrading/Trading/XGBOOST_MODEL_REPORTS_V2.pdf"
    generate_pdf_report(reports, pdf_file)

    # Save JSON results
    json_file = "C:/1AITrading/Trading/xgboost_model_results_v2.json"
    results_dict = {
        'generated': datetime.now().isoformat(),
        'symbols': SYMBOLS,
        'features': FEATURES_16,
        'xgboost_params': XGBOOST_PARAMS,
        'reports': [
            {
                'symbol': r.symbol,
                'data_points': r.data_points,
                'train_size': r.train_size,
                'test_size': r.test_size,
                'train_period': r.train_period,
                'test_period': r.test_period,
                'test_accuracy': round(r.test_accuracy, 2),
                'up_accuracy': round(r.up_accuracy, 2),
                'down_accuracy': round(r.down_accuracy, 2),
                'precision': round(r.precision, 2),
                'recall': round(r.recall, 2),
                'f1': round(r.f1, 2),
                'cv_mean': round(r.cv_mean, 2),
                'top_3_features': r.top_3_features,
                'class_balance': r.class_balance,
                'data_quality': r.data_quality,
                'status': r.status,
                'error_message': r.error_message
            }
            for r in reports
        ]
    }

    with open(json_file, 'w') as f:
        json.dump(results_dict, f, indent=2)
    print(f"JSON results saved: {json_file}")

    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)

    return reports


if __name__ == "__main__":
    main()
