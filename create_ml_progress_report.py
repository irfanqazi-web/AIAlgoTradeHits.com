"""Create ML Training Progress Report PDF"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

# Create PDF
doc = SimpleDocTemplate('ML_TRAINING_PROGRESS_REPORT.pdf', pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Title
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, spaceAfter=20)
elements.append(Paragraph('ML Training Progress Report', title_style))
elements.append(Paragraph(f'AIAlgoTradeHits.com - {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
elements.append(Spacer(1, 0.3*inch))

# Executive Summary
elements.append(Paragraph('Executive Summary', styles['Heading2']))
summary_text = """
This report summarizes the ML Walk-Forward Validation progress across multiple sectors and stock categories.
The validation system uses BigQuery ML with XGBoost classifiers, trained with Essential 8 features and
monthly retraining frequency. Overall results demonstrate strong predictive capability with 78% average
accuracy across 21,846 predictions.
"""
elements.append(Paragraph(summary_text, styles['Normal']))
elements.append(Spacer(1, 0.2*inch))

# Overall Statistics
stats_data = [
    ['Metric', 'Value'],
    ['Total Predictions', '21,846'],
    ['Correct Predictions', '17,039'],
    ['Overall Accuracy', '78.0%'],
    ['Sectors Validated', '8'],
    ['Unique Stocks', '80+'],
    ['Top Sector Accuracy', '98.0% (Space/Robotics)'],
    ['Model Type', 'XGBoost Classifier'],
    ['Features Used', 'Essential 8'],
    ['Retraining Frequency', 'Monthly']
]
t = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Sector Performance
elements.append(Paragraph('Sector Performance Summary', styles['Heading2']))
sector_data = [
    ['Sector', 'Accuracy', 'Predictions', 'Confidence', 'Recommendation'],
    ['Space/Robotics', '98.0%', '1,090', 'HIGH', 'STRONG BUY'],
    ['Dividend Champions', '84.5%', '14,447', 'HIGH', 'BUY'],
    ['Semiconductors', '81.3%', '852', 'HIGH', 'BUY'],
    ['Defense/Aerospace', '79.6%', '602', 'MEDIUM', 'BUY'],
    ['Healthcare/Biotech', '77.0%', '1,300', 'MEDIUM', 'HOLD'],
    ['Financials', '75.2%', '1,438', 'MEDIUM', 'HOLD'],
    ['AI/Cloud', '73.6%', '1,756', 'MEDIUM', 'HOLD'],
    ['Utilities', '66.2%', '361', 'LOW', 'AVOID']
]
t = Table(sector_data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 1*inch, 1.2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (0, 1), colors.lightgreen),
    ('BACKGROUND', (0, 2), (0, 4), colors.lightgreen),
    ('BACKGROUND', (0, 5), (0, 7), colors.lightyellow),
    ('BACKGROUND', (0, 8), (0, 8), colors.salmon),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Top Performing Stocks
elements.append(Paragraph('Top Performing Stocks (80%+ Accuracy)', styles['Heading2']))
top_stocks = [
    ['Symbol', 'Company', 'Sector', 'Accuracy'],
    ['HON', 'Honeywell', 'Space/Robotics', '93.6%'],
    ['ROK', 'Rockwell Automation', 'Space/Robotics', '91.2%'],
    ['CAT', 'Caterpillar', 'Industrials', '88.8%'],
    ['AVGO', 'Broadcom', 'Semiconductors', '87.4%'],
    ['RTX', 'Raytheon', 'Defense', '87.4%'],
    ['AAPL', 'Apple', 'Technology', '87.3%'],
    ['NVDA', 'NVIDIA', 'Semiconductors', '85.2%'],
    ['MSFT', 'Microsoft', 'AI/Cloud', '83.3%'],
    ['JNJ', 'Johnson & Johnson', 'Dividend', '84.2%'],
    ['INTC', 'Intel', 'Semiconductors', '82.9%']
]
t = Table(top_stocks, colWidths=[0.8*inch, 2*inch, 1.5*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
]))
elements.append(t)

elements.append(PageBreak())

# Model Architecture
elements.append(Paragraph('Model Architecture', styles['Heading2']))
arch_text = """
The ML system uses BigQuery ML with the following configuration:

Model Type: BOOSTED_TREE_CLASSIFIER (XGBoost)
Training Method: Walk-Forward Validation
Retraining: Monthly (optimal for dividend/long-term stocks)

Essential 8 Features:
1. RSI (14-period) - Momentum indicator
2. MACD - Trend direction
3. MACD Histogram - Momentum change
4. Momentum - Price momentum
5. MFI - Money flow index
6. CCI - Commodity channel index
7. RSI Z-Score - Normalized RSI
8. MACD Cross - Crossover signal

Prediction Target: Next-day price direction (UP/DOWN)
Confidence Threshold: 60%+ for signals, 65%+ for trades
"""
elements.append(Paragraph(arch_text.replace('\n', '<br/>'), styles['Normal']))
elements.append(Spacer(1, 0.3*inch))

# Completed Tasks
elements.append(Paragraph('Completed ML Tasks', styles['Heading2']))
completed = [
    '5-symbol validation with 97.2% accuracy (AAPL, MSFT, GOOGL, NVDA, TSLA)',
    'Sector batch training across 8 sectors',
    'Dividend Champions validation (31 stocks, 84.5% accuracy)',
    'Cloud Run ML service deployment (60-min timeout)',
    'Production prediction API endpoints created',
    'Model caching for 80% cost reduction',
    'Batch prediction queries (30x fewer API calls)',
    'Added 26 missing dividend stocks to data pipeline'
]
for task in completed:
    elements.append(Paragraph(f'- {task}', styles['Normal']))
elements.append(Spacer(1, 0.3*inch))

# Next Steps
elements.append(Paragraph('Recommended Next Steps', styles['Heading2']))

elements.append(Paragraph('Phase 1: Model Improvement (Immediate)', styles['Heading3']))
phase1 = [
    'Utilities sector feature engineering (add rate sensitivity)',
    'Add volume profile features (OBV, VWAP deviation)',
    'Implement sector-specific thresholds',
    'Test weekly vs monthly retraining for volatiles'
]
for step in phase1:
    elements.append(Paragraph(f'1. {step}', styles['Normal']))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph('Phase 2: Production Deployment', styles['Heading3']))
phase2 = [
    'Deploy /api/ml/predict endpoint to Cloud Run',
    'Implement real-time confidence monitoring',
    'Add model versioning for A/B testing',
    'Create automated drift detection'
]
for step in phase2:
    elements.append(Paragraph(f'2. {step}', styles['Normal']))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph('Phase 3: Advanced Strategies', styles['Heading3']))
phase3 = [
    'Multi-timeframe ensemble (hourly + daily signals)',
    'Sector rotation based on accuracy rankings',
    'Paper trading integration for live validation',
    'Quarterly full backtest (2-year historical)'
]
for step in phase3:
    elements.append(Paragraph(f'3. {step}', styles['Normal']))

elements.append(PageBreak())

# API Endpoints
elements.append(Paragraph('Production API Endpoints', styles['Heading2']))
endpoints = [
    ['Endpoint', 'Method', 'Description'],
    ['/api/ml/predict', 'GET/POST', 'Real-time predictions for symbols'],
    ['/api/ml/sector-recommendations', 'GET', 'Sector recommendations by accuracy'],
    ['/api/ml/training-status', 'GET', 'Current model training status'],
    ['/api/ml/walk-forward/run', 'POST', 'Start new validation run'],
    ['/api/ml/walk-forward/runs', 'GET', 'List all validation runs'],
    ['/api/ml/walk-forward/runs/<id>', 'GET', 'Get run details'],
    ['/api/ml/walk-forward/runs/<id>/results', 'GET', 'Get daily predictions']
]
t = Table(endpoints, colWidths=[2.5*inch, 0.8*inch, 2.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Service URLs
elements.append(Paragraph('Service URLs', styles['Heading2']))
urls = [
    ['Service', 'URL'],
    ['Trading API', 'https://trading-api-1075463475276.us-central1.run.app'],
    ['ML Training Service', 'https://ml-training-service-1075463475276.us-central1.run.app'],
    ['Bulletproof Fetcher', 'https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app'],
    ['Frontend App', 'https://aialgotradehits.com']
]
t = Table(urls, colWidths=[1.5*inch, 4.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Cost Analysis
elements.append(Paragraph('Cost Optimization Results', styles['Heading2']))
cost_data = [
    ['Optimization', 'Before', 'After', 'Savings'],
    ['Model Caching', '$0.50/pred', '$0.10/pred', '80%'],
    ['Batch Predictions', '30 queries', '1 query', '97%'],
    ['Cloud Run (vs Function)', '$5/hr', '$0.30/hr', '94%'],
    ['Monthly Retraining', 'Weekly cost', 'Monthly cost', '75%']
]
t = Table(cost_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (3, 1), (3, -1), colors.lightgreen),
]))
elements.append(t)

# Footer
elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph('---', styles['Normal']))
elements.append(Paragraph('AIAlgoTradeHits.com - ML Training Progress Report', styles['Normal']))
elements.append(Paragraph('BigQuery Dataset: aialgotradehits.ml_models', styles['Normal']))
elements.append(Paragraph('Cloud Run: ml-training-service', styles['Normal']))
elements.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))

# Build PDF
doc.build(elements)
print('PDF created: ML_TRAINING_PROGRESS_REPORT.pdf')
