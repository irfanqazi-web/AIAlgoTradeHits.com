#!/usr/bin/env python3
"""
Generate Stock Data Coverage Report PDF
Analyzes all 106 symbols and their date ranges
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_NAME = 'stocks_daily_clean'

def get_stock_coverage():
    """Get date coverage data from BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT
        symbol,
        COUNT(*) as record_count,
        MIN(DATE(datetime)) as start_date,
        MAX(DATE(datetime)) as end_date,
        DATE_DIFF(MAX(DATE(datetime)), MIN(DATE(datetime)), DAY) + 1 as date_range_days
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`
    GROUP BY symbol
    ORDER BY symbol
    """

    results = client.query(query).result()
    data = []
    for row in results:
        data.append({
            'symbol': row.symbol,
            'record_count': row.record_count,
            'start_date': row.start_date,
            'end_date': row.end_date,
            'date_range_days': row.date_range_days
        })
    return data

def generate_pdf_report(data, output_path):
    """Generate PDF report with stock coverage data"""

    doc = SimpleDocTemplate(output_path, pagesize=landscape(letter),
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=1
    )

    elements = []

    # Title
    elements.append(Paragraph("Stock Daily Data Coverage Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    total_symbols = len(data)
    min_records = min(d['record_count'] for d in data)
    max_records = max(d['record_count'] for d in data)
    avg_records = sum(d['record_count'] for d in data) / total_symbols

    symbols_1_record = [d for d in data if d['record_count'] == 1]
    symbols_139_145 = [d for d in data if 139 <= d['record_count'] <= 145]
    symbols_500 = [d for d in data if d['record_count'] == 500]

    elements.append(Paragraph("<b>SUMMARY STATISTICS</b>", styles['Heading2']))

    summary_data = [
        ['Metric', 'Value'],
        ['Total Symbols', str(total_symbols)],
        ['Minimum Records', str(min_records)],
        ['Maximum Records', str(max_records)],
        ['Average Records', f'{avg_records:.1f}'],
        ['Symbols with 1 record (CRITICAL)', f'{len(symbols_1_record)} ({", ".join([d["symbol"] for d in symbols_1_record])})'],
        ['Symbols with 139-145 records', str(len(symbols_139_145))],
        ['Symbols with 500 records', str(len(symbols_500))],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 6*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Data Quality Issues
    elements.append(Paragraph("<b>DATA QUALITY ISSUES</b>", styles['Heading2']))

    issues_data = [
        ['Issue', 'Symbols Affected', 'Action Required'],
        ['Only 1 day of data', ', '.join([d['symbol'] for d in symbols_1_record]), 'Need full historical backfill (~500 days)'],
        ['Missing recent data (end < 2025-12-06)', ', '.join([d['symbol'] for d in data if d['end_date'].isoformat() < '2025-12-06' and d['record_count'] > 1]), 'Need to fetch missing days'],
        ['Data ends at 2025-11-21', f'{len([d for d in data if d["end_date"].isoformat() == "2025-11-21"])} symbols', 'Need 17 days of backfill'],
    ]

    issues_table = Table(issues_data, colWidths=[2*inch, 4*inch, 3*inch])
    issues_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(issues_table)
    elements.append(Spacer(1, 30))

    # Target State
    elements.append(Paragraph("<b>TARGET STATE</b>", styles['Heading2']))
    target_text = """
    <b>Goal:</b> All 106 symbols should have consistent data from 2023-11-27 to 2025-12-08 (latest market date)<br/>
    <b>Expected trading days:</b> ~510 days (excluding weekends and holidays)<br/>
    <b>Action Plan:</b><br/>
    1. For symbols with only 1 record: Fetch full 500-day historical data<br/>
    2. For symbols ending at 2025-11-21: Fetch data from 2025-11-22 to 2025-12-08<br/>
    3. For symbols with 139-145 records: Verify coverage and fill gaps<br/>
    """
    elements.append(Paragraph(target_text, styles['Normal']))
    elements.append(PageBreak())

    # Detailed Table - All Symbols
    elements.append(Paragraph("<b>DETAILED COVERAGE BY SYMBOL</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # Split into two columns for better readability
    header = ['#', 'Symbol', 'Records', 'Start Date', 'End Date', 'Days', 'Status']

    table_data = [header]
    for i, d in enumerate(data, 1):
        if d['record_count'] == 1:
            status = 'CRITICAL'
        elif d['end_date'].isoformat() < '2025-12-01':
            status = 'OUTDATED'
        elif d['record_count'] < 200:
            status = 'INCOMPLETE'
        else:
            status = 'OK'

        table_data.append([
            str(i),
            d['symbol'],
            str(d['record_count']),
            d['start_date'].isoformat(),
            d['end_date'].isoformat(),
            str(d['date_range_days']),
            status
        ])

    detail_table = Table(table_data, colWidths=[0.4*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch, 0.6*inch, 1*inch])

    # Build style with conditional formatting
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]

    # Add row colors based on status
    for i, row in enumerate(table_data[1:], 1):
        status = row[-1]
        if status == 'CRITICAL':
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightcoral))
        elif status == 'OUTDATED':
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightyellow))
        elif status == 'INCOMPLETE':
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
        else:
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgreen))

    detail_table.setStyle(TableStyle(table_style))
    elements.append(detail_table)

    # Legend
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Legend:</b>", styles['Normal']))
    legend_data = [
        ['Color', 'Status', 'Description'],
        ['', 'CRITICAL', 'Only 1 day of data - needs full backfill'],
        ['', 'OUTDATED', 'Data ends before Dec 1, 2025 - needs recent data'],
        ['', 'INCOMPLETE', 'Less than 200 records - may need historical backfill'],
        ['', 'OK', '200+ records with recent data - good coverage'],
    ]
    legend_table = Table(legend_data, colWidths=[1*inch, 1*inch, 5*inch])
    legend_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (0, 1), colors.lightcoral),
        ('BACKGROUND', (0, 2), (0, 2), colors.lightyellow),
        ('BACKGROUND', (0, 3), (0, 3), colors.lightgrey),
        ('BACKGROUND', (0, 4), (0, 4), colors.lightgreen),
    ]
    legend_table.setStyle(TableStyle(legend_style))
    elements.append(legend_table)

    # Build PDF
    doc.build(elements)
    print(f"PDF report generated: {output_path}")

def main():
    print("Fetching stock coverage data...")
    data = get_stock_coverage()
    print(f"Found {len(data)} symbols")

    output_path = "C:/1AITrading/Trading/STOCK_DATA_COVERAGE_REPORT.pdf"
    print("Generating PDF report...")
    generate_pdf_report(data, output_path)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    symbols_1_record = [d for d in data if d['record_count'] == 1]
    symbols_outdated = [d for d in data if d['end_date'].isoformat() < '2025-12-01' and d['record_count'] > 1]

    print(f"\nCRITICAL (1 record only): {len(symbols_1_record)} symbols")
    for d in symbols_1_record:
        print(f"  - {d['symbol']}: {d['record_count']} records")

    print(f"\nOUTDATED (end < Dec 1, 2025): {len(symbols_outdated)} symbols")
    for d in symbols_outdated:
        print(f"  - {d['symbol']}: ends {d['end_date']}")

if __name__ == "__main__":
    main()
