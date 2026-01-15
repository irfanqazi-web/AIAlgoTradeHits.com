from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=20)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=14, spaceAfter=12, spaceBefore=16)

doc = SimpleDocTemplate('GCP_RESOURCES_INVENTORY.pdf', pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
story = []
story.append(Paragraph('GCP Resources Inventory', title_style))
story.append(Paragraph('Complete Resource Listing', styles['Heading2']))
story.append(Spacer(1, 30))

story.append(Paragraph('GCP Projects', h1))
t = Table([['Project ID','Name','Number','Action'],
['aialgotradehits','aialgotradehits','1075463475276','Target'],
['cryptobot-462709','Cryptobot','252370699783','Migrate'],
['molten-optics-310919','KaamyabPakistan','521451186007','Migrate'],
['fine-effect-271218','My First Project','462483189212','Delete'],
['vertical-orbit-271201','My First Project','816289007899','Delete']], colWidths=[1.6*inch,1.3*inch,1.2*inch,0.8*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),8)]))
story.append(t)
story.append(Spacer(1, 15))

story.append(Paragraph('Cloud Run - aialgotradehits (4 services)', h1))
t = Table([['Service','URL'],
['trading-app','https://trading-app-6pmz2y7ouq-uc.a.run.app'],
['ai-trading-intelligence','https://ai-trading-intelligence-6pmz2y7ouq-uc.a.run.app'],
['smart-search','https://smart-search-6pmz2y7ouq-uc.a.run.app'],
['twelvedata-fetcher','https://twelvedata-fetcher-6pmz2y7ouq-uc.a.run.app']], colWidths=[1.8*inch,4*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),7)]))
story.append(t)
story.append(PageBreak())

story.append(Paragraph('Cloud Run - cryptobot-462709 (24 services)', h1))
services = ['crypto-app','crypto-core','crypto-trading-api','crypto-trading-app','daily-crypto-fetcher','daily-stock-fetcher','fivemin-top10-fetcher','hourly-crypto-fetcher','interest-rates-fetcher','stock-5min-fetcher','stock-daily-fetcher','stock-hourly-fetcher','system-monitoring','trading-analytics-app','trading-api','twelvedata-unified-fetcher','weekly-commodities-fetcher','weekly-crypto-fetcher','weekly-etf-fetcher','weekly-forex-fetcher','weekly-indices-fetcher','weekly-stock-fetcher','herbalhomeo-api','herbalhomeo-frontend']
data = [['Service','URL']]
for s in services:
    data.append([s,'https://'+s+'-cnyn5l4u2a-uc.a.run.app'])
t = Table(data, colWidths=[2*inch,3.8*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),7)]))
story.append(t)
story.append(PageBreak())

story.append(Paragraph('Cloud Schedulers - cryptobot-462709 (24 jobs)', h1))
scheds = [['Name','Schedule','Target'],
['daily-crypto-fetch-job','0 0 * * *','daily-crypto-fetcher'],
['hourly-crypto-fetch-job','0 * * * *','hourly-crypto-fetcher'],
['fivemin-top10-fetch-job','*/5 * * * *','fivemin-top10-fetcher'],
['stock-daily-fetch-job','0 0 * * *','stock-daily-fetcher'],
['stock-hourly-fetch-job','0 * * * *','stock-hourly-fetcher'],
['stock-5min-fetch-job','*/5 * * * *','stock-5min-fetcher'],
['twelvedata-stocks-daily','0 6 * * *','twelvedata-unified'],
['twelvedata-stocks-hourly','30 * * * *','twelvedata-unified'],
['twelvedata-crypto-daily','5 6 * * *','twelvedata-unified'],
['twelvedata-crypto-hourly','32 * * * *','twelvedata-unified'],
['twelvedata-forex-daily','10 6 * * *','twelvedata-unified'],
['twelvedata-forex-hourly','34 * * * *','twelvedata-unified'],
['twelvedata-etfs-daily','15 6 * * *','twelvedata-unified'],
['twelvedata-indices-daily','20 6 * * *','twelvedata-unified'],
['twelvedata-commodities-daily','25 6 * * *','twelvedata-unified'],
['interest-rates-daily','0 7 * * *','interest-rates-fetcher'],
['interest-rates-hourly','45 * * * *','interest-rates-fetcher'],
['weekly-crypto-fetch-job','30 4 * * 6','weekly-crypto-fetcher'],
['weekly-stock-fetch-job','0 4 * * 6','weekly-stock-fetcher'],
['weekly-forex-fetch-job','30 5 * * 6','weekly-forex-fetcher'],
['weekly-etf-fetch-job','0 5 * * 6','weekly-etf-fetcher'],
['weekly-indices-fetch-job','0 6 * * 6','weekly-indices-fetcher'],
['weekly-commodities-fetch-job','30 6 * * 6','weekly-commodities-fetcher'],
['twelvedata-all-weekly','0 8 * * 0','twelvedata-unified']]
t = Table(scheds, colWidths=[2.2*inch,1.2*inch,2*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),7)]))
story.append(t)
story.append(PageBreak())

story.append(Paragraph('BigQuery Tables - cryptobot-462709 (Top 25)', h1))
tables = [['Table','Records','Priority'],
['stocks_historical_daily','1,483,191','High'],
['etfs_historical_daily','527,277','Medium'],
['stocks_historical_daily_v2','616,546','Medium'],
['daily_crypto','196,231','High'],
['commodities_historical_daily','163,593','Medium'],
['forex_historical_daily_v2','150,000','Medium'],
['cryptos_historical_daily_v2','95,386','High'],
['stocks_daily','92,375','High'],
['indices_historical_daily','89,119','Medium'],
['5min_crypto','53,676','Medium'],
['crypto_daily','47,661','High'],
['cryptos_historical_daily','41,786','High'],
['stock_analysis','35,987','High'],
['etfs_daily','20,075','Medium'],
['forex_daily','16,425','Medium'],
['indices_daily','7,300','Medium'],
['commodities_daily','6,032','Medium'],
['hourly_crypto','5,244','Medium'],
['stocks_hourly','3,750','Medium'],
['crypto_hourly','2,530','Medium'],
['interest_rates','1,172','Medium'],
['users','5','High']]
t = Table(tables, colWidths=[2.5*inch,1.3*inch,1*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),8)]))
story.append(t)

doc.build(story)
print('Created: GCP_RESOURCES_INVENTORY.pdf')
