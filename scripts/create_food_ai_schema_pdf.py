#!/usr/bin/env python3
"""Create PDF documentation for Food AI BigQuery schema."""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from datetime import datetime

# Create PDF
doc = SimpleDocTemplate('C:/1AITrading/Trading/FOOD_AI_DATABASE_SCHEMA.pdf', pagesize=letter,
                        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=30, textColor=colors.HexColor('#166534'))
h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18, spaceAfter=12, spaceBefore=20, textColor=colors.HexColor('#166534'))
h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceAfter=8, spaceBefore=15, textColor=colors.HexColor('#15803d'))
body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=8)
code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=9, backColor=colors.HexColor('#f3f4f6'), leftIndent=20)

story = []

# Title
story.append(Paragraph('Food AI Database Schema', title_style))
story.append(Paragraph('BigQuery Data Warehouse Documentation', styles['Heading2']))
story.append(Spacer(1, 0.3*inch))

# Overview
story.append(Paragraph('Overview', h1_style))
story.append(Paragraph('''
The Food AI database is a comprehensive health and nutrition data warehouse hosted on Google BigQuery.
It combines data from USDA FoodData Central and Dr. Duke's Phytochemical Database to provide
AI-powered nutrition intelligence and health recommendations.
''', body_style))

overview_data = [
    ['Dataset', 'aialgotradehits.health_nutrition_warehouse'],
    ['Project', 'aialgotradehits (Google Cloud Platform)'],
    ['Total Foods', '11,166 records'],
    ['Nutrient Records', '8,790 records'],
    ['Phytochemicals', '104,388 records'],
    ['Health Activities', '28,929 records'],
    ['Traditional Uses', '82,873 records'],
]
t = Table(overview_data, colWidths=[2*inch, 4*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dcfce7')),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 8),
]))
story.append(t)
story.append(Spacer(1, 0.3*inch))

# Data Sources
story.append(Paragraph('Data Sources', h1_style))
sources_data = [
    ['Source', 'Records', 'Description'],
    ['USDA_SR28', '8,790', 'USDA Standard Reference database with comprehensive nutrient data'],
    ['DUKE_PHYTOCHEM', '2,376', "Dr. Duke's Ethnobotanical Database with phytochemicals"],
]
t = Table(sources_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 8),
]))
story.append(t)

story.append(PageBreak())

# TABLE 1: foods
story.append(Paragraph('Table: foods', h1_style))
story.append(Paragraph('The central table containing all food and plant entries. Links to all other tables via food_id.', body_style))

foods_schema = [
    ['Column', 'Type', 'Description'],
    ['food_id', 'STRING (PK)', 'Unique identifier for each food/plant'],
    ['source', 'STRING', 'Data source: USDA_SR28 or DUKE_PHYTOCHEM'],
    ['ndb_no', 'STRING', 'USDA NDB Number (for USDA foods)'],
    ['fnf_num', 'INTEGER', "Dr. Duke's FNF Number (for phytochem data)"],
    ['food_name', 'STRING', 'Primary name of the food or plant'],
    ['scientific_name', 'STRING', 'Scientific/taxonomic name'],
    ['common_names', 'ARRAY<STRING>', 'Alternative names for the food'],
    ['food_group', 'STRING', 'USDA food group category'],
    ['plant_family', 'STRING', 'Botanical family (e.g., Rosaceae)'],
    ['plant_part', 'STRING', 'Part used: fruit, leaf, root, seed, etc.'],
    ['usage_type', 'STRING', 'FOOD, MEDICINAL, or BOTH'],
    ['is_whole_food', 'BOOLEAN', 'True if minimally processed'],
    ['is_medicinal_plant', 'BOOLEAN', 'True if used in traditional medicine'],
    ['created_at', 'TIMESTAMP', 'Record creation timestamp'],
]
t = Table(foods_schema, colWidths=[1.8*inch, 1.3*inch, 3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (0, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
story.append(t)
story.append(Spacer(1, 0.3*inch))

# TABLE 2: food_nutrients
story.append(Paragraph('Table: food_nutrients', h1_style))
story.append(Paragraph('Complete nutritional profile for each food. All values per 100g serving.', body_style))

nutrients_schema = [
    ['Column', 'Type', 'Description'],
    ['food_id', 'STRING (FK)', 'Links to foods table'],
    ['energy_kcal', 'FLOAT', 'Calories per 100g'],
    ['protein_g', 'FLOAT', 'Protein in grams'],
    ['total_fat_g', 'FLOAT', 'Total fat in grams'],
    ['carbohydrate_g', 'FLOAT', 'Carbohydrates in grams'],
    ['fiber_g', 'FLOAT', 'Dietary fiber in grams'],
    ['sugar_g', 'FLOAT', 'Total sugars in grams'],
    ['calcium_mg', 'FLOAT', 'Calcium in milligrams'],
    ['iron_mg', 'FLOAT', 'Iron in milligrams'],
    ['magnesium_mg', 'FLOAT', 'Magnesium in milligrams'],
    ['potassium_mg', 'FLOAT', 'Potassium in milligrams'],
    ['zinc_mg', 'FLOAT', 'Zinc in milligrams'],
    ['vitamin_c_mg', 'FLOAT', 'Vitamin C in milligrams'],
    ['vitamin_a_iu', 'FLOAT', 'Vitamin A in IU'],
    ['vitamin_d_mcg', 'FLOAT', 'Vitamin D in micrograms'],
    ['vitamin_e_mg', 'FLOAT', 'Vitamin E in milligrams'],
    ['vitamin_k_mcg', 'FLOAT', 'Vitamin K in micrograms'],
    ['vitamin_b6_mg', 'FLOAT', 'Vitamin B6 in milligrams'],
    ['vitamin_b12_mcg', 'FLOAT', 'Vitamin B12 in micrograms'],
    ['folate_mcg', 'FLOAT', 'Folate in micrograms'],
]
t = Table(nutrients_schema, colWidths=[1.8*inch, 1.3*inch, 3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (0, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
]))
story.append(t)

story.append(PageBreak())

# TABLE 3: food_phytochemicals
story.append(Paragraph('Table: food_phytochemicals', h1_style))
story.append(Paragraph('Phytochemical compounds found in foods/plants with concentration data.', body_style))

phyto_schema = [
    ['Column', 'Type', 'Description'],
    ['food_id', 'STRING (FK)', 'Links to foods table'],
    ['chemical_name', 'STRING', 'Name of phytochemical (e.g., Quercetin, Curcumin)'],
    ['chemical_id', 'STRING', 'Normalized identifier'],
    ['cas_number', 'STRING', 'CAS Registry Number'],
    ['chemical_class', 'STRING', 'Class: flavonoid, alkaloid, terpene, etc.'],
    ['plant_part', 'STRING', 'Plant part containing the compound'],
    ['amount_low_ppm', 'FLOAT', 'Low concentration in parts per million'],
    ['amount_high_ppm', 'FLOAT', 'High concentration in parts per million'],
    ['amount_avg_ppm', 'FLOAT', 'Average concentration in PPM'],
    ['reference', 'STRING', 'Literature reference'],
]
t = Table(phyto_schema, colWidths=[1.8*inch, 1.3*inch, 3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (0, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.3*inch))

# TABLE 4: food_health_activities
story.append(Paragraph('Table: food_health_activities', h1_style))
story.append(Paragraph('Health benefits and biological activities of phytochemicals.', body_style))

activities_schema = [
    ['Column', 'Type', 'Description'],
    ['food_id', 'STRING (FK)', 'Internal reference (link via active_compound)'],
    ['activity', 'STRING', 'Health activity (e.g., Antiinflammatory)'],
    ['activity_category', 'STRING', 'Broad category of the activity'],
    ['mechanism', 'STRING', 'How the compound produces the effect'],
    ['source_type', 'STRING', 'NUTRIENT, PHYTOCHEMICAL, WHOLE_FOOD'],
    ['active_compound', 'STRING', 'Chemical providing the benefit'],
    ['evidence_type', 'STRING', 'CLINICAL, TRADITIONAL, IN_VITRO, RESEARCH'],
    ['evidence_strength', 'STRING', 'STRONG, MODERATE, PRELIMINARY'],
    ['effective_dose', 'STRING', 'Dosage if known'],
]
t = Table(activities_schema, colWidths=[1.8*inch, 1.3*inch, 3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (0, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
]))
story.append(t)

story.append(PageBreak())

# TABLE 5: food_traditional_uses
story.append(Paragraph('Table: food_traditional_uses', h1_style))
story.append(Paragraph('Traditional and ethnobotanical uses of plants across cultures.', body_style))

trad_schema = [
    ['Column', 'Type', 'Description'],
    ['food_id', 'STRING (FK)', 'Links to foods table'],
    ['traditional_use', 'STRING', 'Condition or purpose (e.g., Diabetes, Fever)'],
    ['preparation_method', 'STRING', 'How traditionally prepared'],
    ['country_region', 'STRING', 'Geographic origin of the use'],
    ['culture_community', 'STRING', 'Specific culture or community'],
    ['body_system', 'STRING', 'Body system affected (see list below)'],
    ['reference', 'STRING', 'Literature reference'],
]
t = Table(trad_schema, colWidths=[1.8*inch, 1.3*inch, 3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (0, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph('Body Systems:', h2_style))
body_systems = 'Cardiovascular, Digestive, Endocrine, General, Immune, Integumentary, Musculoskeletal, Nervous, Reproductive, Respiratory, Urinary'
story.append(Paragraph(body_systems, body_style))
story.append(Spacer(1, 0.3*inch))

# Relationship Diagram
story.append(Paragraph('Table Relationships', h1_style))
story.append(Paragraph('''
<b>Primary Relationships:</b><br/>
&#8226; foods.food_id &#8594; food_nutrients.food_id (1:1)<br/>
&#8226; foods.food_id &#8594; food_phytochemicals.food_id (1:many)<br/>
&#8226; food_phytochemicals.chemical_name &#8594; food_health_activities.active_compound (many:many)<br/>
<br/>
<b>Important Note:</b> The food_health_activities table links to foods through the food_phytochemicals
table by matching active_compound to chemical_name. This allows finding foods with specific health
benefits through their phytochemical content.
''', body_style))

story.append(PageBreak())

# Sample Queries
story.append(Paragraph('Sample SQL Queries', h1_style))

story.append(Paragraph('1. Find Foods High in Vitamin C', h2_style))
query1 = '''SELECT f.food_name, n.vitamin_c_mg
FROM foods f
JOIN food_nutrients n ON f.food_id = n.food_id
WHERE n.vitamin_c_mg > 0
ORDER BY n.vitamin_c_mg DESC
LIMIT 20'''
story.append(Paragraph(query1.replace('\n', '<br/>'), code_style))

story.append(Paragraph('2. Find Anti-inflammatory Foods', h2_style))
query2 = '''SELECT DISTINCT f.food_name, a.activity, a.active_compound
FROM food_health_activities a
JOIN food_phytochemicals p
  ON LOWER(a.active_compound) = LOWER(p.chemical_name)
JOIN foods f ON p.food_id = f.food_id
WHERE LOWER(a.activity) LIKE '%antiinflammatory%'
LIMIT 30'''
story.append(Paragraph(query2.replace('\n', '<br/>'), code_style))

story.append(Paragraph('3. Find Foods for Digestive System', h2_style))
query3 = '''SELECT f.food_name, t.traditional_use, t.country_region
FROM food_traditional_uses t
JOIN foods f ON t.food_id = f.food_id
WHERE t.body_system = 'Digestive'
LIMIT 30'''
story.append(Paragraph(query3.replace('\n', '<br/>'), code_style))

story.append(Paragraph('4. Find Foods Containing Quercetin', h2_style))
query4 = '''SELECT f.food_name, p.chemical_name, p.amount_avg_ppm
FROM food_phytochemicals p
JOIN foods f ON p.food_id = f.food_id
WHERE LOWER(p.chemical_name) LIKE '%quercetin%'
ORDER BY p.amount_avg_ppm DESC NULLS LAST
LIMIT 20'''
story.append(Paragraph(query4.replace('\n', '<br/>'), code_style))

story.append(Spacer(1, 0.3*inch))

# API Endpoints
story.append(Paragraph('API Endpoints', h1_style))
story.append(Paragraph('Base URL: https://homeoherbal-api-1075463475276.us-central1.run.app', body_style))

api_data = [
    ['Endpoint', 'Method', 'Description'],
    ['/api/nl2sql/ask', 'POST', 'Natural language queries (NL2SQL)'],
    ['/api/quick/nutrient-rich?nutrient=X', 'GET', 'Foods high in nutrient X'],
    ['/api/quick/health-benefit?q=X', 'GET', 'Foods with health benefit X'],
    ['/api/quick/body-system?system=X', 'GET', 'Foods for body system X'],
    ['/api/quick/phytochemical?q=X', 'GET', 'Foods containing phytochemical X'],
    ['/api/food/search?q=X', 'GET', 'Search foods by name'],
    ['/api/stats', 'GET', 'Database statistics'],
]
t = Table(api_data, colWidths=[2.5*inch, 0.8*inch, 2.8*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (0, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('PADDING', (0, 0), (-1, -1), 6),
]))
story.append(t)

# Sample Health Activities
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph('Sample Health Activities in Database', h1_style))
activities_list = '''
Antiinflammatory, Antioxidant, Anticancer, Antimicrobial, Antiviral, Antibacterial,
Antifungal, Immunostimulant, Cardioprotective, Hypoglycemic, Hepatoprotective,
Neuroprotective, Analgesic, Antipyretic, Sedative, Anxiolytic, Antidepressant,
ACE-Inhibitor, 5-Lipoxygenase-Inhibitor, COX-2-Inhibitor, Antidiabetic, Antihypertensive
'''
story.append(Paragraph(activities_list, body_style))

# Footer
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', body_style))
story.append(Paragraph('Food AI - AI-Powered Nutrition & Health Intelligence', body_style))

doc.build(story)
print('PDF created: C:/1AITrading/Trading/FOOD_AI_DATABASE_SCHEMA.pdf')
