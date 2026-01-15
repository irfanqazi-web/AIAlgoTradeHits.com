#!/usr/bin/env python3
"""Generate PDF from Refactoring Status Report markdown using reportlab"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak
import re

def sanitize_text(text):
    replacements = {
        '\u2193': '->',
        '\u2192': '->',
        '\u2190': '<-',
        '\u2191': '^',
        '\u2022': '*',
        '\u2713': '[x]',
        '\u2717': '[ ]',
        '\u2714': '[x]',
        '\u00b7': '*',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2014': '--',
        '\u2013': '-',
        '\u2026': '...',
        '\u00a0': ' ',
        '`': "'",
        '<': '&lt;',
        '>': '&gt;',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Escape ampersands that aren't already part of HTML entities
    text = re.sub(r'&(?!(lt|gt|amp|quot);)', '&amp;', text)
    return text

def generate_pdf():
    doc = SimpleDocTemplate(
        "REFACTORING_STATUS_REPORT.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='Title1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#006400'),
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Title2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#005000'),
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='Title3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#003c00'),
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='CodeBlock',
        parent=styles['Code'],
        fontSize=8,
        textColor=colors.HexColor('#333333'),
        backColor=colors.HexColor('#f5f5f5'),
        leftIndent=10,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='BulletItem',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='CheckItem',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#006400'),
        leftIndent=20,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='TableText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#333333'),
        spaceAfter=2
    ))

    story = []

    with open('REFACTORING_STATUS_REPORT.md', 'r', encoding='utf-8') as f:
        content = f.read()

    content = sanitize_text(content)
    lines = content.split('\n')

    in_code_block = False

    for line in lines:
        original_line = line
        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        # Handle code blocks
        if line.startswith("'''") or (line.startswith("'") and line.count("'") >= 3):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            story.append(Paragraph(line, styles['CodeBlock']))
            continue

        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['Title1']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['Title2']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['Title3']))
        elif line.startswith('**') and line.endswith('**'):
            text = line.replace('**', '')
            story.append(Paragraph(f'<b>{text}</b>', styles['Normal']))
        elif line.startswith('|') and '|' in line[1:]:
            story.append(Paragraph(line, styles['TableText']))
        elif line.startswith('- [x]'):
            text = line.replace('- [x]', '[DONE]')
            story.append(Paragraph(text, styles['CheckItem']))
        elif line.startswith('- [ ]'):
            text = line.replace('- [ ]', '[PENDING]')
            story.append(Paragraph(text, styles['BulletItem']))
        elif line.startswith('- ') or line.startswith('* '):
            story.append(Paragraph('  ' + line, styles['BulletItem']))
        elif line.startswith('---'):
            story.append(Spacer(1, 10))
        elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.'):
            story.append(Paragraph(line, styles['BulletItem']))
        else:
            story.append(Paragraph(line, styles['Normal']))

    doc.build(story)
    print('PDF generated successfully: REFACTORING_STATUS_REPORT.pdf')

if __name__ == '__main__':
    generate_pdf()
