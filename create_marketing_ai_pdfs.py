"""
Convert Marketing AI Democratization documents to PDF
Uses markdown2 and weasyprint for professional PDF generation
"""

import markdown2
from weasyprint import HTML, CSS
from pathlib import Path

def markdown_to_pdf(md_file, pdf_file, title):
    """Convert markdown file to PDF with professional styling"""

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=[
        'tables',
        'fenced-code-blocks',
        'code-friendly',
        'header-ids',
        'toc'
    ])

    # Professional CSS styling
    css_style = """
    @page {
        size: letter;
        margin: 1in 0.75in;
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9pt;
            color: #666;
        }
    }

    body {
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }

    h1 {
        font-size: 24pt;
        font-weight: bold;
        color: #1a73e8;
        margin-top: 20pt;
        margin-bottom: 12pt;
        page-break-after: avoid;
    }

    h2 {
        font-size: 18pt;
        font-weight: bold;
        color: #1a73e8;
        margin-top: 16pt;
        margin-bottom: 10pt;
        page-break-after: avoid;
        border-bottom: 2px solid #e8eaed;
        padding-bottom: 5pt;
    }

    h3 {
        font-size: 14pt;
        font-weight: bold;
        color: #333;
        margin-top: 12pt;
        margin-bottom: 8pt;
        page-break-after: avoid;
    }

    h4 {
        font-size: 12pt;
        font-weight: bold;
        color: #555;
        margin-top: 10pt;
        margin-bottom: 6pt;
    }

    p {
        margin-bottom: 8pt;
        text-align: justify;
    }

    ul, ol {
        margin-bottom: 10pt;
        padding-left: 25pt;
    }

    li {
        margin-bottom: 4pt;
    }

    code {
        font-family: "Courier New", monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 2pt 4pt;
        border-radius: 3pt;
    }

    pre {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 5pt;
        padding: 10pt;
        margin: 10pt 0;
        overflow-x: auto;
        page-break-inside: avoid;
    }

    pre code {
        background-color: transparent;
        padding: 0;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 10pt 0;
        page-break-inside: avoid;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8pt;
        text-align: left;
    }

    th {
        background-color: #1a73e8;
        color: white;
        font-weight: bold;
    }

    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    blockquote {
        border-left: 4pt solid #1a73e8;
        padding-left: 15pt;
        margin-left: 0;
        color: #666;
        font-style: italic;
    }

    hr {
        border: none;
        border-top: 2px solid #e8eaed;
        margin: 20pt 0;
    }

    a {
        color: #1a73e8;
        text-decoration: none;
    }

    strong {
        font-weight: bold;
        color: #000;
    }

    em {
        font-style: italic;
    }

    .page-break {
        page-break-before: always;
    }
    """

    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>{css_style}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generate PDF
    print(f"Generating PDF: {pdf_file}")
    HTML(string=full_html).write_pdf(pdf_file)
    print(f"✓ PDF created successfully: {pdf_file}")

def main():
    """Convert both Marketing AI documents to PDF"""

    base_dir = Path(r"C:\1AITrading\Trading")

    # Document 1: Vision
    vision_md = base_dir / "MARKETING_AI_DEMOCRATIZATION_VISION.md"
    vision_pdf = base_dir / "MARKETING_AI_DEMOCRATIZATION_VISION.pdf"

    if vision_md.exists():
        markdown_to_pdf(
            vision_md,
            vision_pdf,
            "Marketing AI Democratization Platform - Vision Document"
        )
    else:
        print(f"✗ Vision document not found: {vision_md}")

    # Document 2: Implementation
    impl_md = base_dir / "MARKETING_AI_DEMOCRATIZATION_IMPLEMENTATION.md"
    impl_pdf = base_dir / "MARKETING_AI_DEMOCRATIZATION_IMPLEMENTATION.pdf"

    if impl_md.exists():
        markdown_to_pdf(
            impl_md,
            impl_pdf,
            "Marketing AI Democratization Platform - Implementation Plan"
        )
    else:
        print(f"✗ Implementation document not found: {impl_md}")

    print("\n" + "="*80)
    print("PDF GENERATION COMPLETE")
    print("="*80)
    print(f"\nDocuments created:")
    if vision_pdf.exists():
        print(f"1. {vision_pdf.name} ({vision_pdf.stat().st_size // 1024} KB)")
    if impl_pdf.exists():
        print(f"2. {impl_pdf.name} ({impl_pdf.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
