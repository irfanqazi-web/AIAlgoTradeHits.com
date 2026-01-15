"""
XGBoost Individual Model Reports Generator v3
==============================================
Based on Saleem's validated 16-feature model with 68.5% UP accuracy.

CRITICAL FIX: Deduplicates data to ensure one row per date per symbol
before calculating next-day target.

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
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
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

# Symbols to analyze (including QQQI)
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
    'random_state': 42
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
    """Fetch deduplicated stock data with Saleem's 16 features"""

    query = f"""
    WITH deduplicated AS (
        -- CRITICAL: Deduplicate to one row per date per symbol
        SELECT
            symbol,
            DATE(datetime) as trade_date,
            FIRST_VALUE(datetime) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as datetime,
            FIRST_VALUE(open) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as open,
            FIRST_VALUE(high) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as high,
            FIRST_VALUE(low) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as low,
            FIRST_VALUE(close) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as close,
            FIRST_VALUE(volume) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as volume,
            -- Core indicators
            FIRST_VALUE(rsi) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rsi,
            FIRST_VALUE(macd) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd,
            FIRST_VALUE(macd_signal) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd_signal,
            FIRST_VALUE(macd_histogram) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd_histogram,
            FIRST_VALUE(mfi) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as mfi,
            FIRST_VALUE(cci) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as cci,
            FIRST_VALUE(momentum) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as momentum,
            FIRST_VALUE(awesome_osc) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as awesome_osc,
            -- Derived features
            FIRST_VALUE(rsi_slope) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rsi_slope,
            FIRST_VALUE(rsi_zscore) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rsi_zscore,
            FIRST_VALUE(rsi_overbought) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rsi_overbought,
            FIRST_VALUE(rsi_oversold) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rsi_oversold,
            FIRST_VALUE(macd_cross) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd_cross,
            FIRST_VALUE(vwap_daily) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as vwap_daily,
            -- Pivot flags (KEY FEATURES)
            FIRST_VALUE(pivot_low_flag) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as pivot_low_flag,
            FIRST_VALUE(pivot_high_flag) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as pivot_high_flag,
            -- For analysis
            FIRST_VALUE(ema_12) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as ema_12,
            FIRST_VALUE(ema_26) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as ema_26,
            FIRST_VALUE(sma_50) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as sma_50,
            FIRST_VALUE(sma_200) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as sma_200,
            FIRST_VALUE(adx) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as adx,
            ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE symbol = '{symbol}'
            AND datetime >= '2018-01-01'
            AND rsi IS NOT NULL
            AND close IS NOT NULL
    ),
    unique_daily AS (
        SELECT * EXCEPT(rn, trade_date)
        FROM deduplicated
        WHERE rn = 1
    ),
    with_target AS (
        SELECT
            *,
            -- Target: next day close > today's close
            CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
        FROM unique_daily
    )
    SELECT * FROM with_target WHERE target IS NOT NULL
    ORDER BY datetime
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"  Error fetching stock {symbol}: {e}")
        return pd.DataFrame()


def fetch_etf_data(client, symbol):
    """Fetch deduplicated ETF data"""

    query = f"""
    WITH deduplicated AS (
        SELECT
            symbol,
            DATE(datetime) as trade_date,
            FIRST_VALUE(datetime) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as datetime,
            FIRST_VALUE(open) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as open,
            FIRST_VALUE(high) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as high,
            FIRST_VALUE(low) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as low,
            FIRST_VALUE(close) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as close,
            FIRST_VALUE(volume) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as volume,
            -- Core indicators
            FIRST_VALUE(rsi) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rsi,
            FIRST_VALUE(macd) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd,
            FIRST_VALUE(macd_signal) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd_signal,
            FIRST_VALUE(macd_histogram) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as macd_histogram,
            FIRST_VALUE(mfi) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as mfi,
            FIRST_VALUE(cci) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as cci,
            FIRST_VALUE(momentum) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as momentum,
            FIRST_VALUE(ao) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as awesome_osc,
            FIRST_VALUE(ema_12) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as ema_12,
            FIRST_VALUE(ema_26) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as ema_26,
            FIRST_VALUE(sma_20) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as sma_20,
            FIRST_VALUE(sma_50) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as sma_50,
            FIRST_VALUE(sma_200) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as sma_200,
            FIRST_VALUE(adx) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as adx,
            FIRST_VALUE(atr) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as atr,
            ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rn
        FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
        WHERE symbol = '{symbol}'
            AND datetime >= '2018-01-01'
            AND rsi IS NOT NULL
            AND close IS NOT NULL
    ),
    unique_daily AS (
        SELECT * EXCEPT(rn, trade_date)
        FROM deduplicated
        WHERE rn = 1
    ),
    with_derived AS (
        SELECT
            *,
            -- Calculate derived features
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
            -- Pivot detection
            CASE WHEN low < LAG(low, 1) OVER (ORDER BY datetime) AND low < LAG(low, 2) OVER (ORDER BY datetime)
                  AND low < LEAD(low, 1) OVER (ORDER BY datetime) AND low < LEAD(low, 2) OVER (ORDER BY datetime)
                 THEN 1 ELSE 0 END as pivot_low_flag,
            CASE WHEN high > LAG(high, 1) OVER (ORDER BY datetime) AND high > LAG(high, 2) OVER (ORDER BY datetime)
                  AND high > LEAD(high, 1) OVER (ORDER BY datetime) AND high > LEAD(high, 2) OVER (ORDER BY datetime)
                 THEN 1 ELSE 0 END as pivot_high_flag,
            -- Target
            CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
        FROM unique_daily
    )
    SELECT * FROM with_derived
    WHERE target IS NOT NULL
        AND rsi_slope IS NOT NULL
    ORDER BY datetime
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

    available_features = [f for f in feature_cols if f in df.columns]

    X = df[available_features].copy()
    for col in X.columns:
        if X[col].isnull().sum() > 0:
            X[col] = X[col].fillna(X[col].median() if pd.notna(X[col].median()) else 0)

    y = df['target'].fillna(0).astype(int)

    return X, y, available_features


def train_and_evaluate(X, y, df, report):
    """Train XGBoost model and evaluate"""

    # Time-based split (80% train, 20% test)
    split_idx = int(len(X) * 0.8)

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    train_dates = df['datetime'].iloc[:split_idx]
    test_dates = df['datetime'].iloc[split_idx:]

    report.train_size = len(X_train)
    report.test_size = len(X_test)
    report.train_period = f"{train_dates.min().strftime('%Y-%m-%d')} to {train_dates.max().strftime('%Y-%m-%d')}"
    report.test_period = f"{test_dates.min().strftime('%Y-%m-%d')} to {test_dates.max().strftime('%Y-%m-%d')}"

    up_count = y_train.sum()
    down_count = len(y_train) - up_count
    report.class_balance = f"UP: {up_count} ({up_count/len(y_train)*100:.1f}%), DOWN: {down_count} ({down_count/len(y_train)*100:.1f}%)"

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost
    model = xgb.XGBClassifier(**XGBOOST_PARAMS)
    model.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=False)

    # Predictions
    y_pred = model.predict(X_test_scaled)

    # Metrics
    report.test_accuracy = accuracy_score(y_test, y_pred) * 100
    report.precision = precision_score(y_test, y_pred, zero_division=0) * 100
    report.recall = recall_score(y_test, y_pred, zero_division=0) * 100
    report.f1 = f1_score(y_test, y_pred, zero_division=0) * 100

    cm = confusion_matrix(y_test, y_pred)
    report.confusion_matrix = cm

    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        report.up_accuracy = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0
        report.down_accuracy = (tn / (tn + fp) * 100) if (tn + fp) > 0 else 0

    # Feature importance
    importance_dict = dict(zip(X.columns, model.feature_importances_))
    report.feature_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    report.top_3_features = list(report.feature_importance.keys())[:3]

    # Cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    try:
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=tscv, scoring='accuracy')
        report.cv_mean = cv_scores.mean() * 100
        report.cv_std = cv_scores.std() * 100
    except:
        report.cv_mean = report.test_accuracy

    # Status
    if report.up_accuracy >= 65:
        report.status = "PASS"
    elif report.up_accuracy >= 60:
        report.status = "OK"
    else:
        report.status = "NEEDS_REVIEW"

    return model


def run_individual_report(client, symbol):
    """Run complete analysis for a single symbol"""

    print(f"\n{'='*60}")
    print(f"Processing {symbol}...")
    print(f"{'='*60}")

    report = ModelReport(symbol)
    is_etf = symbol in ['SPY', 'QQQ', 'QQQI', 'IWM', 'DIA', 'VOO', 'VTI']

    print(f"  Fetching deduplicated data from BigQuery ({('ETF' if is_etf else 'Stock')})...")

    if is_etf:
        df = fetch_etf_data(client, symbol)
    else:
        df = fetch_stock_data(client, symbol)

    if df.empty:
        report.status = "ERROR"
        report.error_message = "No data found"
        return report

    report.data_points = len(df)
    print(f"  Found {report.data_points} unique daily records")

    if report.data_points < 500:
        report.status = "ERROR"
        report.error_message = f"Insufficient data: {report.data_points}"
        return report

    print(f"  Preparing features...")
    X, y, features = prepare_features(df)
    print(f"  Using {len(features)} features")

    up_pct = y.mean() * 100
    print(f"  Class distribution: {up_pct:.1f}% UP, {100-up_pct:.1f}% DOWN")

    print(f"  Training XGBoost model...")
    try:
        model = train_and_evaluate(X, y, df, report)
        print(f"  Test Accuracy: {report.test_accuracy:.1f}%")
        print(f"  UP Accuracy: {report.up_accuracy:.1f}%")
        print(f"  DOWN Accuracy: {report.down_accuracy:.1f}%")
        print(f"  Top 3 Features: {', '.join(report.top_3_features)}")
        print(f"  Status: {report.status}")
    except Exception as e:
        report.status = "ERROR"
        report.error_message = str(e)
        print(f"  Error: {e}")

    return report


def generate_pdf_report(reports, filename):
    """Generate comprehensive PDF report"""

    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=22, spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue)

    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
        fontSize=14, spaceAfter=12, spaceBefore=20, textColor=colors.darkblue)

    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
        fontSize=11, spaceAfter=8, spaceBefore=12, textColor=colors.darkgreen)

    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=8)

    story = []

    # Title
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("XGBoost ML Model Validation Report v3", title_style))
    story.append(Paragraph("Individual Symbol Analysis - Deduplicated Data", heading_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", body_style))
    story.append(Paragraph("Based on Saleem's Validated 16-Feature Model (68.5% UP Target)", body_style))
    story.append(Spacer(1, 0.3*inch))

    # Summary stats
    valid_reports = [r for r in reports if r.status not in ["ERROR", "PENDING"]]
    passed = sum(1 for r in reports if r.status == "PASS")
    ok = sum(1 for r in reports if r.status == "OK")
    avg_up = sum(r.up_accuracy for r in valid_reports) / len(valid_reports) if valid_reports else 0

    summary_data = [
        ['Metric', 'Result'],
        ['Symbols Analyzed', str(len(reports))],
        ['Tests Passed (UP >= 65%)', f'{passed}/{len(reports)}'],
        ['Tests OK (UP 60-65%)', f'{ok}/{len(reports)}'],
        ['Average UP Accuracy', f'{avg_up:.1f}%'],
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

    # Results table
    story.append(Paragraph("Results Summary", heading_style))

    results_data = [['Symbol', 'Data', 'Test%', 'UP%', 'DOWN%', 'Top Feature', 'Status']]
    for r in reports:
        top_feat = r.top_3_features[0][:15] if r.top_3_features else 'N/A'
        results_data.append([
            r.symbol, str(r.data_points),
            f'{r.test_accuracy:.1f}%', f'{r.up_accuracy:.1f}%', f'{r.down_accuracy:.1f}%',
            top_feat, r.status
        ])

    results_table = Table(results_data, colWidths=[0.7*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.65*inch, 1.2*inch, 1*inch])
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

    # Features
    story.append(Paragraph("Saleem's 16 Features:", subheading_style))
    story.append(Paragraph("awesome_osc, cci, macd, macd_cross, macd_histogram, macd_signal, mfi, momentum, rsi, rsi_overbought, rsi_oversold, rsi_slope, rsi_zscore, vwap_daily, pivot_high_flag, pivot_low_flag", body_style))
    story.append(PageBreak())

    # Individual reports
    for report in reports:
        story.append(Paragraph(f"Report: {report.symbol}", heading_style))

        if report.status == "ERROR":
            story.append(Paragraph(f"Error: {report.error_message}", body_style))
            continue

        details_data = [
            ['Metric', 'Value'],
            ['Data Points', str(report.data_points)],
            ['Train/Test', f'{report.train_size}/{report.test_size}'],
            ['Train Period', report.train_period],
            ['Test Period', report.test_period],
            ['Class Balance', report.class_balance],
            ['Test Accuracy', f'{report.test_accuracy:.2f}%'],
            ['UP Accuracy', f'{report.up_accuracy:.2f}%'],
            ['DOWN Accuracy', f'{report.down_accuracy:.2f}%'],
            ['Precision', f'{report.precision:.2f}%'],
            ['Recall', f'{report.recall:.2f}%'],
            ['F1 Score', f'{report.f1:.2f}%'],
            ['CV Mean', f'{report.cv_mean:.2f}%'],
            ['Status', report.status],
        ]

        details_table = Table(details_data, colWidths=[1.5*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(details_table)

        story.append(Paragraph("Top 3 Features:", subheading_style))
        for i, feat in enumerate(report.top_3_features[:3]):
            imp = report.feature_importance.get(feat, 0)
            marker = " [KEY]" if 'pivot' in feat else ""
            story.append(Paragraph(f"{i+1}. {feat}: {imp:.4f}{marker}", body_style))

        if report.confusion_matrix is not None and report.confusion_matrix.shape == (2, 2):
            story.append(Paragraph("Confusion Matrix:", subheading_style))
            cm = report.confusion_matrix
            cm_data = [['', 'Pred DOWN', 'Pred UP'],
                       ['Actual DOWN', str(cm[0][0]), str(cm[0][1])],
                       ['Actual UP', str(cm[1][0]), str(cm[1][1])]]
            cm_table = Table(cm_data, colWidths=[1*inch, 0.9*inch, 0.9*inch])
            cm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(cm_table)

        story.append(PageBreak())

    # Footer
    story.append(Paragraph("---", body_style))
    story.append(Paragraph(f"Generated: {datetime.now()}", body_style))
    story.append(Paragraph("AIAlgoTradeHits.com - XGBoost ML Model Validation v3", body_style))

    doc.build(story)
    print(f"\nPDF: {filename}")
    return filename


def main():
    """Main execution"""

    print("="*70)
    print("XGBoost Model Reports v3 - Deduplicated Data")
    print("="*70)
    print(f"Date: {datetime.now()}")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print("="*70)

    client = get_bigquery_client()

    reports = []
    for symbol in SYMBOLS:
        report = run_individual_report(client, symbol)
        reports.append(report)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n{'Symbol':<8} {'Data':<6} {'Test%':<7} {'UP%':<7} {'DOWN%':<7} {'Top Feature':<18} {'Status':<10}")
    print("-"*75)

    for r in reports:
        top = r.top_3_features[0][:16] if r.top_3_features else 'N/A'
        print(f"{r.symbol:<8} {r.data_points:<6} {r.test_accuracy:<7.1f} {r.up_accuracy:<7.1f} {r.down_accuracy:<7.1f} {top:<18} {r.status:<10}")

    # PDF
    pdf_file = "C:/1AITrading/Trading/XGBOOST_MODEL_REPORTS_V3.pdf"
    generate_pdf_report(reports, pdf_file)

    # JSON
    json_file = "C:/1AITrading/Trading/xgboost_model_results_v3.json"
    with open(json_file, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'symbols': SYMBOLS,
            'reports': [{
                'symbol': r.symbol, 'data_points': r.data_points,
                'test_accuracy': round(r.test_accuracy, 2),
                'up_accuracy': round(r.up_accuracy, 2),
                'down_accuracy': round(r.down_accuracy, 2),
                'top_3_features': r.top_3_features,
                'class_balance': r.class_balance,
                'status': r.status
            } for r in reports]
        }, f, indent=2)
    print(f"JSON: {json_file}")

    print("\n" + "="*70 + "\nCOMPLETE!\n" + "="*70)

    return reports


if __name__ == "__main__":
    main()
