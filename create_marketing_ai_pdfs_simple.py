"""
Convert Marketing AI Democratization documents to PDF using reportlab
Windows-compatible solution
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from pathlib import Path
import re

def clean_markdown(text):
    """Remove markdown syntax for plain text conversion"""
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text

def markdown_to_pdf_simple(md_file, pdf_file, title):
    """Convert markdown to PDF using reportlab"""

    print(f"\nGenerating PDF: {pdf_file}")

    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=20,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
        fontName='Helvetica'
    )

    # Build story
    story = []

    # Add title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("AIAlgoTradeHits.com", body_style))
    story.append(Paragraph("December 10, 2025", body_style))
    story.append(PageBreak())

    # Process content
    in_code_block = False
    current_section = []

    for line in lines:
        line = line.strip()

        if not line:
            if current_section:
                story.append(Spacer(1, 0.1*inch))
            continue

        # Skip code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Headers
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, h1_style))

        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, h1_style))

        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, h2_style))

        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Remove markdown syntax
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(f"• {text}", bullet_style))

        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line)
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(f"• {text}", bullet_style))

        # Horizontal rule
        elif line.startswith('---'):
            story.append(Spacer(1, 0.2*inch))

        # Regular paragraph
        else:
            # Skip special markdown elements
            if not line.startswith('**') and not line.startswith('|'):
                # Remove markdown syntax
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                text = re.sub(r'`(.+?)`', r'<i>\1</i>', text)
                story.append(Paragraph(text, body_style))

    # Build PDF
    try:
        doc.build(story)
        file_size = pdf_file.stat().st_size // 1024
        print(f"✓ PDF created successfully: {pdf_file.name} ({file_size} KB)")
        return True
    except Exception as e:
        print(f"✗ Error creating PDF: {e}")
        return False

def main():
    """Convert both Marketing AI documents to PDF"""

    base_dir = Path(r"C:\1AITrading\Trading")

    print("="*80)
    print("MARKETING AI DEMOCRATIZATION PLATFORM - PDF GENERATION")
    print("="*80)

    success_count = 0

    # Document 1: Vision
    vision_md = base_dir / "MARKETING_AI_DEMOCRATIZATION_VISION.md"
    vision_pdf = base_dir / "MARKETING_AI_DEMOCRATIZATION_VISION.pdf"

    if vision_md.exists():
        if markdown_to_pdf_simple(
            vision_md,
            vision_pdf,
            "Marketing AI Democratization Platform - Vision Document"
        ):
            success_count += 1
    else:
        print(f"✗ Vision document not found: {vision_md}")

    # Document 2: Implementation
    impl_md = base_dir / "MARKETING_AI_DEMOCRATIZATION_IMPLEMENTATION.md"
    impl_pdf = base_dir / "MARKETING_AI_DEMOCRATIZATION_IMPLEMENTATION.pdf"

    if impl_md.exists():
        if markdown_to_pdf_simple(
            impl_md,
            impl_pdf,
            "Marketing AI Democratization Platform - Implementation Plan"
        ):
            success_count += 1
    else:
        print(f"✗ Implementation document not found: {impl_md}")

    print("\n" + "="*80)
    print("PDF GENERATION COMPLETE")
    print("="*80)
    print(f"\nSuccess: {success_count}/2 documents created")

    if success_count > 0:
        print("\nCreated PDFs:")
        if vision_pdf.exists():
            print(f"1. {vision_pdf.name} ({vision_pdf.stat().st_size // 1024} KB)")
        if impl_pdf.exists():
            print(f"2. {impl_pdf.name} ({impl_pdf.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
