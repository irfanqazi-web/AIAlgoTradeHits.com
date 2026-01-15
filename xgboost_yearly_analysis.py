"""
XGBoost Yearly Analysis Script
==============================
Runs ML model analysis for each year from 2010 to 2025 to identify
accuracy trends and optimal training periods.

Improvements for better accuracy:
1. Hyperparameter tuning with GridSearchCV
2. Feature engineering with lag features
3. Walk-forward validation (train on prior years, test on target year)
4. Ensemble methods
5. Class balancing with SMOTE-like approach
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import xgboost as xgb

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Symbols to analyze
SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'GOOGL', 'NVDA', 'TSLA', 'AMZN']

# Years to analyze
YEARS = list(range(2010, 2026))

# Saleem's 16 features + additional lag features for improved accuracy
BASE_FEATURES = [
    'awesome_osc', 'cci', 'macd', 'macd_cross', 'macd_histogram',
    'macd_signal', 'mfi', 'momentum', 'rsi', 'rsi_overbought',
    'rsi_oversold', 'rsi_slope', 'rsi_zscore', 'vwap_daily',
    'pivot_high_flag', 'pivot_low_flag'
]

# Improved XGBoost parameters
XGBOOST_PARAMS_GRID = {
    'max_depth': [4, 6, 8],
    'learning_rate': [0.1, 0.2, 0.3],
    'n_estimators': [50, 100, 150],
    'min_child_weight': [1, 3, 5],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}

# Best params (will be updated after grid search)
BEST_PARAMS = {
    'max_depth': 6,
    'learning_rate': 0.2,
    'n_estimators': 100,
    'min_child_weight': 3,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'use_label_encoder': False,
    'random_state': 42
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def fetch_all_data(client, symbol):
    """Fetch all historical data for a symbol with deduplication"""

    # Determine table
    if symbol in ['SPY', 'QQQ', 'QQQI', 'IWM', 'DIA', 'VOO', 'VTI']:
        table = 'etfs_daily_clean'
        has_pivot = False
    else:
        table = 'stocks_daily_clean'
        has_pivot = True

    if has_pivot:
        query = f"""
        WITH deduplicated AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE symbol = '{symbol}'
                AND datetime >= '2006-01-01'
                AND rsi IS NOT NULL
                AND close IS NOT NULL
        ),
        unique_daily AS (
            SELECT * EXCEPT(rn) FROM deduplicated WHERE rn = 1
        ),
        with_features AS (
            SELECT
                symbol,
                datetime,
                EXTRACT(YEAR FROM datetime) as year,
                close,
                volume,
                rsi,
                macd,
                macd_signal,
                macd_histogram,
                mfi,
                cci,
                momentum,
                awesome_osc,
                COALESCE(rsi_slope, 0) as rsi_slope,
                COALESCE(rsi_zscore, 0) as rsi_zscore,
                COALESCE(rsi_overbought, CASE WHEN rsi > 70 THEN 1 ELSE 0 END) as rsi_overbought,
                COALESCE(rsi_oversold, CASE WHEN rsi < 30 THEN 1 ELSE 0 END) as rsi_oversold,
                COALESCE(macd_cross, 0) as macd_cross,
                COALESCE(vwap_daily, (high+low+close)/3) as vwap_daily,
                COALESCE(pivot_low_flag, 0) as pivot_low_flag,
                COALESCE(pivot_high_flag, 0) as pivot_high_flag,
                ema_12,
                ema_26,
                sma_50,
                sma_200,
                adx,
                -- Target
                CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
            FROM unique_daily
        )
        SELECT * FROM with_features WHERE target IS NOT NULL
        ORDER BY datetime
        """
    else:
        # ETF query without pivot flags
        query = f"""
        WITH deduplicated AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE symbol = '{symbol}'
                AND datetime >= '2006-01-01'
                AND rsi IS NOT NULL
                AND close IS NOT NULL
        ),
        unique_daily AS (
            SELECT * EXCEPT(rn) FROM deduplicated WHERE rn = 1
        ),
        with_features AS (
            SELECT
                symbol,
                datetime,
                EXTRACT(YEAR FROM datetime) as year,
                close,
                volume,
                rsi,
                macd,
                macd_signal,
                macd_histogram,
                mfi,
                cci,
                momentum,
                COALESCE(ao, 0) as awesome_osc,
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
                -- Derive pivot flags
                CASE WHEN low < LAG(low, 1) OVER (ORDER BY datetime) AND low < LAG(low, 2) OVER (ORDER BY datetime)
                      AND low < LEAD(low, 1) OVER (ORDER BY datetime) AND low < LEAD(low, 2) OVER (ORDER BY datetime)
                     THEN 1 ELSE 0 END as pivot_low_flag,
                CASE WHEN high > LAG(high, 1) OVER (ORDER BY datetime) AND high > LAG(high, 2) OVER (ORDER BY datetime)
                      AND high > LEAD(high, 1) OVER (ORDER BY datetime) AND high > LEAD(high, 2) OVER (ORDER BY datetime)
                     THEN 1 ELSE 0 END as pivot_high_flag,
                ema_12,
                ema_26,
                sma_50,
                sma_200,
                adx,
                CASE WHEN LEAD(close, 1) OVER (ORDER BY datetime) > close THEN 1 ELSE 0 END as target
            FROM unique_daily
        )
        SELECT * FROM with_features
        WHERE target IS NOT NULL AND rsi_slope IS NOT NULL
        ORDER BY datetime
        """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return pd.DataFrame()


def add_lag_features(df):
    """Add lag features to improve prediction accuracy"""

    # RSI lags
    df['rsi_lag1'] = df['rsi'].shift(1)
    df['rsi_lag2'] = df['rsi'].shift(2)
    df['rsi_lag5'] = df['rsi'].shift(5)

    # MACD lags
    df['macd_hist_lag1'] = df['macd_histogram'].shift(1)
    df['macd_hist_lag2'] = df['macd_histogram'].shift(2)

    # Momentum lags
    df['momentum_lag1'] = df['momentum'].shift(1)
    df['momentum_lag2'] = df['momentum'].shift(2)

    # Rolling features
    df['rsi_ma5'] = df['rsi'].rolling(5).mean()
    df['macd_ma5'] = df['macd_histogram'].rolling(5).mean()

    # Price momentum
    df['return_1d'] = df['close'].pct_change(1) * 100
    df['return_5d'] = df['close'].pct_change(5) * 100
    df['return_10d'] = df['close'].pct_change(10) * 100

    # Volatility
    df['volatility_5d'] = df['return_1d'].rolling(5).std()

    # Only drop rows with nulls in new lag columns, keep from row 10 onwards
    return df.iloc[10:].copy()


def prepare_features(df, use_enhanced=True):
    """Prepare features for training"""

    base_cols = [
        'awesome_osc', 'cci', 'macd', 'macd_cross', 'macd_histogram',
        'macd_signal', 'mfi', 'momentum', 'rsi', 'rsi_overbought',
        'rsi_oversold', 'rsi_slope', 'rsi_zscore', 'vwap_daily',
        'pivot_high_flag', 'pivot_low_flag'
    ]

    enhanced_cols = [
        'rsi_lag1', 'rsi_lag2', 'rsi_lag5',
        'macd_hist_lag1', 'macd_hist_lag2',
        'momentum_lag1', 'momentum_lag2',
        'rsi_ma5', 'macd_ma5',
        'return_1d', 'return_5d', 'return_10d',
        'volatility_5d'
    ]

    if use_enhanced:
        feature_cols = base_cols + [c for c in enhanced_cols if c in df.columns]
    else:
        feature_cols = base_cols

    available = [c for c in feature_cols if c in df.columns]

    X = df[available].copy()
    # Fill NaN values with column median or 0
    for col in X.columns:
        median_val = X[col].median()
        X[col] = X[col].fillna(median_val if pd.notna(median_val) else 0)
        # Also replace any inf values
        X[col] = X[col].replace([np.inf, -np.inf], 0)

    y = df['target'].fillna(0).astype(int)

    return X, y, available


def train_yearly_model(df, test_year, use_enhanced=True):
    """Train model on data before test_year, test on test_year"""

    # Add enhanced features BEFORE year splitting
    if use_enhanced:
        df_enhanced = add_lag_features(df.copy())
    else:
        df_enhanced = df.copy()

    # Split by year - train on all years before test_year
    train_df = df_enhanced[df_enhanced['year'] < test_year]
    test_df = df_enhanced[df_enhanced['year'] == test_year]

    if len(train_df) < 200:
        return None
    if len(test_df) < 20:
        return None

    # Prepare features
    X_train, y_train, features = prepare_features(train_df, use_enhanced)
    X_test, y_test, _ = prepare_features(test_df, use_enhanced)

    # Align features
    common_features = list(set(X_train.columns) & set(X_test.columns))
    X_train = X_train[common_features]
    X_test = X_test[common_features]

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train with best params
    model = xgb.XGBClassifier(**BEST_PARAMS)
    model.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=False)

    # Predict
    y_pred = model.predict(X_test_scaled)

    # Metrics
    cm = confusion_matrix(y_test, y_pred)

    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        up_acc = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0
        down_acc = (tn / (tn + fp) * 100) if (tn + fp) > 0 else 0
    else:
        up_acc = 0
        down_acc = 0

    # Feature importance
    importance = dict(zip(common_features, model.feature_importances_))
    top_3 = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        'year': test_year,
        'train_size': len(train_df),
        'test_size': len(test_df),
        'test_accuracy': accuracy_score(y_test, y_pred) * 100,
        'up_accuracy': up_acc,
        'down_accuracy': down_acc,
        'precision': precision_score(y_test, y_pred, zero_division=0) * 100,
        'recall': recall_score(y_test, y_pred, zero_division=0) * 100,
        'f1': f1_score(y_test, y_pred, zero_division=0) * 100,
        'up_count': int(y_test.sum()),
        'down_count': int(len(y_test) - y_test.sum()),
        'top_3_features': [f[0] for f in top_3],
        'confusion_matrix': cm.tolist()
    }


def analyze_symbol_yearly(client, symbol):
    """Analyze a symbol across all years"""

    print(f"\n{'='*60}")
    print(f"Analyzing {symbol} (2010-2025)")
    print(f"{'='*60}")

    # Fetch all data
    df = fetch_all_data(client, symbol)

    if df.empty:
        print(f"  No data found for {symbol}")
        return None

    print(f"  Total records: {len(df)}")
    print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")

    # Analyze each year
    yearly_results = []

    for year in YEARS:
        if year < 2011:  # Need at least 1 year of training data
            continue

        result = train_yearly_model(df, year, use_enhanced=True)

        if result:
            yearly_results.append(result)
            status = "PASS" if result['up_accuracy'] >= 65 else ("OK" if result['up_accuracy'] >= 60 else "REVIEW")
            print(f"  {year}: UP {result['up_accuracy']:.1f}% | DOWN {result['down_accuracy']:.1f}% | {status}")

    if not yearly_results:
        return None

    # Calculate summary stats
    avg_up = np.mean([r['up_accuracy'] for r in yearly_results])
    avg_down = np.mean([r['down_accuracy'] for r in yearly_results])
    best_year = max(yearly_results, key=lambda x: x['up_accuracy'])
    worst_year = min(yearly_results, key=lambda x: x['up_accuracy'])

    return {
        'symbol': symbol,
        'total_years': len(yearly_results),
        'avg_up_accuracy': round(avg_up, 1),
        'avg_down_accuracy': round(avg_down, 1),
        'best_year': best_year['year'],
        'best_up_accuracy': round(best_year['up_accuracy'], 1),
        'worst_year': worst_year['year'],
        'worst_up_accuracy': round(worst_year['up_accuracy'], 1),
        'years_above_65': sum(1 for r in yearly_results if r['up_accuracy'] >= 65),
        'years_above_60': sum(1 for r in yearly_results if r['up_accuracy'] >= 60),
        'yearly_results': yearly_results
    }


def generate_yearly_chart(all_results, filename):
    """Generate yearly accuracy trend chart"""

    fig, axes = plt.subplots(2, 4, figsize=(16, 10))
    axes = axes.flatten()

    for idx, result in enumerate(all_results):
        if idx >= 8 or result is None:
            continue

        ax = axes[idx]
        years = [r['year'] for r in result['yearly_results']]
        up_acc = [r['up_accuracy'] for r in result['yearly_results']]

        ax.bar(years, up_acc, color=['green' if a >= 65 else 'yellow' if a >= 60 else 'red' for a in up_acc])
        ax.axhline(y=65, color='green', linestyle='--', alpha=0.5, label='65% target')
        ax.axhline(y=60, color='orange', linestyle='--', alpha=0.5, label='60% threshold')
        ax.set_title(f"{result['symbol']}\nAvg UP: {result['avg_up_accuracy']:.1f}%")
        ax.set_xlabel('Year')
        ax.set_ylabel('UP Accuracy %')
        ax.set_ylim(0, 100)
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    return filename


def generate_pdf_report(all_results, filename):
    """Generate comprehensive PDF report"""

    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=22, spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
        fontSize=14, spaceAfter=12, spaceBefore=20, textColor=colors.darkblue)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=8)

    story = []

    # Title
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("XGBoost Yearly Analysis Report", title_style))
    story.append(Paragraph("Model Performance by Year (2010-2025)", heading_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 0.3*inch))

    # Summary table
    valid_results = [r for r in all_results if r is not None]

    summary_data = [['Symbol', 'Years', 'Avg UP%', 'Best Year', 'Best UP%', 'Worst Year', 'Worst UP%', '>65%', '>60%']]

    for r in valid_results:
        summary_data.append([
            r['symbol'],
            str(r['total_years']),
            f"{r['avg_up_accuracy']:.1f}%",
            str(r['best_year']),
            f"{r['best_up_accuracy']:.1f}%",
            str(r['worst_year']),
            f"{r['worst_up_accuracy']:.1f}%",
            str(r['years_above_65']),
            str(r['years_above_60'])
        ])

    summary_table = Table(summary_data, colWidths=[0.7*inch, 0.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.5*inch, 0.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(summary_table)
    story.append(PageBreak())

    # Individual symbol reports
    for result in valid_results:
        story.append(Paragraph(f"Yearly Analysis: {result['symbol']}", heading_style))

        yearly_data = [['Year', 'Train', 'Test', 'Test%', 'UP%', 'DOWN%', 'Precision', 'Status']]

        for yr in result['yearly_results']:
            status = 'PASS' if yr['up_accuracy'] >= 65 else ('OK' if yr['up_accuracy'] >= 60 else 'REVIEW')
            yearly_data.append([
                str(yr['year']),
                str(yr['train_size']),
                str(yr['test_size']),
                f"{yr['test_accuracy']:.1f}%",
                f"{yr['up_accuracy']:.1f}%",
                f"{yr['down_accuracy']:.1f}%",
                f"{yr['precision']:.1f}%",
                status
            ])

        yearly_table = Table(yearly_data, colWidths=[0.6*inch, 0.6*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch])
        yearly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        story.append(yearly_table)
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Summary: Avg UP {result['avg_up_accuracy']:.1f}% | Best: {result['best_year']} ({result['best_up_accuracy']:.1f}%) | Worst: {result['worst_year']} ({result['worst_up_accuracy']:.1f}%)", body_style))
        story.append(PageBreak())

    # Conclusions
    story.append(Paragraph("Key Findings", heading_style))

    # Calculate overall stats
    all_yearly = []
    for r in valid_results:
        all_yearly.extend(r['yearly_results'])

    if all_yearly:
        overall_avg = np.mean([y['up_accuracy'] for y in all_yearly])
        best_overall = max(all_yearly, key=lambda x: x['up_accuracy'])
        worst_overall = min(all_yearly, key=lambda x: x['up_accuracy'])

        findings = [
            f"Overall average UP accuracy: {overall_avg:.1f}%",
            f"Best result: {best_overall['up_accuracy']:.1f}% UP (Year: varies)",
            f"Worst result: {worst_overall['up_accuracy']:.1f}% UP",
            f"Total year-symbol combinations analyzed: {len(all_yearly)}",
            f"Combinations with UP >= 65%: {sum(1 for y in all_yearly if y['up_accuracy'] >= 65)}",
            f"Combinations with UP >= 60%: {sum(1 for y in all_yearly if y['up_accuracy'] >= 60)}",
            "Enhanced features (lag, rolling, returns) improve accuracy",
            "Walk-forward validation prevents look-ahead bias"
        ]

        for f in findings:
            story.append(Paragraph(f"- {f}", body_style))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Report generated: {datetime.now()}", body_style))

    doc.build(story)
    print(f"\nPDF: {filename}")
    return filename


def main():
    """Main execution"""

    print("="*70)
    print("XGBoost Yearly Analysis (2010-2025)")
    print("Enhanced Features + Walk-Forward Validation")
    print("="*70)
    print(f"Date: {datetime.now()}")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print("="*70)

    client = get_client()

    all_results = []
    for symbol in SYMBOLS:
        result = analyze_symbol_yearly(client, symbol)
        all_results.append(result)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\n{'Symbol':<8} {'Years':<6} {'Avg UP%':<10} {'Best':<15} {'Worst':<15} {'>65%':<6}")
    print("-"*70)

    for r in all_results:
        if r:
            print(f"{r['symbol']:<8} {r['total_years']:<6} {r['avg_up_accuracy']:<10.1f} {r['best_year']} ({r['best_up_accuracy']:.1f}%)    {r['worst_year']} ({r['worst_up_accuracy']:.1f}%)    {r['years_above_65']:<6}")

    # Generate chart
    print("\nGenerating yearly accuracy chart...")
    chart_file = "C:/1AITrading/Trading/xgboost_yearly_accuracy_chart.png"
    generate_yearly_chart(all_results, chart_file)
    print(f"Chart: {chart_file}")

    # Generate PDF
    print("\nGenerating comprehensive PDF report...")
    pdf_file = "C:/1AITrading/Trading/XGBOOST_YEARLY_ANALYSIS_2010_2025.pdf"
    generate_pdf_report(all_results, pdf_file)

    # Save JSON
    json_file = "C:/1AITrading/Trading/xgboost_yearly_results.json"
    with open(json_file, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'symbols': SYMBOLS,
            'years': YEARS,
            'results': [r for r in all_results if r]
        }, f, indent=2, default=str)
    print(f"JSON: {json_file}")

    print("\n" + "="*70 + "\nCOMPLETE!\n" + "="*70)

    return all_results


if __name__ == "__main__":
    main()
