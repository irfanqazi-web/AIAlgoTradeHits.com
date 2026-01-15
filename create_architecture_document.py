#!/usr/bin/env python3
"""
Generate AIAlgoTradeHits.com Architecture Document as PDF
Comprehensive system documentation including:
- Folder structure
- Site map
- Component analysis
- Redundancy identification
- Refactoring recommendations
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def create_architecture_pdf():
    """Generate the comprehensive architecture PDF"""

    output_path = "AIALGOTRADEHITS_ARCHITECTURE_DOCUMENT.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1e3a5f'),
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2563eb')
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=14,
        textColor=colors.HexColor('#059669')
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.HexColor('#7c3aed')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        backColor=colors.HexColor('#f1f5f9'),
        leftIndent=10,
        rightIndent=10,
        spaceAfter=8
    )

    story = []

    # ============================================
    # TITLE PAGE
    # ============================================
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AIAlgoTradeHits.com", title_style))
    story.append(Paragraph("Complete Architecture Document", ParagraphStyle('Subtitle', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.HexColor('#64748b'))))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER)))
    story.append(Paragraph("Version 4.0", ParagraphStyle('Version', parent=styles['Normal'], alignment=TA_CENTER)))
    story.append(Spacer(1, 1*inch))

    # Table of Contents style summary
    toc_items = [
        "1. Executive Summary",
        "2. System Architecture Overview",
        "3. Folder & File Structure",
        "4. Complete Site Map",
        "5. Frontend Components Analysis",
        "6. Backend API Structure",
        "7. Cloud Functions Inventory",
        "8. Database Schema",
        "9. Redundancy Analysis",
        "10. NLP Development Roadmap",
        "11. Environment Configuration",
        "12. Refactoring Recommendations"
    ]

    story.append(Paragraph("Table of Contents", h2_style))
    for item in toc_items:
        story.append(Paragraph(item, body_style))

    story.append(PageBreak())

    # ============================================
    # 1. EXECUTIVE SUMMARY
    # ============================================
    story.append(Paragraph("1. Executive Summary", h1_style))

    summary_text = """
    AIAlgoTradeHits.com is a comprehensive AI-powered fintech trading platform that provides:
    <br/><br/>
    <b>Core Capabilities:</b><br/>
    - Multi-timeframe market analysis (Daily, Hourly, 5-Minute)<br/>
    - AI/ML predictions with 66.2% UP accuracy using Nested Multi-Timeframe Model<br/>
    - Natural Language Processing (NLP) for intelligent search<br/>
    - Real-time data from 5 APIs: TwelveData, Kraken, FRED, CoinMarketCap, Finnhub<br/>
    - 6 asset classes: Stocks, Crypto, Forex, ETFs, Indices, Commodities<br/>
    - 24 technical indicators per masterquery.md specifications<br/>
    <br/>
    <b>Technology Stack:</b><br/>
    - Frontend: React 18 + Vite + TradingView Lightweight Charts<br/>
    - Backend: Python Flask API on Google Cloud Run<br/>
    - Database: Google BigQuery (1.2B+ records across 113 tables)<br/>
    - ML: BigQuery ML (XGBoost) + Vertex AI<br/>
    - Infrastructure: GCP Cloud Functions, Cloud Scheduler, Cloud Storage<br/>
    """
    story.append(Paragraph(summary_text, body_style))

    # Key metrics table
    metrics_data = [
        ['Metric', 'Value', 'Notes'],
        ['Total Data Records', '1.2B+', 'Across all timeframes'],
        ['BigQuery Tables', '113', 'Data warehouse'],
        ['Cloud Functions', '33', 'Data pipeline'],
        ['Cloud Schedulers', '54', 'Automation'],
        ['React Components', '42', 'Frontend UI'],
        ['API Endpoints', '80+', 'REST API'],
        ['ML Model Accuracy', '68.4%', 'Nested Multi-TF'],
        ['UP Prediction', '66.2%', '6.2x improvement'],
    ]

    t = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
    ]))
    story.append(Spacer(1, 0.2*inch))
    story.append(t)

    story.append(PageBreak())

    # ============================================
    # 2. SYSTEM ARCHITECTURE OVERVIEW
    # ============================================
    story.append(Paragraph("2. System Architecture Overview", h1_style))

    arch_text = """
    <b>High-Level Architecture:</b><br/><br/>

    <b>Data Layer (BigQuery)</b><br/>
    └── crypto_trading_data dataset (main)<br/>
    └── ml_models dataset (ML features/models)<br/>
    └── 113 tables with partitioning<br/><br/>

    <b>API Layer (Cloud Run)</b><br/>
    └── trading-api service<br/>
    └── Flask-based REST API<br/>
    └── 80+ endpoints<br/><br/>

    <b>Data Collection (Cloud Functions)</b><br/>
    └── bulletproof-fetcher (primary)<br/>
    └── 33 specialized functions<br/>
    └── Multi-source integration<br/><br/>

    <b>Frontend (Cloud Run)</b><br/>
    └── React 18 SPA<br/>
    └── 42 components<br/>
    └── TradingView charts<br/><br/>

    <b>ML Pipeline (BigQuery ML + Vertex AI)</b><br/>
    └── Nested Multi-Timeframe Model<br/>
    └── Walk-Forward Validation<br/>
    └── Feature engineering<br/>
    """
    story.append(Paragraph(arch_text, body_style))

    story.append(Paragraph("2.1 Data Flow Architecture", h2_style))

    flow_text = """
    <b>Data Collection Flow:</b><br/>
    1. Cloud Scheduler triggers Cloud Functions (hourly/daily)<br/>
    2. bulletproof-fetcher calls TwelveData API (800 calls/min)<br/>
    3. Parallel fetching from Kraken, FRED, CMC, Finnhub<br/>
    4. Data processed with 24 indicators per masterquery.md<br/>
    5. Uploaded to BigQuery tables (_clean suffix)<br/>
    6. ML features computed and stored<br/>
    7. Predictions generated and cached<br/><br/>

    <b>User Request Flow:</b><br/>
    1. User interacts with React frontend<br/>
    2. API calls to trading-api (Cloud Run)<br/>
    3. API queries BigQuery (read-only)<br/>
    4. Results transformed and returned as JSON<br/>
    5. Frontend renders data with TradingView charts<br/>
    """
    story.append(Paragraph(flow_text, body_style))

    story.append(PageBreak())

    # ============================================
    # 3. FOLDER & FILE STRUCTURE
    # ============================================
    story.append(Paragraph("3. Folder & File Structure", h1_style))

    story.append(Paragraph("3.1 Root Directory Structure", h2_style))

    root_structure = """
    <font face="Courier" size="8">
    C:\\1AITrading\\Trading\\<br/>
    ├── stock-price-app/          # React Frontend Application<br/>
    ├── cloud_function_api/       # Main REST API (Flask)<br/>
    ├── cloud_function_bulletproof/ # Primary Data Fetcher<br/>
    ├── cloud_function_*/         # 33 Cloud Functions<br/>
    ├── cloud_run_trading_agent/  # AI Trading Agent<br/>
    ├── shared_ai_modules/        # Reusable AI Components<br/>
    ├── agentic_trading_system/   # Multi-Agent Framework<br/>
    ├── models/                   # ML Model Artifacts<br/>
    ├── utils/                    # Utility Scripts<br/>
    ├── documents/                # Generated PDFs<br/>
    ├── masterquery.md            # PRIMARY SPECIFICATION<br/>
    ├── CLAUDE.md                 # AI Assistant Instructions<br/>
    └── *.py                      # 349 Python Scripts<br/>
    </font>
    """
    story.append(Paragraph(root_structure, body_style))

    story.append(Paragraph("3.2 Frontend Structure (stock-price-app/)", h2_style))

    frontend_structure = """
    <font face="Courier" size="8">
    stock-price-app/<br/>
    ├── src/<br/>
    │   ├── components/           # 42 React Components<br/>
    │   │   ├── TradingDashboard.jsx    # Main dashboard<br/>
    │   │   ├── SmartDashboard.jsx      # Search-enabled dashboard<br/>
    │   │   ├── Navigation.jsx          # Side menu + top bar<br/>
    │   │   ├── NestedSignals.jsx       # ML signals display<br/>
    │   │   ├── MultiTimeframeTrader.jsx # Multi-TF analysis<br/>
    │   │   ├── WalkForwardValidation.jsx # ML validation<br/>
    │   │   └── ... (39 more)<br/>
    │   ├── services/<br/>
    │   │   ├── api.js            # API client service<br/>
    │   │   ├── marketData.js     # Market data utilities<br/>
    │   │   ├── aiService.js      # AI integration<br/>
    │   │   └── monitoringService.js<br/>
    │   ├── utils/<br/>
    │   │   └── technicalAnalysis.js<br/>
    │   ├── App.jsx               # Main app + routing<br/>
    │   ├── App.css               # Global styles<br/>
    │   ├── main.jsx              # Entry point<br/>
    │   ├── index.css             # Base CSS<br/>
    │   └── theme.js              # Theme configuration<br/>
    ├── public/                   # Static assets<br/>
    ├── dist/                     # Build output<br/>
    ├── package.json              # Dependencies<br/>
    ├── vite.config.js            # Vite configuration<br/>
    └── Dockerfile                # Container build<br/>
    </font>
    """
    story.append(Paragraph(frontend_structure, body_style))

    story.append(Paragraph("3.3 Backend API Structure (cloud_function_api/)", h2_style))

    api_structure = """
    <font face="Courier" size="8">
    cloud_function_api/<br/>
    ├── main.py                   # Flask app + 80+ endpoints<br/>
    ├── nlp_query_engine.py       # NLP search engine<br/>
    ├── walk_forward_endpoints.py # ML validation API<br/>
    ├── ai_endpoints.py           # AI/ML endpoints<br/>
    ├── ai_trading_service.py     # Trading signal service<br/>
    ├── trading_alerts.py         # Alert system<br/>
    ├── ml_ensemble_endpoints.py  # Ensemble ML<br/>
    ├── requirements.txt          # Python dependencies<br/>
    ├── Dockerfile                # Container build<br/>
    └── deploy_api.py             # Deployment script<br/>
    </font>
    """
    story.append(Paragraph(api_structure, body_style))

    story.append(PageBreak())

    # ============================================
    # 4. COMPLETE SITE MAP
    # ============================================
    story.append(Paragraph("4. Complete Site Map", h1_style))

    story.append(Paragraph("4.1 Public Routes (All Users)", h2_style))

    sitemap_data = [
        ['Route', 'Component', 'Description', 'Status'],
        ['/dashboard', 'SmartDashboard', 'Main dashboard with NLP search', 'ACTIVE'],
        ['/trade-analysis', 'MultiTimeframeTrader', 'Daily/Hourly/5-Min analysis', 'ACTIVE'],
        ['/opportunity-report', 'OpportunityReport', 'Daily ranked opportunities', 'ACTIVE'],
        ['/weekly', 'WeeklyDashboard', 'Weekly analysis all assets', 'ACTIVE'],
        ['/weekly/stocks', 'WeeklyAnalysis', 'Weekly stocks analysis', 'ACTIVE'],
        ['/weekly/cryptos', 'WeeklyAnalysis', 'Weekly crypto analysis', 'ACTIVE'],
        ['/weekly/etfs', 'WeeklyAnalysis', 'Weekly ETF analysis', 'ACTIVE'],
        ['/weekly/forex', 'WeeklyAnalysis', 'Weekly forex analysis', 'ACTIVE'],
        ['/weekly/indices', 'WeeklyAnalysis', 'Weekly indices analysis', 'ACTIVE'],
        ['/weekly/commodities', 'WeeklyAnalysis', 'Weekly commodities', 'ACTIVE'],
        ['/ai-signals/predictions', 'AIPredictions', 'ML price predictions', 'ACTIVE'],
        ['/ai-signals/patterns', 'AIPatternRecognition', 'Chart pattern detection', 'ACTIVE'],
        ['/ai-signals/sentiment', 'ComingSoon', 'Sentiment analysis', 'PLANNED'],
        ['/ai-signals/signals', 'AITradeSignals', 'Buy/sell signals', 'ACTIVE'],
        ['/ai-signals/anomalies', 'ComingSoon', 'Anomaly detection', 'PLANNED'],
        ['/portfolio', 'PortfolioTracker', 'Portfolio management', 'ACTIVE'],
        ['/alerts', 'PriceAlerts', 'Price alert system', 'ACTIVE'],
        ['/strategies', 'StrategyDashboard', 'Trading strategies', 'ACTIVE'],
        ['/market-movers', 'MarketMovers', 'Top gainers/losers', 'ACTIVE'],
        ['/fundamentals', 'FundamentalsView', 'Company fundamentals', 'ACTIVE'],
        ['/etf-analytics', 'ETFAnalytics', 'ETF analysis', 'ACTIVE'],
        ['/ai-training', 'AITrainingDocs', 'ML training docs', 'ACTIVE'],
        ['/documents', 'DocumentsLibrary', 'System documentation', 'ACTIVE'],
        ['/settings', 'Settings (inline)', 'Account settings', 'ACTIVE'],
    ]

    t = Table(sitemap_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 0.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("4.2 Admin Routes (Admin Only)", h2_style))

    admin_data = [
        ['Route', 'Component', 'Description', 'Status'],
        ['/admin', 'AdminPanelEnhanced', 'User management', 'ACTIVE'],
        ['/table-inventory', 'TableInventory', 'BigQuery table browser', 'ACTIVE'],
        ['/data-warehouse-status', 'DataWarehouseStatus', 'Data collection monitor', 'ACTIVE'],
        ['/database-summary', 'DatabaseSummary', 'XLSX export', 'ACTIVE'],
        ['/data-export', 'DataExportDownload', '97-field CSV export', 'ACTIVE'],
        ['/ml-test-data', 'MLTestDataDownload', 'ML test datasets', 'ACTIVE'],
        ['/walk-forward', 'WalkForwardValidation', 'ML validation system', 'ACTIVE'],
    ]

    t = Table(admin_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 0.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f3ff')]),
    ]))
    story.append(t)

    story.append(PageBreak())

    # ============================================
    # 5. FRONTEND COMPONENTS ANALYSIS
    # ============================================
    story.append(Paragraph("5. Frontend Components Analysis", h1_style))

    story.append(Paragraph("5.1 Component Inventory (42 Components)", h2_style))

    components_data = [
        ['Component', 'Lines', 'Purpose', 'Category'],
        ['TradingViewChart.jsx', '1798', 'Full TradingView integration', 'CORE'],
        ['SmartDashboard.jsx', '1255', 'NLP-enabled main dashboard', 'CORE'],
        ['TableInventory.jsx', '1011', 'BigQuery table browser', 'ADMIN'],
        ['OrganizationChart.jsx', '969', 'Org structure display', 'UTILITY'],
        ['WeeklyDashboard.jsx', '966', 'Weekly analysis hub', 'CORE'],
        ['MultiTimeframeTrader.jsx', '944', 'Multi-TF trading analysis', 'CORE'],
        ['TradingDashboard.jsx', '888', 'Main trading dashboard', 'CORE'],
        ['DataDownloadWizard.jsx', '885', 'Data export wizard', 'ADMIN'],
        ['SmartSearchBar.jsx', '827', 'NLP search component', 'CORE'],
        ['EnhancedDashboard.jsx', '821', 'Enhanced dashboard', 'REDUNDANT'],
        ['AIPatternRecognition.jsx', '761', 'Pattern detection UI', 'AI'],
        ['OpportunityReport.jsx', '783', 'Daily opportunities', 'CORE'],
        ['Navigation.jsx', '740', 'Side menu + top bar', 'CORE'],
        ['AITrainingDocs.jsx', '643', 'ML training documents', 'AI'],
        ['NLPSearch.jsx', '628', 'NLP search page', 'REDUNDANT'],
        ['WeeklyReconciliation.jsx', '620', 'Data reconciliation', 'REDUNDANT'],
        ['MLTestDataDownload.jsx', '600', 'ML test data export', 'ADMIN'],
        ['WeeklyAnalysis.jsx', '584', 'Weekly analysis view', 'CORE'],
        ['DataExportDownload.jsx', '576', '97-field export', 'ADMIN'],
        ['AIAlgoTradeHits.jsx', '564', 'Landing page', 'REDUNDANT'],
        ['AIAlgoTradeHitsReal.jsx', '542', 'Alternate landing', 'REDUNDANT'],
    ]

    t = Table(components_data, colWidths=[1.8*inch, 0.5*inch, 2*inch, 0.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Note: Components marked REDUNDANT should be reviewed for removal.", body_style))

    story.append(PageBreak())

    # ============================================
    # 6. BACKEND API STRUCTURE
    # ============================================
    story.append(Paragraph("6. Backend API Structure", h1_style))

    story.append(Paragraph("6.1 API Endpoint Categories", h2_style))

    api_categories = """
    <b>Market Data Endpoints (30+):</b><br/>
    - /api/twelvedata/{asset_type}/{timeframe} - Generic TwelveData<br/>
    - /api/stocks/history, /api/stocks/hourly, /api/stocks/5min<br/>
    - /api/crypto/daily, /api/crypto/hourly, /api/crypto/5min<br/>
    - /api/forex/history, /api/forex/hourly<br/>
    - /api/etfs/history, /api/etfs/hourly<br/>
    - /api/indices/history, /api/indices/hourly<br/>
    - /api/commodities/history, /api/commodities/hourly<br/><br/>

    <b>Analysis Endpoints (15+):</b><br/>
    - /api/analysis/stocks/weekly - Weekly stock analysis<br/>
    - /api/analysis/cryptos/weekly - Weekly crypto analysis<br/>
    - /api/analysis/nlp-search - NLP natural language search<br/>
    - /api/analysis/active-list - Active trading list<br/><br/>

    <b>ML/AI Endpoints (10+):</b><br/>
    - /api/nested/signals - Nested multi-TF signals<br/>
    - /api/nested/alignment - Timeframe alignment<br/>
    - /api/nested/performance - Model performance<br/>
    - /api/nested/features - Feature importance<br/>
    - /api/walk-forward/* - Walk-forward validation<br/><br/>

    <b>Admin Endpoints (10+):</b><br/>
    - /api/admin/scheduler-status - Scheduler monitoring<br/>
    - /api/admin/trigger-scheduler - Manual trigger<br/>
    - /api/admin/table-counts - BigQuery stats<br/>
    - /api/users - User management CRUD<br/><br/>

    <b>Auth Endpoints (4):</b><br/>
    - /api/auth/login - User login<br/>
    - /api/auth/verify - Token verification<br/>
    - /api/auth/change-password - Password change<br/>
    - /health - Health check<br/>
    """
    story.append(Paragraph(api_categories, body_style))

    story.append(PageBreak())

    # ============================================
    # 7. CLOUD FUNCTIONS INVENTORY
    # ============================================
    story.append(Paragraph("7. Cloud Functions Inventory", h1_style))

    story.append(Paragraph("7.1 Active Cloud Functions (33 Total)", h2_style))

    functions_data = [
        ['Function Name', 'Purpose', 'Trigger', 'Status'],
        ['bulletproof-fetcher', 'Primary data fetcher (all APIs)', 'HTTP/Scheduler', 'PRIMARY'],
        ['twelvedata-fetcher', 'TwelveData backup fetcher', 'HTTP/Scheduler', 'BACKUP'],
        ['gap-detector', 'Data gap detection & fill', 'Scheduler', 'ACTIVE'],
        ['data-deduplication', 'Remove duplicate records', 'Scheduler', 'ACTIVE'],
        ['ml-daily-analysis', 'ML feature calculation', 'Scheduler', 'ACTIVE'],
        ['ml-daily-inference', 'ML predictions', 'Scheduler', 'ACTIVE'],
        ['walk-forward-validation', 'ML validation system', 'HTTP', 'ACTIVE'],
        ['etf-analytics-fetcher', 'ETF data collection', 'Scheduler', 'ACTIVE'],
        ['market-movers-fetcher', 'Top gainers/losers', 'Scheduler', 'ACTIVE'],
        ['opportunity-report-generator', 'Daily reports', 'Scheduler', 'ACTIVE'],
        ['smart-search', 'NLP search engine', 'HTTP', 'ACTIVE'],
        ['pdf-report-generator', 'PDF generation', 'HTTP', 'ACTIVE'],
    ]

    t = Table(functions_data, colWidths=[1.8*inch, 2*inch, 1*inch, 0.7*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("7.2 Redundant Functions (Candidates for Removal)", h2_style))

    redundant_functions = [
        ['Function', 'Reason', 'Recommendation'],
        ['cloud_function_5min', 'Replaced by bulletproof-fetcher', 'REMOVE'],
        ['cloud_function_daily', 'Replaced by bulletproof-fetcher', 'REMOVE'],
        ['cloud_function_hourly', 'Replaced by bulletproof-fetcher', 'REMOVE'],
        ['cloud_function_stocks_daily', 'Duplicate of bulletproof', 'REMOVE'],
        ['cloud_function_stocks_hourly', 'Duplicate of bulletproof', 'REMOVE'],
        ['cloud_function_stocks_5min', 'Duplicate of bulletproof', 'REMOVE'],
        ['cloud_function_daily_stocks', 'Duplicate functionality', 'REMOVE'],
        ['cloud_function_max_quota', 'Replaced by bulletproof', 'REMOVE'],
        ['cloud_function_all_assets', 'Merged into bulletproof', 'REMOVE'],
        ['cloud_function_multi_source', 'Merged into bulletproof', 'REMOVE'],
    ]

    t = Table(redundant_functions, colWidths=[2*inch, 2*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffbeb')]),
    ]))
    story.append(t)

    story.append(PageBreak())

    # ============================================
    # 8. DATABASE SCHEMA
    # ============================================
    story.append(Paragraph("8. Database Schema (BigQuery)", h1_style))

    story.append(Paragraph("8.1 Dataset Structure", h2_style))

    db_text = """
    <b>Project:</b> aialgotradehits<br/>
    <b>Primary Dataset:</b> crypto_trading_data<br/>
    <b>ML Dataset:</b> ml_models<br/>
    <b>Total Tables:</b> 113<br/>
    <b>Total Records:</b> 1.2B+<br/><br/>

    <b>Core Tables (Clean Schema):</b><br/>
    - stocks_daily_clean (4M+ records) - Daily stocks<br/>
    - stocks_hourly_clean - Hourly stocks<br/>
    - stocks_5min_clean - 5-minute stocks<br/>
    - crypto_daily_clean (2.7M records) - Daily crypto<br/>
    - crypto_hourly_clean - Hourly crypto<br/>
    - crypto_5min_clean - 5-minute crypto<br/>
    - etfs_daily_clean - ETF daily<br/>
    - forex_daily_clean - Forex daily<br/>
    - indices_daily_clean - Indices daily<br/>
    - commodities_daily_clean - Commodities daily<br/><br/>

    <b>Supplemental Tables:</b><br/>
    - fred_economic_data (247K records) - Economic indicators<br/>
    - cmc_crypto_rankings (2.6K records) - CMC rankings<br/>
    - finnhub_recommendations (1.3K records) - Analyst ratings<br/>
    - kraken_buy_sell_volume - Buy/sell pressure<br/><br/>

    <b>ML Tables:</b><br/>
    - nested_daily, nested_hourly, nested_5min - Feature tables<br/>
    - nested_alignment_final - Alignment features<br/>
    - nested_predictor_v1 - XGBoost model<br/>
    - v_nested_signals_final - Prediction view<br/>
    """
    story.append(Paragraph(db_text, body_style))

    story.append(PageBreak())

    # ============================================
    # 9. REDUNDANCY ANALYSIS
    # ============================================
    story.append(Paragraph("9. Redundancy Analysis", h1_style))

    story.append(Paragraph("9.1 Redundant Frontend Components", h2_style))

    redundant_components = [
        ['Component', 'Lines', 'Reason', 'Action'],
        ['EnhancedDashboard.jsx', '821', 'Superseded by SmartDashboard', 'DELETE'],
        ['NLPSearch.jsx', '628', 'Integrated into SmartDashboard', 'DELETE'],
        ['WeeklyReconciliation.jsx', '620', 'Not used in routing', 'DELETE'],
        ['DataReconciliation.jsx', '384', 'Commented out in App.jsx', 'DELETE'],
        ['AIAlgoTradeHits.jsx', '564', 'Duplicate landing page', 'DELETE'],
        ['AIAlgoTradeHitsReal.jsx', '542', 'Duplicate landing page', 'DELETE'],
        ['AdminPanel.jsx', '453', 'Superseded by AdminPanelEnhanced', 'DELETE'],
        ['StockPriceWindow.jsx', '143', 'Legacy component', 'DELETE'],
        ['SchedulerMonitoring.jsx', '506', 'Moved to Admin panel', 'REVIEW'],
        ['DatabaseMonitoring.jsx', '539', 'Duplicate of TableInventory', 'REVIEW'],
        ['BillingDashboard.jsx', '367', 'Not implemented', 'DELETE'],
        ['DataDownloadControl.jsx', '406', 'Superseded by DataExportDownload', 'DELETE'],
        ['AdvancedTradingChart.jsx', '17', 'Empty wrapper', 'DELETE'],
    ]

    t = Table(redundant_components, colWidths=[1.8*inch, 0.5*inch, 2*inch, 0.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("<b>Estimated Lines to Remove:</b> 5,373 lines (18% reduction)", body_style))

    story.append(Paragraph("9.2 Redundant Python Scripts (Root Directory)", h2_style))

    story.append(Paragraph("""
    The root directory contains 349 Python scripts. Many are one-time migration/setup scripts that should be archived:
    <br/><br/>
    <b>Categories for Cleanup:</b><br/>
    - backfill_*.py (15 files) - Historical data migration<br/>
    - create_*.py (40 files) - Table/schema creation<br/>
    - migrate_*.py (18 files) - Data migration<br/>
    - check_*.py (15 files) - Validation scripts<br/>
    - fix_*.py (12 files) - Bug fix scripts<br/>
    - convert_*.py (7 files) - Document conversion<br/>
    - generate_*.py (10 files) - Report generation<br/>
    - setup_*.py (12 files) - Initial setup<br/><br/>

    <b>Recommendation:</b> Move to /archive folder, keep only active utility scripts.
    """, body_style))

    story.append(PageBreak())

    # ============================================
    # 10. NLP DEVELOPMENT ROADMAP
    # ============================================
    story.append(Paragraph("10. NLP Development Roadmap", h1_style))

    story.append(Paragraph("10.1 Current NLP Capabilities", h2_style))

    nlp_current = """
    <b>Implemented Features:</b><br/>
    - Basic keyword search across all asset types<br/>
    - Filter parsing (oversold, overbought, high volume)<br/>
    - Asset type detection (stocks, crypto, forex, etc.)<br/>
    - Timeframe extraction (daily, weekly, hourly)<br/>
    - Voice search via Web Speech API<br/><br/>

    <b>Search Engine Location:</b> cloud_function_api/nlp_query_engine.py<br/>
    <b>Integration:</b> /api/analysis/nlp-search endpoint<br/>
    """
    story.append(Paragraph(nlp_current, body_style))

    story.append(Paragraph("10.2 NLP Enhancement Roadmap", h2_style))

    nlp_roadmap = [
        ['Phase', 'Feature', 'Description', 'Timeline'],
        ['1', 'Intent Classification', 'Detect user intent (search, analyze, compare)', 'Q1'],
        ['1', 'Entity Extraction', 'Extract symbols, amounts, dates', 'Q1'],
        ['2', 'Conversational Memory', 'Remember context across queries', 'Q2'],
        ['2', 'Gemini 3 Integration', 'LLM-powered understanding', 'Q2'],
        ['3', 'Strategy Generation', 'Generate trading strategies from NLP', 'Q3'],
        ['3', 'Code-Free Customization', 'Build dashboards via NLP', 'Q3'],
        ['4', 'Autonomous Agents', 'Self-executing trade analysis', 'Q4'],
        ['4', 'Voice Commands', 'Full voice-controlled trading', 'Q4'],
    ]

    t = Table(nlp_roadmap, colWidths=[0.5*inch, 1.5*inch, 2.5*inch, 0.7*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f3ff')]),
    ]))
    story.append(t)

    story.append(Paragraph("10.3 Target: Zero-Code Administration", h2_style))

    zero_code = """
    <b>Vision:</b> All system administration via natural language<br/><br/>

    <b>Example Commands:</b><br/>
    - "Show me oversold tech stocks with rising volume"<br/>
    - "Create an alert when AAPL crosses above $250"<br/>
    - "Backtest RSI strategy on crypto for last 6 months"<br/>
    - "Generate weekly report for my portfolio"<br/>
    - "Add new data source for options data"<br/>
    - "Deploy new ML model for sector rotation"<br/><br/>

    <b>Implementation:</b><br/>
    - Gemini 3 Pro for intent understanding<br/>
    - Function calling for action execution<br/>
    - BigQuery integration for data queries<br/>
    - Vertex AI for ML operations<br/>
    """
    story.append(Paragraph(zero_code, body_style))

    story.append(PageBreak())

    # ============================================
    # 11. ENVIRONMENT CONFIGURATION
    # ============================================
    story.append(Paragraph("11. Environment Configuration", h1_style))

    story.append(Paragraph("11.1 Current Environment Variables", h2_style))

    env_vars = """
    <b>Frontend (.env files):</b><br/>
    - VITE_API_BASE_URL - API endpoint URL<br/>
    - VITE_GOOGLE_CLIENT_ID - OAuth client ID<br/><br/>

    <b>Backend (Secret Manager):</b><br/>
    - TWELVEDATA_API_KEY - TwelveData API<br/>
    - FRED_API_KEY - FRED economic data<br/>
    - CMC_API_KEY - CoinMarketCap API<br/>
    - FINNHUB_API_KEY - Finnhub API<br/>
    - KRAKEN_API_KEY - Kraken API<br/>
    - GCP_PROJECT_ID - Google Cloud project<br/>
    - BIGQUERY_DATASET - Dataset name<br/><br/>

    <b>Recommendation:</b> Centralize all configuration into a single config service
    that can be modified via admin panel without code changes.
    """
    story.append(Paragraph(env_vars, body_style))

    story.append(Paragraph("11.2 Proposed Config Architecture", h2_style))

    config_arch = """
    <b>Config Service Design:</b><br/><br/>
    1. Create BigQuery table: system_configuration<br/>
    2. Admin UI for config management<br/>
    3. API endpoint: /api/admin/config<br/>
    4. Real-time config updates without deploy<br/>
    5. Feature flags for gradual rollouts<br/>
    6. Environment-specific overrides (dev/staging/prod)<br/><br/>

    <b>Config Categories:</b><br/>
    - api_keys: External API credentials<br/>
    - feature_flags: Enable/disable features<br/>
    - rate_limits: API throttling settings<br/>
    - ml_params: Model hyperparameters<br/>
    - ui_settings: Dashboard customization<br/>
    - alerts: Alert thresholds and rules<br/>
    """
    story.append(Paragraph(config_arch, body_style))

    story.append(PageBreak())

    # ============================================
    # 12. REFACTORING RECOMMENDATIONS
    # ============================================
    story.append(Paragraph("12. Refactoring Recommendations", h1_style))

    story.append(Paragraph("12.1 Immediate Actions (High Priority)", h2_style))

    immediate = """
    <b>1. Remove Redundant Components (5,373 lines)</b><br/>
    - Delete 13 unused components identified in Section 9.1<br/>
    - Update imports in App.jsx<br/>
    - Test all routes after removal<br/><br/>

    <b>2. Consolidate Cloud Functions</b><br/>
    - Keep only bulletproof-fetcher as primary<br/>
    - Archive 10 redundant functions<br/>
    - Update scheduler configurations<br/><br/>

    <b>3. Archive Root Python Scripts</b><br/>
    - Move 150+ one-time scripts to /archive<br/>
    - Keep only active utilities<br/>
    - Document what each script does<br/><br/>

    <b>4. Clean Deploy Folders</b><br/>
    - Remove deploy-temp/, deploy-clean/, etc.<br/>
    - Keep only dist/ for production builds<br/>
    """
    story.append(Paragraph(immediate, body_style))

    story.append(Paragraph("12.2 Short-Term Improvements (1-2 Months)", h2_style))

    short_term = """
    <b>1. Component Library</b><br/>
    - Extract common UI patterns into shared components<br/>
    - Create consistent button, card, table styles<br/>
    - Implement proper TypeScript types<br/><br/>

    <b>2. State Management</b><br/>
    - Implement React Context for global state<br/>
    - Add Zustand or Redux for complex state<br/>
    - Cache API responses properly<br/><br/>

    <b>3. API Layer Cleanup</b><br/>
    - Consolidate duplicate endpoints<br/>
    - Add proper error handling<br/>
    - Implement request caching<br/><br/>

    <b>4. Testing Infrastructure</b><br/>
    - Add Jest + React Testing Library<br/>
    - Write tests for critical paths<br/>
    - Set up CI/CD pipeline<br/>
    """
    story.append(Paragraph(short_term, body_style))

    story.append(Paragraph("12.3 Long-Term Vision (3-6 Months)", h2_style))

    long_term = """
    <b>1. Full NLP Integration</b><br/>
    - Gemini 3 Pro integration<br/>
    - Conversational interface<br/>
    - Code-free administration<br/><br/>

    <b>2. Real-Time Features</b><br/>
    - WebSocket for live data<br/>
    - Push notifications<br/>
    - Live trading integration<br/><br/>

    <b>3. Mobile App</b><br/>
    - React Native port<br/>
    - Native charts<br/>
    - Biometric auth<br/><br/>

    <b>4. Enterprise Features</b><br/>
    - Multi-tenant support<br/>
    - Role-based access<br/>
    - Audit logging<br/>
    - White-label capability<br/>
    """
    story.append(Paragraph(long_term, body_style))

    # Build PDF
    doc.build(story)
    print(f"PDF created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_architecture_pdf()
