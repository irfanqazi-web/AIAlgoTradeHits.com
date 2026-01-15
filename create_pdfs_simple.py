"""
Create PDF documentation using weasyprint (Python library)
Simpler alternative to Pandoc
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess

print("Installing required packages...")
subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown2', 'weasyprint'], check=True)

from pathlib import Path
import markdown2
from weasyprint import HTML, CSS

KEY_DOCS = [
    'COMPLETE_APPLICATION_SUMMARY.md',
    'AI_CAPABILITIES_ROADMAP.md',
    'COST_ANALYSIS_AND_OPTIMIZATION.md',
    'APP_MENU_STRUCTURE.md',
    'TRADING_APP_DEPLOYMENT_COMPLETE.md',
    'QUICK_ACCESS.md',
    'CLAUDE.md',
]

CSS_STYLE = """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #2563eb;
    border-bottom: 3px solid #10b981;
    padding-bottom: 10px;
    page-break-after: avoid;
}

h2 {
    color: #1e40af;
    margin-top: 30px;
    page-break-after: avoid;
}

h3 {
    color: #374151;
    page-break-after: avoid;
}

code {
    background: #f3f4f6;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

pre {
    background: #1e293b;
    color: #f8fafc;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    page-break-inside: avoid;
}

pre code {
    background: none;
    color: inherit;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #e5e7eb;
    padding: 12px;
    text-align: left;
}

th {
    background: #f3f4f6;
    font-weight: bold;
}

a {
    color: #2563eb;
    text-decoration: none;
}

blockquote {
    border-left: 4px solid #2563eb;
    padding-left: 15px;
    margin-left: 0;
    color: #6b7280;
    font-style: italic;
}

ul, ol {
    margin-left: 20px;
}

.page-break {
    page-break-after: always;
}
"""

def convert_to_pdf():
    output_dir = Path('documents')
    output_dir.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("Converting documentation to PDF...")
    print("="*60)

    for doc_file in KEY_DOCS:
        if not Path(doc_file).exists():
            print(f"⚠ Skipping {doc_file} (not found)")
            continue

        print(f"\n📄 Converting {doc_file}...")

        try:
            # Read markdown
            with open(doc_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convert to HTML
            html_content = markdown2.markdown(
                md_content,
                extras=['fenced-code-blocks', 'tables', 'header-ids', 'task_list']
            )

            # Create full HTML with styling
            full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{doc_file.replace('.md', '').replace('_', ' ').title()}</title>
</head>
<body>
    {html_content}
</body>
</html>
            """

            # Convert to PDF
            output_file = output_dir / doc_file.replace('.md', '.pdf')
            HTML(string=full_html).write_pdf(
                output_file,
                stylesheets=[CSS(string=CSS_STYLE)]
            )

            print(f"   ✓ Created {output_file}")

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

    print("\n" + "="*60)
    print("✓ PDF conversion complete!")
    print("="*60)

if __name__ == '__main__':
    try:
        convert_to_pdf()
        print("""
╔════════════════════════════════════════════════════════════╗
║              ✓ PDF CREATION SUCCESSFUL!                    ║
╚════════════════════════════════════════════════════════════╝

📁 All PDFs are in the 'documents' folder
🌐 Open documents/index.html to access all documentation

        """)
    except Exception as e:
        print(f"""
╔════════════════════════════════════════════════════════════╗
║              ✗ PDF CREATION FAILED                         ║
╚════════════════════════════════════════════════════════════╝

Error: {str(e)}

Don't worry! HTML versions are already created and work perfectly.
Open: documents/index.html

        """)
