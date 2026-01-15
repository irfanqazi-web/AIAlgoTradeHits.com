"""
Create PDF from API_KEYS_RECONCILIATION.md
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

def create_api_keys_pdf():
    filename = "C:/1AITrading/Trading/API_KEYS_RECONCILIATION.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#10b981'),
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#3b82f6')
    )

    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=13,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#1e293b')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=14
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontSize=10,
        backColor=colors.HexColor('#f1f5f9'),
        borderPadding=8,
        spaceAfter=10
    )

    story = []

    # Title
    story.append(Paragraph("API Keys Reconciliation Document", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}",
                          ParagraphStyle('Date', alignment=TA_CENTER, textColor=colors.grey)))
    story.append(Spacer(1, 30))

    # Section 1: TwelveData API Key
    story.append(Paragraph("1. TwelveData API Key (Primary - $229/month Plan)", heading_style))
    story.append(Spacer(1, 10))

    # API Key info table
    key_data = [
        ['Property', 'Value'],
        ['API Key', '16ee060fd4d34a628a14bcb6f0167565'],
        ['Plan', '$229/month (Business Plan)'],
        ['Rate Limit', '600 API credits/minute (~55 requests/minute for time_series)'],
    ]
    key_table = Table(key_data, colWidths=[1.5*inch, 4*inch])
    key_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(key_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Files using this key:", subheading_style))
    files_data = [
        ['File', 'Status'],
        ['batch_weekly_data_fetcher.py', 'ACTIVE'],
        ['weekly_batch_all_assets.py', 'ACTIVE'],
        ['cloud_function_twelvedata/main.py', 'ACTIVE'],
        ['cloud_function_twelvedata_stocks/main.py', 'ACTIVE'],
        ['cloud_function_stocks_daily/main.py', 'ACTIVE'],
        ['cloud_function_weekly_cryptos/main.py', 'ACTIVE'],
        ['cloud_function_weekly_stocks/main.py', 'ACTIVE'],
        ['local_twelvedata_fetcher.py', 'ACTIVE'],
        ['fetch_sample_data.py', 'ACTIVE'],
        ['fetch_all_stocks_basic.py', 'ACTIVE'],
        ['fetch_all_historical_data.py', 'ACTIVE'],
        ['fetch_additional_symbols.py', 'ACTIVE'],
        ['fetch_fresh_twelvedata.py', 'ACTIVE'],
        ['fetch_btc_nvda_ai_training_data.py', 'ACTIVE'],
        ['fetch_historical_enhanced.py', 'ACTIVE'],
        ['fetch_historical_extended.py', 'ACTIVE'],
        ['fetch_today_data.py', 'ACTIVE'],
        ['fetch_test_data.py', 'ACTIVE'],
        ['backfill_historical_data.py', 'ACTIVE'],
        ['explore_twelve_data_complete.py', 'ACTIVE'],
        ['explore_twelve_data_news_sentiment.py', 'ACTIVE'],
        ['test_twelve_data_api.py', 'ACTIVE'],
        ['initialize_stocks_master_list.py', 'ACTIVE'],
    ]
    files_table = Table(files_data, colWidths=[4*inch, 1.5*inch])
    files_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(files_table)

    # Section 2: Finnhub API Key
    story.append(Spacer(1, 20))
    story.append(Paragraph("2. Finnhub API Key", heading_style))

    finnhub_data = [
        ['Property', 'Value'],
        ['API Key', 'd4dg7t9r01qovljpm3g0d4dg7t9r01qovljpm3gg'],
        ['Plan', 'Unknown (likely free tier)'],
        ['File', 'explore_finnhub_api.py'],
    ]
    finnhub_table = Table(finnhub_data, colWidths=[1.5*inch, 4*inch])
    finnhub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(finnhub_table)

    # Section 3: Anthropic API Key
    story.append(Spacer(1, 20))
    story.append(Paragraph("3. Anthropic API Key (Claude)", heading_style))
    story.append(Paragraph("Status: Not set (placeholder only - requires environment variable)", body_style))
    story.append(Paragraph("Files referencing: AI_FEATURES_DEPLOYMENT_GUIDE.md, cloud_function_ai/README.md", body_style))

    # Section 4: Google Cloud Service Account
    story.append(Spacer(1, 20))
    story.append(Paragraph("4. Google Cloud Service Account", heading_style))
    story.append(Paragraph("File: aialgotradehits-8863a22a9958.json", body_style))
    story.append(Paragraph("Project: aialgotradehits", body_style))

    # Section 5: OLD/Invalid Keys
    story.append(Spacer(1, 20))
    story.append(Paragraph("5. Incorrect/Old API Keys Found", heading_style))
    old_data = [
        ['Old Key', 'Status'],
        ['848dc760a3154cb0bf34f85b64845a57', 'INVALID - replaced'],
    ]
    old_table = Table(old_data, colWidths=[3.5*inch, 2*inch])
    old_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(old_table)

    # Recommendations
    story.append(PageBreak())
    story.append(Paragraph("Recommendations", title_style))

    story.append(Paragraph("1. Rate Limit Update for $229/month Plan", heading_style))
    story.append(Paragraph(
        "Your TwelveData $229/month plan includes 600 API credits/minute. "
        "The current scripts use REQUESTS_PER_MINUTE = 8 (free tier limit). "
        "This should be updated to REQUESTS_PER_MINUTE = 55 for paid tier.", body_style))

    story.append(Spacer(1, 15))
    story.append(Paragraph("2. Time Savings with Paid Plan", heading_style))

    time_data = [
        ['Scenario', 'Free Tier (8/min)', 'Paid Tier (55/min)', 'Improvement'],
        ['20,000 stocks', '~42 hours', '~6 hours', '7x faster'],
        ['All assets (1 week)', '~50 hours', '~7 hours', '7x faster'],
    ]
    time_table = Table(time_data, colWidths=[1.8*inch, 1.3*inch, 1.3*inch, 1.1*inch])
    time_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(time_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph("3. Action Items", heading_style))
    story.append(Paragraph("1. Confirm TwelveData API key is correct: 16ee060fd4d34a628a14bcb6f0167565", body_style))
    story.append(Paragraph("2. Update rate limits in weekly_batch_all_assets.py from 8 to 55", body_style))
    story.append(Paragraph("3. Restart batch fetcher with faster rate limits", body_style))

    # Build PDF
    doc.build(story)
    print(f"PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_api_keys_pdf()
