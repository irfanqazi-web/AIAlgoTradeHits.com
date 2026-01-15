"""
Convert Markdown Documentation to PDF
Creates professional PDF documents from all markdown files
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import subprocess
from pathlib import Path

# Key documentation files to convert
KEY_DOCS = [
    'COMPLETE_APPLICATION_SUMMARY.md',
    'AI_CAPABILITIES_ROADMAP.md',
    'COST_ANALYSIS_AND_OPTIMIZATION.md',
    'APP_MENU_STRUCTURE.md',
    'TRADING_APP_DEPLOYMENT_COMPLETE.md',
    'QUICK_ACCESS.md',
    'CLAUDE.md',
]

def install_pandoc_if_needed():
    """Check if pandoc is installed, provide instructions if not"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        print("✓ Pandoc is installed")
        return True
    except FileNotFoundError:
        print("""
╔════════════════════════════════════════════════════════════╗
║  Pandoc is not installed                                   ║
╚════════════════════════════════════════════════════════════╝

To convert markdown to PDF, please install Pandoc:

Option 1: Download installer
https://pandoc.org/installing.html

Option 2: Using Chocolatey (Windows)
choco install pandoc

Option 3: Using winget
winget install pandoc

After installation, run this script again.
        """)
        return False

def create_html_versions():
    """Create HTML versions as fallback"""
    print("\n" + "="*60)
    print("Creating HTML versions of documentation...")
    print("="*60)

    output_dir = Path('documents')
    output_dir.mkdir(exist_ok=True)

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #10b981;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1e40af;
            margin-top: 30px;
        }}
        h3 {{
            color: #374151;
        }}
        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #1e293b;
            color: #f8fafc;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            color: inherit;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #e5e7eb;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #f3f4f6;
            font-weight: bold;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .note {{
            background: #dbeafe;
            border-left: 4px solid #2563eb;
            padding: 15px;
            margin: 20px 0;
        }}
        .warning {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
        }}
        .success {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
    """

    try:
        import markdown2
        print("Using markdown2 for conversion...")
    except ImportError:
        print("Installing markdown2...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown2'], check=True)
        import markdown2

    for doc_file in KEY_DOCS:
        if not os.path.exists(doc_file):
            print(f"⚠ Skipping {doc_file} (not found)")
            continue

        print(f"\n📄 Converting {doc_file}...")

        try:
            # Read markdown content
            with open(doc_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convert to HTML
            html_content = markdown2.markdown(
                md_content,
                extras=['fenced-code-blocks', 'tables', 'header-ids', 'task_list']
            )

            # Get title from first line
            title = doc_file.replace('.md', '').replace('_', ' ').title()

            # Create full HTML
            full_html = html_template.format(
                title=title,
                content=html_content
            )

            # Write HTML file
            output_file = output_dir / doc_file.replace('.md', '.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)

            print(f"   ✓ Created {output_file}")

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

    print("\n" + "="*60)
    print(f"✓ HTML documentation created in 'documents' folder")
    print("="*60)

def convert_to_pdf_with_pandoc():
    """Convert markdown to PDF using Pandoc"""
    print("\n" + "="*60)
    print("Converting to PDF using Pandoc...")
    print("="*60)

    output_dir = Path('documents')
    output_dir.mkdir(exist_ok=True)

    for doc_file in KEY_DOCS:
        if not os.path.exists(doc_file):
            print(f"⚠ Skipping {doc_file} (not found)")
            continue

        print(f"\n📄 Converting {doc_file}...")

        output_file = output_dir / doc_file.replace('.md', '.pdf')

        try:
            # Pandoc command with better formatting
            cmd = [
                'pandoc',
                doc_file,
                '-o', str(output_file),
                '--pdf-engine=xelatex',
                '-V', 'geometry:margin=1in',
                '-V', 'fontsize=11pt',
                '-V', 'colorlinks=true',
                '--toc',
                '--number-sections'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✓ Created {output_file}")
            else:
                print(f"   ✗ Error: {result.stderr}")
                # Fallback to simple conversion
                simple_cmd = ['pandoc', doc_file, '-o', str(output_file)]
                subprocess.run(simple_cmd, check=True)
                print(f"   ✓ Created {output_file} (simple format)")

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

    print("\n" + "="*60)
    print(f"✓ PDF documentation created in 'documents' folder")
    print("="*60)

def copy_markdown_files():
    """Copy markdown files to documents folder as backup"""
    print("\n" + "="*60)
    print("Copying markdown files...")
    print("="*60)

    output_dir = Path('documents')
    output_dir.mkdir(exist_ok=True)

    import shutil

    for doc_file in KEY_DOCS:
        if os.path.exists(doc_file):
            dest = output_dir / doc_file
            shutil.copy2(doc_file, dest)
            print(f"   ✓ Copied {doc_file}")

    print("\n" + "="*60)
    print(f"✓ Markdown files copied to 'documents' folder")
    print("="*60)

def create_index():
    """Create an index HTML file"""
    output_dir = Path('documents')

    index_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AIAlgoTradeHits.com - Documentation Index</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #2563eb;
            text-align: center;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #6b7280;
            margin-bottom: 40px;
        }
        .doc-list {
            display: grid;
            gap: 20px;
        }
        .doc-item {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }
        .doc-item:hover {
            border-color: #2563eb;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }
        .doc-item h3 {
            margin: 0 0 10px 0;
            color: #1e40af;
        }
        .doc-item p {
            color: #6b7280;
            margin: 0 0 15px 0;
        }
        .doc-links {
            display: flex;
            gap: 10px;
        }
        .doc-links a {
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            font-size: 14px;
        }
        .pdf-link {
            background: #2563eb;
            color: white;
        }
        .html-link {
            background: #10b981;
            color: white;
        }
        .md-link {
            background: #6b7280;
            color: white;
        }
        .pdf-link:hover { background: #1e40af; }
        .html-link:hover { background: #059669; }
        .md-link:hover { background: #4b5563; }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            color: #6b7280;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AIAlgoTradeHits.com</h1>
        <p class="subtitle">Complete Documentation Package</p>

        <div class="doc-list">
            <div class="doc-item">
                <h3>📋 Complete Application Summary</h3>
                <p>Comprehensive overview of the entire platform, features, costs, and roadmap</p>
                <div class="doc-links">
                    <a href="COMPLETE_APPLICATION_SUMMARY.pdf" class="pdf-link">📄 PDF</a>
                    <a href="COMPLETE_APPLICATION_SUMMARY.html" class="html-link">🌐 HTML</a>
                    <a href="COMPLETE_APPLICATION_SUMMARY.md" class="md-link">📝 Markdown</a>
                </div>
            </div>

            <div class="doc-item">
                <h3>🤖 AI Capabilities Roadmap</h3>
                <p>18 AI/ML features with implementation details, code examples, and timelines</p>
                <div class="doc-links">
                    <a href="AI_CAPABILITIES_ROADMAP.pdf" class="pdf-link">📄 PDF</a>
                    <a href="AI_CAPABILITIES_ROADMAP.html" class="html-link">🌐 HTML</a>
                    <a href="AI_CAPABILITIES_ROADMAP.md" class="md-link">📝 Markdown</a>
                </div>
            </div>

            <div class="doc-item">
                <h3>💰 Cost Analysis & Optimization</h3>
                <p>Detailed cost breakdown, revenue projections, and optimization strategies</p>
                <div class="doc-links">
                    <a href="COST_ANALYSIS_AND_OPTIMIZATION.pdf" class="pdf-link">📄 PDF</a>
                    <a href="COST_ANALYSIS_AND_OPTIMIZATION.html" class="html-link">🌐 HTML</a>
                    <a href="COST_ANALYSIS_AND_OPTIMIZATION.md" class="md-link">📝 Markdown</a>
                </div>
            </div>

            <div class="doc-item">
                <h3>📱 App Menu Structure</h3>
                <p>Complete menu system with 200+ features and navigation hierarchy</p>
                <div class="doc-links">
                    <a href="APP_MENU_STRUCTURE.pdf" class="pdf-link">📄 PDF</a>
                    <a href="APP_MENU_STRUCTURE.html" class="html-link">🌐 HTML</a>
                    <a href="APP_MENU_STRUCTURE.md" class="md-link">📝 Markdown</a>
                </div>
            </div>

            <div class="doc-item">
                <h3>🚀 Trading App Deployment</h3>
                <p>Deployment guide with backend API, frontend, and data pipeline details</p>
                <div class="doc-links">
                    <a href="TRADING_APP_DEPLOYMENT_COMPLETE.pdf" class="pdf-link">📄 PDF</a>
                    <a href="TRADING_APP_DEPLOYMENT_COMPLETE.html" class="html-link">🌐 HTML</a>
                    <a href="TRADING_APP_DEPLOYMENT_COMPLETE.md" class="md-link">📝 Markdown</a>
                </div>
            </div>

            <div class="doc-item">
                <h3>⚡ Quick Access Guide</h3>
                <p>Quick reference for URLs, commands, and common operations</p>
                <div class="doc-links">
                    <a href="QUICK_ACCESS.pdf" class="pdf-link">📄 PDF</a>
                    <a href="QUICK_ACCESS.html" class="html-link">🌐 HTML</a>
                    <a href="QUICK_ACCESS.md" class="md-link">📝 Markdown</a>
                </div>
            </div>

            <div class="doc-item">
                <h3>📖 Project Instructions (CLAUDE.md)</h3>
                <p>Project overview, architecture, and key implementation details</p>
                <div class="doc-links">
                    <a href="CLAUDE.pdf" class="pdf-link">📄 PDF</a>
                    <a href="CLAUDE.html" class="html-link">🌐 HTML</a>
                    <a href="CLAUDE.md" class="md-link">📝 Markdown</a>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>AIAlgoTradeHits.com - Complete Documentation Package</strong></p>
            <p>Version 2.0 | Generated on November 11, 2025</p>
            <p>Live App: <a href="https://crypto-trading-app-252370699783.us-central1.run.app" target="_blank">https://crypto-trading-app-252370699783.us-central1.run.app</a></p>
        </div>
    </div>
</body>
</html>
    """

    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

    print(f"\n✓ Created index.html in 'documents' folder")

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     AIAlgoTradeHits.com - Documentation Converter          ║
║                                                            ║
║  Converting markdown documentation to PDF and HTML         ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Copy markdown files
    copy_markdown_files()

    # Step 2: Create HTML versions (always works)
    create_html_versions()

    # Step 3: Create index
    create_index()

    # Step 4: Try PDF conversion with Pandoc
    if install_pandoc_if_needed():
        convert_to_pdf_with_pandoc()
    else:
        print("""
╔════════════════════════════════════════════════════════════╗
║  PDF conversion skipped (Pandoc not installed)             ║
║                                                            ║
║  HTML versions have been created and are ready to use.     ║
║  Open 'documents/index.html' to access all documentation.  ║
║                                                            ║
║  To get PDFs, install Pandoc and run this script again.    ║
╚════════════════════════════════════════════════════════════╝
        """)

    print("""
╔════════════════════════════════════════════════════════════╗
║                    ✓ CONVERSION COMPLETE                   ║
╚════════════════════════════════════════════════════════════╝

📁 All documentation is now in the 'documents' folder:

   ├── index.html                          (START HERE!)
   ├── *.md                                (Original markdown)
   ├── *.html                              (HTML versions)
   └── *.pdf                               (PDF versions, if Pandoc installed)

🌐 To view the documentation:
   1. Open: documents/index.html in your browser
   2. Click any document to view it
   3. Share the entire 'documents' folder as needed

📄 Documents included:
   ✓ Complete Application Summary
   ✓ AI Capabilities Roadmap (18 features)
   ✓ Cost Analysis & Optimization
   ✓ App Menu Structure (200+ features)
   ✓ Trading App Deployment Guide
   ✓ Quick Access Reference
   ✓ Project Instructions (CLAUDE.md)

    """)

if __name__ == '__main__':
    main()
