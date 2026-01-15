"""
Generate PDF from Unified Content Marketing Platform Markdown
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import re

def create_unified_platform_pdf():
    """Create PDF document."""

    doc = SimpleDocTemplate(
        "C:/1AITrading/Trading/UNIFIED_CONTENT_MARKETING_PLATFORM.pdf",
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a2e')
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4a4a4a')
    )

    mission_style = ParagraphStyle(
        'Mission',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#d62828'),
        alignment=TA_CENTER
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#16537e')
    )

    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#2d6a4f')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4
    )

    story = []

    # Title page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Unified Content Curation &<br/>AI Marketing Platform", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph('"Inspire to Create" - Best of US, Europe & China', subtitle_style))
    story.append(Spacer(1, 0.5*inch))

    # Mission statement
    story.append(Paragraph("MISSION: AI FOR THE HUNGRY & AMBITIOUS", mission_style))
    story.append(Spacer(1, 0.2*inch))

    mission_text = """
    <b>The Problem:</b> AI wealth and power are concentrating in the hands of billionaires and tech giants.
    Meanwhile, millions of talented, hardworking people in developing nations have the hunger, the drive,
    and the ambition to succeed - but lack access to the same powerful tools.
    <br/><br/>
    <b>Who We're NOT For:</b> This platform is NOT for freeloaders. People looking for "free" everything,
    expecting handouts, unwilling to invest even a small amount in their own future - these couch potatoes
    looking for quick riches without effort will never succeed, with or without AI.
    <br/><br/>
    <b>Who We ARE For:</b> The <b>HUNGRY and AMBITIOUS</b> - people who are poor in resources but RICH in
    determination. Those who will invest in themselves, work harder than anyone else, see obstacles as
    challenges, take responsibility, and understand that nothing worth having comes free.
    """
    story.append(Paragraph(mission_text, body_style))
    story.append(Spacer(1, 0.3*inch))

    # Target platforms
    story.append(Paragraph("Target Platforms", h2_style))

    platform_data = [
        ['Platform', 'Focus Area', 'Domain'],
        ['KaamyabPakistan.org', 'Business opportunities for Pakistani entrepreneurs', '.org'],
        ['YouInvent.Tech', 'Technology innovations and inventions', '.tech'],
        ['HomeFranchise.Biz', 'Home-based franchise opportunities', '.biz'],
        ['NoCodeAI.Cloud', 'No-code AI solutions and tools', '.cloud'],
    ]

    platform_table = Table(platform_data, colWidths=[2*inch, 3.5*inch, 0.8*inch])
    platform_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16537e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    story.append(platform_table)

    story.append(PageBreak())

    # Content Sources
    story.append(Paragraph("Content Sources", h2_style))
    story.append(Paragraph("Social Media Platforms", h3_style))

    social_data = [
        ['Platform', 'Content Types', 'API'],
        ['Instagram', 'Posts, Reels, Stories, IGTV', 'Instagram Graph API'],
        ['TikTok', 'Videos, Live streams', 'TikTok API'],
        ['YouTube', 'Videos, Shorts, Live', 'YouTube Data API v3'],
        ['Facebook', 'Posts, Videos, Stories', 'Meta Graph API'],
        ['Twitter/X', 'Tweets, Threads, Spaces', 'X API v2'],
    ]

    social_table = Table(social_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    social_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e91e63')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fce4ec')]),
    ]))
    story.append(social_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(".COM Websites & Blogs", h3_style))

    web_data = [
        ['Category', 'Examples', 'Capture Method'],
        ['Tech Blogs', 'TechCrunch, Wired, TheVerge', 'Web Scraping + API'],
        ['Business', 'Forbes, Inc, Entrepreneur', 'RSS + Scraping'],
        ['News', 'CNN, BBC, Reuters', 'RSS Feeds'],
        ['E-commerce', 'Amazon, Alibaba', 'Product API'],
        ['Any URL', 'User-provided links', 'Universal Scraper'],
    ]

    web_table = Table(web_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    web_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00bcd4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e0f7fa')]),
    ]))
    story.append(web_table)

    story.append(PageBreak())

    # AI Tools - Best of All Worlds
    story.append(Paragraph("AI Tools - Best of All Worlds", h2_style))

    # US Platforms
    story.append(Paragraph("US Platforms (Innovation Leaders)", h3_style))

    us_ai_data = [
        ['Tool', 'Specialty', 'Best For'],
        ['OpenAI GPT-4/o1', 'General intelligence', 'Content generation, analysis'],
        ['Claude (Anthropic)', 'Long context, reasoning', 'Document processing, coding'],
        ['Grok (xAI)', 'Real-time X/Twitter data', 'Social trends, unfiltered insights'],
        ['Google Gemini', 'Multimodal, Google integration', 'Search, YouTube, workspace'],
        ['Perplexity', 'Web search AI', 'Research, fact-checking'],
        ['Meta Llama 3', 'Open source', 'Custom deployments'],
    ]

    us_table = Table(us_ai_data, colWidths=[1.8*inch, 2*inch, 2.2*inch])
    us_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e3f2fd')]),
    ]))
    story.append(us_table)
    story.append(Spacer(1, 0.2*inch))

    # Grok special section
    story.append(Paragraph("Grok (xAI) - Special Integration", h3_style))
    grok_text = """
    <b>Why Grok?</b> Unlike other LLMs, Grok has direct access to real-time social media data from X (Twitter),
    making it ideal for trending topic analysis, viral content inspiration, social sentiment tracking,
    and meme/humor content generation. Features include: Real-time X Data, Humor Mode, Unfiltered Insights,
    Aurora Image Generation, Voice Mode, and API Access ($25/month for 25B tokens).
    """
    story.append(Paragraph(grok_text, body_style))
    story.append(Spacer(1, 0.2*inch))

    # European Platforms
    story.append(Paragraph("European Platforms (Privacy & Quality)", h3_style))

    eu_data = [
        ['Tool', 'Country', 'Specialty'],
        ['Mistral AI', 'France', 'Open-weight LLM, European data sovereignty'],
        ['DeepL', 'Germany', 'Best-in-class translation'],
        ['Aleph Alpha', 'Germany', 'Enterprise AI, GDPR compliant'],
        ['Stability AI', 'UK', 'Open-source image generation'],
        ['D-ID', 'Israel/EU', 'Talking avatars, photo animation'],
    ]

    eu_table = Table(eu_data, colWidths=[1.5*inch, 1.2*inch, 3.3*inch])
    eu_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4caf50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
    ]))
    story.append(eu_table)
    story.append(Spacer(1, 0.2*inch))

    # Chinese Platforms
    story.append(Paragraph("Chinese Platforms (Cost-Effective & Innovative)", h3_style))

    cn_data = [
        ['Tool', 'Company', 'Best For'],
        ['CapCut', 'ByteDance', 'Free advanced video editing, AI effects'],
        ['Baidu Wenxin', 'Baidu', 'Chinese content, multimodal'],
        ['Kimi Chat', 'Moonshot', '200K+ context, document analysis'],
        ['DeepSeek', 'DeepSeek', 'Cost-effective reasoning, coding'],
        ['Vidu Studio', 'Shengshu', 'High-quality text-to-video'],
    ]

    cn_table = Table(cn_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    cn_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f44336')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffebee')]),
    ]))
    story.append(cn_table)

    story.append(PageBreak())

    # Web Scraping Section
    story.append(Paragraph("Web Scraping Capabilities", h2_style))

    scrape_text = """
    The platform includes enterprise-grade web scraping to capture content from any .com website,
    handling JavaScript-rendered pages, authentication, and rate limiting.
    <br/><br/>
    <b>Tools & Libraries:</b> Playwright, Selenium, Beautiful Soup, Scrapy, ScrapingBee, Bright Data,
    Firecrawl, Jina Reader
    <br/><br/>
    <b>Site-Specific Handlers:</b> News Sites, E-commerce, Social Media, Blogs, Forums, Video Sites, PDF Documents
    """
    story.append(Paragraph(scrape_text, body_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Rate Limiting & Compliance", h3_style))

    rate_data = [
        ['Site Category', 'Rate Limit', 'Notes'],
        ['News sites', '10 req/min', 'Respect robots.txt'],
        ['E-commerce', '5 req/min', 'Higher risk of blocking'],
        ['Social media', 'Via API', 'Use official APIs when available'],
        ['Blogs', '20 req/min', 'Usually lenient'],
        ['Government', '3 req/min', 'Very conservative'],
    ]

    rate_table = Table(rate_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    rate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff3e0')]),
    ]))
    story.append(rate_table)

    story.append(PageBreak())

    # diSearch.ai Section
    story.append(Paragraph("Core Intelligence: diSearch.ai", h2_style))

    disearch_text = """
    <b>Why diSearch.ai Over Consumer Tools?</b>
    <br/><br/>
    diSearch.ai provides enterprise-grade features that consumer tools like Perplexity or ChatGPT cannot match:
    """
    story.append(Paragraph(disearch_text, body_style))

    disearch_data = [
        ['Feature', 'diSearch.ai', 'Consumer Tools'],
        ['Proprietary Data', 'Full control', 'Limited/None'],
        ['Data Security', 'Self-hosted, SOC2', 'Cloud only'],
        ['RAG Content', 'Custom knowledge base', 'Web only'],
        ['Governance', 'RBAC, audit logs', 'None'],
        ['Multi-LLM', 'GPT, Claude, Gemini, Chinese', 'Single model'],
    ]

    disearch_table = Table(disearch_data, colWidths=[1.8*inch, 2*inch, 2.2*inch])
    disearch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9c27b0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3e5f5')]),
    ]))
    story.append(disearch_table)
    story.append(Spacer(1, 0.3*inch))

    # GCP Infrastructure
    story.append(Paragraph("GCP Infrastructure & Costs", h2_style))

    gcp_data = [
        ['Service', 'Purpose', 'Est. Cost/Month'],
        ['Cloud Run', 'API hosting, web apps', '$50-150'],
        ['Cloud Functions', 'Content processing', '$20-50'],
        ['BigQuery', 'Data warehouse', '$20-50'],
        ['Cloud Storage', 'Media files', '$20-100'],
        ['Speech-to-Text', 'Transcription', '$30-100'],
        ['Vertex AI', 'Gemini, embeddings', '$50-200'],
        ['TOTAL GCP', '', '$290-905/month'],
    ]

    gcp_table = Table(gcp_data, colWidths=[1.8*inch, 2.2*inch, 1.5*inch])
    gcp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#607d8b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cfd8dc')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#eceff1')]),
    ]))
    story.append(gcp_table)

    story.append(PageBreak())

    # Pricing Strategy
    story.append(Paragraph("Pricing Strategy", h2_style))

    pricing_data = [
        ['Plan', 'Users', 'Features', 'Price'],
        ['Starter', '3', '50 captures/month, basic transcription, 20 ideas', '$99/month'],
        ['Professional', '10', '200 captures, all transcription, 100 ideas', '$299/month'],
        ['Business', '30', '1000 captures, diSearch access, unlimited ideas', '$999/month'],
        ['Enterprise', 'Unlimited', 'Self-hosted, custom integrations, SLA', 'Custom'],
    ]

    pricing_table = Table(pricing_data, colWidths=[1.3*inch, 0.8*inch, 2.9*inch, 1*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
    ]))
    story.append(pricing_table)
    story.append(Spacer(1, 0.3*inch))

    # Pricing Philosophy - Skin in the Game
    story.append(Paragraph("Pricing Philosophy: Skin in the Game", h3_style))
    pricing_philosophy = """
    <b>NO Free Tier for Production:</b> Free trials only - commitment matters<br/>
    <b>Affordable Entry:</b> $9.99/month - if you can't invest this, you're not ready<br/>
    <b>Sweat Equity Program:</b> Contribute tutorials, translations, support to earn credits<br/>
    <b>Performance Scholarships:</b> Prove results, get discounts - we invest in winners<br/>
    <b>Micro-Investment Plans:</b> $2.50/week for those with irregular income<br/>
    <b>Revenue Share Option:</b> Pay nothing upfront, share 5% of AI-generated revenue<br/><br/>
    <i>"We don't give fish. We give fishing rods to those willing to wake up at dawn."</i>
    """
    story.append(Paragraph(pricing_philosophy, body_style))
    story.append(Spacer(1, 0.3*inch))

    # Implementation Roadmap
    story.append(Paragraph("Implementation Roadmap", h2_style))

    roadmap_data = [
        ['Phase', 'Duration', 'Deliverables'],
        ['Phase 1: Foundation', '3-4 weeks', 'GCP setup, auth, basic UI, BigQuery schema'],
        ['Phase 2: diSearch.ai', '2-3 weeks', 'Deploy diSearch, configure RAG, knowledge base'],
        ['Phase 3: Content Capture', '4-5 weeks', 'Browser extension, social APIs, web scraper'],
        ['Phase 4: Transcription', '3-4 weeks', 'Speech-to-Text, Vision OCR, translation'],
        ['Phase 5: AI Generation', '4-5 weeks', 'Multi-LLM integration, platform prompts'],
        ['Phase 6: Video Tools', '4-5 weeks', 'Descript, InVideo, CapCut integrations'],
        ['Phase 7: Marketing', '3-4 weeks', 'Social posting, scheduling, analytics'],
        ['Phase 8: Polish', '3-4 weeks', 'Testing, optimization, documentation'],
        ['TOTAL', '6-9 months', 'Full platform launch'],
    ]

    roadmap_table = Table(roadmap_data, colWidths=[1.8*inch, 1.2*inch, 3*inch])
    roadmap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c5cae9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8eaf6')]),
    ]))
    story.append(roadmap_table)

    story.append(PageBreak())

    # Success Metrics
    story.append(Paragraph("Success Metrics", h2_style))

    metrics_data = [
        ['Metric', 'Target (Month 6)', 'Target (Month 12)'],
        ['Active Users', '500', '2,000'],
        ['Content Captured', '10,000', '50,000'],
        ['Ideas Generated', '5,000', '25,000'],
        ['Videos Created', '2,000', '10,000'],
        ['Platform Exports', '1,000', '5,000'],
        ['MRR', '$50,000', '$200,000'],
    ]

    metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00897b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e0f2f1')]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 0.5*inch))

    # Footer
    footer_text = """
    <b>Document Version:</b> 2.1<br/>
    <b>Created:</b> December 3, 2025<br/>
    <b>Platforms:</b> KaamyabPakistan.org | YouInvent.Tech | HomeFranchise.Biz | NoCodeAI.Cloud<br/>
    <b>Powered By:</b> diSearch.ai + US/EU/CN AI Tools + Grok + Enterprise Web Scraping<br/><br/>
    <i>"AI weapons for the hungry and ambitious. We don't give fish - we give fishing rods to those willing to wake up at dawn."</i>
    """
    story.append(Paragraph(footer_text, body_style))

    # Build PDF
    doc.build(story)
    print("PDF generated successfully: UNIFIED_CONTENT_MARKETING_PLATFORM.pdf")

if __name__ == "__main__":
    create_unified_platform_pdf()
