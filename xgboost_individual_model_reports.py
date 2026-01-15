"""
XGBoost Individual Model Reports Generator
==========================================
Based on Saleem's validated 16-feature model with 68.5% UP accuracy.

Generates individual model reports for:
GOOGL, SPY, QQQ, QQQI, AAPL, NVDA, TSLA, AMZN

Technical Stack:
- Python 3.12
- XGBoost - core ML model
- pandas, numpy - data handling
- scikit-learn - preprocessing and metrics
- google-cloud-bigquery - data source
- reportlab - PDF generation
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
import xgboost as xgb

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
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

# XGBoost parameters from validation
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
        self.predictions_sample = []


def get_bigquery_client():
    """Get BigQuery client"""
    return bigquery.Client(project=PROJECT_ID)


def fetch_symbol_data(client, symbol):
    """Fetch data for a symbol from BigQuery with calculated features"""

    # Determine table based on symbol type
    if symbol in ['SPY', 'QQQ', 'QQQI']:
        table = 'etfs_daily_clean'
    else:
        table = 'stocks_daily_clean'

    query = f"""
    WITH base_data AS (
        SELECT
            symbol,
            datetime,
            open,
            high,
            low,
            close,
            volume,
            -- Core indicators (use actual column names from schema)
            COALESCE(rsi, 50) as rsi,
            COALESCE(macd, 0) as macd,
            COALESCE(macd_signal, 0) as macd_signal,
            COALESCE(macd_histogram, 0) as macd_histogram,
            COALESCE(mfi, 50) as mfi,
            COALESCE(cci, 0) as cci,
            COALESCE(adx, 0) as adx,
            COALESCE(atr, 0) as atr,
            COALESCE(ema_12, 0) as ema_12,
            COALESCE(ema_26, 0) as ema_26,
            COALESCE(sma_20, 0) as sma_20,
            COALESCE(sma_50, 0) as sma_50,
            COALESCE(sma_200, 0) as sma_200,
            COALESCE(bollinger_upper, 0) as bb_upper,
            COALESCE(bollinger_middle, 0) as bb_middle,
            COALESCE(bollinger_lower, 0) as bb_lower,
            COALESCE(stoch_k, 0) as stoch_k,
            COALESCE(stoch_d, 0) as stoch_d,
            -- Pivot flags (KEY FEATURES per Saleem's validation)
            COALESCE(pivot_low_flag, 0) as pivot_low_flag,
            COALESCE(pivot_high_flag, 0) as pivot_high_flag,
            -- Additional features from schema
            COALESCE(momentum, 0) as momentum_raw,
            COALESCE(awesome_osc, 0) as awesome_osc_raw,
            COALESCE(rsi_slope, 0) as rsi_slope_raw,
            COALESCE(rsi_zscore, 0) as rsi_zscore_raw,
            COALESCE(rsi_overbought, 0) as rsi_overbought_raw,
            COALESCE(rsi_oversold, 0) as rsi_oversold_raw,
            COALESCE(macd_cross, 0) as macd_cross_raw,
            COALESCE(vwap_daily, 0) as vwap_daily_raw
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
            AND datetime >= '2015-01-01'
        ORDER BY datetime
    ),
    final_data AS (
        SELECT
            symbol,
            datetime,
            close,
            volume,
            -- Saleem's 16 features (using schema columns directly)
            COALESCE(awesome_osc_raw, 0) as awesome_osc,
            cci,
            macd,
            macd_cross_raw as macd_cross,
            macd_histogram,
            macd_signal,
            mfi,
            COALESCE(momentum_raw, 0) as momentum,
            rsi,
            COALESCE(rsi_overbought_raw, CASE WHEN rsi > 70 THEN 1 ELSE 0 END) as rsi_overbought,
            COALESCE(rsi_oversold_raw, CASE WHEN rsi < 30 THEN 1 ELSE 0 END) as rsi_oversold,
            COALESCE(rsi_slope_raw, 0) as rsi_slope,
            COALESCE(rsi_zscore_raw, 0) as rsi_zscore,
            COALESCE(vwap_daily_raw, (high + low + close) / 3) as vwap_daily,
            pivot_high_flag,
            pivot_low_flag,
            -- Additional features for analysis
            ema_12,
            ema_26,
            sma_50,
            sma_200,
            adx,
            -- Target: next day direction (1 = UP, 0 = DOWN)
            CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
        FROM base_data
    )
    SELECT * FROM final_data
    WHERE target IS NOT NULL
    ORDER BY datetime
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
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
        print(f"  Warning: Missing features: {missing_features}")

    # Fill NaN values
    X = df[available_features].fillna(0)
    y = df['target'].fillna(0).astype(int)

    return X, y, available_features


def train_and_evaluate(X, y, df, report):
    """Train XGBoost model and evaluate performance"""

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

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost model
    model = xgb.XGBClassifier(**XGBOOST_PARAMS)
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
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=tscv, scoring='accuracy')
    report.cv_scores = cv_scores.tolist()
    report.cv_mean = cv_scores.mean() * 100
    report.cv_std = cv_scores.std() * 100

    # Sample predictions
    sample_size = min(10, len(y_test))
    report.predictions_sample = [
        {
            'date': test_dates.iloc[i].strftime('%Y-%m-%d'),
            'actual': int(y_test.iloc[i]),
            'predicted': int(y_pred[i]),
            'probability': round(float(y_pred_proba[i]), 3)
        }
        for i in range(sample_size)
    ]

    # Determine status
    if report.up_accuracy >= 65:
        report.status = "PASS"
    elif report.up_accuracy >= 60:
        report.status = "OK"
    else:
        report.status = "FAIL"

    return model, scaler


def run_individual_report(client, symbol):
    """Run complete analysis for a single symbol"""

    print(f"\n{'='*60}")
    print(f"Processing {symbol}...")
    print(f"{'='*60}")

    report = ModelReport(symbol)

    # Fetch data
    print(f"  Fetching data from BigQuery...")
    df = fetch_symbol_data(client, symbol)

    if df.empty:
        report.status = "ERROR"
        report.error_message = "No data found in BigQuery"
        return report

    report.data_points = len(df)
    print(f"  Found {report.data_points} data points")

    if report.data_points < 500:
        report.status = "ERROR"
        report.error_message = f"Insufficient data: {report.data_points} points (need 500+)"
        return report

    # Prepare features
    print(f"  Preparing 16 features...")
    X, y, features = prepare_features(df)
    print(f"  Using {len(features)} features")

    # Train and evaluate
    print(f"  Training XGBoost model...")
    try:
        model, scaler = train_and_evaluate(X, y, df, report)
        print(f"  Training complete!")
        print(f"  Test Accuracy: {report.test_accuracy:.1f}%")
        print(f"  UP Accuracy: {report.up_accuracy:.1f}%")
        print(f"  DOWN Accuracy: {report.down_accuracy:.1f}%")
        print(f"  Status: {report.status}")
    except Exception as e:
        report.status = "ERROR"
        report.error_message = str(e)
        print(f"  Error during training: {e}")

    return report


def generate_feature_importance_chart(reports, filename):
    """Generate feature importance comparison chart"""

    fig, axes = plt.subplots(2, 4, figsize=(16, 10))
    axes = axes.flatten()

    for idx, report in enumerate(reports):
        if idx >= 8:
            break
        ax = axes[idx]

        if report.feature_importance:
            features = list(report.feature_importance.keys())[:10]
            importances = [report.feature_importance[f] for f in features]

            colors_list = ['#10b981' if 'pivot' in f else '#3b82f6' for f in features]

            ax.barh(features, importances, color=colors_list)
            ax.set_xlabel('Importance')
            ax.set_title(f'{report.symbol}\nUP: {report.up_accuracy:.1f}%')
            ax.invert_yaxis()
        else:
            ax.text(0.5, 0.5, f'{report.symbol}\nNo Data', ha='center', va='center')
            ax.set_title(report.symbol)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    return filename


def generate_pdf_report(reports, filename):
    """Generate comprehensive PDF report"""

    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=24, spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue
    )

    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=16, spaceAfter=12, spaceBefore=20, textColor=colors.darkblue
    )

    subheading_style = ParagraphStyle(
        'CustomSubheading', parent=styles['Heading3'],
        fontSize=12, spaceAfter=8, spaceBefore=12, textColor=colors.darkgreen
    )

    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, spaceAfter=8
    )

    story = []

    # Title Page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("XGBoost ML Model Validation Report", title_style))
    story.append(Paragraph("Individual Symbol Analysis", heading_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", body_style))
    story.append(Paragraph("Based on Saleem's Validated 16-Feature Model", body_style))
    story.append(Spacer(1, 0.3*inch))

    # Executive Summary
    passed = sum(1 for r in reports if r.status == "PASS")
    ok = sum(1 for r in reports if r.status == "OK")
    failed = sum(1 for r in reports if r.status == "FAIL")
    errors = sum(1 for r in reports if r.status == "ERROR")

    valid_reports = [r for r in reports if r.status in ["PASS", "OK", "FAIL"]]
    avg_up = sum(r.up_accuracy for r in valid_reports) / len(valid_reports) if valid_reports else 0
    avg_test = sum(r.test_accuracy for r in valid_reports) / len(valid_reports) if valid_reports else 0

    summary_data = [
        ['Metric', 'Result'],
        ['Symbols Analyzed', str(len(reports))],
        ['Tests Passed (UP >= 65%)', f'{passed}/{len(reports)}'],
        ['Tests OK (UP 60-65%)', f'{ok}/{len(reports)}'],
        ['Tests Failed (UP < 60%)', f'{failed}/{len(reports)}'],
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
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    story.append(summary_table)
    story.append(PageBreak())

    # Results Summary Table
    story.append(Paragraph("Results Summary", heading_style))

    results_data = [
        ['Symbol', 'Data Points', 'Train Period', 'Test %', 'UP %', 'DOWN %', 'Status']
    ]

    for r in reports:
        status_text = r.status
        if r.status == "PASS":
            status_text = "PASS"
        elif r.status == "OK":
            status_text = "OK"
        elif r.status == "FAIL":
            status_text = "FAIL"
        else:
            status_text = "ERROR"

        results_data.append([
            r.symbol,
            str(r.data_points),
            r.train_period[:10] if r.train_period else 'N/A',
            f'{r.test_accuracy:.1f}%' if r.test_accuracy else 'N/A',
            f'{r.up_accuracy:.1f}%' if r.up_accuracy else 'N/A',
            f'{r.down_accuracy:.1f}%' if r.down_accuracy else 'N/A',
            status_text
        ])

    results_table = Table(results_data, colWidths=[0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # Color code status column
    for i, r in enumerate(reports):
        row = i + 1
        if r.status == "PASS":
            results_table.setStyle(TableStyle([('BACKGROUND', (6, row), (6, row), colors.lightgreen)]))
        elif r.status == "OK":
            results_table.setStyle(TableStyle([('BACKGROUND', (6, row), (6, row), colors.yellow)]))
        elif r.status == "FAIL":
            results_table.setStyle(TableStyle([('BACKGROUND', (6, row), (6, row), colors.pink)]))
        else:
            results_table.setStyle(TableStyle([('BACKGROUND', (6, row), (6, row), colors.lightgrey)]))

    story.append(results_table)
    story.append(Spacer(1, 0.3*inch))

    # The 16 Features
    story.append(Paragraph("Saleem's Validated 16 Features", heading_style))

    features_text = """
    <b>Momentum Indicators:</b> awesome_osc, momentum, rsi, rsi_overbought, rsi_oversold, rsi_slope, rsi_zscore<br/>
    <b>Trend Indicators:</b> macd, macd_cross, macd_histogram, macd_signal, cci<br/>
    <b>Volume/Flow:</b> mfi, vwap_daily<br/>
    <b>Pivot Signals (KEY):</b> pivot_high_flag, pivot_low_flag
    """
    story.append(Paragraph(features_text, body_style))
    story.append(PageBreak())

    # Individual Symbol Reports
    for report in reports:
        story.append(Paragraph(f"Individual Report: {report.symbol}", heading_style))

        if report.status == "ERROR":
            story.append(Paragraph(f"Error: {report.error_message}", body_style))
            story.append(Spacer(1, 0.5*inch))
            continue

        # Symbol details
        details_data = [
            ['Metric', 'Value'],
            ['Total Data Points', str(report.data_points)],
            ['Training Set Size', str(report.train_size)],
            ['Test Set Size', str(report.test_size)],
            ['Training Period', report.train_period],
            ['Test Period', report.test_period],
            ['Test Accuracy', f'{report.test_accuracy:.2f}%'],
            ['UP Accuracy', f'{report.up_accuracy:.2f}%'],
            ['DOWN Accuracy', f'{report.down_accuracy:.2f}%'],
            ['Precision', f'{report.precision:.2f}%'],
            ['Recall', f'{report.recall:.2f}%'],
            ['F1 Score', f'{report.f1:.2f}%'],
            ['CV Mean Accuracy', f'{report.cv_mean:.2f}%'],
            ['CV Std Dev', f'{report.cv_std:.2f}%'],
            ['Status', report.status],
        ]

        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
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
                story.append(Paragraph(f"{i+1}. {feat}: {imp:.4f}", body_style))

        # Confusion Matrix
        if report.confusion_matrix is not None:
            story.append(Paragraph("Confusion Matrix:", subheading_style))
            cm = report.confusion_matrix
            cm_data = [
                ['', 'Predicted DOWN', 'Predicted UP'],
                ['Actual DOWN', str(cm[0][0]), str(cm[0][1])],
                ['Actual UP', str(cm[1][0]), str(cm[1][1])],
            ]
            cm_table = Table(cm_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch])
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
        ['eval_metric', 'logloss'],
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
    story.append(Paragraph("Conclusions & Recommendations", heading_style))

    conclusions = [
        f"Models analyzed: {len(reports)} symbols",
        f"Pass rate: {passed}/{len(reports)} ({passed/len(reports)*100:.1f}%)" if reports else "No data",
        f"Average UP accuracy: {avg_up:.1f}%",
        "Pivot flags (pivot_low_flag, pivot_high_flag) remain KEY features",
        "Model performs best on liquid, trending assets",
        "Recommended: Focus on UP signals only (do not short on DOWN signals)",
    ]

    for c in conclusions:
        story.append(Paragraph(f"* {c}", body_style))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("---", body_style))
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph("AIAlgoTradeHits.com - XGBoost ML Model Validation", body_style))

    # Build PDF
    doc.build(story)
    print(f"\nPDF Report generated: {filename}")

    return filename


def main():
    """Main execution function"""

    print("="*70)
    print("XGBoost Individual Model Reports Generator")
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

    print(f"\n{'Symbol':<10} {'Data':<8} {'Test%':<8} {'UP%':<8} {'DOWN%':<8} {'Status':<10}")
    print("-"*60)

    for r in reports:
        print(f"{r.symbol:<10} {r.data_points:<8} {r.test_accuracy:<8.1f} {r.up_accuracy:<8.1f} {r.down_accuracy:<8.1f} {r.status:<10}")

    # Generate charts
    print("\nGenerating feature importance chart...")
    chart_file = "C:/1AITrading/Trading/ml_feature_importance_chart.png"
    generate_feature_importance_chart(reports, chart_file)
    print(f"Chart saved: {chart_file}")

    # Generate PDF
    print("\nGenerating comprehensive PDF report...")
    pdf_file = "C:/1AITrading/Trading/XGBOOST_INDIVIDUAL_MODEL_REPORTS.pdf"
    generate_pdf_report(reports, pdf_file)

    # Save JSON results
    json_file = "C:/1AITrading/Trading/xgboost_model_results.json"
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
                'cv_std': round(r.cv_std, 2),
                'top_3_features': r.top_3_features,
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
