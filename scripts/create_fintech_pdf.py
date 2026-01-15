"""
Create PDF version of FINTECH_AI_DATA_ARCHITECTURE_MASTER_SPECIFICATION
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def create_pdf():
    doc = SimpleDocTemplate(
        "FINTECH_AI_DATA_ARCHITECTURE_MASTER_SPECIFICATION.pdf",
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=20,
        textColor=colors.darkblue
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=15,
        textColor=colors.darkblue
    )

    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.navy
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        spaceAfter=6,
        leftIndent=20
    )

    story = []

    # Title
    story.append(Paragraph("AIAlgoTradeHits.com", title_style))
    story.append(Paragraph("Fintech AI Data Architecture & Implementation Specification", title_style))
    story.append(Spacer(1, 20))

    # Meta info
    meta_data = [
        ['Version:', '2.0'],
        ['Platform:', 'Google Cloud Platform (GCP)'],
        ['AI Engine:', 'Vertex AI + Gemini 3'],
        ['Date:', 'November 2025'],
        ['Classification:', 'Technical Specification']
    ]
    meta_table = Table(meta_data, colWidths=[1.5*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 30))

    # Executive Summary
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "AIAlgoTradeHits.com is a comprehensive cross-asset, AI-driven analytics, alerting, and intelligence "
        "platform delivering institutional-grade insights across equities, ETFs, cryptocurrency, forex, "
        "commodities, and interest-rate markets. Built entirely on Google Cloud Platform, the system leverages "
        "Vertex AI, Gemini 3 LLM, BigQuery, and Cloud Run to create a next-generation fintech trading intelligence engine.",
        body_style
    ))

    story.append(Paragraph("Platform Vision", h2_style))
    platform_data = [
        ['Component', 'Technology', 'Purpose'],
        ['Data Warehouse', 'BigQuery', 'Multi-layer data architecture (Bronze/Silver/Gold)'],
        ['AI/ML Engine', 'Vertex AI', 'Predictive models, pattern recognition, regime classification'],
        ['LLM Intelligence', 'Gemini 3 Pro', 'Natural language analysis, RAG-powered commentary'],
        ['Document Intelligence', 'Document AI + RAG', 'Research document processing, knowledge retrieval'],
        ['Real-Time Serving', 'Cloud Run + Functions', 'API endpoints, scheduled data collection'],
        ['Frontend', 'React + TradingView', 'Professional trading interface'],
    ]
    platform_table = Table(platform_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    platform_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(platform_table)
    story.append(Spacer(1, 20))

    # Part 1: Data Architecture
    story.append(Paragraph("Part 1: Data Architecture", h1_style))

    story.append(Paragraph("1.1 Multi-Layer Data Architecture", h2_style))
    story.append(Paragraph(
        "The platform implements a rigorous four-layer data architecture inspired by institutional quant trading desks:",
        body_style
    ))

    layers = [
        "<b>BRONZE LAYER</b> - Raw, Immutable Market Data: Exact API responses preserved, full lineage and audit trail, compliance-grade immutability",
        "<b>SILVER LAYER</b> - Cleaned & Standardized Data: Normalized timestamps (UTC), missing data handling, anomaly removal, session calendar alignment",
        "<b>GOLD LAYER</b> - Engineered Features & Intelligence: 70+ Technical Indicators, pattern recognition signals, cross-asset correlations, volatility regime classification, ML-ready feature vectors",
        "<b>WIDE TABLES</b> - Materialized Fast-Access Layer: Flattened serving tables, real-time UI/API access, LLM RAG retrieval optimized, ML inference ready"
    ]
    for layer in layers:
        story.append(Paragraph(layer, body_style))

    story.append(Paragraph("1.2 BigQuery Table Structure", h2_style))
    story.append(Paragraph("1.2.1 Asset Class Tables (6 Categories)", h3_style))

    table_data = [
        ['Table Name', 'Asset Class', 'Timeframes', 'Data Source'],
        ['stocks_historical_daily', 'US Equities', 'Daily, Weekly', 'TwelveData'],
        ['stocks_hourly', 'US Equities', 'Hourly, 5-min', 'TwelveData'],
        ['cryptos_historical_daily', 'Cryptocurrency', 'Daily, Weekly', 'Kraken/TwelveData'],
        ['crypto_hourly_data', 'Cryptocurrency', 'Hourly, 5-min', 'Kraken'],
        ['etfs_historical_daily', 'ETFs', 'Daily, Weekly', 'TwelveData'],
        ['forex_historical_daily', 'FX Pairs', 'Daily, Weekly', 'TwelveData'],
        ['indices_historical_daily', 'Market Indices', 'Daily, Weekly', 'TwelveData'],
        ['commodities_historical_daily', 'Commodities', 'Daily, Weekly', 'TwelveData'],
    ]
    t = Table(table_data, colWidths=[2*inch, 1.3*inch, 1.2*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Core OHLCV Fields
    story.append(Paragraph("Core OHLCV Fields (Required)", h3_style))
    ohlcv_data = [
        ['Field Name', 'Type', 'Description', 'Status'],
        ['symbol', 'STRING', 'Asset ticker symbol', 'Available'],
        ['datetime', 'TIMESTAMP', 'Candle timestamp (UTC)', 'Available'],
        ['open', 'FLOAT64', 'Opening price', 'Available'],
        ['high', 'FLOAT64', 'High price', 'Available'],
        ['low', 'FLOAT64', 'Low price', 'Available'],
        ['close', 'FLOAT64', 'Closing price', 'Available'],
        ['volume', 'FLOAT64', 'Trading volume', 'Available'],
        ['candle_body_pct', 'FLOAT64', '(close - open) / open', 'Add'],
        ['candle_range_pct', 'FLOAT64', '(high - low) / open', 'Add'],
    ]
    t = Table(ohlcv_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # RSI Indicators
    story.append(Paragraph("RSI Indicators", h3_style))
    rsi_data = [
        ['Field Name', 'Type', 'Description', 'Status'],
        ['rsi_7', 'FLOAT64', 'RSI 7-period', 'Available'],
        ['rsi_14', 'FLOAT64', 'RSI 14-period', 'Available'],
        ['rsi_21', 'FLOAT64', 'RSI 21-period', 'Available'],
        ['rsi_slope', 'FLOAT64', 'RSI change rate', 'Add'],
        ['rsi_zscore', 'FLOAT64', 'RSI z-score (100-week)', 'Add'],
        ['rsi_overbought_flag', 'INT64', 'RSI > 70 flag', 'Add'],
        ['rsi_oversold_flag', 'INT64', 'RSI < 30 flag', 'Add'],
    ]
    t = Table(rsi_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t)
    story.append(PageBreak())

    # Part 2: AI & ML Architecture
    story.append(Paragraph("Part 2: AI & Machine Learning Architecture", h1_style))

    story.append(Paragraph("2.1 Vertex AI Integration", h2_style))
    story.append(Paragraph("2.1.1 Model Types & Use Cases", h3_style))

    ml_data = [
        ['Model Type', 'Vertex AI Service', 'Use Case'],
        ['Gradient Boosting', 'AutoML Tables', 'Regime classification, direction prediction'],
        ['Time Series', 'Vertex AI Forecasting', 'Price prediction, volatility forecasting'],
        ['LSTM/Transformer', 'Custom Training', 'Sequential pattern learning'],
        ['Vision Models', 'AutoML Vision', 'Chart pattern recognition'],
        ['LLM', 'Gemini 3 Pro', 'Commentary generation, analysis'],
    ]
    t = Table(ml_data, colWidths=[1.5*inch, 1.8*inch, 2.7*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("2.2 Gemini 3 LLM Integration", h2_style))
    story.append(Paragraph("2.2.1 LLM Use Cases", h3_style))

    llm_data = [
        ['Use Case', 'Input', 'Output', 'Frequency'],
        ['Market Commentary', 'Indicators, patterns, regime', 'Research-style analysis', 'Real-time'],
        ['Alert Explanations', 'Alert trigger data, context', 'Natural language reasoning', 'Per alert'],
        ['Pattern Analysis', 'Chart patterns, structure', 'Professional interpretation', 'On detection'],
        ['Risk Assessment', 'Cross-asset correlations', 'Risk narrative', 'Hourly'],
        ['Q&A Interface', 'User questions + RAG context', 'Informed responses', 'On-demand'],
    ]
    t = Table(llm_data, colWidths=[1.3*inch, 1.5*inch, 1.8*inch, 1.4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("2.2.2 RAG (Retrieval-Augmented Generation) Architecture", h3_style))
    story.append(Paragraph(
        "The RAG pipeline consists of: 1) USER QUERY / TRIGGER, 2) CONTEXT RETRIEVAL from BigQuery Market Data, "
        "Vector DB Research Embeddings, and Document Store, 3) PROMPT CONSTRUCTION with System Instructions + "
        "Retrieved Context + User Query, 4) GEMINI 3 PRO for grounded response generation with citation and "
        "hallucination prevention, 5) STRUCTURED OUTPUT with market analysis, key insights, risk warnings, "
        "and actionable recommendations.",
        body_style
    ))

    # Part 3: Implementation Phases
    story.append(Paragraph("Part 3: Implementation Phases", h1_style))

    story.append(Paragraph("3.1 Phase 1: Trader-Focused AI Alert Engine", h2_style))
    story.append(Paragraph("Focus: Real-time alerts for equities and cryptocurrency", body_style))

    story.append(Paragraph("MVP Symbol Universe", h3_style))
    mvp_data = [
        ['Category', 'Examples', 'Count'],
        ['US Equities', 'AAPL, NVDA, JPM, LLY, MSFT, GOOGL, AMZN, META, TSLA', '50'],
        ['ETFs', 'SPY, QQQ, IWM, DIA, VTI, VOO, GLD', '30'],
        ['Cryptocurrency', 'BTC/USD, ETH/USD, SOL/USD, XRP/USD', '20'],
        ['Forex', 'EUR/USD, GBP/USD, USD/JPY', '20'],
        ['Indices', 'SPX, NDX, DJI, VIX', '14'],
        ['Commodities', 'XAU/USD, XAG/USD, CL, NG', '16'],
    ]
    t = Table(mvp_data, colWidths=[1.2*inch, 3.5*inch, 1.3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Phase 1 Deliverables:", h3_style))
    deliverables = [
        "<b>1. Real-Time Alert System:</b> Trend flip alerts, momentum reversal signals, volatility expansion warnings, breakout/breakdown detection, pattern confirmation alerts",
        "<b>2. AI-Enhanced Dashboards:</b> Regime classification display, volatility heatmaps, correlation monitors, sentiment indicators",
        "<b>3. LLM Commentary (Basic):</b> Alert explanation generation, daily market summaries, pattern interpretation"
    ]
    for d in deliverables:
        story.append(Paragraph(d, body_style))

    story.append(PageBreak())

    # Part 4: GCP Infrastructure
    story.append(Paragraph("Part 4: GCP Infrastructure", h1_style))

    story.append(Paragraph("4.1 Service Architecture", h2_style))
    story.append(Paragraph("GCP PROJECT: cryptobot-462709", body_style))
    story.append(Paragraph(
        "The infrastructure consists of: Cloud Run (Frontend + API), BigQuery (Data Warehouse), "
        "Vertex AI (ML + Gemini 3), Cloud Functions (Data Fetch), Cloud Storage (Documents), "
        "and Cloud Scheduler (Triggers).",
        body_style
    ))

    story.append(Paragraph("4.2 Cost Optimization Strategy", h2_style))
    cost_data = [
        ['Service', 'Optimization', 'Monthly Estimate'],
        ['BigQuery', 'Partitioned tables, clustering', '$50-100'],
        ['Cloud Functions', 'Efficient scheduling, cold start optimization', '$130'],
        ['Cloud Run', 'Auto-scaling, min instances', '$50-100'],
        ['Vertex AI', 'Batch predictions, model caching', '$200-500'],
        ['Gemini 3', 'Caching, prompt optimization', '$100-300'],
        ['Total Estimate', '', '$530-1,130/month'],
    ]
    t = Table(cost_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Part 5: Missing Fields Implementation
    story.append(Paragraph("Part 5: Missing Fields Implementation Plan", h1_style))

    story.append(Paragraph("Priority 1: Critical ML Features (Add Immediately)", h2_style))
    priority1 = [
        "Log returns: weekly_log_return - ln(close_t / close_t-1)",
        "Multi-lag returns: return_2w, return_4w",
        "RSI enhancements: rsi_slope, rsi_zscore, rsi_overbought_flag, rsi_oversold_flag",
        "MACD enhancements: macd_hist, macd_cross_flag",
        "EMA suite: ema_5, ema_10, ema_20, ema_50, ema_100, ema_200",
        "MA distance features: close_vs_sma20_pct, close_vs_sma50_pct, close_vs_sma200_pct, close_vs_ema20_pct",
        "EMA slopes: ema_slope_20, ema_slope_50"
    ]
    for p in priority1:
        story.append(Paragraph("• " + p, body_style))

    story.append(Paragraph("Priority 2: Enhanced Features (Add Next Sprint)", h2_style))
    priority2 = [
        "ATR enhancements: atr_pct, atr_zscore, atr_slope",
        "Volume enhancements: volume_zscore, volume_ratio",
        "ADX trend: adx, plus_di, minus_di",
        "Candle geometry: candle_body_pct, candle_range_pct"
    ]
    for p in priority2:
        story.append(Paragraph("• " + p, body_style))

    # Part 6: Implementation Roadmap
    story.append(Paragraph("Part 6: Implementation Roadmap", h1_style))

    roadmap = [
        ("<b>Week 1-2: Data Schema Enhancement</b>", [
            "Add Priority 1 missing fields to BigQuery tables",
            "Update data fetching scripts with new calculations",
            "Backfill historical data with new indicators"
        ]),
        ("<b>Week 3-4: ML Pipeline Setup</b>", [
            "Configure Vertex AI Feature Store",
            "Create initial training pipelines",
            "Deploy baseline models"
        ]),
        ("<b>Week 5-6: LLM Integration</b>", [
            "Implement RAG pipeline with BigQuery",
            "Configure Gemini 3 Pro prompts",
            "Build commentary generation endpoints"
        ]),
        ("<b>Week 7-8: Testing & Optimization</b>", [
            "Backtest ML models",
            "Evaluate LLM output quality",
            "Performance optimization"
        ]),
    ]

    for title, items in roadmap:
        story.append(Paragraph(title, body_style))
        for item in items:
            story.append(Paragraph("  • " + item, body_style))

    story.append(PageBreak())

    # Appendix
    story.append(Paragraph("Appendix A: Technical Indicator Formulas", h1_style))

    formulas = [
        ("A.1 Log Return", "weekly_log_return = ln(close_t) - ln(close_t-1)"),
        ("A.2 RSI Slope", "rsi_slope = rsi_t - rsi_t-1"),
        ("A.3 RSI Z-Score", "rsi_zscore = (rsi - mean_100w) / std_100w"),
        ("A.4 MACD Cross Flag", "+1 if macd crosses above signal, -1 if below, 0 otherwise"),
        ("A.5 MA Distance", "close_vs_sma20_pct = (close / sma_20 - 1) * 100"),
        ("A.6 EMA Slope", "ema_slope_20 = ema_20_t - ema_20_t-1"),
        ("A.7 ATR Percentage", "atr_pct = (atr_14 / close) * 100"),
        ("A.8 Volume Z-Score", "volume_zscore = (volume - mean_20) / std_20"),
    ]

    for title, formula in formulas:
        story.append(Paragraph(f"<b>{title}</b>", body_style))
        story.append(Paragraph(formula, code_style))

    # Document Control
    story.append(Spacer(1, 30))
    story.append(Paragraph("Document Control", h1_style))

    control_data = [
        ['Version', 'Date', 'Author', 'Changes'],
        ['1.0', 'Nov 2025', 'System', 'Initial draft'],
        ['2.0', 'Nov 2025', 'Claude/AI', 'Combined Phase 1 + AI/LLM specs'],
    ]
    t = Table(control_data, colWidths=[1*inch, 1.2*inch, 1.3*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)

    story.append(Spacer(1, 30))
    story.append(Paragraph("End of Document", ParagraphStyle('Center', alignment=TA_CENTER)))

    # Build PDF
    doc.build(story)
    print("PDF created successfully: FINTECH_AI_DATA_ARCHITECTURE_MASTER_SPECIFICATION.pdf")


if __name__ == '__main__':
    create_pdf()
