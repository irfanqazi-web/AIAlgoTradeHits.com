import markdown
from pathlib import Path

# Read markdown
md_content = Path('C:/1AITrading/Trading/COMPLETE_TICKER_REFERENCE.md').read_text(encoding='utf-8')

# Convert to HTML
html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Create full HTML document
full_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Complete Ticker Reference - AIAlgoTradeHits</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 40px; }}
h1 {{ color: #1e293b; border-bottom: 3px solid #10b981; padding-bottom: 10px; }}
h2 {{ color: #334155; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; margin-top: 30px; }}
h3 {{ color: #475569; margin-top: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #e2e8f0; padding: 10px 12px; text-align: left; }}
th {{ background: #f1f5f9; font-weight: 600; }}
tr:nth-child(even) {{ background: #f8fafc; }}
code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #0f172a; }}
strong {{ color: #1e293b; }}
hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }}
@media print {{
    body {{ margin: 20px; }}
    h1 {{ page-break-after: avoid; }}
    h2 {{ page-break-after: avoid; }}
    table {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>
{html}
</body>
</html>'''

# Save HTML
Path('C:/1AITrading/Trading/COMPLETE_TICKER_REFERENCE.html').write_text(full_html, encoding='utf-8')
print('HTML created successfully: C:/1AITrading/Trading/COMPLETE_TICKER_REFERENCE.html')
print('Open in browser and use Print to PDF to create PDF version')
