"""
Convert REFACTORING_STATUS_REPORT.md to PDF
Handles Unicode characters by sanitizing text
"""

from fpdf import FPDF
import re

def sanitize_text(text):
    """Replace Unicode characters with ASCII equivalents"""
    replacements = {
        '\u2193': '->',      # ↓ down arrow
        '\u2192': '->',      # → right arrow
        '\u2190': '<-',      # ← left arrow
        '\u2191': '^',       # ↑ up arrow
        '\u2713': '[x]',     # ✓ check mark
        '\u2717': '[ ]',     # ✗ x mark
        '\u2022': '*',       # • bullet
        '\u26a0': '[!]',     # ⚠ warning
        '\u2714': '[x]',     # ✔ check
        '\u2718': '[ ]',     # ✘ x mark
        '\u2026': '...',     # … ellipsis
        '\u201c': '"',       # " left quote
        '\u201d': '"',       # " right quote
        '\u2018': "'",       # ' left single quote
        '\u2019': "'",       # ' right single quote
        '\u2014': '--',      # — em dash
        '\u2013': '-',       # – en dash
        '\u00a0': ' ',       # non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove any remaining non-ASCII characters
    text = text.encode('ascii', 'replace').decode('ascii')
    return text

class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'AIAlgoTradeHits Trading App - Refactoring Status Report', align='C', new_x='LMARGIN', new_y='NEXT')

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title, level=1):
        title = sanitize_text(title)
        if level == 1:
            self.set_font('Helvetica', 'B', 18)
            self.set_text_color(16, 185, 129)  # Emerald
        elif level == 2:
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(59, 130, 246)  # Blue
        elif level == 3:
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(50, 50, 50)
        else:
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(70, 70, 70)

        self.ln(4)
        self.multi_cell(0, 8, title)
        self.ln(2)

    def body_text(self, text):
        text = sanitize_text(text)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, code):
        code = sanitize_text(code)
        self.set_font('Courier', '', 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(50, 50, 50)
        self.ln(2)
        for line in code.split('\n'):
            if line.strip():
                self.cell(0, 5, '  ' + line[:80], fill=True, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def table_row(self, cells, is_header=False):
        cells = [sanitize_text(c) for c in cells]
        self.set_font('Helvetica', 'B' if is_header else '', 9)
        if is_header:
            self.set_fill_color(59, 130, 246)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(248, 250, 252)
            self.set_text_color(30, 30, 30)

        col_width = (self.w - 20) / max(len(cells), 1)
        for cell in cells:
            self.cell(col_width, 7, cell[:35], border=1, fill=True)
        self.ln()

    def bullet_point(self, text, indent=0):
        text = sanitize_text(text)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        x = 10 + indent * 5
        self.set_x(x)
        self.cell(5, 6, '*')
        self.multi_cell(0, 6, text)

def parse_markdown_to_pdf(md_file, pdf_file):
    """Parse markdown and generate PDF"""

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = MarkdownPDF()

    lines = content.split('\n')
    in_code_block = False
    code_buffer = []
    in_table = False
    table_rows = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block handling
        if line.startswith('```'):
            if in_code_block:
                pdf.code_block('\n'.join(code_buffer))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Table handling
        if '|' in line and not line.startswith('```'):
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells and not all(c.replace('-', '').replace(':', '') == '' for c in cells):
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(cells)
            elif in_table and all(c.replace('-', '').replace(':', '') == '' for c in cells):
                # Separator row, skip
                pass
            i += 1
            continue
        elif in_table:
            # End of table
            if table_rows:
                for idx, row in enumerate(table_rows):
                    pdf.table_row(row, is_header=(idx == 0))
                pdf.ln(3)
            in_table = False
            table_rows = []

        # Headers
        if line.startswith('# '):
            pdf.chapter_title(line[2:].strip(), level=1)
        elif line.startswith('## '):
            pdf.chapter_title(line[3:].strip(), level=2)
        elif line.startswith('### '):
            pdf.chapter_title(line[4:].strip(), level=3)
        elif line.startswith('#### '):
            pdf.chapter_title(line[5:].strip(), level=4)
        # Bullet points
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            indent = len(line) - len(line.lstrip())
            text = line.strip()[2:]
            pdf.bullet_point(text, indent // 2)
        elif line.strip().startswith('1. ') or re.match(r'^\d+\. ', line.strip()):
            text = re.sub(r'^\d+\. ', '', line.strip())
            pdf.bullet_point(text)
        # Horizontal rule
        elif line.strip() in ['---', '***', '___']:
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
            pdf.ln(5)
        # Bold text handling
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(30, 30, 30)
            text = sanitize_text(line.strip()[2:-2])
            pdf.multi_cell(0, 6, text)
            pdf.ln(2)
        # Empty lines
        elif not line.strip():
            pdf.ln(2)
        # Regular text
        else:
            # Clean markdown formatting
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)
            if text.strip():
                pdf.body_text(text)

        i += 1

    # Handle any remaining table
    if in_table and table_rows:
        for idx, row in enumerate(table_rows):
            pdf.table_row(row, is_header=(idx == 0))

    pdf.output(pdf_file)
    print(f"PDF created successfully: {pdf_file}")

if __name__ == '__main__':
    md_file = r'C:\1AITrading\Trading\REFACTORING_STATUS_REPORT.md'
    pdf_file = r'C:\1AITrading\Trading\REFACTORING_STATUS_REPORT.pdf'
    parse_markdown_to_pdf(md_file, pdf_file)
