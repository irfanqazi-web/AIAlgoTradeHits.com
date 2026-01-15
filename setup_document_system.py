"""
Document Management System Setup Script
Converts all project documentation to PDF/HTML and uploads to GCP Cloud Storage
"""
import os
import sys
import subprocess
from pathlib import Path
import markdown
from google.cloud import storage
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "cryptobot-462709"
BUCKET_NAME = "trading-app-documents"
BASE_DIR = Path(__file__).parent

# Document files to process
MD_FILES = [
    "README.md",
    "DAILY_CRYPTO_FETCHER_SUMMARY.md",
    "DEPLOYMENT_STATUS_REPORT.md",
    "COMPLETE_DEPLOYMENT_SUMMARY.md",
    "deploy_all_with_indicators.md",
    "DEPLOYMENT_COMPLETE_WITH_INDICATORS.md",
    "CRYPTOBOT_DEPLOYMENT_COMPLETE.md",
    "FINAL_DEPLOYMENT_STATUS.md",
    "QUICK_START_GUIDE.md",
    "DEPLOYMENT_COMPLETE_STATUS.md",
    "FINAL_COMPLETION_REPORT.md",
    "CLAUDE.md",
    "TIMEOUT_FIX_GUIDE.md",
    "ELLIOTT_WAVE_DEPLOYMENT_GUIDE.md",
    "STOCK_DEPLOYMENT_GUIDE.md",
    "STOCK_PIPELINE_COMPLETE.md",
    "DEPLOY_STOCK_FUNCTION.md",
    "COMPLETE_PROJECT_STATUS.md",
    "STOCK_FUNCTION_DEPLOYMENT_COMPLETE.md",
    "FULL_STACK_DEPLOYMENT_COMPLETE.md",
    "TRADING_APP_DEPLOYMENT_COMPLETE.md",
    "QUICK_ACCESS.md",
    "COST_ANALYSIS_AND_OPTIMIZATION.md",
    "AI_CAPABILITIES_ROADMAP.md",
    "APP_MENU_STRUCTURE.md",
    "COMPLETE_APPLICATION_SUMMARY.md",
    "TRADING_APP_COMPLETION_SUMMARY.md",
    "MULTI_USER_DEPLOYMENT_SUMMARY.md",
    "USER_INVITATION_TEMPLATE.md",
    "DEPLOYMENT_COMPLETE.md",
    "TRADING_APP_UPDATES_PLAN.md",
    "OPTION_2_IMPLEMENTATION_STATUS.md",
    "OPTION_2_COMPLETE.md"
]

PDF_FILES = [
    "THE CANDLESTICK TRADING BIBLE.pdf",
    "Trading Application Requirements Document.pdf",
    "AIAlgoTradeHits.com - Complete Implementation Plan.pdf"
]

DOCX_FILES = [
    "backtesting algorithm.docx",
    "ccxt pro.docx",
    "bitcoin sentiment logic.docx",
    "Crypto Stock Platform comparison.docx",
    "Trading Application Requirements Document.docx",
    "Fibanocci Curves and Elliot wave theory.docx",
    "Newsletter Insights.docx"
]

def create_bucket():
    """Create GCS bucket if it doesn't exist"""
    print(f"Creating bucket: {BUCKET_NAME}...")
    try:
        storage_client = storage.Client(project=PROJECT_ID)

        # Check if bucket exists
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
            print(f"Bucket {BUCKET_NAME} already exists")
            return bucket
        except Exception:
            # Create bucket
            bucket = storage_client.create_bucket(BUCKET_NAME, location="us-central1")
            print(f"Bucket {BUCKET_NAME} created successfully")

            # Make bucket publicly readable
            bucket.make_public(recursive=True, future=True)
            print(f"Bucket {BUCKET_NAME} made public")

            return bucket
    except Exception as e:
        print(f"Error creating bucket: {e}")
        return None

def md_to_html(md_file):
    """Convert markdown to HTML"""
    try:
        with open(BASE_DIR / md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert to HTML with GitHub-flavored markdown
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_file.replace('.md', '')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #24292e;
            background: #ffffff;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        h2 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        code {{
            background-color: rgba(27,31,35,0.05);
            border-radius: 3px;
            font-size: 85%;
            margin: 0;
            padding: 0.2em 0.4em;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            font-size: 85%;
            line-height: 1.45;
            overflow: auto;
            padding: 16px;
        }}
        pre code {{
            background-color: transparent;
            border: 0;
            display: inline;
            line-height: inherit;
            margin: 0;
            overflow: visible;
            padding: 0;
            word-wrap: normal;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}
        table tr:nth-child(2n) {{
            background-color: #f6f8fa;
        }}
        blockquote {{
            border-left: 4px solid #dfe2e5;
            color: #6a737d;
            padding: 0 1em;
            margin: 0;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
{markdown.markdown(md_content, extensions=['extra', 'codehilite', 'tables', 'fenced_code'])}
</body>
</html>"""

        html_file = BASE_DIR / "documents" / "html" / md_file.replace('.md', '.html')
        html_file.parent.mkdir(parents=True, exist_ok=True)

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Converted {md_file} to HTML")
        return html_file
    except Exception as e:
        print(f"Error converting {md_file} to HTML: {e}")
        return None

def upload_to_gcs(local_file, gcs_path, bucket):
    """Upload file to Google Cloud Storage"""
    try:
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_file)

        # Make blob publicly readable
        blob.make_public()

        print(f"Uploaded {local_file} to gs://{BUCKET_NAME}/{gcs_path}")
        return blob.public_url
    except Exception as e:
        print(f"Error uploading {local_file}: {e}")
        return None

def main():
    print("=" * 60)
    print("AI Algo Trade Hits - Document Management System Setup")
    print("=" * 60)

    # Create output directories
    (BASE_DIR / "documents" / "html").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "documents" / "md").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "documents" / "pdf").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "documents" / "docx").mkdir(parents=True, exist_ok=True)

    # Create GCS bucket
    bucket = create_bucket()
    if not bucket:
        print("Failed to create bucket. Exiting.")
        return

    print("\n" + "=" * 60)
    print("Processing Markdown Files")
    print("=" * 60)

    document_manifest = []

    # Process MD files
    for md_file in MD_FILES:
        if not (BASE_DIR / md_file).exists():
            print(f"Skipping {md_file} (not found)")
            continue

        print(f"\nProcessing: {md_file}")

        # Convert to HTML
        html_file = md_to_html(md_file)

        # Upload original MD
        md_url = upload_to_gcs(BASE_DIR / md_file, f"md/{md_file}", bucket)

        # Upload HTML
        html_url = None
        if html_file:
            html_url = upload_to_gcs(html_file, f"html/{html_file.name}", bucket)

        document_manifest.append({
            'title': md_file.replace('.md', '').replace('_', ' ').title(),
            'filename': md_file,
            'type': 'markdown',
            'md_url': md_url,
            'html_url': html_url,
            'category': categorize_document(md_file)
        })

    print("\n" + "=" * 60)
    print("Processing PDF Files")
    print("=" * 60)

    # Process PDF files
    for pdf_file in PDF_FILES:
        if not (BASE_DIR / pdf_file).exists():
            print(f"Skipping {pdf_file} (not found)")
            continue

        print(f"\nProcessing: {pdf_file}")
        pdf_url = upload_to_gcs(BASE_DIR / pdf_file, f"pdf/{pdf_file}", bucket)

        document_manifest.append({
            'title': pdf_file.replace('.pdf', ''),
            'filename': pdf_file,
            'type': 'pdf',
            'pdf_url': pdf_url,
            'category': categorize_document(pdf_file)
        })

    print("\n" + "=" * 60)
    print("Processing DOCX Files")
    print("=" * 60)

    # Process DOCX files
    for docx_file in DOCX_FILES:
        if not (BASE_DIR / docx_file).exists():
            print(f"Skipping {docx_file} (not found)")
            continue

        print(f"\nProcessing: {docx_file}")
        docx_url = upload_to_gcs(BASE_DIR / docx_file, f"docx/{docx_file}", bucket)

        document_manifest.append({
            'title': docx_file.replace('.docx', ''),
            'filename': docx_file,
            'type': 'docx',
            'docx_url': docx_url,
            'category': categorize_document(docx_file)
        })

    # Save manifest
    import json
    manifest_file = BASE_DIR / "documents" / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(document_manifest, f, indent=2)

    # Upload manifest
    upload_to_gcs(manifest_file, "manifest.json", bucket)

    print("\n" + "=" * 60)
    print("Document Upload Summary")
    print("=" * 60)
    print(f"Total documents processed: {len(document_manifest)}")
    print(f"Bucket: gs://{BUCKET_NAME}")
    print(f"Public URL: https://storage.googleapis.com/{BUCKET_NAME}/")
    print("\nManifest uploaded to: manifest.json")
    print("=" * 60)

    # Print IAM instructions
    print("\n" + "=" * 60)
    print("Next Steps: Set IAM Permissions")
    print("=" * 60)
    print("\nRun these commands to grant upload permissions:\n")
    print(f"gsutil iam ch user:haq.irfanul@gmail.com:roles/storage.objectAdmin gs://{BUCKET_NAME}")
    print(f"gsutil iam ch user:saleem26@gmail.com:roles/storage.objectAdmin gs://{BUCKET_NAME}")
    print("\nOr use the Cloud Console:")
    print(f"https://console.cloud.google.com/storage/browser/{BUCKET_NAME}?project={PROJECT_ID}")

def categorize_document(filename):
    """Categorize document based on filename"""
    filename_lower = filename.lower()

    if any(x in filename_lower for x in ['deployment', 'deploy', 'complete', 'status']):
        return 'Deployment'
    elif any(x in filename_lower for x in ['ai', 'capabilities', 'roadmap', 'menu', 'app']):
        return 'Planning & Features'
    elif any(x in filename_lower for x in ['guide', 'quick', 'timeout', 'elliott', 'stock']):
        return 'Technical Guides'
    elif any(x in filename_lower for x in ['cost', 'analysis']):
        return 'Business Analysis'
    elif any(x in filename_lower for x in ['requirements', 'implementation', 'plan']):
        return 'Requirements & Planning'
    elif any(x in filename_lower for x in ['trading', 'candlestick', 'backtest', 'sentiment', 'fibonacci']):
        return 'Trading Education'
    elif any(x in filename_lower for x in ['user', 'invitation', 'multi']):
        return 'User Management'
    else:
        return 'General Documentation'

if __name__ == "__main__":
    main()
