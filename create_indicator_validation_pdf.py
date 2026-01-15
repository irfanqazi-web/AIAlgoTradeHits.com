"""
Create PDF Document: Financial Indicator Validation Analysis
For Saleem (SME) Review and Decision
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def create_indicator_validation_pdf():
    filename = "C:/1AITrading/Trading/INDICATOR_VALIDATION_ANALYSIS_FOR_SME_REVIEW.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=20, spaceAfter=20, textColor=colors.HexColor('#1a365d'))
    heading1_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=16, spaceBefore=20, spaceAfter=12, textColor=colors.HexColor('#2c5282'))
    heading2_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=13, spaceBefore=15, spaceAfter=8, textColor=colors.HexColor('#2b6cb0'))
    heading3_style = ParagraphStyle('Heading3', parent=styles['Heading3'], fontSize=11, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#3182ce'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_JUSTIFY)
    code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=9, backColor=colors.HexColor('#f7fafc'), leftIndent=20, rightIndent=20, spaceAfter=10)
    note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#718096'), leftIndent=20, spaceAfter=8, fontName='Helvetica-Oblique')
    option_title = ParagraphStyle('OptionTitle', parent=styles['Heading2'], fontSize=12, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#276749'), backColor=colors.HexColor('#f0fff4'))

    story = []

    # Title Page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("FINANCIAL INDICATOR", title_style))
    story.append(Paragraph("VALIDATION ANALYSIS", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Technical Analysis for SME Review", styles['Heading2']))
    story.append(Spacer(1, 0.5*inch))

    info_data = [
        ['Document Purpose:', 'SME Review and Decision on Indicator Implementation'],
        ['Prepared For:', 'Saleem Ahmad (Subject Matter Expert)'],
        ['Prepared By:', 'AI Trading System Development Team'],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Version:', '1.0'],
        ['Classification:', 'Internal - Technical Review'],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
    ]))
    story.append(info_table)
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("1. EXECUTIVE SUMMARY", heading1_style))
    story.append(Paragraph(
        "This document presents the validation analysis of 24 technical indicators implemented in our trading system. "
        "Saleem's validation testing revealed discrepancies between our calculated values and industry-standard benchmarks "
        "(pandas_ta library). This document explains the root causes and presents options for resolution.",
        body_style))
    story.append(Spacer(1, 0.2*inch))

    # Validation Results Summary
    summary_data = [
        ['Metric', 'Value', 'Status'],
        ['Total Indicators Tested', '24', ''],
        ['Indicators Passed', '11', 'PASS'],
        ['Indicators Failed', '13', 'REQUIRES REVIEW'],
        ['Success Rate', '45.8%', ''],
        ['Primary Root Cause', 'Smoothing Method Differences', ''],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (2, 2), (2, 2), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (2, 3), (2, 3), colors.HexColor('#fed7d7')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # Detailed Validation Results
    story.append(Paragraph("2. DETAILED VALIDATION RESULTS", heading1_style))
    story.append(Paragraph(
        "The following table shows each indicator's validation status, the maximum difference observed, "
        "and the identified root cause:",
        body_style))
    story.append(Spacer(1, 0.1*inch))

    indicator_data = [
        ['Indicator', 'Status', 'Max Diff', 'Root Cause'],
        ['RSI (14)', 'FAIL', '42%', 'SMA vs Wilder\'s RMA smoothing'],
        ['ADX (14)', 'FAIL', 'Large', 'Standard EMA vs Wilder\'s RMA'],
        ['+DI / -DI', 'FAIL', 'Large', 'Standard EMA vs Wilder\'s RMA'],
        ['ATR (14)', 'FAIL', 'Varies', 'SMA vs Wilder\'s RMA'],
        ['Stochastic %K', 'FAIL', 'Varies', 'Fast (raw) vs Slow (smoothed)'],
        ['Stochastic %D', 'FAIL', 'Varies', 'Upstream %K difference'],
        ['ROC', 'FAIL', 'Varies', 'Period 12 vs Test Period 10'],
        ['Ichimoku Senkou A', 'FAIL', 'Small', 'Missing 26-period forward shift'],
        ['Ichimoku Senkou B', 'FAIL', 'Small', 'Missing 26-period forward shift'],
        ['Bollinger Upper', 'FAIL', 'Small', 'Sample vs Population std'],
        ['Bollinger Lower', 'FAIL', 'Small', 'Sample vs Population std'],
        ['BB Width', 'FAIL', 'Small', 'Upstream band differences'],
        ['CCI', 'FAIL', 'Small', 'Mean deviation calculation'],
        ['SMA (20/50/200)', 'PASS', '<0.1%', 'Matches standard'],
        ['EMA (12/26/50)', 'PASS', '<0.1%', 'Matches standard'],
        ['MACD', 'PASS', '<0.1%', 'Matches standard'],
        ['MACD Signal', 'PASS', '<0.1%', 'Matches standard'],
        ['Bollinger Middle', 'PASS', '<0.1%', 'Uses SMA correctly'],
        ['Williams %R', 'PASS', '<0.1%', 'Matches standard'],
        ['Momentum', 'PASS', '<0.1%', 'Matches standard'],
        ['OBV', 'PASS', '<0.1%', 'Matches standard'],
        ['KAMA', 'PASS', '<0.1%', 'Matches standard'],
        ['TRIX', 'PASS', '<0.1%', 'Matches standard'],
    ]

    indicator_table = Table(indicator_data, colWidths=[1.8*inch, 0.8*inch, 0.8*inch, 2.8*inch])
    indicator_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        # Color FAIL rows
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 3), (1, 3), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 4), (1, 4), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 5), (1, 5), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 6), (1, 6), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 7), (1, 7), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 8), (1, 8), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 9), (1, 9), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 10), (1, 10), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 11), (1, 11), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 12), (1, 12), colors.HexColor('#fed7d7')),
        ('BACKGROUND', (1, 13), (1, 13), colors.HexColor('#fed7d7')),
        # Color PASS rows
        ('BACKGROUND', (1, 14), (1, 14), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 15), (1, 15), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 16), (1, 16), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 17), (1, 17), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 18), (1, 18), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 19), (1, 19), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 20), (1, 20), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 21), (1, 21), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 22), (1, 22), colors.HexColor('#c6f6d5')),
        ('BACKGROUND', (1, 23), (1, 23), colors.HexColor('#c6f6d5')),
    ]))
    story.append(indicator_table)
    story.append(PageBreak())

    # Root Cause Analysis
    story.append(Paragraph("3. ROOT CAUSE ANALYSIS", heading1_style))

    # 3.1 Wilder's Smoothing
    story.append(Paragraph("3.1 Wilder's Smoothing vs Simple Moving Average", heading2_style))
    story.append(Paragraph(
        "The primary cause of indicator discrepancies is the difference between Wilder's Smoothing (also called "
        "Relative Moving Average or RMA) and Simple Moving Average (SMA). J. Welles Wilder Jr., creator of RSI, ATR, "
        "and ADX, specified a particular smoothing method that gives more weight to recent values.",
        body_style))

    story.append(Paragraph("Our Current Implementation (SMA-based):", heading3_style))
    story.append(Paragraph(
        "gain = delta.where(delta > 0, 0).rolling(window=period).mean()<br/>"
        "loss = (-delta).where(delta < 0, 0).rolling(window=period).mean()",
        code_style))

    story.append(Paragraph("Industry Standard (Wilder's RMA):", heading3_style))
    story.append(Paragraph(
        "gain = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False).mean()<br/>"
        "loss = (-delta).where(delta < 0, 0).ewm(alpha=1/period, adjust=False).mean()",
        code_style))

    story.append(Paragraph("Key Differences:", heading3_style))
    wilder_diff = [
        ['Aspect', 'SMA (Our Current)', 'Wilder\'s RMA (Industry Standard)'],
        ['Formula', 'sum(values) / n', 'alpha * current + (1-alpha) * previous'],
        ['Alpha', 'N/A', '1/period (e.g., 1/14 for RSI)'],
        ['Weight Distribution', 'Equal weight to all values', 'Exponentially decaying weights'],
        ['Responsiveness', 'Slower to react', 'Faster to react to recent changes'],
        ['Used By', 'Some academic models', 'TradingView, Bloomberg, pandas_ta'],
    ]
    wilder_table = Table(wilder_diff, colWidths=[1.5*inch, 2.25*inch, 2.5*inch])
    wilder_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(wilder_table)
    story.append(Spacer(1, 0.15*inch))

    # 3.2 Stochastic Variants
    story.append(Paragraph("3.2 Stochastic Oscillator Variants", heading2_style))
    story.append(Paragraph(
        "There are multiple variants of the Stochastic Oscillator. Our implementation uses the 'Fast' variant, "
        "while most platforms default to the 'Slow' variant.",
        body_style))

    stoch_diff = [
        ['Variant', '%K Calculation', '%D Calculation', 'Used By'],
        ['Fast (Our Current)', 'Raw formula', 'SMA of raw %K', 'Some day traders'],
        ['Slow (Industry Std)', 'SMA(3) of raw %K', 'SMA(3) of smoothed %K', 'TradingView, Most platforms'],
        ['Full', 'SMA(n) of raw %K', 'SMA(m) of smoothed %K', 'Configurable platforms'],
    ]
    stoch_table = Table(stoch_diff, colWidths=[1.3*inch, 1.8*inch, 1.8*inch, 1.5*inch])
    stoch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(stoch_table)
    story.append(Spacer(1, 0.15*inch))

    # 3.3 Ichimoku Cloud
    story.append(Paragraph("3.3 Ichimoku Cloud Projection", heading2_style))
    story.append(Paragraph(
        "The Ichimoku Cloud's Senkou Span A and Senkou Span B lines are designed to be projected FORWARD in time "
        "by 26 periods. This creates the 'cloud' that shows future support/resistance levels. Our current "
        "implementation calculates these values at the current candle without the forward shift.",
        body_style))

    story.append(Paragraph("Our Current Implementation:", heading3_style))
    story.append(Paragraph(
        "senkou_a = (tenkan + kijun) / 2  # Calculated at current candle<br/>"
        "senkou_b = (high_52 + low_52) / 2  # Calculated at current candle",
        code_style))

    story.append(Paragraph("Industry Standard:", heading3_style))
    story.append(Paragraph(
        "senkou_a = ((tenkan + kijun) / 2).shift(26)  # Shifted 26 periods forward<br/>"
        "senkou_b = ((high_52 + low_52) / 2).shift(26)  # Shifted 26 periods forward",
        code_style))

    story.append(Paragraph(
        "Note: The shift creates a 'cloud' that projects into the future, helping traders anticipate "
        "support/resistance. Without the shift, the cloud loses its predictive value.",
        note_style))
    story.append(PageBreak())

    # 3.4 Other Differences
    story.append(Paragraph("3.4 Other Minor Differences", heading2_style))

    other_diff = [
        ['Indicator', 'Our Implementation', 'Industry Standard', 'Impact'],
        ['Bollinger Bands', 'ddof=1 (sample std)', 'ddof=0 (population std)', 'Very small (<0.5%)'],
        ['ROC', 'Period = 12', 'Often Period = 10', 'Test config mismatch'],
        ['CCI', 'Standard mean deviation', 'Some use median', 'Small difference'],
    ]
    other_table = Table(other_diff, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.3*inch])
    other_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(other_table)
    story.append(PageBreak())

    # Options Section
    story.append(Paragraph("4. OPTIONS FOR SME DECISION", heading1_style))
    story.append(Paragraph(
        "The following options are presented for Saleem's review and decision. Each option has different "
        "trade-offs in terms of industry compatibility, development effort, and flexibility.",
        body_style))
    story.append(Spacer(1, 0.2*inch))

    # Option A
    story.append(Paragraph("OPTION A: Match Industry Standards (RECOMMENDED)", option_title))
    story.append(Paragraph(
        "Update all indicator calculations to match industry-standard implementations used by TradingView, "
        "Bloomberg, and pandas_ta library.",
        body_style))

    option_a_changes = [
        ['Indicator', 'Change Required', 'Complexity'],
        ['RSI', 'Change from SMA to Wilder\'s RMA (ewm alpha=1/14)', 'Low'],
        ['ATR', 'Change from SMA to Wilder\'s RMA (ewm alpha=1/14)', 'Low'],
        ['ADX', 'Change smoothing to Wilder\'s RMA for all components', 'Medium'],
        ['+DI / -DI', 'Change smoothing to Wilder\'s RMA', 'Medium'],
        ['Stochastic', 'Add %K smoothing (SMA of 3) for Slow variant', 'Low'],
        ['Ichimoku', 'Add .shift(26) to Senkou A and B', 'Low'],
        ['Bollinger', 'Change ddof=1 to ddof=0 (optional)', 'Very Low'],
    ]
    option_a_table = Table(option_a_changes, colWidths=[1.5*inch, 3.5*inch, 1*inch])
    option_a_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#276749')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9ae6b4')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
    ]))
    story.append(option_a_table)
    story.append(Spacer(1, 0.1*inch))

    # Pros/Cons Option A
    story.append(Paragraph("<b>Pros:</b>", body_style))
    story.append(Paragraph("- Values will match TradingView charts exactly", body_style))
    story.append(Paragraph("- Industry-standard implementation increases credibility", body_style))
    story.append(Paragraph("- Users can cross-reference with other platforms", body_style))
    story.append(Paragraph("- pandas_ta validation will pass at >95%", body_style))
    story.append(Paragraph("<b>Cons:</b>", body_style))
    story.append(Paragraph("- Requires re-backfilling all historical data", body_style))
    story.append(Paragraph("- 2-3 days development and testing effort", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Option B
    story.append(Paragraph("OPTION B: Document as Custom Implementation", option_title))
    story.append(Paragraph(
        "Keep current implementation but document it as a 'custom' or 'modified' calculation method. "
        "This approach acknowledges the differences while explaining the rationale.",
        body_style))

    story.append(Paragraph("<b>Pros:</b>", body_style))
    story.append(Paragraph("- No code changes required", body_style))
    story.append(Paragraph("- No data re-backfill needed", body_style))
    story.append(Paragraph("- SMA-based RSI is valid (just different)", body_style))
    story.append(Paragraph("<b>Cons:</b>", body_style))
    story.append(Paragraph("- Values won't match TradingView or other platforms", body_style))
    story.append(Paragraph("- May confuse users expecting standard values", body_style))
    story.append(Paragraph("- Documentation overhead for explaining differences", body_style))
    story.append(Paragraph("- Cannot use standard trading strategies without adjustment", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Option C
    story.append(Paragraph("OPTION C: Add Configurable Parameters", option_title))
    story.append(Paragraph(
        "Implement both calculation methods and allow users to select which variant they prefer. "
        "Store both values or calculate on-demand based on user preference.",
        body_style))

    story.append(Paragraph("<b>Pros:</b>", body_style))
    story.append(Paragraph("- Maximum flexibility for users", body_style))
    story.append(Paragraph("- Can support multiple trading strategies", body_style))
    story.append(Paragraph("- Research-friendly (compare methods)", body_style))
    story.append(Paragraph("<b>Cons:</b>", body_style))
    story.append(Paragraph("- Most complex implementation", body_style))
    story.append(Paragraph("- Nearly doubles storage requirements if storing both", body_style))
    story.append(Paragraph("- UI complexity for user selection", body_style))
    story.append(Paragraph("- 1-2 weeks development effort", body_style))
    story.append(PageBreak())

    # Recommendation
    story.append(Paragraph("5. RECOMMENDATION", heading1_style))
    story.append(Paragraph(
        "Based on our analysis, we strongly recommend <b>OPTION A: Match Industry Standards</b> for the following reasons:",
        body_style))
    story.append(Spacer(1, 0.1*inch))

    reasons = [
        "1. <b>User Expectations:</b> Traders expect RSI 30 to mean oversold based on Wilder's original formula. "
        "Our SMA-based RSI produces values up to 42% different, which could lead to incorrect trading decisions.",

        "2. <b>Cross-Platform Compatibility:</b> Users will inevitably compare our charts to TradingView. "
        "Matching values builds trust and allows users to validate our platform.",

        "3. <b>AI/ML Training:</b> If training AI models on our data, non-standard indicators may produce "
        "models that don't generalize to real-world trading scenarios.",

        "4. <b>Industry Credibility:</b> A professional trading platform should implement standard calculations. "
        "Custom implementations require significant documentation and may raise questions.",

        "5. <b>Moderate Effort:</b> The changes are straightforward - primarily replacing .rolling().mean() with "
        ".ewm(alpha=1/period).mean() in key functions. Estimated 1-2 days coding + 1 day testing."
    ]

    for reason in reasons:
        story.append(Paragraph(reason, body_style))
        story.append(Spacer(1, 0.05*inch))

    story.append(PageBreak())

    # Implementation Plan
    story.append(Paragraph("6. IMPLEMENTATION PLAN (IF OPTION A APPROVED)", heading1_style))

    impl_steps = [
        ['Step', 'Task', 'Estimated Time'],
        ['1', 'Create indicator_calculations_v2.py with corrected formulas', '4 hours'],
        ['2', 'Unit test each indicator against pandas_ta library', '4 hours'],
        ['3', 'Update backfill scripts to use new calculation module', '2 hours'],
        ['4', 'Clear existing data and re-run backfill for all 106 stocks', '8-12 hours'],
        ['5', 'Re-run backfill for 50 crypto assets', '6-8 hours'],
        ['6', 'Validation testing with Saleem\'s validation script', '2 hours'],
        ['7', 'Deploy updated Cloud Functions', '2 hours'],
        ['', 'TOTAL ESTIMATED TIME', '28-34 hours'],
    ]
    impl_table = Table(impl_steps, colWidths=[0.6*inch, 4*inch, 1.5*inch])
    impl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(impl_table)
    story.append(Spacer(1, 0.3*inch))

    # Sign-off Section
    story.append(Paragraph("7. SME DECISION AND SIGN-OFF", heading1_style))
    story.append(Paragraph(
        "Please review the options above and indicate your decision:",
        body_style))
    story.append(Spacer(1, 0.2*inch))

    decision_data = [
        ['', 'Option A: Match Industry Standards (Recommended)'],
        ['', 'Option B: Document as Custom Implementation'],
        ['', 'Option C: Add Configurable Parameters'],
        ['', 'Other (please specify below)'],
    ]
    decision_table = Table(decision_data, colWidths=[0.5*inch, 5.5*inch])
    decision_table.setStyle(TableStyle([
        ('BOX', (0, 0), (0, 0), 1, colors.black),
        ('BOX', (0, 1), (0, 1), 1, colors.black),
        ('BOX', (0, 2), (0, 2), 1, colors.black),
        ('BOX', (0, 3), (0, 3), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(decision_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Additional Comments / Special Instructions:", body_style))
    story.append(Spacer(1, 0.1*inch))
    # Comment box
    comment_data = [['', '', '']]
    comment_table = Table(comment_data, colWidths=[6.5*inch], rowHeights=[1.5*inch])
    comment_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(comment_table)
    story.append(Spacer(1, 0.3*inch))

    # Signature
    sig_data = [
        ['SME Name:', '_' * 40, 'Date:', '_' * 20],
        ['Signature:', '_' * 40, '', ''],
    ]
    sig_table = Table(sig_data, colWidths=[1.2*inch, 2.5*inch, 0.8*inch, 1.8*inch])
    sig_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(sig_table)

    # Appendix
    story.append(PageBreak())
    story.append(Paragraph("APPENDIX A: WILDER'S SMOOTHING FORMULA", heading1_style))
    story.append(Paragraph(
        "For reference, here is the mathematical definition of Wilder's Smoothing (RMA):",
        body_style))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("Initial Value (first period):", heading3_style))
    story.append(Paragraph("RMA_1 = SMA(values, period)", code_style))

    story.append(Paragraph("Subsequent Values:", heading3_style))
    story.append(Paragraph(
        "RMA_n = (previous_RMA * (period - 1) + current_value) / period<br/><br/>"
        "Or equivalently using exponential weighting:<br/>"
        "RMA_n = alpha * current_value + (1 - alpha) * previous_RMA<br/>"
        "where alpha = 1/period",
        code_style))

    story.append(Paragraph(
        "This is equivalent to pandas: <b>ewm(alpha=1/period, adjust=False).mean()</b>",
        note_style))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("APPENDIX B: AFFECTED INDICATORS AND FORMULAS", heading1_style))

    formulas = [
        ['Indicator', 'Current Formula', 'Corrected Formula'],
        ['RSI', 'gain.rolling(14).mean()', 'gain.ewm(alpha=1/14, adjust=False).mean()'],
        ['ATR', 'tr.rolling(14).mean()', 'tr.ewm(alpha=1/14, adjust=False).mean()'],
        ['ADX Smoothing', 'EMA calculation', 'ewm(alpha=1/14, adjust=False)'],
        ['Stochastic %K', 'raw_k (no smoothing)', 'raw_k.rolling(3).mean()'],
        ['Senkou Span A', 'value (no shift)', 'value.shift(26)'],
        ['Senkou Span B', 'value (no shift)', 'value.shift(26)'],
    ]
    formula_table = Table(formulas, colWidths=[1.3*inch, 2.5*inch, 2.5*inch])
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(formula_table)

    # Build PDF
    doc.build(story)
    print(f"PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_indicator_validation_pdf()
