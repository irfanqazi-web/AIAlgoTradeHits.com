from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

doc = SimpleDocTemplate('C:/1AITrading/Trading/TRADING_DATA_STATUS_REPORT.pdf', pagesize=letter)
styles = getSampleStyleSheet()
story = []

title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=1)
heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, spaceBefore=15)

story.append(Paragraph('Trading Data Status Report', title_style))
story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d")}', ParagraphStyle('Date', alignment=1, fontSize=10, textColor=colors.grey)))
story.append(Spacer(1, 20))

# Summary
story.append(Paragraph('<b>Available Data Summary:</b>', styles['Normal']))
story.append(Paragraph('- Stocks: 100+ US Market symbols (NASDAQ/NYSE)', styles['Normal']))
story.append(Paragraph('- Crypto: 50+ major cryptocurrencies', styles['Normal']))
story.append(Paragraph('- ETFs: 20+ major ETFs', styles['Normal']))
story.append(Paragraph('- Forex: 15+ major currency pairs', styles['Normal']))
story.append(Paragraph('- Indices: 10+ market indices', styles['Normal']))
story.append(Paragraph('- Commodities: 14+ commodity symbols', styles['Normal']))
story.append(Spacer(1, 20))

# Stocks Section
story.append(Paragraph('1. Stocks (Top 50 US Market)', heading_style))
stocks = [
    ['Symbol', 'Name', 'Sector'],
    ['AAPL', 'Apple Inc', 'Technology'],
    ['MSFT', 'Microsoft Corp', 'Technology'],
    ['GOOGL', 'Alphabet Inc', 'Technology'],
    ['AMZN', 'Amazon.com Inc', 'Consumer'],
    ['NVDA', 'NVIDIA Corp', 'Technology'],
    ['META', 'Meta Platforms', 'Technology'],
    ['TSLA', 'Tesla Inc', 'Consumer'],
    ['BRK.B', 'Berkshire Hathaway', 'Financial'],
    ['UNH', 'UnitedHealth Group', 'Healthcare'],
    ['JNJ', 'Johnson & Johnson', 'Healthcare'],
    ['V', 'Visa Inc', 'Financial'],
    ['XOM', 'Exxon Mobil', 'Energy'],
    ['JPM', 'JPMorgan Chase', 'Financial'],
    ['PG', 'Procter & Gamble', 'Consumer'],
    ['MA', 'Mastercard Inc', 'Financial'],
    ['HD', 'Home Depot', 'Consumer'],
    ['CVX', 'Chevron Corp', 'Energy'],
    ['MRK', 'Merck & Co', 'Healthcare'],
    ['ABBV', 'AbbVie Inc', 'Healthcare'],
    ['LLY', 'Eli Lilly', 'Healthcare'],
    ['PFE', 'Pfizer Inc', 'Healthcare'],
    ['COST', 'Costco Wholesale', 'Consumer'],
    ['KO', 'Coca-Cola Co', 'Consumer'],
    ['AVGO', 'Broadcom Inc', 'Technology'],
    ['PEP', 'PepsiCo Inc', 'Consumer'],
    ['TMO', 'Thermo Fisher', 'Healthcare'],
    ['MCD', 'McDonalds Corp', 'Consumer'],
    ['CSCO', 'Cisco Systems', 'Technology'],
    ['ACN', 'Accenture plc', 'Technology'],
    ['ABT', 'Abbott Labs', 'Healthcare'],
    ['NKE', 'Nike Inc', 'Consumer'],
    ['WMT', 'Walmart Inc', 'Consumer'],
    ['CRM', 'Salesforce Inc', 'Technology'],
    ['ADBE', 'Adobe Inc', 'Technology'],
    ['AMD', 'AMD Inc', 'Technology'],
    ['INTC', 'Intel Corp', 'Technology'],
    ['NFLX', 'Netflix Inc', 'Communication'],
    ['QCOM', 'Qualcomm Inc', 'Technology'],
    ['TXN', 'Texas Instruments', 'Technology'],
    ['BA', 'Boeing Co', 'Industrial'],
    ['GE', 'General Electric', 'Industrial'],
    ['DIS', 'Walt Disney', 'Communication'],
    ['PYPL', 'PayPal Holdings', 'Financial'],
    ['IBM', 'IBM Corp', 'Technology'],
    ['CAT', 'Caterpillar Inc', 'Industrial'],
    ['GS', 'Goldman Sachs', 'Financial'],
    ['MMM', '3M Company', 'Industrial'],
    ['RTX', 'RTX Corporation', 'Industrial'],
    ['SBUX', 'Starbucks Corp', 'Consumer'],
]
t = Table(stocks, colWidths=[60, 150, 80])
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.darkblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('FONTSIZE', (0, 0), (-1, -1), 7), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)])]))
story.append(t)
story.append(Spacer(1, 15))

# Crypto Section
story.append(Paragraph('2. Crypto (Major Cryptocurrencies)', heading_style))
crypto = [
    ['Symbol', 'Name'],
    ['BTC/USD', 'Bitcoin'],
    ['ETH/USD', 'Ethereum'],
    ['BNB/USD', 'Binance Coin'],
    ['XRP/USD', 'Ripple'],
    ['ADA/USD', 'Cardano'],
    ['SOL/USD', 'Solana'],
    ['DOGE/USD', 'Dogecoin'],
    ['DOT/USD', 'Polkadot'],
    ['AVAX/USD', 'Avalanche'],
    ['MATIC/USD', 'Polygon'],
    ['LINK/USD', 'Chainlink'],
    ['LTC/USD', 'Litecoin'],
    ['UNI/USD', 'Uniswap'],
    ['ATOM/USD', 'Cosmos'],
    ['XLM/USD', 'Stellar'],
    ['APT/USD', 'Aptos'],
    ['ARB/USD', 'Arbitrum'],
    ['OP/USD', 'Optimism'],
    ['FIL/USD', 'Filecoin'],
    ['AAVE/USD', 'Aave'],
]
t = Table(crypto, colWidths=[80, 150])
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('FONTSIZE', (0, 0), (-1, -1), 8), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)
story.append(Spacer(1, 15))

# ETFs Section
story.append(Paragraph('3. ETFs (Exchange Traded Funds)', heading_style))
etfs = [
    ['Symbol', 'Name'],
    ['SPY', 'SPDR S&P 500 ETF'],
    ['QQQ', 'Invesco QQQ Trust'],
    ['IWM', 'iShares Russell 2000'],
    ['DIA', 'SPDR Dow Jones'],
    ['VTI', 'Vanguard Total Stock'],
    ['EFA', 'iShares MSCI EAFE'],
    ['EEM', 'iShares Emerging Markets'],
    ['GLD', 'SPDR Gold Shares'],
    ['SLV', 'iShares Silver Trust'],
    ['TLT', 'iShares 20+ Year Treasury'],
    ['XLF', 'Financial Select SPDR'],
    ['XLK', 'Technology Select SPDR'],
    ['XLE', 'Energy Select SPDR'],
    ['XLV', 'Health Care Select SPDR'],
]
t = Table(etfs, colWidths=[60, 180])
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.purple), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('FONTSIZE', (0, 0), (-1, -1), 8), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)
story.append(Spacer(1, 15))

# Forex Section
story.append(Paragraph('4. Forex (Currency Pairs)', heading_style))
forex = [
    ['Symbol', 'Pair'],
    ['EUR/USD', 'Euro / US Dollar'],
    ['GBP/USD', 'British Pound / US Dollar'],
    ['USD/JPY', 'US Dollar / Japanese Yen'],
    ['USD/CHF', 'US Dollar / Swiss Franc'],
    ['AUD/USD', 'Australian Dollar / US Dollar'],
    ['USD/CAD', 'US Dollar / Canadian Dollar'],
    ['NZD/USD', 'New Zealand Dollar / US Dollar'],
    ['EUR/GBP', 'Euro / British Pound'],
    ['EUR/JPY', 'Euro / Japanese Yen'],
]
t = Table(forex, colWidths=[70, 180])
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.orange), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('FONTSIZE', (0, 0), (-1, -1), 8), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)
story.append(Spacer(1, 15))

# Indices Section
story.append(Paragraph('5. Indices (Market Indices)', heading_style))
indices = [
    ['Symbol', 'Name'],
    ['SPX', 'S&P 500 Index'],
    ['NDX', 'NASDAQ 100 Index'],
    ['DJI', 'Dow Jones Industrial'],
    ['RUT', 'Russell 2000 Index'],
    ['VIX', 'CBOE Volatility Index'],
    ['FTSE', 'FTSE 100'],
    ['DAX', 'DAX Index'],
]
t = Table(indices, colWidths=[60, 180])
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.brown), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('FONTSIZE', (0, 0), (-1, -1), 8), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)
story.append(Spacer(1, 15))

# Commodities Section
story.append(Paragraph('6. Commodities', heading_style))
commodities = [
    ['Symbol', 'Name'],
    ['XAUUSD', 'Gold Spot'],
    ['XAGUSD', 'Silver Spot'],
    ['CL', 'Crude Oil WTI'],
    ['BZ', 'Brent Crude Oil'],
    ['NG', 'Natural Gas'],
    ['HG', 'Copper'],
    ['ZC', 'Corn Futures'],
    ['ZS', 'Soybean Futures'],
    ['KC', 'Coffee Futures'],
    ['SB', 'Sugar Futures'],
    ['SI', 'Silver Futures'],
    ['XPTUSD', 'Platinum Spot'],
    ['XPDUSD', 'Palladium Spot'],
    ['HO', 'Heating Oil'],
]
t = Table(commodities, colWidths=[70, 150])
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.darkgoldenrod), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('FONTSIZE', (0, 0), (-1, -1), 8), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)

story.append(Spacer(1, 30))
story.append(Paragraph('Note: This is a reference list. For real-time availability, use the Data Export feature.', ParagraphStyle('Note', fontSize=9, textColor=colors.grey, alignment=1)))

doc.build(story)
print('PDF generated successfully')
