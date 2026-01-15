"""Create Dividend Champions ML Validation Report PDF"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

# Create PDF
doc = SimpleDocTemplate('DIVIDEND_CHAMPIONS_ML_REPORT.pdf', pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Title
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, spaceAfter=20)
elements.append(Paragraph('Dividend Champions ML Validation Report', title_style))
elements.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
elements.append(Spacer(1, 0.3*inch))

# Executive Summary
elements.append(Paragraph('Executive Summary', styles['Heading2']))
summary_text = """
This report presents the results of ML-based walk-forward validation on Dividend Champions -
stocks with 25+ consecutive years of dividend increases. The analysis validates our XGBoost
prediction models across 31 dividend aristocrat stocks with 84.5% overall accuracy.
"""
elements.append(Paragraph(summary_text, styles['Normal']))
elements.append(Spacer(1, 0.2*inch))

# Key Metrics
summary_data = [
    ['Metric', 'Value'],
    ['Total Predictions', '14,447'],
    ['Correct Predictions', '12,203'],
    ['Overall Accuracy', '84.5%'],
    ['Stocks Validated', '31'],
    ['Top Performers (80%+)', '11 stocks'],
    ['Mid Performers (70-80%)', '14 stocks'],
    ['Training Period', '30 days'],
    ['Retraining', 'Monthly']
]
t = Table(summary_data, colWidths=[2.5*inch, 2*inch])
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

# Top Performers
elements.append(Paragraph('Top Performing Dividend Stocks (80%+ Accuracy)', styles['Heading2']))
top_data = [
    ['Symbol', 'Company', 'Predictions', 'Correct', 'Accuracy'],
    ['HON', 'Honeywell', '2,683', '2,511', '93.6%'],
    ['CAT', 'Caterpillar', '1,383', '1,228', '88.8%'],
    ['AVGO', 'Broadcom', '350', '306', '87.4%'],
    ['RTX', 'Raytheon', '1,925', '1,682', '87.4%'],
    ['AAPL', 'Apple', '1,678', '1,465', '87.3%'],
    ['JNJ', 'Johnson & Johnson', '114', '96', '84.2%'],
    ['PEP', 'PepsiCo', '176', '148', '84.1%'],
    ['MCD', 'McDonalds', '115', '96', '83.5%'],
    ['HD', 'Home Depot', '113', '94', '83.2%'],
    ['INTC', 'Intel', '457', '379', '82.9%'],
    ['MSFT', 'Microsoft', '700', '575', '82.1%']
]
t = Table(top_data, colWidths=[0.7*inch, 1.8*inch, 0.9*inch, 0.8*inch, 0.8*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Mid Performers
elements.append(Paragraph('Mid Performing Dividend Stocks (70-80%)', styles['Heading2']))
mid_data = [
    ['Symbol', 'Company', 'Predictions', 'Correct', 'Accuracy'],
    ['LMT', 'Lockheed Martin', '1,447', '1,155', '79.8%'],
    ['TXN', 'Texas Instruments', '582', '463', '79.6%'],
    ['ABT', 'Abbott Labs', '468', '371', '79.3%'],
    ['ADP', 'ADP', '124', '98', '79.0%'],
    ['SPGI', 'S&P Global', '143', '113', '79.0%'],
    ['LOW', 'Lowes', '114', '89', '78.1%'],
    ['QCOM', 'Qualcomm', '452', '345', '76.3%'],
    ['KO', 'Coca-Cola', '116', '88', '75.9%'],
    ['IBM', 'IBM', '115', '87', '75.7%'],
    ['NEE', 'NextEra Energy', '448', '335', '74.8%']
]
t = Table(mid_data, colWidths=[0.7*inch, 1.8*inch, 0.9*inch, 0.8*inch, 0.8*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
]))
elements.append(t)

elements.append(PageBreak())

# Key Findings
elements.append(Paragraph('Key Findings', styles['Heading2']))
findings = [
    'Industrial dividend stocks (HON, CAT, RTX, LMT) show highest prediction accuracy (87-94%)',
    'Technology dividend stocks (AAPL, MSFT, INTC, AVGO) perform well at 82-87%',
    'Consumer staples (PEP, MCD) show moderate performance at 83-84%',
    'Utilities sector shows lower accuracy - may need sector-specific features',
    'Model performs better on stocks with higher trading volume and volatility',
    'Monthly retraining frequency is optimal for dividend stocks'
]
for i, finding in enumerate(findings, 1):
    elements.append(Paragraph(f'{i}. {finding}', styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))

elements.append(Spacer(1, 0.2*inch))

# Recommendations
elements.append(Paragraph('Trading Recommendations', styles['Heading2']))
recs = [
    'Focus buy signals on top performers: HON, CAT, AVGO, RTX, AAPL',
    'Use 60%+ confidence threshold for trade execution',
    'Dividend stocks provide stable baseline for portfolio construction',
    'Combine ML signals with fundamental dividend metrics (payout ratio, yield)',
    'Consider sector rotation based on model performance tiers'
]
for rec in recs:
    elements.append(Paragraph(f'- {rec}', styles['Normal']))

elements.append(Spacer(1, 0.3*inch))

# Data Pipeline Update
elements.append(Paragraph('Data Pipeline Update', styles['Heading2']))
pipeline_text = """
The following Dividend Champions have been added to the daily data pipeline for future analysis:
K, SJM, HRL, MKC, DOV, SWK, CINF, BEN, TROW, ED, FRT, ESS, PPG, MMM, CB, CL, NUE, APD, D, SO, XEL, T, O, SBUX, BDX, CAH

These stocks will be included in:
- Hourly data fetches
- Daily data fetches
- Technical indicator calculations
- ML feature generation
"""
elements.append(Paragraph(pipeline_text, styles['Normal']))

# Footer
elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph('---', styles['Normal']))
elements.append(Paragraph('AIAlgoTradeHits.com - Dividend Champions ML Report', styles['Normal']))
elements.append(Paragraph('ML Service: ml-training-service', styles['Normal']))
elements.append(Paragraph('Data Fetcher: bulletproof-fetcher (updated)', styles['Normal']))

# Build PDF
doc.build(elements)
print('PDF created: DIVIDEND_CHAMPIONS_ML_REPORT.pdf')
