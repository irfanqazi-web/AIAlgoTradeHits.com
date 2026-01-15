#!/usr/bin/env python3
"""
Generate PDF Report: Data Pipeline Status
Shows ALL 7 asset types with tickers, record counts, and date ranges
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# All 7 asset types with their tables
ASSET_TABLES = {
    'Stocks': 'stocks_daily_clean',
    'Crypto': 'crypto_daily_clean',
    'ETFs': 'etfs_daily_clean',
    'Forex': 'forex_daily_clean',
    'Indices': 'indices_daily_clean',
    'Commodities': 'commodities_daily_clean',
    'Stocks Hourly': 'stocks_hourly_clean'
}

def get_asset_data(client, table_name, asset_name):
    """Get asset data summary from BigQuery"""
    query = f"""
    SELECT
        symbol,
        MIN(datetime) as start_date,
        MAX(datetime) as end_date,
        COUNT(*) as record_count,
        MAX(close) as last_close,
        '{asset_name}' as asset_type
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    GROUP BY symbol
    ORDER BY symbol
    """
    try:
        return client.query(query).to_dataframe()
    except Exception as e:
        print(f"  Warning: Could not fetch {asset_name}: {e}")
        return pd.DataFrame()


def get_all_freshness(client):
    """Check data freshness for all asset types"""
    results = []

    for asset_name, table_name in ASSET_TABLES.items():
        query = f"""
        SELECT
            '{asset_name}' as asset_type,
            COUNT(DISTINCT symbol) as total_symbols,
            COUNT(*) as total_records,
            MAX(datetime) as latest_data,
            DATE_DIFF(CURRENT_DATE(), DATE(MAX(datetime)), DAY) as days_stale
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        """
        try:
            df = client.query(query).to_dataframe()
            if not df.empty and df['total_records'].iloc[0] > 0:
                results.append(df.iloc[0].to_dict())
        except Exception as e:
            print(f"  Warning: Could not get freshness for {asset_name}: {e}")

    return pd.DataFrame(results)


def get_recent_activity(client):
    """Get recent data ingestion activity for all asset types"""
    all_activity = []

    for asset_name, table_name in ASSET_TABLES.items():
        query = f"""
        SELECT
            '{asset_name}' as asset_type,
            DATE(datetime) as date,
            COUNT(DISTINCT symbol) as symbols_updated,
            COUNT(*) as records_added
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY DATE(datetime)
        ORDER BY date DESC
        LIMIT 7
        """
        try:
            df = client.query(query).to_dataframe()
            all_activity.append(df)
        except:
            pass

    if all_activity:
        return pd.concat(all_activity, ignore_index=True).sort_values(['asset_type', 'date'], ascending=[True, False])
    return pd.DataFrame()


def create_pdf_report(all_assets_data, freshness_df, activity_df):
    """Generate comprehensive PDF report for all 7 asset types"""

    filename = f"C:/1AITrading/Trading/DATA_PIPELINE_STATUS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter),
                           leftMargin=0.5*inch, rightMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=16, spaceAfter=10, spaceBefore=20)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading2'], fontSize=12, spaceAfter=5)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)

    elements = []

    # Title
    elements.append(Paragraph("TwelveData Pipeline Status Report", title_style))
    elements.append(Paragraph("Complete 7 Asset Type Analysis", ParagraphStyle('Subtitle', alignment=TA_CENTER, fontSize=14, textColor=colors.HexColor('#3b82f6'))))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                             ParagraphStyle('Date', alignment=TA_CENTER, fontSize=12, textColor=colors.grey)))
    elements.append(Spacer(1, 20))

    # Executive Summary - All 7 Assets
    elements.append(Paragraph("Executive Summary - All 7 Asset Types", heading_style))

    summary_data = [
        ['Asset Type', 'Total Symbols', 'Total Records', 'Latest Data', 'Days Stale', 'Status']
    ]

    total_symbols = 0
    total_records = 0

    for _, row in freshness_df.iterrows():
        days_stale = int(row['days_stale']) if pd.notna(row['days_stale']) else 999
        status = "FRESH" if days_stale <= 1 else ("STALE" if days_stale <= 3 else "OUTDATED")
        latest = row['latest_data'].strftime('%Y-%m-%d') if pd.notna(row['latest_data']) else 'N/A'

        symbols = int(row['total_symbols']) if pd.notna(row['total_symbols']) else 0
        records = int(row['total_records']) if pd.notna(row['total_records']) else 0
        total_symbols += symbols
        total_records += records

        summary_data.append([
            row['asset_type'],
            f"{symbols:,}",
            f"{records:,}",
            latest,
            str(days_stale),
            status
        ])

    # Add totals row
    summary_data.append(['TOTAL', f"{total_symbols:,}", f"{total_records:,}", '-', '-', '-'])

    summary_table = Table(summary_data, colWidths=[1.4*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f1f5f9')]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Recent Activity
    elements.append(Paragraph("Recent Data Ingestion (Last 7 Days)", heading_style))

    if not activity_df.empty:
        activity_data = [['Date', 'Asset Type', 'Symbols Updated', 'Records Added']]
        for _, row in activity_df.head(21).iterrows():  # Show top 21 rows (3 per asset type)
            activity_data.append([
                row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'N/A',
                row['asset_type'],
                f"{int(row['symbols_updated']):,}",
                f"{int(row['records_added']):,}"
            ])

        activity_table = Table(activity_data, colWidths=[1.5*inch, 1.4*inch, 1.5*inch, 1.5*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
        ]))
        elements.append(activity_table)
    else:
        elements.append(Paragraph("No recent activity found.", normal_style))

    # Color map for each asset type
    asset_colors = {
        'Stocks': '#7c3aed',
        'Crypto': '#ea580c',
        'ETFs': '#0891b2',
        'Forex': '#16a34a',
        'Indices': '#dc2626',
        'Commodities': '#ca8a04',
        'Stocks Hourly': '#6366f1'
    }

    # Detailed sections for each asset type
    for asset_name, df in all_assets_data.items():
        if df.empty:
            continue

        elements.append(PageBreak())
        elements.append(Paragraph(f"{asset_name} Assets Detail", heading_style))
        elements.append(Paragraph(f"Total: {len(df)} symbols", subheading_style))

        asset_data = [['Symbol', 'Start Date', 'End Date', 'Records', 'Last Close']]
        for _, row in df.iterrows():
            start = row['start_date'].strftime('%Y-%m-%d') if pd.notna(row['start_date']) else 'N/A'
            end = row['end_date'].strftime('%Y-%m-%d') if pd.notna(row['end_date']) else 'N/A'
            close = f"${row['last_close']:.2f}" if pd.notna(row['last_close']) else 'N/A'
            asset_data.append([
                row['symbol'],
                start,
                end,
                f"{int(row['record_count']):,}",
                close
            ])

        # Split into chunks for multiple pages if needed
        chunk_size = 35
        color = colors.HexColor(asset_colors.get(asset_name, '#6b7280'))

        for i in range(0, len(asset_data), chunk_size):
            chunk = [asset_data[0]] + asset_data[i+1:i+1+chunk_size] if i > 0 else asset_data[:chunk_size+1]

            asset_table = Table(chunk, colWidths=[1.4*inch, 1.3*inch, 1.3*inch, 1*inch, 1.2*inch])
            asset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))
            elements.append(asset_table)
            if i + chunk_size < len(asset_data) - 1:
                elements.append(PageBreak())

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("-" * 100, ParagraphStyle('Line', alignment=TA_CENTER, textColor=colors.grey)))
    elements.append(Paragraph("AIAlgoTradeHits.com | TwelveData $229 Plan | All 7 Asset Types | Auto-Generated Report",
                             ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=9, textColor=colors.grey)))

    # Build PDF
    doc.build(elements)
    return filename


def main():
    print("=" * 60)
    print("Generating Complete 7-Asset Pipeline Status Report")
    print("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    # Fetch data for all asset types
    all_assets_data = {}

    for asset_name, table_name in ASSET_TABLES.items():
        print(f"\n{len(all_assets_data)+1}. Fetching {asset_name} data summary...")
        df = get_asset_data(client, table_name, asset_name)
        all_assets_data[asset_name] = df
        print(f"   Found {len(df)} {asset_name.lower()} symbols")

    print(f"\n{len(ASSET_TABLES)+1}. Checking data freshness for all assets...")
    freshness_df = get_all_freshness(client)
    for _, row in freshness_df.iterrows():
        days = int(row['days_stale']) if pd.notna(row['days_stale']) else 999
        status = "FRESH" if days <= 1 else ("STALE" if days <= 3 else "OUTDATED")
        records = int(row['total_records']) if pd.notna(row['total_records']) else 0
        symbols = int(row['total_symbols']) if pd.notna(row['total_symbols']) else 0
        print(f"   {row['asset_type']}: {symbols} symbols, {records:,} records, {days} days stale [{status}]")

    print(f"\n{len(ASSET_TABLES)+2}. Fetching recent activity...")
    activity_df = get_recent_activity(client)
    print(f"   Found {len(activity_df)} activity records")

    print(f"\n{len(ASSET_TABLES)+3}. Generating PDF report...")
    filename = create_pdf_report(all_assets_data, freshness_df, activity_df)
    print(f"\n   Report saved to: {filename}")

    print("\n" + "=" * 60)
    print("REPORT GENERATION COMPLETE - ALL 7 ASSETS INCLUDED")
    print("=" * 60)

    return filename


if __name__ == "__main__":
    main()
