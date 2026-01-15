#!/usr/bin/env python3
"""
Generate Detailed Asset Status Report PDF
Shows ticker, name, price, records, start/end dates for all assets
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
import pandas as pd

PROJECT_ID = 'aialgotradehits'

# Company/Asset name mappings
STOCK_NAMES = {
    'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corp.', 'GOOGL': 'Alphabet Inc. Class A',
    'GOOG': 'Alphabet Inc. Class C', 'AMZN': 'Amazon.com Inc.', 'NVDA': 'NVIDIA Corp.',
    'META': 'Meta Platforms Inc.', 'TSLA': 'Tesla Inc.', 'BRK.B': 'Berkshire Hathaway B',
    'UNH': 'UnitedHealth Group', 'LLY': 'Eli Lilly & Co.', 'JPM': 'JPMorgan Chase',
    'XOM': 'Exxon Mobil Corp.', 'V': 'Visa Inc.', 'JNJ': 'Johnson & Johnson',
    'AVGO': 'Broadcom Inc.', 'PG': 'Procter & Gamble', 'MA': 'Mastercard Inc.',
    'HD': 'Home Depot Inc.', 'COST': 'Costco Wholesale', 'MRK': 'Merck & Co.',
    'ABBV': 'AbbVie Inc.', 'CVX': 'Chevron Corp.', 'CRM': 'Salesforce Inc.',
    'KO': 'Coca-Cola Co.', 'PEP': 'PepsiCo Inc.', 'AMD': 'Advanced Micro Devices',
    'ADBE': 'Adobe Inc.', 'WMT': 'Walmart Inc.', 'MCD': "McDonald's Corp.",
    'CSCO': 'Cisco Systems', 'BAC': 'Bank of America', 'ACN': 'Accenture plc',
    'NFLX': 'Netflix Inc.', 'TMO': 'Thermo Fisher Scientific', 'LIN': 'Linde plc',
    'ORCL': 'Oracle Corp.', 'ABT': 'Abbott Laboratories', 'DHR': 'Danaher Corp.',
    'INTC': 'Intel Corp.', 'DIS': 'Walt Disney Co.', 'PM': 'Philip Morris Intl',
    'CMCSA': 'Comcast Corp.', 'VZ': 'Verizon Communications', 'WFC': 'Wells Fargo',
    'TXN': 'Texas Instruments', 'NKE': 'Nike Inc.', 'COP': 'ConocoPhillips',
    'INTU': 'Intuit Inc.', 'RTX': 'RTX Corp.', 'NEE': 'NextEra Energy',
    'QCOM': 'Qualcomm Inc.', 'HON': 'Honeywell Intl', 'IBM': 'IBM Corp.',
    'AMGN': 'Amgen Inc.', 'UNP': 'Union Pacific Corp.', 'LOW': "Lowe's Companies",
    'SPGI': 'S&P Global Inc.', 'CAT': 'Caterpillar Inc.', 'GE': 'General Electric',
    'BA': 'Boeing Co.', 'PLD': 'Prologis Inc.', 'SBUX': 'Starbucks Corp.',
    'DE': 'Deere & Co.', 'ELV': 'Elevance Health', 'AMAT': 'Applied Materials',
    'BMY': 'Bristol-Myers Squibb', 'GS': 'Goldman Sachs', 'BLK': 'BlackRock Inc.',
    'MDLZ': 'Mondelez Intl', 'ADI': 'Analog Devices', 'ISRG': 'Intuitive Surgical',
    'GILD': 'Gilead Sciences', 'MMC': 'Marsh & McLennan', 'ADP': 'ADP Inc.',
    'TJX': 'TJX Companies', 'VRTX': 'Vertex Pharmaceuticals', 'AMT': 'American Tower',
    'SYK': 'Stryker Corp.', 'REGN': 'Regeneron Pharma', 'LMT': 'Lockheed Martin',
    'BKNG': 'Booking Holdings', 'MO': 'Altria Group', 'ETN': 'Eaton Corp.',
    'LRCX': 'Lam Research', 'CB': 'Chubb Ltd.', 'CI': 'Cigna Group',
    'PGR': 'Progressive Corp.', 'C': 'Citigroup Inc.', 'ZTS': 'Zoetis Inc.',
    'PANW': 'Palo Alto Networks', 'BDX': 'Becton Dickinson', 'SCHW': 'Charles Schwab',
    'EOG': 'EOG Resources', 'SO': 'Southern Co.', 'MU': 'Micron Technology',
    'CME': 'CME Group Inc.', 'NOC': 'Northrop Grumman', 'DUK': 'Duke Energy',
    'SLB': 'Schlumberger Ltd.', 'PNC': 'PNC Financial', 'ICE': 'Intercontinental Exchange',
    'MCK': 'McKesson Corp.', 'CL': 'Colgate-Palmolive', 'SNPS': 'Synopsys Inc.',
    'BSX': 'Boston Scientific', 'CDNS': 'Cadence Design', 'AON': 'Aon plc',
    'ITW': 'Illinois Tool Works', 'USB': 'U.S. Bancorp', 'CMG': 'Chipotle Mexican Grill',
    'WM': 'Waste Management', 'EQIX': 'Equinix Inc.', 'SHW': 'Sherwin-Williams',
    'FCX': 'Freeport-McMoRan', 'ORLY': "O'Reilly Automotive", 'APD': 'Air Products',
    'KLAC': 'KLA Corp.', 'MSI': 'Motorola Solutions', 'GD': 'General Dynamics',
    'MPC': 'Marathon Petroleum', 'TGT': 'Target Corp.', 'EMR': 'Emerson Electric',
    'PSX': 'Phillips 66', 'MMM': '3M Company', 'PH': 'Parker-Hannifin',
    'AJG': 'Arthur J. Gallagher', 'ROP': 'Roper Technologies', 'CARR': 'Carrier Global',
    'NSC': 'Norfolk Southern', 'PCAR': 'PACCAR Inc.', 'MAR': 'Marriott Intl',
    'GM': 'General Motors', 'CTAS': 'Cintas Corp.', 'HLT': 'Hilton Worldwide',
    'NEM': 'Newmont Corp.', 'AZO': 'AutoZone Inc.', 'WELL': 'Welltower Inc.',
    'TRV': 'Travelers Companies', 'MCHP': 'Microchip Technology', 'AIG': 'American Intl Group',
    'FDX': 'FedEx Corp.', 'OXY': 'Occidental Petroleum', 'ECL': 'Ecolab Inc.',
    'F': 'Ford Motor Co.', 'AFL': 'Aflac Inc.', 'TEL': 'TE Connectivity',
    'CPRT': 'Copart Inc.', 'DXCM': 'DexCom Inc.', 'KMB': 'Kimberly-Clark',
    'FTNT': 'Fortinet Inc.', 'SRE': 'Sempra Energy', 'PAYX': 'Paychex Inc.',
    'D': 'Dominion Energy', 'AEP': 'American Electric Power', 'A': 'Agilent Technologies',
    'PSA': 'Public Storage', 'MSCI': 'MSCI Inc.', 'O': 'Realty Income Corp.',
    'DHI': 'D.R. Horton', 'BK': 'Bank of New York Mellon', 'IDXX': 'IDEXX Laboratories',
    'GIS': 'General Mills', 'CCI': 'Crown Castle Intl', 'ROST': 'Ross Stores',
    'KDP': 'Keurig Dr Pepper', 'JCI': 'Johnson Controls', 'MNST': 'Monster Beverage',
    'FAST': 'Fastenal Co.', 'KMI': 'Kinder Morgan', 'YUM': 'Yum! Brands',
    'CTVA': 'Corteva Inc.', 'AME': 'AMETEK Inc.', 'AMP': 'Ameriprise Financial',
    'ODFL': 'Old Dominion Freight', 'EXC': 'Exelon Corp.', 'GWW': 'W.W. Grainger',
    'CMI': 'Cummins Inc.', 'LHX': 'L3Harris Technologies', 'ALL': 'Allstate Corp.',
    'VRSK': 'Verisk Analytics', 'OTIS': 'Otis Worldwide', 'IQV': 'IQVIA Holdings',
    'HAL': 'Halliburton Co.', 'XEL': 'Xcel Energy', 'PCG': 'PG&E Corp.',
    'GEHC': 'GE HealthCare', 'CTSH': 'Cognizant Technology', 'IT': 'Gartner Inc.',
    'HUM': 'Humana Inc.', 'DVN': 'Devon Energy', 'MLM': 'Martin Marietta',
    'KR': 'Kroger Co.', 'EW': 'Edwards Lifesciences', 'WEC': 'WEC Energy Group',
    'ED': 'Consolidated Edison', 'VMC': 'Vulcan Materials', 'FANG': 'Diamondback Energy',
    'DD': 'DuPont de Nemours', 'PYPL': 'PayPal Holdings', 'NOW': 'ServiceNow Inc.',
    'UBER': 'Uber Technologies', 'ABNB': 'Airbnb Inc.', 'SQ': 'Block Inc.',
    'SHOP': 'Shopify Inc.', 'SNOW': 'Snowflake Inc.', 'PLTR': 'Palantir Technologies',
    'COIN': 'Coinbase Global', 'RIVN': 'Rivian Automotive', 'LCID': 'Lucid Group',
    'NIO': 'NIO Inc.', 'XPEV': 'XPeng Inc.', 'LI': 'Li Auto Inc.',
    'DKNG': 'DraftKings Inc.', 'RBLX': 'Roblox Corp.', 'U': 'Unity Software',
    'CRWD': 'CrowdStrike Holdings', 'ZS': 'Zscaler Inc.', 'OKTA': 'Okta Inc.',
    'DDOG': 'Datadog Inc.', 'NET': 'Cloudflare Inc.', 'MDB': 'MongoDB Inc.',
    'TWLO': 'Twilio Inc.', 'DOCU': 'DocuSign Inc.', 'ZM': 'Zoom Video',
    'SPOT': 'Spotify Technology', 'PINS': 'Pinterest Inc.', 'SNAP': 'Snap Inc.',
    'TTD': 'The Trade Desk', 'AFRM': 'Affirm Holdings', 'PATH': 'UiPath Inc.',
    'BILL': 'Bill Holdings', 'HUBS': 'HubSpot Inc.', 'ESTC': 'Elastic N.V.',
    'MNDY': 'monday.com Ltd.', 'GTLB': 'GitLab Inc.', 'S': 'SentinelOne Inc.',
    'IOT': 'Samsara Inc.', 'AI': 'C3.ai Inc.'
}

CRYPTO_NAMES = {
    'BTCUSD': 'Bitcoin', 'ETHUSD': 'Ethereum', 'BNBUSD': 'Binance Coin',
    'XRPUSD': 'Ripple', 'SOLUSD': 'Solana', 'DOGEUSD': 'Dogecoin',
    'ADAUSD': 'Cardano', 'AVAXUSD': 'Avalanche', 'LINKUSD': 'Chainlink',
    'DOTUSD': 'Polkadot', 'SHIBUSD': 'Shiba Inu', 'TRXUSD': 'TRON',
    'UNIUSD': 'Uniswap', 'ATOMUSD': 'Cosmos', 'LTCUSD': 'Litecoin',
    'NEARUSD': 'NEAR Protocol', 'APTUSD': 'Aptos', 'FILUSD': 'Filecoin',
    'ARBUSD': 'Arbitrum', 'XMRUSD': 'Monero', 'BCHUSD': 'Bitcoin Cash',
    'XLMUSD': 'Stellar', 'ETCUSD': 'Ethereum Classic', 'HBARUSD': 'Hedera',
    'VETUSD': 'VeChain', 'ALGOUSD': 'Algorand', 'SANDUSD': 'The Sandbox',
    'MANAUSD': 'Decentraland', 'AAVEUSD': 'Aave', 'THETAUSD': 'Theta Network',
    'XTZUSD': 'Tezos', 'AXSUSD': 'Axie Infinity', 'SNXUSD': 'Synthetix',
    'COMPUSD': 'Compound', 'ZECUSD': 'Zcash', 'DASHUSD': 'Dash',
    'ENJUSD': 'Enjin Coin', 'BATUSD': 'Basic Attention Token', 'CRVUSD': 'Curve DAO',
    'LRCUSD': 'Loopring', 'SUSHIUSD': 'SushiSwap', 'YFIUSD': 'yearn.finance',
    '1INCHUSD': '1inch Network', 'GRTUSD': 'The Graph', 'CHZUSD': 'Chiliz',
    'IOTAUSD': 'IOTA', 'KAVAUSD': 'Kava', 'CELOUSD': 'Celo',
    'ZRXUSD': '0x Protocol', 'ANKRUSD': 'Ankr', 'GALAUSD': 'Gala',
    'IMXUSD': 'Immutable X', 'LDOUSD': 'Lido DAO', 'RPLUSD': 'Rocket Pool',
    'OPUSD': 'Optimism', 'INJUSD': 'Injective', 'RUNEUSD': 'THORChain',
    'KSMUSD': 'Kusama', 'FLOWUSD': 'Flow', 'EGLDUSD': 'MultiversX',
    'NEOUSD': 'NEO', 'WAVESUSD': 'Waves', 'QTUMUSD': 'Qtum',
    'ICXUSD': 'ICON', 'ONTUSD': 'Ontology', 'ZILUSD': 'Zilliqa',
    'STORJUSD': 'Storj', 'SKLUSD': 'SKALE Network'
}

ETF_NAMES = {
    'SPY': 'SPDR S&P 500 ETF', 'QQQ': 'Invesco QQQ Trust', 'IWM': 'iShares Russell 2000',
    'DIA': 'SPDR Dow Jones ETF', 'VTI': 'Vanguard Total Stock Market', 'VOO': 'Vanguard S&P 500',
    'VEA': 'Vanguard FTSE Developed', 'VWO': 'Vanguard FTSE Emerging', 'EFA': 'iShares MSCI EAFE',
    'EEM': 'iShares MSCI Emerging', 'XLF': 'Financial Select Sector', 'XLE': 'Energy Select Sector',
    'XLK': 'Technology Select Sector', 'XLV': 'Health Care Select Sector', 'XLI': 'Industrial Select Sector',
    'XLY': 'Consumer Discretionary', 'XLP': 'Consumer Staples Select', 'XLB': 'Materials Select Sector',
    'XLU': 'Utilities Select Sector', 'XLRE': 'Real Estate Select', 'GLD': 'SPDR Gold Shares',
    'SLV': 'iShares Silver Trust', 'USO': 'United States Oil Fund', 'UNG': 'United States Natural Gas',
    'TLT': 'iShares 20+ Year Treasury', 'IEF': 'iShares 7-10 Year Treasury', 'SHY': 'iShares 1-3 Year Treasury',
    'LQD': 'iShares Investment Grade', 'HYG': 'iShares High Yield Corp', 'JNK': 'SPDR High Yield Bond',
    'VNQ': 'Vanguard Real Estate', 'ARKK': 'ARK Innovation ETF', 'ARKG': 'ARK Genomic Revolution',
    'ARKW': 'ARK Next Gen Internet', 'ARKF': 'ARK Fintech Innovation', 'SMH': 'VanEck Semiconductor',
    'XBI': 'SPDR S&P Biotech', 'IBB': 'iShares Biotechnology', 'KRE': 'SPDR Regional Banking',
    'XHB': 'SPDR Homebuilders'
}

INDEX_NAMES = {
    'SPX': 'S&P 500 Index', 'NDX': 'NASDAQ-100 Index', 'DJI': 'Dow Jones Industrial',
    'VIX': 'CBOE Volatility Index', 'FTSE': 'FTSE 100 Index', 'DAX': 'DAX Index',
    'CAC': 'CAC 40 Index', 'HSI': 'Hang Seng Index', 'IBEX': 'IBEX 35 Index',
    'SMI': 'Swiss Market Index', 'AEX': 'AEX Index'
}

FOREX_NAMES = {
    'EURUSD': 'Euro/US Dollar', 'GBPUSD': 'British Pound/US Dollar', 'USDJPY': 'US Dollar/Japanese Yen',
    'USDCHF': 'US Dollar/Swiss Franc', 'AUDUSD': 'Australian Dollar/US Dollar', 'USDCAD': 'US Dollar/Canadian Dollar',
    'NZDUSD': 'New Zealand Dollar/USD', 'EURGBP': 'Euro/British Pound', 'EURJPY': 'Euro/Japanese Yen',
    'GBPJPY': 'British Pound/Japanese Yen', 'EURCHF': 'Euro/Swiss Franc', 'EURAUD': 'Euro/Australian Dollar',
    'EURCAD': 'Euro/Canadian Dollar', 'EURNZD': 'Euro/New Zealand Dollar', 'GBPCHF': 'British Pound/Swiss Franc',
    'GBPAUD': 'British Pound/Australian Dollar', 'GBPCAD': 'British Pound/Canadian Dollar',
    'GBPNZD': 'British Pound/New Zealand Dollar', 'AUDJPY': 'Australian Dollar/Japanese Yen',
    'AUDNZD': 'Australian Dollar/New Zealand Dollar', 'AUDCAD': 'Australian Dollar/Canadian Dollar',
    'CADJPY': 'Canadian Dollar/Japanese Yen', 'NZDJPY': 'New Zealand Dollar/Japanese Yen',
    'CHFJPY': 'Swiss Franc/Japanese Yen', 'USDMXN': 'US Dollar/Mexican Peso',
    'USDZAR': 'US Dollar/South African Rand', 'USDTRY': 'US Dollar/Turkish Lira',
    'USDSGD': 'US Dollar/Singapore Dollar', 'USDHKD': 'US Dollar/Hong Kong Dollar',
    'USDSEK': 'US Dollar/Swedish Krona'
}

def get_name(symbol, asset_type):
    """Get the full name for a symbol"""
    symbol_clean = symbol.replace('/', '')
    if asset_type == 'STOCK':
        return STOCK_NAMES.get(symbol, symbol)
    elif asset_type == 'CRYPTO':
        return CRYPTO_NAMES.get(symbol_clean, symbol)
    elif asset_type == 'ETF':
        return ETF_NAMES.get(symbol, symbol)
    elif asset_type == 'INDEX':
        return INDEX_NAMES.get(symbol, symbol)
    elif asset_type == 'FOREX':
        return FOREX_NAMES.get(symbol_clean, symbol)
    return symbol

def main():
    print("="*70)
    print("GENERATING DETAILED ASSET STATUS REPORT")
    print(f"Started: {datetime.now()}")
    print("="*70)

    # Query BigQuery for detailed data
    client = bigquery.Client(project=PROJECT_ID)

    query = '''
    WITH latest_prices AS (
        SELECT
            symbol,
            close as latest_price,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
        FROM `aialgotradehits.crypto_trading_data.twelvedata_max_quota`
    )
    SELECT
        t.asset_type,
        t.symbol,
        t.`interval` as time_interval,
        COUNT(*) as records,
        MIN(t.datetime) as start_date,
        MAX(t.datetime) as end_date,
        lp.latest_price
    FROM `aialgotradehits.crypto_trading_data.twelvedata_max_quota` t
    LEFT JOIN latest_prices lp ON t.symbol = lp.symbol AND lp.rn = 1
    GROUP BY t.asset_type, t.symbol, t.`interval`, lp.latest_price
    ORDER BY t.asset_type, records DESC
    '''

    print("Querying BigQuery...")
    df = client.query(query).to_dataframe()

    # Add names
    df['name'] = df.apply(lambda row: get_name(row['symbol'], row['asset_type']), axis=1)

    # Convert date columns to datetime
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')

    # Create PDF with datetime in filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = f"C:/1AITrading/Trading/ASSET_STATUS_REPORT_{timestamp}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter),
                           leftMargin=0.5*inch, rightMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18,
                                  alignment=1, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14,
                                    spaceAfter=10, spaceBefore=15)

    elements = []

    # Title
    elements.append(Paragraph("TwelveData $229 Pro Plan - Asset Status Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Executive Summary
    total_records = df['records'].sum()
    total_symbols = df['symbol'].nunique()

    summary_data = [
        ['Metric', 'Value'],
        ['Total Records', f'{total_records:,}'],
        ['Unique Symbols', f'{total_symbols}'],
        ['Daily Quota', '2,000,000'],
        ['Quota Used', f'{(total_records/2000000*100):.1f}%'],
        ['Last Fetch', df['end_date'].max().strftime('%Y-%m-%d %H:%M') if pd.notna(df['end_date'].max()) else 'N/A']
    ]

    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))

    # Asset Type Summary
    elements.append(Paragraph("Summary by Asset Type", heading_style))

    asset_summary = df.groupby('asset_type').agg({
        'symbol': 'nunique',
        'records': 'sum'
    }).reset_index()
    asset_summary.columns = ['Asset Type', 'Symbols', 'Records']
    asset_summary['Records'] = asset_summary['Records'].apply(lambda x: f'{x:,}')

    asset_data = [['Asset Type', 'Symbols', 'Records']] + asset_summary.values.tolist()
    asset_table = Table(asset_data, colWidths=[2*inch, 1.5*inch, 2*inch])
    asset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(asset_table)

    # Detailed tables for each asset type
    for asset_type in ['STOCK', 'CRYPTO', 'ETF', 'INDEX', 'FOREX']:
        asset_df = df[df['asset_type'] == asset_type].copy()
        if len(asset_df) == 0:
            continue

        elements.append(PageBreak())
        elements.append(Paragraph(f"{asset_type} - Detailed Breakdown ({len(asset_df)} items)", heading_style))

        # Prepare data
        asset_df = asset_df.sort_values('records', ascending=False)

        table_data = [['#', 'Ticker', 'Name', 'Interval', 'Price', 'Records', 'Start Date', 'End Date']]

        for idx, row in enumerate(asset_df.itertuples(), 1):
            price_str = f"${row.latest_price:,.2f}" if pd.notna(row.latest_price) and row.latest_price > 0 else 'N/A'
            if asset_type == 'CRYPTO' and pd.notna(row.latest_price):
                if row.latest_price < 1:
                    price_str = f"${row.latest_price:.6f}"
                elif row.latest_price > 1000:
                    price_str = f"${row.latest_price:,.0f}"

            start_str = row.start_date.strftime('%Y-%m-%d') if pd.notna(row.start_date) else 'N/A'
            end_str = row.end_date.strftime('%Y-%m-%d') if pd.notna(row.end_date) else 'N/A'

            # Truncate name if too long
            name = row.name[:25] + '...' if len(row.name) > 28 else row.name

            table_data.append([
                str(idx),
                row.symbol,
                name,
                row.time_interval,
                price_str,
                f'{row.records:,}',
                start_str,
                end_str
            ])

        # Create table with appropriate column widths
        col_widths = [0.4*inch, 0.8*inch, 2.2*inch, 0.7*inch, 1*inch, 0.9*inch, 1*inch, 1*inch]
        detail_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Determine header color based on asset type
        header_colors = {
            'STOCK': colors.darkblue,
            'CRYPTO': colors.darkorange,
            'ETF': colors.darkgreen,
            'INDEX': colors.purple,
            'FOREX': colors.darkred
        }

        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_colors.get(asset_type, colors.black)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))

        elements.append(detail_table)

    # Build PDF
    print("Building PDF...")
    doc.build(elements)

    print(f"\n{'='*70}")
    print(f"REPORT GENERATED SUCCESSFULLY")
    print(f"{'='*70}")
    print(f"File: {pdf_path}")
    print(f"Total Records: {total_records:,}")
    print(f"Total Symbols: {total_symbols}")
    print(f"Quota Used: {(total_records/2000000*100):.1f}%")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
