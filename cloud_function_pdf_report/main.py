"""
Cloud Function to generate TwelveData Asset Status Report PDF
Matches the format of ASSET_STATUS_REPORT_20251222_123636.pdf
Triggered after daily TwelveData fetch completes
"""

import functions_framework
from google.cloud import bigquery, storage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import tempfile
import os

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'  # This is the correct dataset
BUCKET_NAME = 'aialgotradehits-assets'
PDF_FILENAME = 'TRADING_DATA_STATUS_REPORT.pdf'

# Color scheme for each asset type
ASSET_COLORS = {
    'STOCK': colors.HexColor('#1a237e'),  # Dark blue
    'CRYPTO': colors.HexColor('#e65100'),  # Orange
    'ETF': colors.HexColor('#2e7d32'),     # Green
    'INDEX': colors.HexColor('#6a1b9a'),   # Purple
    'FOREX': colors.HexColor('#b71c1c'),   # Dark red
}


def get_asset_data_from_bigquery(client):
    """Fetch all asset data from BigQuery tables"""
    results = {
        'STOCK': [],
        'CRYPTO': [],
        'ETF': [],
        'INDEX': [],
        'FOREX': []
    }

    # Tables and their corresponding queries - using correct table names from crypto_trading_data dataset
    # Note: 'interval' is a reserved keyword in BigQuery, so we use 'timeframe' as alias
    table_queries = {
        'STOCK': [
            # Daily stocks
            f"""
            SELECT DISTINCT
                symbol as ticker,
                name,
                '1day' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                CAST(NULL AS STRING) as start_date,
                CAST(NULL AS STRING) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 300
            """,
            # Hourly stocks
            f"""
            SELECT DISTINCT
                symbol as ticker,
                name,
                '1h' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                FORMAT_TIMESTAMP('%Y-%m-%d', MIN(datetime) OVER (PARTITION BY symbol)) as start_date,
                FORMAT_TIMESTAMP('%Y-%m-%d', MAX(datetime) OVER (PARTITION BY symbol)) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.stocks_hourly_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 100
            """
        ],
        'CRYPTO': [
            # Hourly crypto
            f"""
            SELECT DISTINCT
                symbol as ticker,
                name,
                '1h' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                FORMAT_TIMESTAMP('%Y-%m-%d', MIN(datetime) OVER (PARTITION BY symbol)) as start_date,
                FORMAT_TIMESTAMP('%Y-%m-%d', MAX(datetime) OVER (PARTITION BY symbol)) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.crypto_hourly_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 100
            """,
            # Daily crypto
            f"""
            SELECT DISTINCT
                symbol as ticker,
                name,
                '1day' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                CAST(NULL AS STRING) as start_date,
                CAST(NULL AS STRING) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 100
            """
        ],
        'ETF': [
            f"""
            SELECT DISTINCT
                symbol as ticker,
                name,
                '1day' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                CAST(NULL AS STRING) as start_date,
                CAST(NULL AS STRING) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 100
            """
        ],
        'INDEX': [
            f"""
            SELECT DISTINCT
                symbol as ticker,
                COALESCE(name, symbol) as name,
                '1day' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                CAST(NULL AS STRING) as start_date,
                CAST(NULL AS STRING) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.indices_daily_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 50
            """
        ],
        'FOREX': [
            f"""
            SELECT DISTINCT
                symbol as ticker,
                COALESCE(name, symbol) as name,
                '1day' as timeframe,
                close as price,
                COUNT(*) OVER (PARTITION BY symbol) as records,
                CAST(NULL AS STRING) as start_date,
                CAST(NULL AS STRING) as end_date
            FROM `{PROJECT_ID}.{DATASET_ID}.forex_daily_clean`
            WHERE symbol IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) = 1
            ORDER BY symbol
            LIMIT 50
            """
        ]
    }

    for asset_type, queries in table_queries.items():
        for query in queries:
            try:
                rows = list(client.query(query).result())
                for r in rows:
                    item = {
                        'ticker': r.ticker or '',
                        'name': (r.name or '')[:30],
                        'interval': r.timeframe or '1day',  # Use timeframe from query, but keep 'interval' as key
                        'price': float(r.price) if r.price else 0,
                        'records': int(r.records) if r.records else 0,
                        'start_date': r.start_date or 'N/A',
                        'end_date': r.end_date or 'N/A'
                    }
                    # Avoid duplicates
                    existing = [x for x in results[asset_type] if x['ticker'] == item['ticker'] and x['interval'] == item['interval']]
                    if not existing:
                        results[asset_type].append(item)
                print(f"Fetched {len(rows)} {asset_type} records from query")
            except Exception as e:
                print(f"Error fetching {asset_type}: {e}")

    return results


def get_summary_stats(client):
    """Get summary statistics from BigQuery"""
    stats = {
        'total_records': 0,
        'unique_symbols': 0,
        'daily_quota': 2000000,
        'last_fetch': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    }

    # Count total records across all tables - using correct table names
    count_queries = [
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.stocks_hourly_clean`",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.crypto_hourly_clean`",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.indices_daily_clean`",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.forex_daily_clean`",
    ]

    for query in count_queries:
        try:
            result = list(client.query(query).result())
            if result:
                stats['total_records'] += result[0].cnt
        except Exception as e:
            print(f"Error counting: {e}")

    # Count unique symbols - using correct table names
    symbol_query = f"""
    SELECT COUNT(DISTINCT symbol) as cnt FROM (
        SELECT symbol FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean` WHERE symbol IS NOT NULL
        UNION ALL
        SELECT symbol FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean` WHERE symbol IS NOT NULL
        UNION ALL
        SELECT symbol FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean` WHERE symbol IS NOT NULL
        UNION ALL
        SELECT symbol FROM `{PROJECT_ID}.{DATASET_ID}.indices_daily_clean` WHERE symbol IS NOT NULL
        UNION ALL
        SELECT symbol FROM `{PROJECT_ID}.{DATASET_ID}.forex_daily_clean` WHERE symbol IS NOT NULL
    )
    """
    try:
        result = list(client.query(symbol_query).result())
        if result:
            stats['unique_symbols'] = result[0].cnt
    except Exception as e:
        print(f"Error counting symbols: {e}")

    return stats


def format_price(price):
    """Format price based on value"""
    if price is None or price == 0:
        return 'N/A'
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def generate_pdf(data, stats, output_path):
    """Generate PDF report matching reference format"""
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Title style
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, spaceAfter=10, alignment=1, textColor=colors.black)
    subtitle_style = ParagraphStyle('Subtitle', fontSize=10, alignment=0, textColor=colors.grey, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, spaceBefore=15, textColor=colors.black, fontName='Helvetica-Bold')

    # Title
    story.append(Paragraph('TwelveData $229 Pro Plan - Asset Status Report', title_style))
    story.append(Paragraph(f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_style))

    # Summary metrics table
    quota_used = (stats['total_records'] / stats['daily_quota'] * 100) if stats['daily_quota'] > 0 else 0
    metrics_data = [
        ['Metric', 'Value'],
        ['Total Records', f"{stats['total_records']:,}"],
        ['Unique Symbols', f"{stats['unique_symbols']:,}"],
        ['Daily Quota', f"{stats['daily_quota']:,}"],
        ['Quota Used', f"{quota_used:.1f}%"],
        ['Last Fetch', stats['last_fetch']],
    ]

    metrics_table = Table(metrics_data, colWidths=[200, 200])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 20))

    # Summary by Asset Type
    story.append(Paragraph('Summary by Asset Type', heading_style))

    summary_data = [['Asset Type', 'Symbols', 'Records']]
    total_records_by_type = {}
    for asset_type, items in data.items():
        symbols = len(set(item['ticker'] for item in items))
        records = sum(item['records'] for item in items)
        total_records_by_type[asset_type] = records
        summary_data.append([asset_type, str(symbols), f"{records:,}"])

    summary_table = Table(summary_data, colWidths=[150, 100, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # Detailed breakdown for each asset type
    for asset_type in ['STOCK', 'CRYPTO', 'ETF', 'INDEX', 'FOREX']:
        items = data.get(asset_type, [])
        if not items:
            continue

        # Section header
        story.append(Paragraph(f'{asset_type} - Detailed Breakdown ({len(items)} items)', heading_style))

        # Table header
        detail_data = [['#', 'Ticker', 'Name', 'Interval', 'Price', 'Records', 'Start Date', 'End Date']]

        # Add rows
        for idx, item in enumerate(items, 1):
            detail_data.append([
                str(idx),
                item['ticker'],
                item['name'][:25] if item['name'] else '',
                item['interval'],
                format_price(item['price']),
                f"{item['records']:,}",
                item['start_date'],
                item['end_date']
            ])

        # Create table with appropriate column widths
        col_widths = [30, 70, 140, 50, 70, 60, 70, 70]
        detail_table = Table(detail_data, colWidths=col_widths, repeatRows=1)

        header_color = ASSET_COLORS.get(asset_type, colors.HexColor('#1a237e'))
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Name column left aligned
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(detail_table)
        story.append(PageBreak())

    doc.build(story)
    print(f"PDF generated: {output_path}")


def upload_to_gcs(local_path, bucket_name, blob_name):
    """Upload PDF to Google Cloud Storage"""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path, content_type='application/pdf')
    return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"


@functions_framework.http
def generate_report(request):
    """HTTP Cloud Function entry point"""
    try:
        print("Starting Asset Status Report PDF generation...")

        # Initialize BigQuery client
        bq_client = bigquery.Client(project=PROJECT_ID)

        # Fetch summary statistics
        print("Fetching summary statistics...")
        stats = get_summary_stats(bq_client)
        print(f"Stats: {stats}")

        # Fetch detailed asset data
        print("Fetching asset data from BigQuery...")
        data = get_asset_data_from_bigquery(bq_client)

        # Log counts
        for asset_type, items in data.items():
            print(f"{asset_type}: {len(items)} items")

        # Generate PDF in temp directory
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        print("Generating PDF...")
        generate_pdf(data, stats, tmp_path)

        # Upload to GCS
        print("Uploading to Cloud Storage...")
        url = upload_to_gcs(tmp_path, BUCKET_NAME, PDF_FILENAME)

        # Cleanup
        os.unlink(tmp_path)

        result = {
            'success': True,
            'message': 'Asset Status Report PDF generated successfully',
            'url': url,
            'timestamp': datetime.utcnow().isoformat(),
            'stats': stats,
            'counts': {k: len(v) for k, v in data.items()}
        }
        print(f"Done: {result}")
        return result, 200

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}, 500
