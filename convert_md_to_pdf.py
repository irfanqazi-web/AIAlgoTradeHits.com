"""
Convert all Markdown files to PDF using fpdf2
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import subprocess
import re

# Install required packages
subprocess.run([sys.executable, '-m', 'pip', 'install', 'fpdf2', '-q'], capture_output=True)
subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown', '-q'], capture_output=True)

from fpdf import FPDF
import markdown
from html.parser import HTMLParser

# Base directory
BASE_DIR = r'C:\1AITrading\Trading'

# List of MD files to convert (Trading folder only)
MD_FILES = [
    'TWELVEDATA_COMPLETE_INDICATORS.md',
    'TWELVEDATA_INDICATORS_LIST.md',
    'STRATEGY_TWELVEDATA_ONLY.md',
    'CLAUDE.md',
    'CLAUDE_MEMORY.md',
    'README.md',
    'QUICK_START_GUIDE.md',
    'QUICK_ACCESS.md',
    'COMPLETE_APPLICATION_SUMMARY.md',
    'TRADING_APP_COMPLETION_SUMMARY.md',
    'TRADING_APP_DEPLOYMENT_COMPLETE.md',
    'FINAL_DEPLOYMENT_COMPLETE.md',
    'DEPLOYMENT_COMPLETE.md',
    'COST_ANALYSIS_AND_OPTIMIZATION.md',
    'COST_ANALYSIS_AND_SUBSCRIPTIONS.md',
    'AI_CAPABILITIES_ROADMAP.md',
    'APP_MENU_STRUCTURE.md',
    'MASTER_TRADING_IMPLEMENTATION_PLAN.md',
    'NLP_SEARCH_ENGINE_DESIGN.md',
    'NLP_SEARCH_USER_GUIDE.md',
    'STOCK_DATA_SOURCE_RECOMMENDATION.md',
    'VERTEX_AI_COST_BREAKDOWN.md',
    'GEMINI_3_PRO_COST_BREAKDOWN.md',
    'US_STOCK_IMPLEMENTATION_PLAN.md',
    'TWELVE_DATA_COUNTRIES.md',
    'LOCALHOST_TESTING_GUIDE.md',
    'TESTING_INSTRUCTIONS.md',
    'MULTI_USER_DEPLOYMENT_SUMMARY.md',
    'USER_INVITATION_TEMPLATE.md',
    'DAILY_CRYPTO_FETCHER_SUMMARY.md',
    'DEPLOYMENT_STATUS_REPORT.md',
    'COMPLETE_DEPLOYMENT_SUMMARY.md',
    'CRYPTOBOT_DEPLOYMENT_COMPLETE.md',
    'FINAL_DEPLOYMENT_STATUS.md',
    'DEPLOYMENT_COMPLETE_STATUS.md',
    'FINAL_COMPLETION_REPORT.md',
    'TIMEOUT_FIX_GUIDE.md',
    'ELLIOTT_WAVE_DEPLOYMENT_GUIDE.md',
    'STOCK_DEPLOYMENT_GUIDE.md',
    'STOCK_PIPELINE_COMPLETE.md',
    'DEPLOY_STOCK_FUNCTION.md',
    'COMPLETE_PROJECT_STATUS.md',
    'STOCK_FUNCTION_DEPLOYMENT_COMPLETE.md',
    'FULL_STACK_DEPLOYMENT_COMPLETE.md',
    'TRADING_APP_UPDATES_PLAN.md',
    'OPTION_2_IMPLEMENTATION_STATUS.md',
    'OPTION_2_COMPLETE.md',
    'BACKEND_FRONTEND_INTEGRATION_STATUS.md',
    'FRONTEND_FIX_COMPLETE.md',
    'OVERNIGHT_FIX_SUMMARY.md',
    'STOCK_CRYPTO_FIX_COMPLETE.md',
    'NLP_AND_SCHEDULER_STATUS.md',
    'COMPLETE_SESSION_SUMMARY.md',
    'SESSION_COMPLETION_SUMMARY_NOV16.md',
    'SEARCH_BAR_AND_INDICATORS_FIX.md',
    'TRADINGVIEW_CHART_REDESIGN_COMPLETE.md',
    'COMPLETE_CHART_REDESIGN_NOV16.md',
    'TABLE_RENAMING_STRATEGY.md',
    'DATA_ISSUES_REPORT.md',
    'COMPREHENSIVE_TEST_REPORT.md',
    'AI_FEATURES_DEPLOYMENT_GUIDE.md',
    'AI_FEATURES_IMPLEMENTATION_SUMMARY.md',
    'ADMIN_MONITORING_DEPLOYMENT_GUIDE.md',
    'TEST_DATA_SETUP_COMPLETE.md',
    'DEBUG_DAILY_CHARTS.md',
]


class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_title(self, title):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(26, 54, 93)
        self.multi_cell(0, 10, title)
        self.set_draw_color(49, 130, 206)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def add_h2(self, text):
        self.ln(5)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(44, 82, 130)
        self.multi_cell(0, 8, text)
        self.ln(2)

    def add_h3(self, text):
        self.ln(3)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(43, 108, 176)
        self.multi_cell(0, 7, text)
        self.ln(2)

    def add_paragraph(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(51, 51, 51)
        # Truncate extremely long lines (usually URLs)
        if len(text) > 500:
            text = text[:500] + '...'
        self.multi_cell(0, 6, text)
        self.ln(2)

    def add_code(self, text):
        self.set_font('Courier', '', 7)  # Smaller font for code
        self.set_fill_color(245, 245, 245)
        self.set_text_color(51, 51, 51)
        # Wrap long lines at 105 characters to fit page width with smaller font
        wrapped_lines = []
        for line in text.split('\n'):
            # First check for extremely long unbreakable segments
            if len(line) > 105:
                words = line.split(' ')
                current_line = ''
                for word in words:
                    # Break very long words
                    while len(word) > 50:
                        if current_line:
                            wrapped_lines.append(current_line)
                            current_line = ''
                        wrapped_lines.append(word[:50])
                        word = word[50:]
                    # Add word to current line or start new line
                    if len(current_line) + len(word) + 1 <= 105:
                        current_line = current_line + ' ' + word if current_line else word
                    else:
                        if current_line:
                            wrapped_lines.append(current_line)
                        current_line = '  ' + word
                if current_line:
                    wrapped_lines.append(current_line)
            else:
                wrapped_lines.append(line)
        self.multi_cell(0, 3.5, '\n'.join(wrapped_lines), fill=True)
        self.ln(2)

    def add_bullet(self, text, level=0):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(51, 51, 51)
        indent = 10 + (level * 5)
        bullet = '  ' * level + '- '  # Use simple dash instead of Unicode bullet
        self.set_x(indent)
        self.multi_cell(0, 6, bullet + text)


def wrap_long_words(text, max_length=80):
    """Break long words/URLs that would overflow the page"""
    words = text.split(' ')
    result = []
    for word in words:
        while len(word) > max_length:
            result.append(word[:max_length])
            word = word[max_length:]
        result.append(word)
    return ' '.join(result)


def clean_text(text):
    """Clean text for PDF output"""
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Inline code
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
    text = re.sub(r'#+\s*', '', text)  # Headers
    text = text.replace('\\n', '\n')

    # Replace Unicode characters with ASCII equivalents
    replacements = {
        '•': '-',
        '●': '-',
        '○': '-',
        '◦': '-',
        '▪': '-',
        '▫': '-',
        '→': '->',
        '←': '<-',
        '↓': 'v',
        '↑': '^',
        '✓': '[x]',
        '✔': '[x]',
        '✗': '[ ]',
        '✘': '[ ]',
        '❌': '[X]',
        '✅': '[OK]',
        '⚠': '[!]',
        '⚡': '*',
        '🔒': '[lock]',
        '🔓': '[unlock]',
        '📁': '[folder]',
        '📂': '[folder]',
        '📄': '[file]',
        '📝': '[note]',
        '💡': '[idea]',
        '🚀': '[rocket]',
        '🎯': '[target]',
        '⭐': '*',
        '★': '*',
        '☆': '*',
        '│': '|',
        '┌': '+',
        '┐': '+',
        '└': '+',
        '┘': '+',
        '├': '+',
        '┤': '+',
        '┬': '+',
        '┴': '+',
        '┼': '+',
        '─': '-',
        '═': '=',
        '║': '|',
        '╔': '+',
        '╗': '+',
        '╚': '+',
        '╝': '+',
        '╠': '+',
        '╣': '+',
        '╦': '+',
        '╩': '+',
        '╬': '+',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        '–': '-',
        '—': '--',
        '©': '(c)',
        '®': '(R)',
        '™': '(TM)',
        '°': 'deg',
        '±': '+/-',
        '×': 'x',
        '÷': '/',
        '≈': '~',
        '≠': '!=',
        '≤': '<=',
        '≥': '>=',
        '∞': 'inf',
    }

    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)

    # Handle special characters - encode to latin-1 with replacement
    text = text.encode('latin-1', 'replace').decode('latin-1')

    # Break long words that would overflow the page
    text = wrap_long_words(text, 80)

    return text.strip()


def convert_md_to_pdf(md_path, pdf_path):
    """Convert a markdown file to PDF"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pdf = MarkdownPDF()
        lines = content.split('\n')

        in_code_block = False
        code_buffer = []

        for line in lines:
            try:
                # Code blocks
                if line.strip().startswith('```'):
                    if in_code_block:
                        if code_buffer:
                            try:
                                pdf.add_code('\n'.join(code_buffer))
                            except Exception:
                                # Skip problematic code blocks
                                pdf.add_paragraph("[Code block omitted - too wide for PDF]")
                        code_buffer = []
                    in_code_block = not in_code_block
                    continue

                if in_code_block:
                    code_buffer.append(clean_text(line))
                    continue

                # Headers
                if line.startswith('# '):
                    pdf.add_title(clean_text(line[2:]))
                elif line.startswith('## '):
                    pdf.add_h2(clean_text(line[3:]))
                elif line.startswith('### '):
                    pdf.add_h3(clean_text(line[4:]))
                # Bullets
                elif line.strip().startswith('- ') or line.strip().startswith('* '):
                    level = (len(line) - len(line.lstrip())) // 2
                    text = line.strip()[2:]
                    pdf.add_bullet(clean_text(text), level)
                elif re.match(r'^\d+\.\s', line.strip()):
                    text = re.sub(r'^\d+\.\s*', '', line.strip())
                    pdf.add_bullet(clean_text(text))
                # Empty lines
                elif not line.strip():
                    pdf.ln(3)
                # Regular paragraphs
                else:
                    text = clean_text(line)
                    if text:
                        pdf.add_paragraph(text)
            except Exception:
                # Skip problematic lines
                continue

        pdf.output(pdf_path)
        return True

    except Exception as e:
        print(f"    Error: {e}")
        return False


def main():
    print("=" * 60)
    print("CONVERTING MARKDOWN FILES TO PDF")
    print("=" * 60)

    # Create output directory
    pdf_dir = os.path.join(BASE_DIR, 'pdf_documents')
    os.makedirs(pdf_dir, exist_ok=True)

    success = 0
    failed = 0
    skipped = 0

    for md_file in MD_FILES:
        md_path = os.path.join(BASE_DIR, md_file)

        if not os.path.exists(md_path):
            skipped += 1
            continue

        pdf_file = md_file.replace('.md', '.pdf')
        pdf_path = os.path.join(pdf_dir, pdf_file)

        print(f"Converting: {md_file}")

        if convert_md_to_pdf(md_path, pdf_path):
            print(f"  -> {pdf_file}")
            success += 1
        else:
            print(f"  FAILED")
            failed += 1

    print("\n" + "=" * 60)
    print(f"CONVERSION COMPLETE")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Skipped (not found): {skipped}")
    print(f"Output directory: {pdf_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
