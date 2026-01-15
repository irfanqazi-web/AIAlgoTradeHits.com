"""
Generate Trading Data Status Report PDF from BigQuery data
This script queries the database for all available symbols and generates a PDF report.
Can be scheduled to run daily for automatic updates.
"""

from google.cloud import bigquery
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import os

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'trading_data'
OUTPUT_PATH = 'C:/1AITrading/Trading/TRADING_DATA_STATUS_REPORT.pdf'

def get_symbols_from_bigquery():
    """Fetch all available symbols from BigQuery tables"""
    client = bigquery.Client(project=PROJECT_ID)

    results = {}

    # Stocks
    try:
        query = f"""
        SELECT DISTINCT symbol, name, sector
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        LIMIT 500
        """
        rows = list(client.query(query).result())
        results['stocks'] = [{'symbol': r.symbol, 'name': r.name or '', 'sector': r.sector or ''} for r in rows]
    except Exception as e:
        print(f"Error fetching stocks: {e}")
        results['stocks'] = []

    # Crypto
    try:
        query = f"""
        SELECT DISTINCT symbol, name
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        LIMIT 500
        """
        rows = list(client.query(query).result())
        results['crypto'] = [{'symbol': r.symbol, 'name': r.name or ''} for r in rows]
    except Exception as e:
        print(f"Error fetching crypto: {e}")
        results['crypto'] = []

    # ETFs
    try:
        query = f"""
        SELECT DISTINCT symbol, name
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_etfs_daily`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        LIMIT 100
        """
        rows = list(client.query(query).result())
        results['etfs'] = [{'symbol': r.symbol, 'name': r.name or ''} for r in rows]
    except Exception as e:
        print(f"Error fetching ETFs: {e}")
        results['etfs'] = []

    # Forex
    try:
        query = f"""
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_forex_daily`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        LIMIT 100
        """
        rows = list(client.query(query).result())
        results['forex'] = [{'symbol': r.symbol, 'name': ''} for r in rows]
    except Exception as e:
        print(f"Error fetching forex: {e}")
        results['forex'] = []

    # Indices
    try:
        query = f"""
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_indices_daily`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        LIMIT 100
        """
        rows = list(client.query(query).result())
        results['indices'] = [{'symbol': r.symbol, 'name': ''} for r in rows]
    except Exception as e:
        print(f"Error fetching indices: {e}")
        results['indices'] = []

    # Commodities
    try:
        query = f"""
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_commodities_daily`
        WHERE symbol IS NOT NULL
        ORDER BY symbol
        LIMIT 100
        """
        rows = list(client.query(query).result())
        results['commodities'] = [{'symbol': r.symbol, 'name': ''} for r in rows]
    except Exception as e:
        print(f"Error fetching commodities: {e}")
        results['commodities'] = []

    return results

def generate_pdf(data, output_path):
    """Generate PDF report from the data"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, spaceBefore=15)

    story.append(Paragraph('Trading Data Status Report', title_style))
    story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC',
                          ParagraphStyle('Date', alignment=1, fontSize=10, textColor=colors.grey)))
    story.append(Spacer(1, 20))

    # Summary
    summary_text = f"""
    <b>Available Data Summary:</b><br/>
    - Stocks: {len(data.get('stocks', []))} symbols<br/>
    - Crypto: {len(data.get('crypto', []))} symbols<br/>
    - ETFs: {len(data.get('etfs', []))} symbols<br/>
    - Forex: {len(data.get('forex', []))} symbols<br/>
    - Indices: {len(data.get('indices', []))} symbols<br/>
    - Commodities: {len(data.get('commodities', []))} symbols<br/>
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))

    # Stocks
    if data.get('stocks'):
        story.append(Paragraph('1. Stocks (US Markets)', heading_style))
        stocks_data = [['Symbol', 'Name', 'Sector']]
        for s in data['stocks'][:100]:  # Limit to first 100
            stocks_data.append([s['symbol'], s['name'][:30] if s['name'] else '', s['sector'][:20] if s['sector'] else ''])
        t = Table(stocks_data, colWidths=[60, 180, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        if len(data['stocks']) > 100:
            story.append(Paragraph(f'... and {len(data["stocks"]) - 100} more stocks',
                                  ParagraphStyle('More', fontSize=8, textColor=colors.grey)))
        story.append(Spacer(1, 15))

    # Crypto
    if data.get('crypto'):
        story.append(Paragraph('2. Crypto', heading_style))
        crypto_data = [['Symbol', 'Name']]
        for s in data['crypto'][:50]:
            crypto_data.append([s['symbol'], s['name'][:40] if s['name'] else ''])
        t = Table(crypto_data, colWidths=[100, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        if len(data['crypto']) > 50:
            story.append(Paragraph(f'... and {len(data["crypto"]) - 50} more cryptocurrencies',
                                  ParagraphStyle('More', fontSize=8, textColor=colors.grey)))
        story.append(Spacer(1, 15))

    # ETFs
    if data.get('etfs'):
        story.append(Paragraph('3. ETFs', heading_style))
        etfs_data = [['Symbol', 'Name']]
        for s in data['etfs'][:30]:
            etfs_data.append([s['symbol'], s['name'][:40] if s['name'] else ''])
        t = Table(etfs_data, colWidths=[80, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

    # Forex
    if data.get('forex'):
        story.append(Paragraph('4. Forex', heading_style))
        forex_data = [['Symbol']]
        for s in data['forex'][:20]:
            forex_data.append([s['symbol']])
        t = Table(forex_data, colWidths=[100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

    # Indices
    if data.get('indices'):
        story.append(Paragraph('5. Indices', heading_style))
        indices_data = [['Symbol']]
        for s in data['indices'][:20]:
            indices_data.append([s['symbol']])
        t = Table(indices_data, colWidths=[100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.brown),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

    # Commodities
    if data.get('commodities'):
        story.append(Paragraph('6. Commodities', heading_style))
        commodities_data = [['Symbol']]
        for s in data['commodities'][:20]:
            commodities_data.append([s['symbol']])
        t = Table(commodities_data, colWidths=[100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgoldenrod),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)

    story.append(Spacer(1, 30))
    story.append(Paragraph('This report is automatically generated daily from the trading database.',
                          ParagraphStyle('Footer', fontSize=9, textColor=colors.grey, alignment=1)))

    doc.build(story)
    print(f"PDF generated: {output_path}")

def upload_to_gcs(local_path, bucket_name, blob_name):
    """Upload PDF to Google Cloud Storage"""
    from google.cloud import storage

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(local_path)
    blob.make_public()

    print(f"Uploaded to: https://storage.googleapis.com/{bucket_name}/{blob_name}")
    return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

if __name__ == '__main__':
    print("Fetching data from BigQuery...")
    data = get_symbols_from_bigquery()

    print("Generating PDF...")
    generate_pdf(data, OUTPUT_PATH)

    print("Uploading to Cloud Storage...")
    url = upload_to_gcs(OUTPUT_PATH, 'aialgotradehits-assets', 'TRADING_DATA_STATUS_REPORT.pdf')

    print(f"\nDone! PDF available at: {url}")
