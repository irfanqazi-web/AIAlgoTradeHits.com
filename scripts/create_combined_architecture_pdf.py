"""
Create Combined Architecture & Refactoring Plan PDF
Merges AIAlgoTradeHits architecture with Saleem's EI Platform clean architecture
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def create_combined_architecture_pdf():
    """Generate comprehensive combined architecture PDF"""

    filename = "C:/1AITrading/Trading/AIALGOTRADEHITS_REFACTORING_MASTERPLAN.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24,
                                  spaceAfter=20, textColor=colors.HexColor('#1e3a5f'))

    heading1_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=16,
                                     spaceBefore=20, spaceAfter=12,
                                     textColor=colors.HexColor('#2563eb'))

    heading2_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=13,
                                     spaceBefore=15, spaceAfter=8,
                                     textColor=colors.HexColor('#059669'))

    heading3_style = ParagraphStyle('Heading3', parent=styles['Heading3'], fontSize=11,
                                     spaceBefore=10, spaceAfter=6,
                                     textColor=colors.HexColor('#7c3aed'))

    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10,
                                 spaceAfter=8, alignment=TA_JUSTIFY, leading=14)

    code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=8,
                                 spaceAfter=6, backColor=colors.HexColor('#f1f5f9'),
                                 leftIndent=10, rightIndent=10)

    quote_style = ParagraphStyle('Quote', parent=styles['Normal'], fontSize=10,
                                  spaceAfter=8, leftIndent=20, rightIndent=20,
                                  textColor=colors.HexColor('#4b5563'),
                                  fontName='Helvetica-Oblique')

    story = []

    # ==================== TITLE PAGE ====================
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("AIAlgoTradeHits.com", title_style))
    story.append(Paragraph("Architecture Refactoring Masterplan",
                          ParagraphStyle('Subtitle', parent=styles['Title'], fontSize=18,
                                        textColor=colors.HexColor('#059669'))))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Combined Architecture Document & Reengineering Strategy", body_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(f"<b>Document Version:</b> 3.0", body_style))
    story.append(Paragraph(f"<b>Platform Version:</b> 2.0.0 (Current) -> 3.0.0 (Target)", body_style))
    story.append(Paragraph(f"<b>Created:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Paragraph("<b>Status:</b> Refactoring Required | Architecture Redesign", body_style))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<b>Reference Documents:</b>", body_style))
    story.append(Paragraph("1. AIAlgoTradeHits Architecture Document (January 2026)", body_style))
    story.append(Paragraph("2. Economic Intelligence Platform File Architecture v2.0 (Saleem Ahmad)", body_style))
    story.append(Paragraph("3. masterquery.md v4.0 - Trading System Specifications", body_style))

    story.append(PageBreak())

    # ==================== EXECUTIVE SUMMARY ====================
    story.append(Paragraph("Executive Summary", heading1_style))

    story.append(Paragraph("""
    This document presents a comprehensive refactoring plan for AIAlgoTradeHits.com, combining insights from
    two architectural approaches: the current React/Vite-based trading platform and Saleem Ahmad's clean
    architecture principles from the Economic Intelligence Platform. The goal is to transform AIAlgoTradeHits
    into a state-of-the-art fintech application with enterprise-grade architecture.
    """, body_style))

    story.append(Paragraph("Key Transformation Goals:", heading3_style))

    goals = [
        ["Single Source of Truth (SSOT)", "All configuration centralized in one location"],
        ["Layer Cake Architecture", "Config -> Engine -> Service -> API -> UI separation"],
        ["TypeScript Migration", "Full type safety across the codebase"],
        ["Feature-Based Organization", "Components grouped by feature, not type"],
        ["NLP-Driven Operations", "Eliminate need for external programming"],
        ["Redundancy Elimination", "Remove 13 redundant components (5,373 lines)"],
    ]

    goals_table = Table(goals, colWidths=[2.5*inch, 4*inch])
    goals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2563eb')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(goals_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(PageBreak())

    # ==================== SECTION 1: ARCHITECTURE COMPARISON ====================
    story.append(Paragraph("1. Architecture Comparison", heading1_style))

    story.append(Paragraph("1.1 Technology Stack Comparison", heading2_style))

    tech_comparison = [
        ["Layer", "AIAlgoTradeHits (Current)", "EI Platform (Target)", "Migration"],
        ["Framework", "React 18 + Vite", "Next.js 14 App Router", "Major"],
        ["Language", "JavaScript (JSX)", "TypeScript (TSX)", "Required"],
        ["Styling", "Inline Styles + CSS", "Tailwind CSS 3.x", "Recommended"],
        ["Database", "Google BigQuery", "BigQuery + Supabase", "Optional"],
        ["Charts", "Lightweight Charts", "Recharts 2.x", "Keep Current"],
        ["AI", "Gemini + XGBoost", "Claude API", "Keep Gemini"],
        ["Deployment", "GCP Cloud Run", "Vercel", "Keep GCP"],
        ["State", "React useState", "Context + Hooks", "Enhance"],
    ]

    tech_table = Table(tech_comparison, colWidths=[1.2*inch, 1.8*inch, 1.8*inch, 1.2*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("1.2 Architecture Philosophy Comparison", heading2_style))

    philosophy_comparison = [
        ["Principle", "AIAlgoTradeHits", "EI Platform", "Gap Analysis"],
        ["Config Location", "Scattered in components", "lib/config/macro-config.ts", "CRITICAL GAP"],
        ["Calculation Logic", "Mixed in components", "Pure engines (no I/O)", "CRITICAL GAP"],
        ["Data Flow", "Bidirectional", "Unidirectional down only", "MAJOR GAP"],
        ["Import Paths", "Relative (../../../)", "Absolute (@/)", "MODERATE GAP"],
        ["Component Org", "Flat (42 files)", "Feature-based folders", "MAJOR GAP"],
        ["Type Safety", "None (JavaScript)", "Full TypeScript", "MAJOR GAP"],
        ["API Structure", "Single service file", "Route-based handlers", "MODERATE GAP"],
    ]

    philosophy_table = Table(philosophy_comparison, colWidths=[1.3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    philosophy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (3, 1), (3, 2), colors.HexColor('#fee2e2')),  # Critical gaps
        ('BACKGROUND', (3, 3), (3, 5), colors.HexColor('#fef3c7')),  # Major gaps
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(philosophy_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("1.3 The Layer Cake Architecture (Target)", heading2_style))

    story.append(Paragraph("""
    The EI Platform uses a strict layered architecture where data flows DOWN only.
    This prevents circular dependencies and makes the system testable and maintainable.
    """, body_style))

    layer_data = [
        ["Layer", "Purpose", "AIAlgoTradeHits Equivalent", "Required Changes"],
        ["USER INTERFACE", "Pages & Components", "src/components/*.jsx", "Reorganize by feature"],
        ["API ROUTES", "Request Handlers", "cloud_function_api/", "Add frontend API layer"],
        ["SERVICE LAYER", "Orchestration & Logic", "src/services/api.js", "Split into services"],
        ["ENGINE LAYER", "Pure Calculations", "MISSING", "CREATE NEW"],
        ["CONFIG LAYER", "SSOT Configuration", "MISSING", "CREATE NEW"],
        ["DATA LAYER", "BigQuery, APIs", "BigQuery + 5 APIs", "Keep, add abstraction"],
    ]

    layer_table = Table(layer_data, colWidths=[1.3*inch, 1.4*inch, 1.6*inch, 1.5*inch])
    layer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
        ('BACKGROUND', (2, 4), (2, 5), colors.HexColor('#fee2e2')),  # Missing layers
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(layer_table)

    story.append(PageBreak())

    # ==================== SECTION 2: CURRENT STATE ANALYSIS ====================
    story.append(Paragraph("2. Current State Analysis", heading1_style))

    story.append(Paragraph("2.1 AIAlgoTradeHits Current File Structure", heading2_style))

    story.append(Paragraph("""
    The current AIAlgoTradeHits platform has grown organically, resulting in a flat component structure
    with 42 React components, scattered configuration, and mixed concerns within components.
    """, body_style))

    current_structure = """
    stock-price-app/
    ├── src/
    │   ├── components/           # FLAT: 42 components in one folder
    │   │   ├── TradingDashboard.jsx (1,847 lines) - Main dashboard
    │   │   ├── AdminPanelEnhanced.jsx (687 lines) - Admin functions
    │   │   ├── ProfessionalChart.jsx (612 lines) - Chart component
    │   │   ├── SmartDashboard.jsx (580 lines) - AI dashboard
    │   │   ├── ... (38 more components)
    │   │   └── Navigation.jsx (740 lines) - Side navigation
    │   │
    │   ├── services/
    │   │   ├── api.js (2,100+ lines) - ALL API calls in ONE file
    │   │   ├── marketData.js - Market data service
    │   │   ├── aiService.js - AI service calls
    │   │   └── monitoringService.js - Monitoring
    │   │
    │   ├── App.jsx - Main app with ALL routes (25+)
    │   ├── App.css - Global styles
    │   └── main.jsx - Entry point
    │
    └── public/ - Static assets
    """
    story.append(Paragraph(current_structure.replace('\n', '<br/>'), code_style))

    story.append(Paragraph("2.2 Identified Redundant Components", heading2_style))

    redundant_components = [
        ["Component", "Lines", "Reason for Redundancy", "Action"],
        ["EnhancedDashboard.jsx", "821", "Superseded by SmartDashboard", "DELETE"],
        ["NLPSearch.jsx", "628", "Integrated into SmartDashboard", "DELETE"],
        ["WeeklyReconciliation.jsx", "620", "Not used in routing", "DELETE"],
        ["AIAlgoTradeHits.jsx", "564", "Duplicate landing page", "DELETE"],
        ["AIAlgoTradeHitsReal.jsx", "542", "Duplicate landing page", "DELETE"],
        ["AdminPanel.jsx", "453", "Superseded by AdminPanelEnhanced", "DELETE"],
        ["DataDownloadControl.jsx", "398", "Merged into DataExportDownload", "DELETE"],
        ["AdvancedChart.jsx", "380", "Replaced by ProfessionalChart", "DELETE"],
        ["WeeklyAnalysis.jsx", "367", "Merged into WeeklyDashboard", "DELETE"],
        ["DataDownloadWizard.jsx", "352", "Duplicate of DataExportDownload", "DELETE"],
        ["AdvancedTradingChart.jsx", "318", "Replaced by TradingViewChart", "DELETE"],
        ["MultiPanelChart.jsx", "280", "Not actively used", "REVIEW"],
        ["FundamentalsView.jsx", "250", "Incomplete implementation", "REVIEW"],
        ["TOTAL", "5,373", "Lines to eliminate", "-"],
    ]

    redundant_table = Table(redundant_components, colWidths=[2*inch, 0.8*inch, 2.2*inch, 0.8*inch])
    redundant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fecaca')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
    ]))
    story.append(redundant_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("2.3 Redundant Cloud Functions", heading2_style))

    redundant_functions = [
        ["Function Folder", "Status", "Replaced By"],
        ["cloud_function_5min/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_daily/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_hourly/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_stocks_5min/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_stocks_daily/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_stocks_hourly/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_weekly_cryptos/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_weekly_stocks/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_max_quota/", "Redundant", "bulletproof-fetcher"],
        ["cloud_function_multi_source/", "Redundant", "bulletproof-fetcher"],
    ]

    func_table = Table(redundant_functions, colWidths=[2.5*inch, 1.2*inch, 2*inch])
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffbeb')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(func_table)

    story.append(PageBreak())

    # ==================== SECTION 3: TARGET ARCHITECTURE ====================
    story.append(Paragraph("3. Target Architecture Design", heading1_style))

    story.append(Paragraph("3.1 New Directory Structure (Following EI Platform Pattern)", heading2_style))

    target_structure = """
    stock-price-app/
    │
    ├── src/
    │   ├── lib/                              # CORE LOGIC LAYER
    │   │   ├── config/                       # CONFIGURATION (SSOT)
    │   │   │   ├── trading-config.ts         # Master config - indicators, thresholds
    │   │   │   ├── scoring-config.ts         # Growth score, sentiment rules
    │   │   │   ├── api-config.ts             # API endpoints, rate limits
    │   │   │   └── ui-config.ts              # Theme, colors, chart settings
    │   │   │
    │   │   ├── engines/                      # CALCULATION ENGINES (Pure functions)
    │   │   │   ├── indicator-engine.ts       # Technical indicator calculations
    │   │   │   ├── signal-engine.ts          # Buy/Sell/Hold signal generation
    │   │   │   ├── growth-score-engine.ts    # Growth score calculations
    │   │   │   └── nested-ml-engine.ts       # ML prediction logic
    │   │   │
    │   │   ├── services/                     # SERVICE ORCHESTRATION
    │   │   │   ├── market-data-service.ts    # TwelveData integration
    │   │   │   ├── trading-signal-service.ts # Signal orchestration
    │   │   │   ├── ai-prediction-service.ts  # ML/AI predictions
    │   │   │   ├── nlp-query-service.ts      # Natural language queries
    │   │   │   └── data-export-service.ts    # Data download service
    │   │   │
    │   │   ├── hooks/                        # REACT HOOKS
    │   │   │   ├── useMarketData.ts          # Market data hook
    │   │   │   ├── useTradingSignals.ts      # Signals hook
    │   │   │   ├── useMLPredictions.ts       # ML predictions hook
    │   │   │   └── useNLPQuery.ts            # NLP query hook
    │   │   │
    │   │   └── utils/                        # UTILITIES
    │   │       ├── formatters.ts             # Number/date formatting
    │   │       ├── validators.ts             # Input validation
    │   │       └── transforms.ts             # Data transformations
    │   │
    │   ├── components/                       # UI COMPONENT LAYER
    │   │   ├── dashboard/                    # Dashboard-specific
    │   │   │   ├── TradingDashboard.tsx
    │   │   │   ├── SmartDashboard.tsx
    │   │   │   └── StatCards.tsx
    │   │   │
    │   │   ├── charts/                       # Chart components
    │   │   │   ├── ProfessionalChart.tsx
    │   │   │   ├── VolumeChart.tsx
    │   │   │   └── IndicatorOverlay.tsx
    │   │   │
    │   │   ├── signals/                      # Signal components
    │   │   │   ├── NestedSignals.tsx
    │   │   │   ├── AITradeSignals.tsx
    │   │   │   └── SignalCard.tsx
    │   │   │
    │   │   ├── admin/                        # Admin components
    │   │   │   ├── AdminPanelEnhanced.tsx
    │   │   │   ├── SchedulerMonitoring.tsx
    │   │   │   └── DatabaseMonitoring.tsx
    │   │   │
    │   │   ├── shared/                       # Reusable across pages
    │   │   │   ├── Navigation.tsx
    │   │   │   ├── SearchBar.tsx
    │   │   │   └── LoadingSpinner.tsx
    │   │   │
    │   │   └── ui/                           # Base UI primitives
    │   │       ├── Button.tsx
    │   │       ├── Card.tsx
    │   │       └── Badge.tsx
    │   │
    │   ├── pages/                            # PAGE COMPONENTS
    │   │   ├── Dashboard.tsx
    │   │   ├── Signals.tsx
    │   │   ├── Admin.tsx
    │   │   └── Settings.tsx
    │   │
    │   ├── types/                            # TYPE DEFINITIONS
    │   │   ├── trading.ts                    # Trading types
    │   │   ├── api.ts                        # API response types
    │   │   └── index.ts                      # Re-exports
    │   │
    │   ├── App.tsx                           # Main app (simplified routing)
    │   └── main.tsx                          # Entry point
    │
    ├── tailwind.config.ts                    # Tailwind configuration
    ├── tsconfig.json                         # TypeScript configuration
    └── vite.config.ts                        # Vite configuration
    """

    story.append(Paragraph(target_structure.replace('\n', '<br/>').replace('  ', '&nbsp;&nbsp;'), code_style))

    story.append(PageBreak())

    # ==================== SECTION 4: CONFIG LAYER DESIGN ====================
    story.append(Paragraph("4. Config Layer Design (SSOT)", heading1_style))

    story.append(Paragraph('"One config to rule them all" - All business logic configuration in one place', quote_style))

    story.append(Paragraph("4.1 Master Trading Config (trading-config.ts)", heading2_style))

    config_example = """
    // src/lib/config/trading-config.ts

    export const LOGIC_VERSION = "3.0.0";

    // INDICATOR THRESHOLDS (from masterquery.md v4.0)
    export const INDICATOR_THRESHOLDS = {
      RSI: { oversold: 30, overbought: 70, sweet_spot: [50, 70] },
      MACD: { signal_cross: 0, histogram_threshold: 0 },
      ADX: { weak: 20, strong: 25, very_strong: 40 },
      VOLUME: { surge_multiplier: 1.5 },
    };

    // GROWTH SCORE CALCULATION (0-100)
    export const GROWTH_SCORE_RULES = {
      rsi_sweet_spot: 25,      // RSI 50-70 = 25 points
      macd_positive: 25,        // MACD histogram > 0 = 25 points
      strong_trend: 25,         // ADX > 25 = 25 points
      above_sma200: 25,         // Close > SMA200 = 25 points
    };

    // TREND REGIME CLASSIFICATION
    export const TREND_REGIMES = {
      STRONG_UPTREND: { sma_condition: 'above_both', adx_min: 25 },
      WEAK_UPTREND: { sma_condition: 'above_50_200' },
      STRONG_DOWNTREND: { sma_condition: 'below_both', adx_min: 25 },
      WEAK_DOWNTREND: { sma_condition: 'below_50_200' },
      CONSOLIDATION: { default: true },
    };

    // EMA CYCLE DETECTION
    export const EMA_CYCLES = {
      rise_cycle: { condition: 'ema12 > ema26' },
      fall_cycle: { condition: 'ema12 < ema26' },
    };

    // NESTED ML SIGNAL THRESHOLDS
    export const NESTED_SIGNAL_THRESHOLDS = {
      ULTRA_BUY: { aligned_pct: 60, min_scores: [5, 6, 5] },
      STRONG_BUY: { aligned_pct: 50, min_scores: [4, 5, 4] },
      BUY: { daily_hourly_aligned: true, min_scores: [4, 4] },
      WEAK_BUY: { daily_bullish: true, min_score: 4 },
      HOLD: { default: true },
    };

    // API RATE LIMITS
    export const API_LIMITS = {
      TWELVEDATA: { calls_per_min: 800, outputsize: 5000 },
      KRAKEN: { calls_per_min: 60 },
      FRED: { calls_per_day: 100 },
      FINNHUB: { calls_per_min: 60 },
      COINMARKETCAP: { calls_per_day: 333 },
    };
    """

    story.append(Paragraph(config_example.replace('\n', '<br/>').replace('  ', '&nbsp;&nbsp;'), code_style))

    story.append(Paragraph("4.2 Config Files Summary", heading2_style))

    config_files = [
        ["Config File", "Purpose", "Contents"],
        ["trading-config.ts", "Master config (SSOT)", "Indicators, thresholds, regimes, ML params"],
        ["scoring-config.ts", "Scoring rules", "Growth score, sentiment, signal logic"],
        ["api-config.ts", "API configuration", "Endpoints, rate limits, keys reference"],
        ["ui-config.ts", "UI constants", "Colors, chart sizes, theme settings"],
    ]

    config_table = Table(config_files, colWidths=[1.5*inch, 1.8*inch, 2.5*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eff6ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(config_table)

    story.append(PageBreak())

    # ==================== SECTION 5: ENGINE LAYER DESIGN ====================
    story.append(Paragraph("5. Engine Layer Design (Pure Logic)", heading1_style))

    story.append(Paragraph('"No side effects, no I/O, just math" - Engines are pure functions', quote_style))

    story.append(Paragraph("5.1 Engine Design Principles", heading2_style))

    story.append(Paragraph("""
    Engines contain all calculation logic but never make API calls, access databases, or have side effects.
    They take inputs and return outputs - making them fully testable and reusable.
    """, body_style))

    engine_example = """
    // src/lib/engines/growth-score-engine.ts

    import { GROWTH_SCORE_RULES, INDICATOR_THRESHOLDS } from '@/lib/config/trading-config';

    interface IndicatorData {
      rsi_14: number;
      macd_histogram: number;
      adx: number;
      close: number;
      sma_200: number;
    }

    /**
     * Calculate Growth Score (0-100) - PURE FUNCTION
     * No API calls, no database access, just calculations
     */
    export function calculateGrowthScore(data: IndicatorData): number {
      let score = 0;

      // RSI sweet spot (50-70)
      const [low, high] = INDICATOR_THRESHOLDS.RSI.sweet_spot;
      if (data.rsi_14 >= low && data.rsi_14 <= high) {
        score += GROWTH_SCORE_RULES.rsi_sweet_spot;
      }

      // MACD histogram positive
      if (data.macd_histogram > 0) {
        score += GROWTH_SCORE_RULES.macd_positive;
      }

      // Strong trend (ADX > 25)
      if (data.adx > INDICATOR_THRESHOLDS.ADX.strong) {
        score += GROWTH_SCORE_RULES.strong_trend;
      }

      // Above SMA200
      if (data.close > data.sma_200) {
        score += GROWTH_SCORE_RULES.above_sma200;
      }

      return score;
    }

    /**
     * Classify Trend Regime - PURE FUNCTION
     */
    export function classifyTrendRegime(
      close: number,
      sma50: number,
      sma200: number,
      adx: number
    ): string {
      if (close > sma50 && sma50 > sma200 && adx > 25) return 'STRONG_UPTREND';
      if (close > sma50 && close > sma200) return 'WEAK_UPTREND';
      if (close < sma50 && sma50 < sma200 && adx > 25) return 'STRONG_DOWNTREND';
      if (close < sma50 && close < sma200) return 'WEAK_DOWNTREND';
      return 'CONSOLIDATION';
    }
    """

    story.append(Paragraph(engine_example.replace('\n', '<br/>').replace('  ', '&nbsp;&nbsp;'), code_style))

    story.append(Paragraph("5.2 Engine Files Summary", heading2_style))

    engine_files = [
        ["Engine", "Purpose", "Key Functions"],
        ["indicator-engine.ts", "Technical indicators", "calculateRSI, calculateMACD, calculateEMA"],
        ["signal-engine.ts", "Trade signals", "generateSignal, classifyAction, getRecommendation"],
        ["growth-score-engine.ts", "Growth scoring", "calculateGrowthScore, classifyTrendRegime"],
        ["nested-ml-engine.ts", "ML predictions", "calculateNestedSignal, predictDirection"],
        ["sentiment-engine.ts", "Sentiment analysis", "calculateSentiment, analyzeNews"],
    ]

    engine_table = Table(engine_files, colWidths=[1.5*inch, 1.5*inch, 2.8*inch])
    engine_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(engine_table)

    story.append(PageBreak())

    # ==================== SECTION 6: REFACTORING PHASES ====================
    story.append(Paragraph("6. Refactoring Implementation Phases", heading1_style))

    story.append(Paragraph("6.1 Phase Overview", heading2_style))

    phases = [
        ["Phase", "Focus Area", "Effort", "Risk", "Priority"],
        ["Phase 1", "Config Layer (SSOT)", "Medium", "Low", "CRITICAL"],
        ["Phase 2", "Engine Layer", "High", "Medium", "HIGH"],
        ["Phase 3", "TypeScript Migration", "High", "Medium", "HIGH"],
        ["Phase 4", "Component Reorganization", "Medium", "Low", "MEDIUM"],
        ["Phase 5", "Redundancy Cleanup", "Low", "Low", "MEDIUM"],
        ["Phase 6", "NLP Enhancement", "High", "Medium", "HIGH"],
        ["Phase 7", "Testing & Validation", "Medium", "Low", "HIGH"],
    ]

    phases_table = Table(phases, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1*inch])
    phases_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (4, 1), (4, 1), colors.HexColor('#fee2e2')),  # Critical
        ('BACKGROUND', (4, 2), (4, 4), colors.HexColor('#fef3c7')),  # High
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(phases_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("6.2 Phase 1: Config Layer (SSOT)", heading2_style))

    phase1_tasks = [
        "Create src/lib/config/ directory structure",
        "Extract all hardcoded thresholds from components into trading-config.ts",
        "Move indicator calculations to scoring-config.ts",
        "Centralize API endpoints and limits in api-config.ts",
        "Extract UI constants (colors, sizes) to ui-config.ts",
        "Update all components to import from config files",
        "Add LOGIC_VERSION for cache invalidation",
    ]

    story.append(Paragraph("<b>Tasks:</b>", body_style))
    for i, task in enumerate(phase1_tasks, 1):
        story.append(Paragraph(f"{i}. {task}", body_style))

    story.append(Paragraph("6.3 Phase 2: Engine Layer", heading2_style))

    phase2_tasks = [
        "Create src/lib/engines/ directory",
        "Extract calculateGrowthScore from TradingDashboard.jsx",
        "Extract signal generation logic from AITradeSignals.jsx",
        "Create indicator-engine.ts with pure calculation functions",
        "Create nested-ml-engine.ts for ML prediction logic",
        "Ensure all engines have NO I/O operations",
        "Add comprehensive unit tests for each engine",
    ]

    story.append(Paragraph("<b>Tasks:</b>", body_style))
    for i, task in enumerate(phase2_tasks, 1):
        story.append(Paragraph(f"{i}. {task}", body_style))

    story.append(Paragraph("6.4 Phase 3: TypeScript Migration", heading2_style))

    phase3_tasks = [
        "Configure TypeScript in vite.config.ts",
        "Create src/types/ directory with type definitions",
        "Define Trading, API, and UI types",
        "Migrate config files to TypeScript first",
        "Migrate engine files to TypeScript",
        "Migrate service files to TypeScript",
        "Migrate components (starting with shared/)",
        "Update import statements to use absolute paths (@/)",
    ]

    story.append(Paragraph("<b>Tasks:</b>", body_style))
    for i, task in enumerate(phase3_tasks, 1):
        story.append(Paragraph(f"{i}. {task}", body_style))

    story.append(PageBreak())

    story.append(Paragraph("6.5 Phase 4: Component Reorganization", heading2_style))

    component_mapping = [
        ["Current Location", "Target Location", "Components"],
        ["components/*.jsx", "components/dashboard/", "TradingDashboard, SmartDashboard, StatCards"],
        ["components/*.jsx", "components/charts/", "ProfessionalChart, TradingViewChart"],
        ["components/*.jsx", "components/signals/", "NestedSignals, AITradeSignals, AIPredictions"],
        ["components/*.jsx", "components/admin/", "AdminPanelEnhanced, SchedulerMonitoring"],
        ["components/*.jsx", "components/shared/", "Navigation, SmartSearchBar, Login"],
        ["components/*.jsx", "components/data/", "DataExportDownload, MLTestDataDownload"],
    ]

    mapping_table = Table(component_mapping, colWidths=[1.8*inch, 1.8*inch, 2.4*inch])
    mapping_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(mapping_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("6.6 Phase 5: Redundancy Cleanup", heading2_style))

    story.append(Paragraph("""
    Delete the 13 redundant components identified in Section 2.2. This will eliminate 5,373 lines of
    duplicate code and simplify maintenance. Archive files before deletion for reference.
    """, body_style))

    story.append(Paragraph("6.7 Phase 6: NLP Enhancement", heading2_style))

    nlp_features = [
        ["Feature", "Description", "Implementation"],
        ["Text-to-SQL", "Natural language to BigQuery", "Gemini Pro + SQL templates"],
        ["Voice Search", "Spoken queries to actions", "Web Speech API + NLP"],
        ["Smart Autocomplete", "Context-aware suggestions", "History + ML predictions"],
        ["Natural Commands", "\"Show AAPL daily chart\"", "Intent classification + routing"],
        ["Report Generation", "\"Generate weekly report\"", "Template + AI summarization"],
    ]

    nlp_table = Table(nlp_features, colWidths=[1.5*inch, 2*inch, 2.3*inch])
    nlp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecfeff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(nlp_table)

    story.append(PageBreak())

    # ==================== SECTION 7: SITE MAP ====================
    story.append(Paragraph("7. Refactored Site Map", heading1_style))

    story.append(Paragraph("7.1 Core Navigation Structure", heading2_style))

    sitemap = [
        ["Route", "Component", "Description", "Status"],
        ["/", "Dashboard", "Main trading dashboard with overview", "Keep"],
        ["/dashboard", "TradingDashboard", "Detailed trading view", "Keep"],
        ["/signals", "NestedSignals", "Multi-timeframe ML signals", "NEW"],
        ["/ai-signals", "AITradeSignals", "AI-generated trade signals", "Keep"],
        ["/ai-predictions", "AIPredictions", "ML prediction display", "Keep"],
        ["/charts/:symbol", "ProfessionalChart", "Symbol-specific chart", "Keep"],
        ["/admin", "AdminPanelEnhanced", "Administration panel", "Keep"],
        ["/scheduler", "SchedulerMonitoring", "Job scheduler monitor", "Keep"],
        ["/database", "DatabaseMonitoring", "Database status monitor", "Keep"],
        ["/data-export", "DataExportDownload", "Data download wizard", "Keep"],
        ["/settings", "Settings", "User preferences", "NEW"],
        ["/login", "Login", "Authentication", "Keep"],
    ]

    sitemap_table = Table(sitemap, colWidths=[1.2*inch, 1.8*inch, 2.2*inch, 0.8*inch])
    sitemap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (3, 3), (3, 3), colors.HexColor('#dcfce7')),
        ('BACKGROUND', (3, 11), (3, 11), colors.HexColor('#dcfce7')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
    ]))
    story.append(sitemap_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("7.2 Routes to Remove", heading2_style))

    remove_routes = [
        ["/enhanced-dashboard", "Merged into /dashboard"],
        ["/nlp-search", "Integrated into SmartSearchBar"],
        ["/weekly-reconciliation", "Not actively used"],
        ["/landing", "Duplicate - use /"],
        ["/data-wizard", "Merged into /data-export"],
    ]

    remove_table = Table([["Route", "Reason"]] + remove_routes, colWidths=[2*inch, 4*inch])
    remove_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(remove_table)

    story.append(PageBreak())

    # ==================== SECTION 8: ML INTEGRATION ====================
    story.append(Paragraph("8. ML Model Integration Architecture", heading1_style))

    story.append(Paragraph("8.1 Nested Multi-Timeframe Model", heading2_style))

    story.append(Paragraph("""
    The Nested Multi-Timeframe ML Model (66.2% UP accuracy) requires proper integration into
    the refactored architecture. This section outlines how to structure the ML components.
    """, body_style))

    ml_integration = [
        ["Component", "Location", "Purpose"],
        ["Model Config", "lib/config/trading-config.ts", "ML thresholds, signal definitions"],
        ["Prediction Engine", "lib/engines/nested-ml-engine.ts", "Pure prediction calculations"],
        ["ML Service", "lib/services/ai-prediction-service.ts", "BigQuery ML orchestration"],
        ["ML Hook", "lib/hooks/useMLPredictions.ts", "React integration"],
        ["Signals Component", "components/signals/NestedSignals.tsx", "UI display"],
    ]

    ml_table = Table(ml_integration, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    ml_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ml_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("8.2 Feature Importance (from ML Model)", heading2_style))

    features = [
        ["Feature", "Importance", "Layer"],
        ["fivemin_price_up_pct", "0.0665", "5-Min (Most Predictive)"],
        ["fivemin_ema_pct", "0.0373", "5-Min"],
        ["avg_5min_score", "0.0355", "5-Min"],
        ["fivemin_macd_pct", "0.0275", "5-Min"],
        ["max_5min_score", "0.0134", "5-Min"],
        ["daily_score", "0.0030", "Daily"],
    ]

    features_table = Table(features, colWidths=[2*inch, 1.2*inch, 2.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(features_table)

    story.append(PageBreak())

    # ==================== SECTION 9: API INTEGRATION ====================
    story.append(Paragraph("9. API Integration Architecture", heading1_style))

    story.append(Paragraph("9.1 Data Sources (5 APIs)", heading2_style))

    api_sources = [
        ["API", "Purpose", "Rate Limit", "Daily Quota"],
        ["TwelveData ($229)", "OHLCV + Indicators", "800/min", "2M records"],
        ["Kraken", "Buy/Sell Volume", "60/min", "Unlimited"],
        ["FRED", "Economic Indicators", "100/day", "100 calls"],
        ["CoinMarketCap", "Crypto Rankings", "333/day", "10K credits"],
        ["Finnhub", "Analyst Ratings", "60/min", "60 calls"],
    ]

    api_table = Table(api_sources, colWidths=[1.5*inch, 1.8*inch, 1.2*inch, 1.2*inch])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eff6ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("9.2 Backend API Endpoints", heading2_style))

    endpoints = [
        ["Endpoint", "Method", "Purpose"],
        ["/api/market-data/:symbol", "GET", "OHLCV data with indicators"],
        ["/api/ai/trading-signals", "GET", "AI-generated signals"],
        ["/api/ai/rise-cycle-candidates", "GET", "EMA crossover detection"],
        ["/api/ai/ml-predictions", "GET", "Growth score predictions"],
        ["/api/ai/nested-signals", "GET", "Multi-timeframe signals"],
        ["/api/ai/nested-summary", "GET", "Nested model summary"],
        ["/api/ai/text-to-sql", "POST", "Natural language queries"],
        ["/api/data/download", "GET", "Data export endpoint"],
        ["/api/admin/schedulers", "GET", "Scheduler status"],
        ["/api/admin/tables", "GET", "BigQuery table info"],
    ]

    endpoints_table = Table(endpoints, colWidths=[2.2*inch, 0.8*inch, 2.8*inch])
    endpoints_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(endpoints_table)

    story.append(PageBreak())

    # ==================== SECTION 10: QUICK REFERENCE ====================
    story.append(Paragraph("10. Quick Reference Card", heading1_style))

    quick_ref = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                      REFACTORING QUICK REFERENCE                      ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║                                                                      ║
    ║  CONFIGURATION (SSOT)                                                ║
    ║  ─────────────────────                                               ║
    ║  Master Config:    @/lib/config/trading-config.ts                    ║
    ║  Scoring Rules:    @/lib/config/scoring-config.ts                    ║
    ║  API Config:       @/lib/config/api-config.ts                        ║
    ║  UI Config:        @/lib/config/ui-config.ts                         ║
    ║                                                                      ║
    ║  CALCULATION ENGINES                                                 ║
    ║  ─────────────────────                                               ║
    ║  Indicators:       @/lib/engines/indicator-engine.ts                 ║
    ║  Signals:          @/lib/engines/signal-engine.ts                    ║
    ║  Growth Score:     @/lib/engines/growth-score-engine.ts              ║
    ║  ML Predictions:   @/lib/engines/nested-ml-engine.ts                 ║
    ║                                                                      ║
    ║  SERVICES                                                            ║
    ║  ─────────────────────                                               ║
    ║  Market Data:      @/lib/services/market-data-service.ts             ║
    ║  Trading Signals:  @/lib/services/trading-signal-service.ts          ║
    ║  AI Predictions:   @/lib/services/ai-prediction-service.ts           ║
    ║  NLP Queries:      @/lib/services/nlp-query-service.ts               ║
    ║                                                                      ║
    ║  COMPONENTS                                                          ║
    ║  ─────────────────────                                               ║
    ║  Dashboard:        @/components/dashboard/                           ║
    ║  Charts:           @/components/charts/                              ║
    ║  Signals:          @/components/signals/                             ║
    ║  Admin:            @/components/admin/                               ║
    ║  Shared:           @/components/shared/                              ║
    ║                                                                      ║
    ║  KEY METRICS                                                         ║
    ║  ─────────────────────                                               ║
    ║  ML Accuracy:      66.2% UP | 70.6% DOWN | 68.4% Overall             ║
    ║  ROC AUC:          0.777                                             ║
    ║  API Budget:       $229/month (TwelveData)                           ║
    ║  Components:       42 -> 29 (after cleanup)                          ║
    ║  Lines Removed:    5,373 (redundant code)                            ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """

    story.append(Paragraph(quick_ref.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(PageBreak())

    # ==================== SECTION 11: CONCLUSION ====================
    story.append(Paragraph("11. Conclusion & Next Steps", heading1_style))

    story.append(Paragraph("""
    This refactoring plan combines the best practices from Saleem Ahmad's Economic Intelligence Platform
    clean architecture with the specific requirements of AIAlgoTradeHits.com trading platform. The
    transformation will result in a maintainable, testable, and scalable fintech application.
    """, body_style))

    story.append(Paragraph("11.1 Immediate Actions", heading2_style))

    actions = [
        "1. Create lib/config/ directory and migrate hardcoded values",
        "2. Create lib/engines/ with pure calculation functions",
        "3. Configure TypeScript and create type definitions",
        "4. Delete 13 redundant components (5,373 lines)",
        "5. Reorganize components into feature-based folders",
        "6. Update import statements to use @/ absolute paths",
        "7. Add comprehensive tests for engine functions",
    ]

    for action in actions:
        story.append(Paragraph(action, body_style))

    story.append(Paragraph("11.2 Success Criteria", heading2_style))

    criteria = [
        ["Metric", "Current", "Target"],
        ["TypeScript Coverage", "0%", "100%"],
        ["Config Centralization", "Scattered", "SSOT"],
        ["Component Organization", "Flat (42)", "Feature-based (29)"],
        ["Engine Test Coverage", "0%", "80%+"],
        ["Redundant Code", "5,373 lines", "0 lines"],
        ["Build Time", "~30s", "<15s"],
    ]

    criteria_table = Table(criteria, colWidths=[2*inch, 2*inch, 2*inch])
    criteria_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(criteria_table)

    story.append(Spacer(1, 0.5*inch))

    # Document footer
    story.append(Paragraph("─" * 80, body_style))
    story.append(Paragraph("<i>AIAlgoTradeHits.com Architecture Refactoring Masterplan</i>",
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
                                        textColor=colors.gray, alignment=TA_CENTER)))
    story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</i>",
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
                                        textColor=colors.gray, alignment=TA_CENTER)))
    story.append(Paragraph("<i>Reference: EI Platform Architecture v2.0 + masterquery.md v4.0</i>",
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
                                        textColor=colors.gray, alignment=TA_CENTER)))

    # Build PDF
    doc.build(story)
    print(f"PDF created successfully: {filename}")
    return filename

if __name__ == "__main__":
    create_combined_architecture_pdf()
