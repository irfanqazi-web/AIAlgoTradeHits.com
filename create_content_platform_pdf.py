"""
Create PDF for Content Curation & AI Idea Generation Platform
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def create_pdf():
    doc = SimpleDocTemplate(
        "C:/1AITrading/Trading/CONTENT_CURATION_AI_PLATFORM.pdf",
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#1a73e8')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#1a73e8')
    )

    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#333333')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=14
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4,
        leading=14
    )

    story = []

    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Content Curation &<br/>AI Idea Generation Platform", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph('"Inspire to Create"', ParagraphStyle(
        'Tagline', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER,
        textColor=colors.gray, fontName='Helvetica-Oblique'
    )))
    story.append(Spacer(1, 1*inch))

    # Target platforms table
    platform_data = [
        ['Target Platforms', 'Focus Area'],
        ['KaamyabPakistan.org', 'Business opportunities for Pakistani entrepreneurs'],
        ['YouInvent.Tech', 'Technology innovations and inventions'],
        ['HomeFranchise.Biz', 'Home-based franchise opportunities'],
        ['NoCodeAI.Cloud', 'No-code AI solutions and tools']
    ]

    platform_table = Table(platform_data, colWidths=[2*inch, 3.5*inch])
    platform_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(platform_table)

    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(f"Version 1.0 | {datetime.now().strftime('%B %d, %Y')}",
        ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)))

    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", heading_style))
    story.append(Paragraph(
        "A unified platform that allows users to capture inspiring content from social media "
        "(Instagram, TikTok, YouTube) and websites, automatically transcribe it, and use AI "
        "to generate new business ideas tailored to specific target platforms.",
        body_style
    ))

    story.append(Paragraph("Key Features:", subheading_style))
    features = [
        "One-Click Capture - Browser extension to save content instantly",
        "Multi-Platform Auth - Connect Instagram, TikTok, YouTube accounts",
        "Auto-Transcription - Speech-to-text for videos, OCR for images",
        "AI Idea Generator - Gemini-powered contextual idea creation",
        "Platform Targeting - Customize ideas for specific audiences",
        "Export Options - PDF, Word, direct publish to platforms"
    ]
    for feature in features:
        story.append(Paragraph(f"• {feature}", bullet_style))

    # Supported Content Sources
    story.append(Paragraph("2. Supported Content Sources", heading_style))
    sources_data = [
        ['Platform', 'Content Types'],
        ['Instagram', 'Posts, Reels, Stories'],
        ['TikTok', 'Videos'],
        ['YouTube', 'Videos, Shorts'],
        ['Websites', 'Articles, Blog posts']
    ]
    sources_table = Table(sources_data, colWidths=[2*inch, 3.5*inch])
    sources_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sources_table)

    # User Flow
    story.append(Paragraph("3. User Flow", heading_style))

    story.append(Paragraph("Content Capture Flow:", subheading_style))
    capture_steps = [
        "1. User browses Instagram/TikTok/YouTube/Website",
        "2. User clicks browser extension OR pastes URL in web app",
        "3. System authenticates user (OAuth 2.0)",
        "4. Content is fetched and stored",
        "5. Automatic transcription begins",
        "6. User receives notification when ready"
    ]
    for step in capture_steps:
        story.append(Paragraph(step, bullet_style))

    story.append(Paragraph("Idea Generation Flow:", subheading_style))
    idea_steps = [
        "1. User views transcribed content",
        "2. User selects target platform (e.g., YouInvent.Tech)",
        "3. User clicks 'Generate Ideas'",
        "4. AI analyzes content + platform context",
        "5. Multiple idea variations generated",
        "6. User reviews, edits, and saves preferred idea",
        "7. Idea exported to target platform database"
    ]
    for step in idea_steps:
        story.append(Paragraph(step, bullet_style))

    story.append(PageBreak())

    # AI Capabilities
    story.append(Paragraph("4. AI Capabilities", heading_style))

    ai_data = [
        ['Capability', 'Technology', 'Use Case'],
        ['Video Transcription', 'Google Speech-to-Text', 'Convert spoken content to text'],
        ['Image Text Extraction', 'Google Vision OCR', 'Extract text from images'],
        ['Content Analysis', 'Gemini Pro', 'Understand context and themes'],
        ['Idea Generation', 'Gemini Pro', 'Create business opportunities'],
        ['Translation', 'Google Translate', 'Urdu/English support'],
        ['Sentiment Analysis', 'Natural Language API', 'Gauge content tone']
    ]
    ai_table = Table(ai_data, colWidths=[1.5*inch, 1.8*inch, 2.2*inch])
    ai_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ai_table)

    # Platform-Specific AI Prompts
    story.append(Paragraph("5. Platform-Specific AI Prompts", heading_style))

    story.append(Paragraph("YouInvent.Tech Prompt:", subheading_style))
    story.append(Paragraph(
        '"Based on this content, propose an innovative technology solution or invention. Consider: '
        'Technical feasibility, Market potential, Patent possibilities, Development complexity, Scalability"',
        ParagraphStyle('Quote', parent=body_style, leftIndent=20, rightIndent=20,
                      textColor=colors.HexColor('#666666'), fontName='Helvetica-Oblique')
    ))

    story.append(Paragraph("KaamyabPakistan.org Prompt:", subheading_style))
    story.append(Paragraph(
        '"Analyze this content and generate a business opportunity suitable for Pakistani entrepreneurs. '
        'Consider: Local market conditions, Available resources, Cultural relevance, Investment requirements, Job creation potential"',
        ParagraphStyle('Quote', parent=body_style, leftIndent=20, rightIndent=20,
                      textColor=colors.HexColor('#666666'), fontName='Helvetica-Oblique')
    ))

    story.append(Paragraph("HomeFranchise.Biz Prompt:", subheading_style))
    story.append(Paragraph(
        '"Transform this inspiration into a home-based franchise concept. Consider: Work-from-home viability, '
        'Startup costs under $10,000, Training requirements, Scalability through franchising"',
        ParagraphStyle('Quote', parent=body_style, leftIndent=20, rightIndent=20,
                      textColor=colors.HexColor('#666666'), fontName='Helvetica-Oblique')
    ))

    story.append(Paragraph("NoCodeAI.Cloud Prompt:", subheading_style))
    story.append(Paragraph(
        '"Create a no-code AI tool concept inspired by this content. Consider: User-friendly interface, '
        'AI/ML capabilities needed, Integration possibilities, Subscription model potential"',
        ParagraphStyle('Quote', parent=body_style, leftIndent=20, rightIndent=20,
                      textColor=colors.HexColor('#666666'), fontName='Helvetica-Oblique')
    ))

    story.append(PageBreak())

    # GCP Services
    story.append(Paragraph("6. GCP Services Required", heading_style))

    gcp_data = [
        ['Service', 'Purpose', 'Est. Cost/Month'],
        ['Cloud Run', 'API hosting, web app', '$20-50'],
        ['Cloud Functions', 'Content processing', '$10-30'],
        ['BigQuery', 'Data storage & analytics', '$10-20'],
        ['Cloud Storage', 'Media files storage', '$5-15'],
        ['Speech-to-Text', 'Video transcription', '$20-50'],
        ['Vision API', 'OCR for images', '$10-25'],
        ['Vertex AI (Gemini)', 'Idea generation', '$15-40'],
        ['Cloud Scheduler', 'Background jobs', '$0.10/job'],
    ]
    gcp_table = Table(gcp_data, colWidths=[1.8*inch, 2.2*inch, 1.5*inch])
    gcp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fbbc04')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(gcp_table)

    # Implementation Phases
    story.append(Paragraph("7. Implementation Phases", heading_style))

    phases = [
        ("Phase 1: Foundation (Week 1-2)", [
            "Set up GCP project structure",
            "Create BigQuery dataset and tables",
            "Build basic Cloud Run API",
            "Implement user authentication"
        ]),
        ("Phase 2: Content Capture (Week 3-4)", [
            "Develop browser extension",
            "Integrate YouTube Data API",
            "Build web scraper for websites",
            "Create content library UI"
        ]),
        ("Phase 3: Transcription (Week 5-6)", [
            "Integrate Speech-to-Text API",
            "Integrate Vision OCR API",
            "Build transcription queue",
            "Add transcription viewer"
        ]),
        ("Phase 4: AI Generation (Week 7-8)", [
            "Create Gemini integration",
            "Build prompt templates per platform",
            "Implement idea generation pipeline",
            "Create idea scoring system"
        ]),
        ("Phase 5: Export & Polish (Week 9-10)", [
            "Build PDF export functionality",
            "Create platform export APIs",
            "Add idea library search",
            "Implement analytics dashboard"
        ])
    ]

    for phase_title, tasks in phases:
        story.append(Paragraph(phase_title, subheading_style))
        for task in tasks:
            story.append(Paragraph(f"□ {task}", bullet_style))

    story.append(PageBreak())

    # Cost Estimation
    story.append(Paragraph("8. Cost Estimation", heading_style))

    cost_data = [
        ['Item', 'Low Usage', 'Medium Usage', 'High Usage'],
        ['Cloud Run', '$20', '$40', '$80'],
        ['Cloud Functions', '$10', '$25', '$50'],
        ['BigQuery', '$10', '$20', '$40'],
        ['Cloud Storage', '$5', '$15', '$30'],
        ['Speech-to-Text', '$20', '$50', '$100'],
        ['Vision API', '$10', '$25', '$50'],
        ['Gemini API', '$15', '$40', '$80'],
        ['TOTAL', '$90', '$215', '$430'],
    ]
    cost_table = Table(cost_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0fe')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(cost_table)

    # Future Enhancements
    story.append(Paragraph("9. Future Enhancements", heading_style))

    enhancements = [
        "Mobile App - iOS/Android native apps",
        "Team Collaboration - Share ideas with team members",
        "AI Training - Custom fine-tuned models per platform",
        "Marketplace - Buy/sell generated ideas",
        "Analytics Dashboard - Trend analysis and insights",
        "Multi-language - Support for Urdu, Arabic, Hindi"
    ]
    for item in enhancements:
        story.append(Paragraph(f"• {item}", bullet_style))

    # Monetization
    story.append(Paragraph("10. Monetization Options", heading_style))
    monetization = [
        "Freemium model (5 ideas/month free)",
        "Pro subscription ($9.99/month)",
        "Enterprise plans for teams",
        "Per-idea generation credits"
    ]
    for item in monetization:
        story.append(Paragraph(f"• {item}", bullet_style))

    # Conclusion
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Paragraph(
        "This platform bridges the gap between social media inspiration and actionable business ideas. "
        "By leveraging GCP's powerful AI services (Speech-to-Text, Vision, Gemini), we can automate "
        "the tedious process of content analysis and idea generation, allowing entrepreneurs to focus "
        "on execution rather than ideation. The modular architecture ensures scalability, while the "
        "platform-specific prompts guarantee relevant, contextual ideas for each target audience.",
        body_style
    ))

    # Build PDF
    doc.build(story)
    print("PDF created successfully: C:/1AITrading/Trading/CONTENT_CURATION_AI_PLATFORM.pdf")

if __name__ == "__main__":
    create_pdf()
