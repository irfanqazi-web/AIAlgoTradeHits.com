"""
Convert Walk-Forward Gap Analysis to PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def create_walk_forward_pdf():
    """Create the walk-forward gap analysis PDF"""

    filename = "WALK_FORWARD_GAP_ANALYSIS_AND_PLAN.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4a5568')
    )

    heading1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#2c5282')
    )

    heading2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#2d3748')
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=14
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4,
        leading=12
    )

    story = []

    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("ML Walk-Forward Validation System", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Gap Analysis & Implementation Plan", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Date: January 9, 2026", subtitle_style))
    story.append(Paragraph("Document Version: 1.0", subtitle_style))
    story.append(Paragraph("Status: PENDING IRFAN APPROVAL", subtitle_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Platform: AIAlgoTradeHits.com", subtitle_style))
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", heading1_style))
    story.append(Paragraph(
        "This document analyzes the ML Walk-Forward Validation System specification against "
        "current implementation, identifies gaps, and proposes an implementation plan.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))

    summary_data = [
        ['Metric', 'Value'],
        ['Current State', '~60% Complete'],
        ['Estimated Remaining Effort', '20-30 hours'],
        ['Monthly Cost Increase', '~$20-30'],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))

    # Part 1: Already Implemented
    story.append(Paragraph("PART 1: WHAT'S ALREADY IMPLEMENTED", heading1_style))

    implemented_data = [
        ['#', 'Component', 'Status', 'Notes'],
        ['1', 'XGBoost Model Training', 'DONE', 'Using BigQuery ML'],
        ['2', 'Walk-Forward 3-Period Split', 'DONE', 'Train/Test/Validate'],
        ['3', 'Prediction Storage', 'DONE', 'walk_forward_predictions_v2'],
        ['4', 'Sector-Specific Models', 'DONE', '86.4% avg accuracy (5 sectors)'],
        ['5', 'Model Drift Detection', 'DONE', 'ml_phase5_model_monitoring.py'],
        ['6', 'Real-time Inference', 'DONE', 'ml_phase6_realtime_inference.py'],
        ['7', 'Backtesting Framework', 'DONE', 'ml_phase7_backtesting_framework.py'],
        ['8', 'Basic ML API Endpoints', 'DONE', '/api/ml/predictions, etc.'],
        ['9', 'Cloud Schedulers', 'DONE', 'Daily inference, monitoring'],
        ['10', 'Sector Classification', 'DONE', '346 stocks, 11 sectors'],
        ['11', 'Sentiment Integration', 'DONE', '12,155 records'],
    ]

    impl_table = Table(implemented_data, colWidths=[0.4*inch, 1.8*inch, 0.7*inch, 2.5*inch])
    impl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ae6b4')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(impl_table)
    story.append(PageBreak())

    # Part 2: Missing Components
    story.append(Paragraph("PART 2: MISSING COMPONENTS (GAPS)", heading1_style))

    gaps_data = [
        ['#', 'Component', 'Priority', 'Effort', 'Description'],
        ['1', 'Interactive Dashboard UI', 'P0', '12-16 hrs', 'React component for config & results'],
        ['2', 'Walk-Forward Cloud Function', 'P0', '8-10 hrs', 'Dedicated function with progress'],
        ['3', 'The 16 Validated Features', 'P0', '2 hrs', 'Verify/add specific features'],
        ['4', 'Walk-Forward API Endpoints', 'P0', '4-6 hrs', 'Full CRUD for runs'],
        ['5', 'model_versions Table', 'P1', '1 hr', 'Track all model versions'],
        ['6', 'walk_forward_runs Table', 'P1', '1 hr', 'Run-level summaries'],
        ['7', 'Confidence Threshold Filters', 'P1', '2 hrs', '50%, 60%, 70%, 80% filtering'],
        ['8', 'Rolling Accuracy Charts', 'P1', '3 hrs', '30-day rolling accuracy viz'],
        ['9', 'Multi-Ticker Support', 'P2', '3 hrs', '1-5 tickers per run'],
        ['10', 'CSV Export', 'P2', '1 hr', 'Export results'],
        ['11', 'Progress Tracking', 'P2', '2 hrs', 'Real-time progress updates'],
        ['12', 'Cancellation Support', 'P3', '1 hr', 'Cancel long runs'],
        ['13', 'A/B Testing Framework', 'P3', '4 hrs', 'Compare feature sets'],
        ['14', 'Model Artifact Storage', 'P3', '2 hrs', 'Store .pkl in GCS'],
    ]

    gaps_table = Table(gaps_data, colWidths=[0.4*inch, 1.8*inch, 0.6*inch, 0.8*inch, 2*inch])
    gaps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e53e3e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#feb2b2')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))
    story.append(gaps_table)
    story.append(Spacer(1, 0.3*inch))

    # Gap Details
    story.append(Paragraph("DETAILED GAP ANALYSIS", heading1_style))

    story.append(Paragraph("Gap 1: Interactive Dashboard UI (P0)", heading2_style))
    story.append(Paragraph("Current State: No dedicated walk-forward UI component exists in Trading App", body_style))
    story.append(Paragraph("Required:", body_style))
    story.append(Paragraph("- Configuration panel with asset class, ticker selection, date ranges", bullet_style))
    story.append(Paragraph("- Feature selection toggle (16 default vs 97 advanced)", bullet_style))
    story.append(Paragraph("- Validation window and retraining frequency options", bullet_style))
    story.append(Paragraph("- Results display: summary cards, equity curve, rolling accuracy", bullet_style))
    story.append(Paragraph("- Run controls: RUN button, progress indicator, cancel button", bullet_style))
    story.append(Paragraph("Files to Create:", body_style))
    story.append(Paragraph("- WalkForwardValidation.jsx, WalkForwardResults.jsx, WalkForwardCharts.jsx", bullet_style))

    story.append(Paragraph("Gap 2: Walk-Forward Cloud Function (P0)", heading2_style))
    story.append(Paragraph("Current State: Basic backtesting exists, but not the full walk-forward engine", body_style))
    story.append(Paragraph("Required:", body_style))
    story.append(Paragraph("- Day-by-day prediction loop with configurable retraining", bullet_style))
    story.append(Paragraph("- Progress tracking in BigQuery", bullet_style))
    story.append(Paragraph("- Support for 500-day runs with batch result insertion", bullet_style))
    story.append(Paragraph("Files to Create: cloud_function_walk_forward/main.py", bullet_style))

    story.append(Paragraph("Gap 3: The 16 Validated Features (P0)", heading2_style))
    story.append(Paragraph("Current State: Using different feature set (rsi, macd, adx, etc.)", body_style))
    story.append(Paragraph("Specified 16 Features:", body_style))
    features_text = ("pivot_low_flag, pivot_high_flag, rsi, rsi_slope, rsi_zscore, rsi_overbought, "
                     "rsi_oversold, macd, macd_signal, macd_histogram, macd_cross, momentum, mfi, cci, "
                     "awesome_osc, vwap_daily")
    story.append(Paragraph(features_text, bullet_style))

    story.append(PageBreak())

    # Part 3: Implementation Plan
    story.append(Paragraph("PART 3: IMPLEMENTATION PLAN", heading1_style))

    story.append(Paragraph("Phase 1: Core Backend (Week 1)", heading2_style))
    phase1_data = [
        ['Task', 'Hours'],
        ['Create walk_forward_runs table', '0.5'],
        ['Create model_versions table', '0.5'],
        ['Verify 16 validated features', '1'],
        ['Create walk-forward Cloud Function', '8'],
        ['Add API endpoints to Trading API', '4'],
        ['Subtotal', '14 hrs'],
    ]
    phase1_table = Table(phase1_data, colWidths=[4*inch, 1.5*inch])
    phase1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(phase1_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Phase 2: Dashboard UI (Week 2)", heading2_style))
    phase2_data = [
        ['Task', 'Hours'],
        ['WalkForwardValidation.jsx (config)', '6'],
        ['WalkForwardResults.jsx (results)', '4'],
        ['WalkForwardCharts.jsx (charts)', '4'],
        ['Integration testing', '2'],
        ['Subtotal', '16 hrs'],
    ]
    phase2_table = Table(phase2_data, colWidths=[4*inch, 1.5*inch])
    phase2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(phase2_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Phase 3: Advanced Features (Week 3)", heading2_style))
    phase3_data = [
        ['Task', 'Hours'],
        ['Confidence threshold filtering', '2'],
        ['Rolling accuracy calculation', '2'],
        ['CSV export', '1'],
        ['Progress tracking', '2'],
        ['Multi-ticker support', '3'],
        ['Subtotal', '10 hrs'],
    ]
    phase3_table = Table(phase3_data, colWidths=[4*inch, 1.5*inch])
    phase3_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(phase3_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Phase 4: Testing & Deployment (Week 4)", heading2_style))
    phase4_data = [
        ['Task', 'Hours'],
        ['End-to-end testing', '4'],
        ['500-day validation runs', '2'],
        ['Bug fixes', '4'],
        ['Documentation', '2'],
        ['Subtotal', '12 hrs'],
    ]
    phase4_table = Table(phase4_data, colWidths=[4*inch, 1.5*inch])
    phase4_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(phase4_table)
    story.append(PageBreak())

    # Part 4: Questions for Irfan
    story.append(Paragraph("PART 4: QUESTIONS FOR IRFAN", heading1_style))

    story.append(Paragraph("Q1: Cloud Infrastructure", heading2_style))
    story.append(Paragraph("Options:", body_style))
    story.append(Paragraph("A) Cloud Function Gen2 (60-min timeout) - Good for runs up to 200 days", bullet_style))
    story.append(Paragraph("B) Cloud Run Jobs (24-hour timeout) - Required for 500-day runs", bullet_style))
    story.append(Paragraph("Recommendation: Cloud Run Jobs for flexibility", body_style))

    story.append(Paragraph("Q2: Model Storage Bucket", heading2_style))
    story.append(Paragraph("Suggested: gs://aialgotradehits-ml-models/", body_style))

    story.append(Paragraph("Q3: Priority Order", heading2_style))
    story.append(Paragraph("Should we implement in this order?", body_style))
    story.append(Paragraph("1. Core Backend (Cloud Function + API)", bullet_style))
    story.append(Paragraph("2. Dashboard UI", bullet_style))
    story.append(Paragraph("3. Advanced Features", bullet_style))

    story.append(Paragraph("Q4: Multi-Ticker Mode", heading2_style))
    story.append(Paragraph("Options:", body_style))
    story.append(Paragraph("A) Individual mode only (train separate model per ticker)", bullet_style))
    story.append(Paragraph("B) Combined mode only (single model for all tickers)", bullet_style))
    story.append(Paragraph("C) Both modes (user selects)", bullet_style))
    story.append(Paragraph("Recommendation: Start with Individual mode, add Combined later", body_style))
    story.append(Spacer(1, 0.3*inch))

    # Part 5: Cost Estimates
    story.append(Paragraph("PART 5: COST ESTIMATES", heading1_style))

    story.append(Paragraph("Development Cost (One-Time)", heading2_style))
    dev_cost_data = [
        ['Item', 'Hours', 'Cost'],
        ['Backend Development', '14', '$0 (Claude)'],
        ['UI Development', '16', '$0 (Claude)'],
        ['Advanced Features', '10', '$0 (Claude)'],
        ['Testing', '12', '$0 (Claude)'],
        ['Total Development', '52 hrs', '$0'],
    ]
    dev_table = Table(dev_cost_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    dev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(dev_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Infrastructure Cost (Monthly Incremental)", heading2_style))
    infra_cost_data = [
        ['Resource', 'Usage', 'Cost/Month'],
        ['Cloud Run Jobs', '~50 runs @ 30 min', '$15-25'],
        ['BigQuery Storage', '~5 GB new tables', '$0.10'],
        ['BigQuery Queries', '~200 GB scanned', '$1.00'],
        ['Cloud Storage', '~500 MB models', '$0.01'],
        ['Total Monthly', '', '~$20-30'],
    ]
    infra_table = Table(infra_cost_data, colWidths=[2*inch, 1.5*inch, 2*inch])
    infra_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(infra_table)
    story.append(PageBreak())

    # Part 6: Approval Section
    story.append(Paragraph("APPROVAL REQUIRED", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Please confirm the following:", body_style))
    story.append(Spacer(1, 0.1*inch))

    approval_items = [
        "[ ] Implementation priority order is correct",
        "[ ] Cloud Run Jobs for long-running validation",
        "[ ] Model storage bucket name: gs://aialgotradehits-ml-models/",
        "[ ] Start with Individual multi-ticker mode",
    ]
    for item in approval_items:
        story.append(Paragraph(item, bullet_style))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Once approved, implementation will begin immediately.", body_style))

    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("_" * 50, body_style))
    story.append(Paragraph("Signature: ______________________    Date: ____________", body_style))

    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Document prepared by: Claude (AI)", subtitle_style))
    story.append(Paragraph("For: Irfan Qazi", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))

    # Build PDF
    doc.build(story)
    print(f"\nPDF created successfully: {filename}")
    return filename

if __name__ == "__main__":
    create_walk_forward_pdf()
