#!/usr/bin/env python3
"""Generate PDF report for TwelveData Capacity Analysis"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def create_capacity_pdf():
    doc = SimpleDocTemplate(
        "TWELVEDATA_CAPACITY_ANALYSIS.pdf",
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
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a237e')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#1565c0')
    )

    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#2e7d32')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=14
    )

    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        backColor=colors.HexColor('#fff3e0'),
        borderPadding=10,
        textColor=colors.HexColor('#e65100')
    )

    story = []

    # Title
    story.append(Paragraph("TwelveData $229 Plan", title_style))
    story.append(Paragraph("Capacity Analysis Report", styles['Heading2']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Paragraph("API Plan: Pro ($229/month)", body_style))
    story.append(Spacer(1, 20))

    # Key Finding Box
    story.append(Paragraph(
        "<b>KEY FINDING: You are using less than 1% of your TwelveData plan capacity!</b>",
        highlight_style
    ))
    story.append(Spacer(1, 20))

    # API Usage Status
    story.append(Paragraph("Current API Usage Status", heading_style))

    usage_data = [
        ['Metric', 'Value'],
        ['Plan Category', 'Pro'],
        ['Credits per Minute', '800'],
        ['Credits per Day (Theoretical)', '1,152,000'],
        ['Current Daily Usage', '~7,200'],
        ['Capacity Utilization', '0.63%'],
        ['Unused Capacity', '99.37%']
    ]

    usage_table = Table(usage_data, colWidths=[3*inch, 2.5*inch])
    usage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#90caf9')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(usage_table)
    story.append(Spacer(1, 25))

    # Available vs Extracted
    story.append(Paragraph("Available Data vs Currently Extracted", heading_style))

    comparison_data = [
        ['Asset Type', 'Available', 'Extracted', 'Utilization'],
        ['US Stocks (NYSE+NASDAQ)', '7,641', '152', '2.0%'],
        ['Cryptocurrencies', '2,136', '45', '2.1%'],
        ['Forex Pairs', '1,459', '30', '2.1%'],
        ['US ETFs', '10,299', '40', '0.4%'],
        ['Indices', '1,355', '9', '0.7%'],
        ['Commodities', '60', '14', '23.3%'],
        ['US Mutual Funds', '82,695', '15', '0.02%'],
        ['TOTAL', '105,645', '305', '0.29%']
    ]

    comp_table = Table(comparison_data, colWidths=[2.2*inch, 1.3*inch, 1.3*inch, 1.2*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c8e6c9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#81c784')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f1f8e9')]),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 25))

    # Daily Capacity
    story.append(Paragraph("Daily Data Extraction Capacity", heading_style))

    capacity_data = [
        ['Metric', 'Current', 'Potential'],
        ['Symbols Tracked', '305', '2,000+'],
        ['Daily API Calls', '~7,200', '100,000+'],
        ['Capacity Used', '0.63%', '10%+'],
        ['Records per Day', '7,200', '100,000+'],
        ['Data Points/Month', '10 Million', '100+ Million']
    ]

    cap_table = Table(capacity_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    cap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7b1fa2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ce93d8')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f3e5f5'), colors.white]),
    ]))
    story.append(cap_table)

    # Page break
    story.append(PageBreak())

    # Expansion Options
    story.append(Paragraph("Expansion Opportunities", heading_style))

    story.append(Paragraph("Option 1: Conservative Expansion", subheading_style))
    story.append(Paragraph("Expand to full S&P 500 coverage", body_style))

    opt1_data = [
        ['Asset', 'Current', 'Proposed', 'Additional Calls'],
        ['Stocks', '152', '500', '+348'],
        ['Impact', '', '', '< 1% capacity']
    ]

    opt1_table = Table(opt1_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
    opt1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#455a64')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#90a4ae')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(opt1_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Option 2: Moderate Expansion (Recommended)", subheading_style))
    story.append(Paragraph("Triple symbol coverage across all asset classes", body_style))

    opt2_data = [
        ['Asset Type', 'Current', 'Proposed', 'Additional'],
        ['Stocks', '152', '500', '+348'],
        ['Crypto', '45', '100', '+55'],
        ['ETFs', '40', '150', '+110'],
        ['Forex', '30', '50', '+20'],
        ['Indices', '9', '30', '+21'],
        ['Commodities', '14', '40', '+26'],
        ['Funds', '15', '50', '+35'],
        ['TOTAL', '305', '920', '+615']
    ]

    opt2_table = Table(opt2_data, colWidths=[1.5*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    opt2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bbdefb')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#64b5f6')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e3f2fd')]),
    ]))
    story.append(opt2_table)
    story.append(Paragraph("<b>Result: 3x data coverage at only 2% capacity</b>", body_style))
    story.append(Spacer(1, 20))

    # Untapped Endpoints
    story.append(Paragraph("Additional Endpoints Available (Not Yet Used)", heading_style))

    story.append(Paragraph("Fundamentals Data", subheading_style))
    endpoints_data = [
        ['Endpoint', 'Data Provided'],
        ['/earnings', 'Quarterly earnings reports'],
        ['/earnings_calendar', 'Upcoming earnings dates'],
        ['/dividends', 'Dividend history'],
        ['/dividends_calendar', 'Ex-dividend dates'],
        ['/statistics', 'P/E ratio, Beta, Market Cap'],
        ['/profile', 'Company description, sector'],
        ['/financials', 'Balance sheet, income statement'],
        ['/cash_flow', 'Cash flow statements'],
    ]

    ep_table = Table(endpoints_data, colWidths=[2*inch, 3.5*inch])
    ep_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6f00')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffb74d')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8e1')]),
    ]))
    story.append(ep_table)
    story.append(Spacer(1, 20))

    # Recommendations
    story.append(Paragraph("Recommendations for Maximum Value", heading_style))

    story.append(Paragraph("<b>Phase 1: Immediate (This Week)</b>", body_style))
    story.append(Paragraph("1. Expand to full S&P 500 (add 348 stocks)", body_style))
    story.append(Paragraph("2. Add top 100 cryptocurrencies (add 55 cryptos)", body_style))
    story.append(Paragraph("3. Add top 100 ETFs (add 60 ETFs)", body_style))
    story.append(Paragraph("4. Enable fundamentals endpoints (earnings, dividends)", body_style))
    story.append(Paragraph("<i>Impact: 2x data, still under 3% capacity</i>", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Phase 2: Short-Term (Next Month)</b>", body_style))
    story.append(Paragraph("1. Add international stocks (FTSE 100, DAX 40)", body_style))
    story.append(Paragraph("2. Expand all valid indices", body_style))
    story.append(Paragraph("3. Historical backfill (5+ years daily data)", body_style))
    story.append(Paragraph("4. Weekly financial statements", body_style))
    story.append(Paragraph("<i>Impact: 3x data, under 5% capacity</i>", body_style))
    story.append(Spacer(1, 20))

    # Summary Box
    story.append(Paragraph("Executive Summary", heading_style))

    summary_text = """
    <b>Current State:</b> Extracting 305 symbols using ~7,200 API calls/day (0.63% of capacity)<br/><br/>
    <b>Available Capacity:</b> 1,152,000 API calls/day with $229 plan<br/><br/>
    <b>Opportunity:</b> Can expand to 2,000+ symbols and add fundamentals data while using only 10% of plan capacity<br/><br/>
    <b>Recommendation:</b> Implement Phase 1 expansion immediately to maximize ROI on $229/month investment
    """

    story.append(Paragraph(summary_text, body_style))

    # Build PDF
    doc.build(story)
    print("PDF created: TWELVEDATA_CAPACITY_ANALYSIS.pdf")

if __name__ == "__main__":
    create_capacity_pdf()
