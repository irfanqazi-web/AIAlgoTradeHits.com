from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=20)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=14, spaceAfter=12, spaceBefore=16)
h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=10, spaceBefore=12)
normal = styles['Normal']

doc = SimpleDocTemplate('DOMAIN_MIGRATION_COMPLETE.pdf', pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
story = []

story.append(Paragraph('Domain Services Migration Complete', title_style))
story.append(Paragraph('November 29, 2025 - Status: COMPLETED', styles['Heading2']))
story.append(Spacer(1, 20))

story.append(Paragraph('Cloud Run Services - aialgotradehits Project', h1))
services = [
    ['Service', 'URL', 'Domain'],
    ['trading-app', 'trading-app-6pmz2y7ouq-uc.a.run.app', 'AIAlgoTradeHits.com'],
    ['crypto-trading-api', 'crypto-trading-api-6pmz2y7ouq-uc.a.run.app', 'API Backend'],
    ['ai-trading-intelligence', 'ai-trading-intelligence-...', 'AI Services'],
    ['smart-search', 'smart-search-6pmz2y7ouq-uc.a.run.app', 'Search API'],
    ['twelvedata-fetcher', 'twelvedata-fetcher-6pmz2y7ouq-uc.a.run.app', 'Data Fetcher'],
    ['kaamyabpakistan', 'kaamyabpakistan-6pmz2y7ouq-uc.a.run.app', 'KaamyabPakistan.org'],
    ['youinvent-tech', 'youinvent-tech-6pmz2y7ouq-uc.a.run.app', 'YouInvent.Tech'],
    ['homefranchise-biz', 'homefranchise-biz-6pmz2y7ouq-uc.a.run.app', 'HomeFranchise.Biz'],
    ['iotmotorz-com', 'iotmotorz-com-6pmz2y7ouq-uc.a.run.app', 'IoTMotorz.com'],
    ['herbalhomeo-api', 'herbalhomeo-api-6pmz2y7ouq-uc.a.run.app', 'HerbalHomeo API'],
    ['herbalhomeo-frontend', 'herbalhomeo-frontend-6pmz2y7ouq-uc.a.run.app', 'HerbalHomeo'],
]
t = Table(services, colWidths=[1.8*inch, 2.5*inch, 1.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
]))
story.append(t)
story.append(Spacer(1, 20))

story.append(Paragraph('Domain DNS Configuration - Point to Cloud Run URLs', h1))
dns = [
    ['Domain', 'Cloud Run Service'],
    ['aialgotradehits.com', 'trading-app'],
    ['kaamyabpakistan.org', 'kaamyabpakistan'],
    ['youinvent.tech', 'youinvent-tech'],
    ['homefranchise.biz', 'homefranchise-biz'],
    ['iotmotorz.com', 'iotmotorz-com'],
    ['nocodeai.cloud', '(to be created)'],
]
t = Table(dns, colWidths=[2*inch, 2.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
]))
story.append(t)
story.append(Spacer(1, 20))

story.append(Paragraph('BigQuery Datasets to Create', h1))
story.append(Paragraph('Log in as irfan.qazi@aialgotradehits.com and create these datasets:', normal))
story.append(Spacer(1, 10))
datasets = [
    ['Dataset Name', 'Purpose'],
    ['kaamyabpakistan_data', 'KaamyabPakistan.org user data'],
    ['youinvent_data', 'YouInvent.Tech invention data'],
    ['homefranchise_data', 'HomeFranchise.Biz franchise data'],
    ['iotmotorz_data', 'IoTMotorz.com IoT device data'],
    ['herbalhomeo_data', 'HerbalHomeo product data'],
    ['nocodeai_data', 'NoCodeAI.cloud platform data'],
]
t = Table(datasets, colWidths=[2*inch, 3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
]))
story.append(t)
story.append(Spacer(1, 20))

story.append(Paragraph('Claude.ai Subscription', h1))
story.append(Paragraph('Personal Claude.ai (haq.irfanul@gmail.com):', normal))
story.append(Paragraph('Check billing at: https://claude.ai/settings/billing', normal))
story.append(Paragraph('Cancel before renewal date to avoid charges.', normal))
story.append(Spacer(1, 20))

story.append(Paragraph('Next Steps', h1))
steps = [
    '1. Log in to GCP Console as irfan.qazi@aialgotradehits.com',
    '2. Set Cloud Run services to allow unauthenticated access',
    '3. Create BigQuery datasets for each domain',
    '4. Configure custom domain mappings in Cloud Run',
    '5. Update DNS records at Interserver.net',
    '6. Check and cancel personal Claude.ai subscription',
]
for step in steps:
    story.append(Paragraph(step, normal))

doc.build(story)
print('Created: DOMAIN_MIGRATION_COMPLETE.pdf')
