"""
Create PDF Guide for AI Model Training Docs Feature
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def create_pdf():
    doc = SimpleDocTemplate(
        "AI_MODEL_TRAINING_DOCS_USER_GUIDE.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a5f')
    )

    heading1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#10b981')
    )

    heading2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#3b82f6')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=4,
        leading=14
    )

    note_style = ParagraphStyle(
        'CustomNote',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=10,
        spaceAfter=10,
        backColor=colors.HexColor('#f0f9ff'),
        borderPadding=10,
        textColor=colors.HexColor('#1e40af')
    )

    story = []

    # Title
    story.append(Paragraph("AI Model Training Docs", title_style))
    story.append(Paragraph("User Guide for AIAlgoTradeHits.com", styles['Heading2']))
    story.append(Spacer(1, 30))

    # Introduction
    story.append(Paragraph("1. Introduction", heading1_style))
    story.append(Paragraph(
        """The AI Model Training Docs feature allows you to upload custom documents to train and enhance
        the Gemini 2.5 Pro AI model. By providing your own trading strategies, technical analysis guides,
        and market research documents, the AI learns from your expertise and provides more personalized,
        accurate trading insights tailored to your investment approach.""",
        body_style
    ))
    story.append(Spacer(1, 10))

    # AI Service Status
    story.append(Paragraph("2. Understanding the AI Service Status Panel", heading1_style))
    story.append(Paragraph(
        """The status panel at the top of the screen shows the current state of AI services:""",
        body_style
    ))

    status_data = [
        ['Component', 'Status Indicator', 'Description'],
        ['Vertex AI', 'Green = Available', 'Google Cloud AI platform connection status'],
        ['Model', 'gemini-2.5-pro', 'The AI model being used for training and inference'],
        ['Training Bucket', 'Green/Red', 'Cloud Storage bucket for storing training documents'],
        ['Training Documents', 'Count', 'Number of documents currently uploaded']
    ]

    status_table = Table(status_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 15))

    # Uploading Documents
    story.append(Paragraph("3. Uploading Training Documents", heading1_style))

    story.append(Paragraph("3.1 Supported File Formats", heading2_style))
    story.append(Paragraph("The system accepts the following document types:", body_style))
    story.append(Paragraph("- <b>PDF</b> - Research papers, strategy guides, market reports", bullet_style))
    story.append(Paragraph("- <b>DOC/DOCX</b> - Microsoft Word documents", bullet_style))
    story.append(Paragraph("- <b>TXT</b> - Plain text files with trading notes or strategies", bullet_style))
    story.append(Paragraph("- <b>CSV</b> - Structured data like historical trades or indicators", bullet_style))
    story.append(Paragraph("- <b>JSON</b> - Structured trading rules or configuration files", bullet_style))
    story.append(Paragraph("- <b>MD</b> - Markdown formatted documentation", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.2 Step-by-Step Upload Process", heading2_style))
    story.append(Paragraph("<b>Step 1:</b> Click the 'Choose File' button to select your document", bullet_style))
    story.append(Paragraph("<b>Step 2:</b> Select a Category from the dropdown (e.g., General, Technical Analysis, Strategies)", bullet_style))
    story.append(Paragraph("<b>Step 3:</b> Or create a new category by typing in the 'Create New Category' field", bullet_style))
    story.append(Paragraph("<b>Step 4:</b> Add an optional description to help identify the document later", bullet_style))
    story.append(Paragraph("<b>Step 5:</b> Click the blue 'Upload Document' button", bullet_style))
    story.append(Spacer(1, 10))

    # Categories
    story.append(Paragraph("4. Organizing Documents by Category", heading1_style))
    story.append(Paragraph(
        """Categories help organize your training documents and allow you to train the AI on specific
        topics. Recommended categories include:""",
        body_style
    ))

    category_data = [
        ['Category', 'What to Include'],
        ['Technical Analysis', 'Candlestick patterns, indicators (RSI, MACD), chart patterns'],
        ['Trading Strategies', 'Entry/exit rules, position sizing, risk management'],
        ['Market Research', 'Sector analysis, earnings reports, economic indicators'],
        ['Risk Management', 'Stop-loss strategies, portfolio allocation, hedging'],
        ['Crypto Trading', 'Blockchain analysis, DeFi protocols, tokenomics'],
        ['Options Strategies', 'Greeks, spreads, volatility trading'],
        ['Fundamental Analysis', 'Financial statements, valuation methods, ratios']
    ]

    cat_table = Table(category_data, colWidths=[2*inch, 4*inch])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#86efac')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 15))

    # Training the Model
    story.append(Paragraph("5. Training the AI Model", heading1_style))
    story.append(Paragraph(
        """Once you have uploaded your documents, you can train the Gemini 2.5 model to learn from them:""",
        body_style
    ))

    story.append(Paragraph("5.1 Training Scope Options", heading2_style))
    story.append(Paragraph("- <b>All Categories</b> - Train on all uploaded documents", bullet_style))
    story.append(Paragraph("- <b>Specific Category</b> - Train only on documents in a selected category", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 How to Start Training", heading2_style))
    story.append(Paragraph("<b>Step 1:</b> Select the Training Scope from the dropdown", bullet_style))
    story.append(Paragraph("<b>Step 2:</b> Click the green 'Start Training' button", bullet_style))
    story.append(Paragraph("<b>Step 3:</b> Wait for the training to complete (may take a few moments)", bullet_style))
    story.append(Paragraph("<b>Step 4:</b> The AI will now use your documents to enhance its responses", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        """<b>Note:</b> Training will process documents and update the AI's context. After training,
        the AI will reference your uploaded materials when providing trading insights, pattern
        recognition, and price predictions.""",
        note_style
    ))
    story.append(Spacer(1, 15))

    # Managing Documents
    story.append(Paragraph("6. Managing Training Documents", heading1_style))
    story.append(Paragraph(
        """The Training Documents section at the bottom shows all uploaded files with the following information:""",
        body_style
    ))
    story.append(Paragraph("- <b>Name</b> - The filename of the uploaded document", bullet_style))
    story.append(Paragraph("- <b>Category</b> - The category assigned to the document", bullet_style))
    story.append(Paragraph("- <b>Size</b> - File size in KB", bullet_style))
    story.append(Paragraph("- <b>Type</b> - The MIME type (e.g., text/plain, application/pdf)", bullet_style))
    story.append(Paragraph("- <b>Updated</b> - Date the document was last modified", bullet_style))
    story.append(Paragraph("- <b>Actions</b> - Delete button to remove the document", bullet_style))
    story.append(Spacer(1, 15))

    # Best Practices
    story.append(Paragraph("7. Best Practices for Effective Training", heading1_style))

    story.append(Paragraph("7.1 Document Quality", heading2_style))
    story.append(Paragraph("- Use clear, well-structured documents with proper formatting", bullet_style))
    story.append(Paragraph("- Include specific examples and case studies", bullet_style))
    story.append(Paragraph("- Avoid duplicate content across multiple documents", bullet_style))
    story.append(Paragraph("- Keep file sizes reasonable (under 10MB per document)", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7.2 Content Recommendations", heading2_style))
    story.append(Paragraph("- Define your trading rules with clear entry/exit criteria", bullet_style))
    story.append(Paragraph("- Include indicator settings and thresholds you use", bullet_style))
    story.append(Paragraph("- Document your risk management approach", bullet_style))
    story.append(Paragraph("- Add examples of successful and failed trades with analysis", bullet_style))
    story.append(Paragraph("- Include your market analysis methodology", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7.3 Training Frequency", heading2_style))
    story.append(Paragraph("- Retrain after uploading new significant documents", bullet_style))
    story.append(Paragraph("- Update documents when your strategies evolve", bullet_style))
    story.append(Paragraph("- Remove outdated or irrelevant documents before retraining", bullet_style))
    story.append(Spacer(1, 15))

    # Example Documents
    story.append(Paragraph("8. Example Documents to Upload", heading1_style))
    story.append(Paragraph(
        """Here are examples of documents that can significantly improve AI insights:""",
        body_style
    ))

    example_data = [
        ['Document Type', 'Example Content'],
        ['OHLCV Guide', 'Explanation of Open, High, Low, Close, Volume and their significance'],
        ['RSI Strategy', 'Your custom RSI settings, overbought/oversold thresholds, divergence rules'],
        ['Candlestick Patterns', 'Pattern definitions with entry/exit rules for each'],
        ['Sector Analysis', 'How you analyze sector rotation and momentum'],
        ['Risk Rules', 'Your position sizing formula, max drawdown rules, stop-loss methodology'],
        ['Trade Journal', 'Historical trades with reasoning and lessons learned']
    ]

    example_table = Table(example_data, colWidths=[2*inch, 4*inch])
    example_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c4b5fd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(example_table)
    story.append(Spacer(1, 15))

    # Troubleshooting
    story.append(Paragraph("9. Troubleshooting", heading1_style))

    trouble_data = [
        ['Issue', 'Solution'],
        ['Training Bucket: Not Found', 'Contact admin to create the GCS bucket: aialgotradehits-training-docs'],
        ['Upload fails', 'Check file size (<10MB) and format (PDF, DOC, TXT, CSV, JSON, MD)'],
        ['Training takes too long', 'Large documents may take several minutes; try smaller batches'],
        ['AI not using my documents', 'Ensure training completed successfully; retrain if needed'],
        ['Vertex AI: Unavailable', 'Check internet connection; service may be temporarily down']
    ]

    trouble_table = Table(trouble_data, colWidths=[2.5*inch, 3.5*inch])
    trouble_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fca5a5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(trouble_table)
    story.append(Spacer(1, 20))

    # Footer
    story.append(Paragraph(
        """<b>AIAlgoTradeHits.com</b> - Powered by Google Gemini 2.5 Pro and Vertex AI""",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.gray)
    ))
    story.append(Paragraph(
        """Document Version 1.0 - December 2025""",
        ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.gray)
    ))

    doc.build(story)
    print("PDF created successfully: AI_MODEL_TRAINING_DOCS_USER_GUIDE.pdf")

if __name__ == "__main__":
    create_pdf()
