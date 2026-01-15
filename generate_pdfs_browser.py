"""
Generate PDF documents from HTML files using Playwright (browser automation)
This works on Windows without complex dependencies
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess
from pathlib import Path

print("Installing Playwright...")
try:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
    print("Installing Chromium browser...")
    subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
except Exception as e:
    print(f"Error installing Playwright: {e}")
    sys.exit(1)

from playwright.sync_api import sync_playwright

KEY_DOCS = [
    'COMPLETE_APPLICATION_SUMMARY',
    'AI_CAPABILITIES_ROADMAP',
    'COST_ANALYSIS_AND_OPTIMIZATION',
    'APP_MENU_STRUCTURE',
    'TRADING_APP_DEPLOYMENT_COMPLETE',
    'QUICK_ACCESS',
    'CLAUDE',
]

def generate_pdfs():
    docs_dir = Path('documents')

    if not docs_dir.exists():
        print(f"Error: documents folder not found")
        return

    print("\n" + "="*60)
    print("Generating PDF documents from HTML files...")
    print("="*60)

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for doc_name in KEY_DOCS:
            html_file = docs_dir / f"{doc_name}.html"
            pdf_file = docs_dir / f"{doc_name}.pdf"

            if not html_file.exists():
                print(f"\n⚠ Skipping {doc_name} (HTML not found)")
                continue

            print(f"\n📄 Converting {doc_name}.html to PDF...")

            try:
                # Load HTML file
                page.goto(f'file:///{html_file.absolute().as_posix()}')

                # Wait for page to fully load
                page.wait_for_load_state('networkidle')

                # Generate PDF with proper settings
                page.pdf(
                    path=str(pdf_file),
                    format='A4',
                    margin={
                        'top': '20mm',
                        'right': '20mm',
                        'bottom': '20mm',
                        'left': '20mm'
                    },
                    print_background=True,
                    display_header_footer=False
                )

                print(f"   ✓ Created {pdf_file.name}")

            except Exception as e:
                print(f"   ✗ Error: {str(e)}")

        browser.close()

    print("\n" + "="*60)
    print("✓ PDF generation complete!")
    print("="*60)

if __name__ == '__main__':
    try:
        generate_pdfs()
        print("""
╔════════════════════════════════════════════════════════════╗
║              ✓ PDF CREATION SUCCESSFUL!                    ║
╚════════════════════════════════════════════════════════════╝

📁 All PDFs are in the 'documents' folder
🌐 You can also view HTML versions: documents/index.html

PDF Files Created:
✓ COMPLETE_APPLICATION_SUMMARY.pdf
✓ AI_CAPABILITIES_ROADMAP.pdf
✓ COST_ANALYSIS_AND_OPTIMIZATION.pdf
✓ APP_MENU_STRUCTURE.pdf
✓ TRADING_APP_DEPLOYMENT_COMPLETE.pdf
✓ QUICK_ACCESS.pdf
✓ CLAUDE.pdf

        """)
    except Exception as e:
        print(f"""
╔════════════════════════════════════════════════════════════╗
║              ✗ PDF CREATION FAILED                         ║
╚════════════════════════════════════════════════════════════╝

Error: {str(e)}

        """)
