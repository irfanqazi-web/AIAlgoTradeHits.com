"""Create ML Sector Training Plan PDF"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Create PDF
doc = SimpleDocTemplate('ML_SECTOR_TRAINING_PLAN.pdf', pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Title
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20)
elements.append(Paragraph('ML Sector Training, Testing & Validation Plan', title_style))
elements.append(Spacer(1, 0.2*inch))

# Executive Summary
elements.append(Paragraph('Executive Summary', styles['Heading2']))
elements.append(Paragraph(
    'This document outlines the comprehensive ML training strategy for walk-forward validation '
    'across key market sectors. The plan prioritizes high-growth sectors: Semiconductors, AI/Cloud, '
    'Defense/Aerospace, Nuclear Energy, and Quantum Computing.',
    styles['Normal']))
elements.append(Spacer(1, 0.2*inch))

# Sector 1: Semiconductors
elements.append(Paragraph('1. SEMICONDUCTORS (19 Stocks)', styles['Heading2']))
semi_data = [
    ['Sub-Industry', 'Symbols', 'Description'],
    ['Chip Makers', 'NVDA, AMD, INTC, AVGO, QCOM, MU, MRVL', 'GPU, CPU, memory'],
    ['Equipment', 'ASML, LRCX, AMAT, KLAC', 'Lithography, etch'],
    ['Design/EDA', 'SNPS, CDNS, ADI, MCHP, TXN, NXPI, ON', 'Chip design'],
    ['AI Servers', 'SMCI', 'AI infrastructure']
]
t = Table(semi_data, colWidths=[1.5*inch, 3*inch, 2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
]))
elements.append(t)
elements.append(Spacer(1, 0.2*inch))

# Sector 2: AI & Cloud
elements.append(Paragraph('2. AI & CLOUD (16 Stocks)', styles['Heading2']))
ai_data = [
    ['Sub-Industry', 'Symbols', 'Description'],
    ['AI Leaders', 'NVDA, MSFT, GOOGL, META, AMZN', 'Major AI platforms'],
    ['Enterprise AI', 'CRM, NOW, PANW, CRWD', 'Business AI apps'],
    ['AI Infrastructure', 'PLTR, PATH, DDOG, MDB, TEAM', 'Data platforms'],
    ['Quantum', 'IONQ', 'Quantum computing']
]
t = Table(ai_data, colWidths=[1.5*inch, 3*inch, 2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
]))
elements.append(t)
elements.append(Spacer(1, 0.2*inch))

# Sector 3: Defense
elements.append(Paragraph('3. DEFENSE & AEROSPACE (6 Stocks)', styles['Heading2']))
def_data = [
    ['Sub-Industry', 'Symbols', 'Description'],
    ['Prime Contractors', 'LMT, RTX, NOC, GD', 'Defense systems'],
    ['Space/Drones', 'RKLB, JOBY', 'Space launch, eVTOL']
]
t = Table(def_data, colWidths=[1.5*inch, 3*inch, 2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
]))
elements.append(t)
elements.append(Spacer(1, 0.2*inch))

# Sector 4: Energy
elements.append(Paragraph('4. NUCLEAR & CLEAN ENERGY (4 Stocks)', styles['Heading2']))
nuc_data = [
    ['Sub-Industry', 'Symbols', 'Description'],
    ['Nuclear', 'CEG', 'Nuclear power'],
    ['Solar', 'ENPH, FSLR', 'Solar tech'],
    ['Utilities', 'NEE', 'Clean energy']
]
t = Table(nuc_data, colWidths=[1.5*inch, 3*inch, 2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Training Configuration
elements.append(Paragraph('Training Configuration', styles['Heading2']))
config_data = [
    ['Parameter', 'Value'],
    ['Algorithm', 'XGBoost Classifier (BigQuery ML)'],
    ['Features', 'Essential 8 (rsi, macd, macd_histogram, momentum, mfi, cci, rsi_zscore, macd_cross)'],
    ['Retraining', 'Monthly (21 trading days)'],
    ['Validation Period', '60-252 trading days'],
    ['Model Caching', '80% cost reduction'],
    ['Batch Predictions', '30x fewer queries']
]
t = Table(config_data, colWidths=[2*inch, 4.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(t)
elements.append(Spacer(1, 0.2*inch))

# Cost Estimates
elements.append(Paragraph('Estimated Costs', styles['Heading2']))
cost_data = [
    ['Batch', 'Stocks', 'Est. Cost'],
    ['Semiconductors', '19', '$3.00'],
    ['AI & Cloud', '16', '$2.50'],
    ['Defense', '6', '$1.00'],
    ['Energy', '4', '$0.75'],
    ['TOTAL', '45', '$7.25']
]
t = Table(cost_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*inch))

# Execution Plan
elements.append(Paragraph('Execution Plan', styles['Heading2']))
exec_data = [
    ['Phase', 'Action', 'Duration'],
    ['1', 'Generate PDF Report', 'Complete'],
    ['2', 'Run Semiconductor Batch (19 stocks)', '~30 min'],
    ['3', 'Run AI/Cloud Batch (16 stocks)', '~25 min'],
    ['4', 'Run Defense Batch (6 stocks)', '~10 min'],
    ['5', 'Run Energy Batch (4 stocks)', '~8 min'],
    ['6', 'Compile Final Results Report', '~5 min']
]
t = Table(exec_data, colWidths=[0.7*inch, 3.5*inch, 1.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(t)

# Service Info
elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph('Service Information', styles['Heading2']))
elements.append(Paragraph('Cloud Run Service: ml-training-service', styles['Normal']))
elements.append(Paragraph('Timeout: 60 minutes | Memory: 4GB | Region: us-central1', styles['Normal']))
elements.append(Paragraph('Project: aialgotradehits', styles['Normal']))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph('Generated: 2026-01-10', styles['Normal']))

# Build PDF
doc.build(elements)
print('PDF created: ML_SECTOR_TRAINING_PLAN.pdf')
