"""
Generate PDF Documentation for Gemini 2.5 Training
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fpdf import FPDF
from datetime import datetime
import os
import re

class TradingPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'AIAlgoTradeHits Trading Documentation', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(text):
    """Remove markdown formatting"""
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text

def create_pdf(md_file, pdf_file, title):
    """Convert markdown file to PDF"""
    print(f'Creating PDF: {pdf_file}')

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = TradingPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.cell(0, 30, '', 0, 1)
    pdf.multi_cell(0, 15, title, 0, 'C')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 14)
    pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Developer: irfan.qazi@aialgotradehits.com', 0, 1, 'C')

    pdf.add_page()

    # Process content
    lines = content.split('\n')
    in_code_block = False

    for line in lines:
        line = line.rstrip()

        # Handle code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                pdf.set_fill_color(240, 240, 240)
            continue

        if in_code_block:
            pdf.set_font('Courier', '', 8)
            pdf.set_text_color(50, 50, 50)
            safe_line = line[:100].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 4, safe_line)
            continue

        # Headers
        if line.startswith('# '):
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(26, 54, 93)
            safe_text = clean_text(line[2:])[:80].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 12, safe_text, 0, 1)
            pdf.ln(5)
        elif line.startswith('## '):
            pdf.ln(8)
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(44, 82, 130)
            safe_text = clean_text(line[3:])[:80].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 10, safe_text, 0, 1)
            pdf.ln(3)
        elif line.startswith('### '):
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(43, 108, 176)
            safe_text = clean_text(line[4:])[:80].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 8, safe_text, 0, 1)
        elif line.startswith('---'):
            pdf.ln(3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
        elif line.startswith('|'):
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and not all(c.replace('-', '') == '' for c in cells):
                cell_text = ' | '.join(cells[:4])
                safe_text = cell_text[:100].encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, safe_text)
        elif line.startswith('- '):
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            safe_text = clean_text(line[2:])[:150].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, '  * ' + safe_text)
        elif line.strip():
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            safe_text = clean_text(line)[:200].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, safe_text)

    pdf.output(pdf_file)
    print(f'Created: {pdf_file} ({os.path.getsize(pdf_file) / 1024:.1f} KB)')

def main():
    docs = [
        ('TRADING_TABLE_DOCUMENTATION.md', 'TRADING_TABLE_DOCUMENTATION.pdf', 'Trading Table Documentation'),
        ('AGENTIC_TEXT_TO_SQL_STRATEGY.md', 'AGENTIC_TEXT_TO_SQL_STRATEGY.pdf', 'Agentic Text-to-SQL Strategy'),
        ('GCP_ADK_IMPLEMENTATION_GUIDE.md', 'GCP_ADK_IMPLEMENTATION_GUIDE.pdf', 'GCP ADK Implementation Guide'),
    ]

    print('=' * 60)
    print('Creating PDF Documentation Package')
    print('=' * 60)

    for md_file, pdf_file, title in docs:
        if os.path.exists(md_file):
            try:
                create_pdf(md_file, pdf_file, title)
            except Exception as e:
                print(f'Error converting {md_file}: {e}')
        else:
            print(f'File not found: {md_file}')

    print('=' * 60)
    print('PDF generation complete!')

if __name__ == "__main__":
    main()
