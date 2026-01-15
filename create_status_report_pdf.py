#!/usr/bin/env python3
"""Generate PDF from Trading Data Status Report"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def create_pdf():
    filename = "C:/1AITrading/Trading/TRADING_DATA_STATUS_REPORT.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                  fontSize=24, alignment=TA_CENTER, spaceAfter=20,
                                  textColor=colors.HexColor('#1a365d'))

    h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
                               fontSize=16, spaceAfter=12, spaceBefore=20,
                               textColor=colors.HexColor('#2c5282'))

    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                               fontSize=13, spaceAfter=8, spaceBefore=15,
                               textColor=colors.HexColor('#2b6cb0'))

    normal_style = ParagraphStyle('Normal', parent=styles['Normal'],
                                   fontSize=10, spaceAfter=6)

    story = []

    # Title
    story.append(Paragraph("Trading Data Status Report", title_style))
    story.append(Paragraph("AIAlgoTradeHits - TwelveData Pipeline", styles['Heading2']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph("GCP Project: aialgotradehits | Dataset: crypto_trading_data", normal_style))
    story.append(Spacer(1, 20))

    # Executive Summary
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "The TwelveData data pipeline is operational across <b>7 asset types</b> with <b>28 tables</b> "
        "covering 4 timeframes (daily, hourly, 5-minute, weekly). The latest parallel fetch added "
        "<b>91,615 new records</b> across all asset types.", normal_style))
    story.append(Spacer(1, 10))

    # Overall Statistics Table
    stats_data = [
        ['Metric', 'Value'],
        ['Total Asset Types', '7'],
        ['Total Tables', '28'],
        ['Total Symbols Tracked', '305+'],
        ['Data Range', '2022-2025'],
        ['API Plan', 'TwelveData $229/month'],
        ['API Credits', '800/minute']
    ]

    stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf8ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#90cdf4')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))

    # Asset Type Coverage
    story.append(Paragraph("Asset Type Coverage", h1_style))

    # Main data table
    asset_data = [
        ['Asset Type', 'Table', 'Records', 'Symbols', 'Date Range'],
        ['STOCKS', 'v2_stocks_daily', '186,150', '152', 'Jul 2024 - Dec 2025'],
        ['CRYPTO', 'v2_crypto_daily', '98,550', '45', 'Dec 2024 - Dec 2025'],
        ['FOREX', 'v2_forex_daily', '54,750', '30', 'Aug 2024 - Dec 2025'],
        ['ETFs', 'v2_etfs_daily', '67,160', '40', 'Jul 2024 - Dec 2025'],
        ['INDICES', 'v2_indices_daily', '5,475', '9', 'Jan 2022 - Dec 2025'],
        ['COMMODITIES', 'v2_commodities_daily', '29,407', '14', 'Jul 2024 - Dec 2025'],
        ['FUNDS (NEW)', 'v2_funds_daily', '5,475', '15', 'Jan 2024 - Dec 2025'],
    ]

    asset_table = Table(asset_data, colWidths=[1.2*inch, 1.5*inch, 0.9*inch, 0.8*inch, 1.6*inch])
    asset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fed7aa')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#bee3f8')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#e9d8fd')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#fefcbf')),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#fbb6ce')),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#9ae6b4')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a0aec0')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(asset_table)
    story.append(Spacer(1, 20))

    # Symbol Lists
    story.append(Paragraph("Top Symbols by Asset Type", h2_style))

    symbols_text = """
    <b>Stocks:</b> AAPL, MSFT, AMZN, NVDA, GOOGL, META, TSLA, JPM, V, MA, JNJ, UNH, HD, PG, WMT, CVX, MRK, ABBV, LLY, KO, etc.<br/><br/>
    <b>Crypto:</b> BTCUSD, ETHUSD, BNBUSD, XRPUSD, SOLUSD, ADAUSD, DOGEUSD, AVAXUSD, LINKUSD, DOTUSD, etc.<br/><br/>
    <b>Forex:</b> EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD, EUR/GBP, EUR/JPY, GBP/JPY, etc.<br/><br/>
    <b>ETFs:</b> SPY, QQQ, DIA, IWM, VOO, VTI, ARKK, XLF, XLK, XLE, XLV, GLD, SLV, TLT, SMH, SOXX, etc.<br/><br/>
    <b>Indices:</b> SPX, NDX, DAX, CAC, FTSE, HSI, AEX, SMI, IBEX<br/><br/>
    <b>Commodities:</b> XAU/USD (Gold), XAG/USD (Silver), CL (WTI), BZ (Brent), NG (Natural Gas), HG (Copper), ZC (Corn), ZS (Soybeans)<br/><br/>
    <b>Funds:</b> VFINX, VTSAX, FXAIX, VFIAX, VGTSX, VTSMX, FMAGX, PRWCX, AGTHX, OAKMX
    """
    story.append(Paragraph(symbols_text, normal_style))
    story.append(Spacer(1, 15))

    # Latest Fetch Results
    story.append(Paragraph("Latest Fetch Results", h1_style))

    fetch_data = [
        ['Metric', 'Value'],
        ['Records Added', '91,615'],
        ['Processing Time', '16.6 minutes'],
        ['API Calls Made', '320'],
        ['Success Rate', '78%'],
        ['Timestamp', datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]

    fetch_table = Table(fetch_data, colWidths=[2*inch, 2*inch])
    fetch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#68d391')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(fetch_table)
    story.append(Spacer(1, 20))

    # Cloud Schedulers
    story.append(Paragraph("Cloud Schedulers Status", h1_style))
    story.append(Paragraph("All 40+ Cloud Schedulers are <b>ENABLED</b> and running automatically:", normal_style))

    scheduler_data = [
        ['Scheduler', 'Schedule', 'Asset', 'Status'],
        ['twelvedata-daily-stocks', '0 0 * * *', 'Stocks', 'ENABLED'],
        ['twelvedata-daily-crypto', '5 0 * * *', 'Crypto', 'ENABLED'],
        ['twelvedata-daily-forex', '10 0 * * *', 'Forex', 'ENABLED'],
        ['twelvedata-daily-etfs', '15 0 * * *', 'ETFs', 'ENABLED'],
        ['twelvedata-daily-indices', '20 0 * * *', 'Indices', 'ENABLED'],
        ['twelvedata-daily-commodities', '25 0 * * *', 'Commodities', 'ENABLED'],
        ['twelvedata-hourly-*', '0-25 * * * *', 'All', 'ENABLED'],
        ['twelvedata-5min-*', '*/5 9-16 * * 1-5', 'All', 'ENABLED'],
        ['twelvedata-weekly-all', '0 0 * * 0', 'All', 'ENABLED'],
    ]

    sched_table = Table(scheduler_data, colWidths=[2.2*inch, 1.5*inch, 1*inch, 0.8*inch])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#805ad5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#b794f4')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 20))

    # Technical Indicators
    story.append(Paragraph("Technical Indicators (24 per Masterquery Spec)", h1_style))

    indicators_text = """
    <b>Momentum (6):</b> RSI_14, MACD, MACD_Signal, MACD_Histogram, Stoch_K, Stoch_D<br/><br/>
    <b>Trend (10):</b> SMA_20, SMA_50, SMA_200, EMA_12, EMA_20, EMA_26, EMA_50, EMA_200, Ichimoku Tenkan, Kijun<br/><br/>
    <b>Volatility (4):</b> ATR_14, BB_Upper, BB_Middle, BB_Lower<br/><br/>
    <b>Trend Strength (3):</b> ADX, Plus_DI, Minus_DI<br/><br/>
    <b>Flow (2):</b> MFI, CMF<br/><br/>
    <b>Computed Signals:</b> Growth Score (0-100), In Rise Cycle (boolean), Trend Regime (string)
    """
    story.append(Paragraph(indicators_text, normal_style))
    story.append(Spacer(1, 20))

    # API Endpoints
    story.append(Paragraph("API Endpoints", h1_style))
    story.append(Paragraph("<b>Base URL:</b> https://trading-api-1075463475276.us-central1.run.app", normal_style))

    api_data = [
        ['Endpoint', 'Purpose'],
        ['/api/ai/trading-signals', 'Generate buy/sell signals'],
        ['/api/ai/rise-cycle-candidates', 'EMA crossover detection'],
        ['/api/ai/ml-predictions', 'Growth score predictions'],
        ['/api/ai/growth-screener', 'High growth scanner'],
        ['/api/ai/text-to-sql', 'Natural language queries'],
    ]

    api_table = Table(api_data, colWidths=[2.5*inch, 3*inch])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dd6b20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffaf0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ed8936')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 20))

    # Cost Estimate
    story.append(Paragraph("Monthly Cost Estimate", h1_style))

    cost_data = [
        ['Component', 'Cost'],
        ['TwelveData API ($229 Plan)', '$229'],
        ['Cloud Functions', '~$50'],
        ['BigQuery Storage', '~$5'],
        ['Cloud Schedulers', '~$1'],
        ['TOTAL', '$285/month'],
    ]

    cost_table = Table(cost_data, colWidths=[2.5*inch, 1.5*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#319795')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#319795')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#e6fffa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4fd1c5')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cost_table)
    story.append(Spacer(1, 30))

    # Footer
    story.append(Paragraph("---", styles['Normal']))
    story.append(Paragraph(
        f"Report generated by parallel_all_assets_fetcher.py | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))

    # Build PDF
    doc.build(story)
    print(f"PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_pdf()
