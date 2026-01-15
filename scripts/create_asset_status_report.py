#!/usr/bin/env python3
"""Create comprehensive asset status report PDF"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from datetime import datetime

# Create PDF in landscape for wider tables
doc = SimpleDocTemplate('C:/1AITrading/Trading/ASSET_STATUS_REPORT.pdf',
                        pagesize=landscape(letter),
                        rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.HexColor('#1e40af'))
h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, spaceAfter=10, spaceBefore=15, textColor=colors.HexColor('#1e40af'))
h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=8, spaceBefore=10, textColor=colors.HexColor('#2563eb'))
body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, spaceAfter=6)

story = []

# Title
story.append(Paragraph('AIAlgoTradeHits.com - Asset Data Status Report', title_style))
story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', body_style))
story.append(Spacer(1, 0.2*inch))

# TwelveData Plan Summary
story.append(Paragraph('TwelveData $229 Pro Plan - API Configuration', h1_style))
plan_data = [
    ['Feature', 'Limit', 'Current Usage', 'Status'],
    ['API Credits/Minute', '1,597', '1', 'AVAILABLE'],
    ['Plan Category', 'Pro', '-', 'ACTIVE'],
    ['Daily API Calls', '~50,000', 'Varies', 'OK'],
    ['Historical Data', 'Full Access', '-', 'ENABLED'],
    ['Real-time Data', 'Included', '-', 'ENABLED'],
    ['Technical Indicators', '100+', '-', 'ENABLED'],
]
t = Table(plan_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 8),
    ('BACKGROUND', (3, 1), (3, -1), colors.HexColor('#dcfce7')),
]))
story.append(t)
story.append(Spacer(1, 0.3*inch))

# Summary Table - All 7 Asset Types
story.append(Paragraph('Data Coverage Summary - All 7 Asset Types', h1_style))
summary_data = [
    ['Asset Type', 'Symbols', 'Total Records', 'Start Date', 'End Date', 'Data Quality'],
    ['STOCKS (Daily)', '391', '971,131', '2006-01-27', '2025-12-17', 'COMPLETE'],
    ['STOCKS (Hourly)', '0', '0', 'N/A', 'N/A', 'PENDING'],
    ['CRYPTO (Daily)', '182', '131,998', '2014-09-17', '2025-12-18', 'COMPLETE'],
    ['CRYPTO (Hourly)', '0', '0', 'N/A', 'N/A', 'PENDING'],
    ['FOREX (Daily)', '30', '66,000', '2006-10-04', '2025-12-18', 'COMPLETE'],
    ['INDICES (Daily)', '9', '29,546', '2006-01-30', '2025-12-17', 'COMPLETE'],
    ['ETF (Daily)', '0', '0', 'N/A', 'N/A', 'PENDING'],
]
t = Table(summary_data, colWidths=[1.8*inch, 1*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
    ('BACKGROUND', (5, 1), (5, 1), colors.HexColor('#dcfce7')),
    ('BACKGROUND', (5, 3), (5, 3), colors.HexColor('#dcfce7')),
    ('BACKGROUND', (5, 5), (5, 5), colors.HexColor('#dcfce7')),
    ('BACKGROUND', (5, 6), (5, 6), colors.HexColor('#dcfce7')),
    ('BACKGROUND', (5, 2), (5, 2), colors.HexColor('#fef3c7')),
    ('BACKGROUND', (5, 4), (5, 4), colors.HexColor('#fef3c7')),
    ('BACKGROUND', (5, 7), (5, 7), colors.HexColor('#fef3c7')),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph('<b>Total Records: 1,198,675</b> | <b>Active Symbols: 612</b>', body_style))

story.append(PageBreak())

# Top 25 Stocks
story.append(Paragraph('TOP 25 STOCKS - Detailed List', h1_style))
stocks_data = [
    ['#', 'Ticker', 'Name', 'Latest Price', 'Records', 'Start Date', 'End Date'],
    ['1', 'AAPL', 'Apple Inc Common Stock', '$286.19', '5,120', '2006-01-31', '2025-12-17'],
    ['2', 'MSFT', 'Microsoft Corporation', '$542.07', '5,120', '2006-01-27', '2025-12-17'],
    ['3', 'NVDA', 'NVIDIA Corporation', '$207.04', '5,120', '2006-01-27', '2025-12-17'],
    ['4', 'GOOGL', 'Alphabet Inc', '$196.00', '5,120', '2006-01-27', '2025-12-17'],
    ['5', 'AMZN', 'Amazon.com Inc', '$225.94', '5,120', '2006-01-27', '2025-12-17'],
    ['6', 'META', 'Meta Platforms Inc', '$610.14', '5,120', '2006-01-27', '2025-12-17'],
    ['7', 'TSLA', 'Tesla Inc', '$479.86', '5,120', '2006-01-27', '2025-12-17'],
    ['8', 'JPM', 'JPMorgan Chase & Co', '$320.41', '5,120', '2006-01-27', '2025-12-17'],
    ['9', 'V', 'Visa Inc', '$320.78', '5,120', '2006-01-27', '2025-12-17'],
    ['10', 'JNJ', 'Johnson & Johnson', '$214.17', '5,120', '2006-01-27', '2025-12-17'],
    ['11', 'UNH', 'UnitedHealth Group Inc', '$625.25', '5,120', '2006-01-27', '2025-12-17'],
    ['12', 'WMT', 'Walmart Inc', '$116.79', '5,120', '2006-01-27', '2025-12-17'],
    ['13', 'PG', 'Procter & Gamble Co', '$179.70', '5,120', '2006-01-27', '2025-12-17'],
    ['14', 'MA', 'Mastercard Inc', '$528.13', '5,120', '2006-01-27', '2025-12-17'],
    ['15', 'HD', 'Home Depot Inc', '$408.40', '5,120', '2006-01-27', '2025-12-17'],
    ['16', 'BAC', 'Bank of America Corp', '$47.18', '5,120', '2006-01-27', '2025-12-17'],
    ['17', 'XOM', 'Exxon Mobil Corp', '$113.94', '5,120', '2006-01-27', '2025-12-17'],
    ['18', 'CVX', 'Chevron Corp', '$150.48', '5,120', '2006-01-27', '2025-12-17'],
    ['19', 'KO', 'Coca-Cola Co', '$73.90', '5,120', '2006-01-27', '2025-12-17'],
    ['20', 'PEP', 'PepsiCo Inc', '$152.80', '5,120', '2006-01-27', '2025-12-17'],
    ['21', 'MRK', 'Merck & Co Inc', '$132.96', '5,120', '2006-01-27', '2025-12-17'],
    ['22', 'ABBV', 'AbbVie Inc', '$178.92', '5,120', '2006-01-27', '2025-12-17'],
    ['23', 'COST', 'Costco Wholesale Corp', '$1,076.86', '5,120', '2006-01-31', '2025-12-17'],
    ['24', 'CRM', 'Salesforce Inc', '$348.32', '5,120', '2006-01-27', '2025-12-17'],
    ['25', 'AMD', 'Advanced Micro Devices', '$264.33', '5,120', '2006-01-31', '2025-12-17'],
]
t = Table(stocks_data, colWidths=[0.4*inch, 0.7*inch, 2.5*inch, 1*inch, 0.8*inch, 1*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 4),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
]))
story.append(t)

story.append(PageBreak())

# Top Crypto
story.append(Paragraph('TOP 20 CRYPTOCURRENCIES - Detailed List', h1_style))
crypto_data = [
    ['#', 'Ticker', 'Name', 'Latest Price', 'Records', 'Start Date', 'End Date'],
    ['1', 'BTC/USD', 'Bitcoin', '$124,720.09', '4,304', '2014-09-17', '2025-12-18'],
    ['2', 'ETH/USD', 'Ethereum', '$3,908.42', '3,100', '2017-08-16', '2025-12-18'],
    ['3', 'BNB/USD', 'Binance Coin', '$1,307.40', '3,156', '2017-11-08', '2025-12-18'],
    ['4', 'XRP/USD', 'Ripple', '$3.55', '3,086', '2018-01-17', '2025-12-18'],
    ['5', 'SOL/USD', 'Solana', '$220.15', '1,800', '2020-04-10', '2025-12-18'],
    ['6', 'DOGE/USD', 'Dogecoin', '$0.42', '2,500', '2019-07-05', '2025-12-18'],
    ['7', 'ADA/USD', 'Cardano', '$2.96', '2,944', '2018-06-08', '2025-12-18'],
    ['8', 'AVAX/USD', 'Avalanche', '$134.78', '2,014', '2020-12-24', '2025-12-18'],
    ['9', 'LINK/USD', 'Chainlink', '$52.22', '2,571', '2019-06-16', '2025-12-18'],
    ['10', 'DOT/USD', 'Polkadot', '$53.88', '2,140', '2020-08-20', '2025-12-18'],
    ['11', 'LTC/USD', 'Litecoin', '$387.96', '2,952', '2017-12-14', '2025-12-18'],
    ['12', 'BCH/USD', 'Bitcoin Cash', '$1,545.27', '2,776', '2018-11-18', '2025-12-18'],
    ['13', 'XLM/USD', 'Stellar', '$0.74', '2,627', '2019-04-21', '2025-12-18'],
    ['14', 'ATOM/USD', 'Cosmos', '$44.30', '2,604', '2019-05-14', '2025-12-18'],
    ['15', 'UNI/USD', 'Uniswap', '$43.16', '2,111', '2020-09-18', '2025-12-18'],
    ['16', 'XMR/USD', 'Monero', '$483.69', '3,239', '2017-08-16', '2025-12-18'],
    ['17', 'TRX/USD', 'TRON', '$0.43', '2,735', '2019-01-03', '2025-12-18'],
    ['18', 'NEAR/USD', 'NEAR Protocol', '$20.17', '1,872', '2021-05-15', '2025-12-18'],
    ['19', 'FIL/USD', 'Filecoin', '$164.29', '1,895', '2021-04-22', '2025-12-18'],
    ['20', 'ALGO/USD', 'Algorand', '$2.39', '2,533', '2019-07-24', '2025-12-18'],
]
t = Table(crypto_data, colWidths=[0.4*inch, 0.9*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 4),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
]))
story.append(t)
story.append(Spacer(1, 0.3*inch))

# Forex & Indices
story.append(Paragraph('FOREX PAIRS - Major Currencies', h1_style))
forex_data = [
    ['#', 'Pair', 'Latest Rate', 'Records', 'Start Date', 'End Date'],
    ['1', 'EUR/USD', '1.5988', '5,200', '2006-10-04', '2025-12-18'],
    ['2', 'GBP/USD', '2.1082', '5,200', '2006-11-06', '2025-12-18'],
    ['3', 'USD/JPY', '157.5340', '200', '2025-08-15', '2025-12-18'],
    ['4', 'USD/CAD', '1.4112', '200', '2025-08-23', '2025-12-18'],
    ['5', 'AUD/JPY', '109.1000', '5,200', '2007-01-22', '2025-12-18'],
    ['6', 'EUR/CAD', '1.7198', '5,200', '2006-10-10', '2025-12-18'],
    ['7', 'GBP/AUD', '2.6496', '5,200', '2007-01-22', '2025-12-18'],
    ['8', 'USD/MXN', '25.3380', '5,200', '2007-01-16', '2025-12-18'],
    ['9', 'USD/ZAR', '19.8048', '5,200', '2007-01-17', '2025-12-18'],
    ['10', 'USD/TRY', '42.7352', '5,200', '2007-01-11', '2025-12-18'],
]
t = Table(forex_data, colWidths=[0.4*inch, 0.9*inch, 1*inch, 0.8*inch, 1*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 4),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph('INDICES - Global Markets', h1_style))
indices_data = [
    ['#', 'Index', 'Name', 'Latest Value', 'Records', 'Start Date', 'End Date'],
    ['1', 'SPX', 'S&P 500', '6,131.00', '4,574', '2010-05-28', '2025-12-17'],
    ['2', 'NDX', 'NASDAQ 100', '2,700.00', '842', '2020-11-27', '2025-12-17'],
    ['3', 'DAX', 'German DAX', '4,598.00', '3,001', '2014-10-23', '2025-12-17'],
    ['4', 'FTSE', 'UK FTSE 100', '6,062.56', '2,505', '2016-12-13', '2025-12-17'],
    ['5', 'CAC', 'French CAC 40', '5,163.00', '5,200', '2006-01-30', '2025-12-17'],
    ['6', 'AEX', 'Amsterdam AEX', '371.19', '5,200', '2007-11-08', '2025-12-17'],
    ['7', 'SMI', 'Swiss Market Index', '1.47', '4,758', '2007-12-28', '2025-12-17'],
    ['8', 'HSI', 'Hang Seng', '5,100.00', '2,122', '2018-05-18', '2025-12-11'],
    ['9', 'IBEX', 'Spanish IBEX 35', '4,200.00', '1,344', '2020-08-07', '2025-12-11'],
]
t = Table(indices_data, colWidths=[0.4*inch, 0.7*inch, 1.8*inch, 1*inch, 0.8*inch, 1*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 4),
]))
story.append(t)

story.append(PageBreak())

# Quota Recommendations
story.append(Paragraph('TwelveData $229 Plan - Quota Utilization Recommendations', h1_style))
story.append(Paragraph('''
<b>Current Plan Limits:</b><br/>
- 1,597 API credits per minute<br/>
- Pro tier with full historical data access<br/>
- 100+ technical indicators available<br/>
<br/>
<b>Recommended Daily Fetch Strategy:</b>
''', body_style))

recommendations = [
    ['Asset Type', 'Recommended Symbols', 'Frequency', 'Credits/Day Est.', 'Priority'],
    ['US Stocks', '100 top by market cap', 'Daily + Hourly', '~2,500', 'HIGH'],
    ['Cryptocurrencies', '50 by market cap', 'Daily + Hourly', '~1,500', 'HIGH'],
    ['Forex Pairs', '20 major pairs', 'Daily + Hourly', '~600', 'MEDIUM'],
    ['ETFs', '20 major ETFs', 'Daily', '~400', 'MEDIUM'],
    ['Indices', '10 global indices', 'Daily', '~200', 'MEDIUM'],
    ['Commodities', '10 (Gold, Oil, etc)', 'Daily', '~200', 'LOW'],
    ['TOTAL', '210 symbols', 'Mixed', '~5,400', '-'],
]
t = Table(recommendations, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.3*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e7ff')),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph('''
<b>Action Items to Maximize Quota:</b><br/>
1. Set up Cloud Schedulers for automated daily fetches at market close<br/>
2. Enable hourly fetches for top 50 stocks and top 20 crypto during trading hours<br/>
3. Batch indicator calculations locally instead of fetching each indicator separately<br/>
4. Use the time_series endpoint with 250+ outputsize for historical backfill<br/>
5. Monitor API usage dashboard to stay within limits<br/>
<br/>
<b>BigQuery Storage:</b> aialgotradehits.crypto_trading_data / aialgotradehits.ml_models<br/>
<b>API Base URL:</b> https://api.twelvedata.com
''', body_style))

# Footer
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph('AIAlgoTradeHits.com - Trading Data Infrastructure Report', body_style))
story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Project: aialgotradehits', body_style))

doc.build(story)
print('PDF created: C:/1AITrading/Trading/ASSET_STATUS_REPORT.pdf')
