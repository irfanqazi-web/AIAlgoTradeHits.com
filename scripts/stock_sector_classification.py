#!/usr/bin/env python3
"""
Stock Sector & Industry Classification
=======================================
Creates a comprehensive classification table for all stocks with:
- GICS Sector (11 sectors)
- Industry Group
- Industry
- Sub-Industry

This will be used for sector-based ML models and sentiment integration.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 70)
print("STOCK SECTOR & INDUSTRY CLASSIFICATION")
print("=" * 70)
print(f"Started: {datetime.now()}")

# =============================================================================
# GICS Sector Classification for S&P 500 and Major Stocks
# =============================================================================

# Complete stock classification by sector and industry
STOCK_CLASSIFICATION = {
    # =========================================================================
    # TECHNOLOGY SECTOR
    # =========================================================================
    'Technology': {
        'Software & Services': {
            'Software': ['MSFT', 'CRM', 'ADBE', 'NOW', 'INTU', 'SNPS', 'CDNS', 'ANSS', 'FTNT', 'PANW'],
            'IT Services': ['IBM', 'ACN', 'CTSH', 'IT'],
            'Internet Services': ['GOOGL', 'META', 'NFLX'],
        },
        'Hardware & Equipment': {
            'Semiconductors': ['NVDA', 'AMD', 'AVGO', 'QCOM', 'TXN', 'INTC', 'AMAT', 'LRCX', 'KLAC', 'MCHP', 'ADI', 'MU', 'ON'],
            'Hardware': ['AAPL', 'CSCO', 'HPQ', 'KEYS', 'TEL', 'MSI'],
            'Communications Equipment': ['CSCO', 'MSI'],
        },
    },

    # =========================================================================
    # HEALTHCARE SECTOR
    # =========================================================================
    'Healthcare': {
        'Pharmaceuticals': {
            'Large Pharma': ['JNJ', 'LLY', 'MRK', 'PFE', 'ABBV', 'BMY'],
            'Biotech': ['AMGN', 'GILD', 'VRTX', 'REGN', 'BIIB', 'MRNA'],
        },
        'Healthcare Equipment': {
            'Medical Devices': ['ABT', 'MDT', 'SYK', 'BSX', 'EW', 'ISRG', 'DXCM', 'BDX', 'ZBH'],
            'Diagnostics': ['DHR', 'TMO', 'A', 'IQV', 'IDXX'],
        },
        'Healthcare Services': {
            'Managed Care': ['UNH', 'ELV', 'CI', 'HUM', 'CNC'],
            'Healthcare Facilities': ['HCA'],
            'Distributors': ['MCK', 'CAH', 'ABC'],
        },
    },

    # =========================================================================
    # FINANCIALS SECTOR
    # =========================================================================
    'Financials': {
        'Banks': {
            'Diversified Banks': ['JPM', 'BAC', 'WFC', 'C', 'USB', 'PNC', 'TFC'],
            'Investment Banks': ['GS', 'MS'],
        },
        'Financial Services': {
            'Payment Processors': ['V', 'MA', 'PYPL', 'AXP', 'FIS', 'FISV', 'GPN'],
            'Exchanges': ['CME', 'ICE', 'NDAQ', 'CBOE'],
            'Asset Managers': ['BLK', 'BK', 'STT', 'TROW', 'SCHW'],
        },
        'Insurance': {
            'P&C Insurance': ['CB', 'TRV', 'ALL', 'PGR', 'AIG'],
            'Life Insurance': ['MET', 'PRU', 'AFL', 'LNC'],
            'Insurance Brokers': ['MMC', 'AON', 'AJG', 'WTW', 'BRO'],
        },
    },

    # =========================================================================
    # CONSUMER DISCRETIONARY SECTOR
    # =========================================================================
    'Consumer Discretionary': {
        'Retail': {
            'E-Commerce': ['AMZN', 'EBAY', 'ETSY'],
            'Home Improvement': ['HD', 'LOW'],
            'Specialty Retail': ['TJX', 'ROST', 'ULTA', 'BBY', 'TSCO', 'ORLY', 'AZO', 'AAP'],
            'Department Stores': ['TGT', 'KSS', 'M', 'JWN'],
        },
        'Automotive': {
            'Auto Manufacturers': ['TSLA', 'GM', 'F'],
            'Auto Parts': ['APTV', 'BWA', 'LEA'],
        },
        'Consumer Services': {
            'Hotels & Resorts': ['MAR', 'HLT', 'H', 'WH'],
            'Restaurants': ['MCD', 'SBUX', 'CMG', 'YUM', 'DRI', 'DPZ'],
            'Leisure': ['DIS', 'NCLH', 'CCL', 'RCL', 'LVS', 'WYNN', 'MGM'],
        },
        'Apparel': {
            'Footwear & Apparel': ['NKE', 'VFC', 'PVH', 'RL', 'TPR', 'LULU'],
        },
    },

    # =========================================================================
    # CONSUMER STAPLES SECTOR
    # =========================================================================
    'Consumer Staples': {
        'Food & Beverage': {
            'Beverages': ['KO', 'PEP', 'KDP', 'STZ', 'MNST', 'TAP', 'BF.B'],
            'Packaged Foods': ['MDLZ', 'GIS', 'K', 'KHC', 'CPB', 'SJM', 'HSY', 'MKC', 'CAG'],
        },
        'Household Products': {
            'Personal Care': ['PG', 'CL', 'EL', 'CHD', 'CLX'],
        },
        'Retail': {
            'Food Retail': ['WMT', 'COST', 'KR', 'SYY', 'WBA', 'CVS'],
            'Drug Retail': ['WBA', 'CVS'],
        },
        'Tobacco': {
            'Tobacco': ['PM', 'MO', 'BTI'],
        },
    },

    # =========================================================================
    # INDUSTRIALS SECTOR
    # =========================================================================
    'Industrials': {
        'Aerospace & Defense': {
            'Aerospace': ['BA', 'LMT', 'RTX', 'NOC', 'GD', 'TDG', 'HII', 'LHX'],
        },
        'Machinery': {
            'Construction & Farm': ['CAT', 'DE', 'AGCO', 'CMI'],
            'Industrial Machinery': ['EMR', 'ROK', 'AME', 'ETN', 'PH', 'ITW', 'DOV', 'IR'],
        },
        'Transportation': {
            'Railroads': ['UNP', 'CSX', 'NSC'],
            'Airlines': ['DAL', 'UAL', 'LUV', 'AAL'],
            'Trucking & Logistics': ['UPS', 'FDX', 'CHRW', 'EXPD', 'XPO'],
        },
        'Commercial Services': {
            'Staffing': ['PAYX', 'ADP'],
            'Waste Management': ['WM', 'RSG', 'WCN'],
            'Security': ['ALLE', 'JCI'],
        },
        'Electrical Equipment': {
            'Electrical': ['GE', 'HON', 'MMM', 'CARR'],
        },
    },

    # =========================================================================
    # ENERGY SECTOR
    # =========================================================================
    'Energy': {
        'Oil & Gas': {
            'Integrated Oil': ['XOM', 'CVX', 'COP', 'OXY', 'PSX', 'VLO', 'MPC'],
            'Exploration & Production': ['EOG', 'PXD', 'DVN', 'FANG', 'HES', 'APA', 'MRO'],
        },
        'Oil Services': {
            'Equipment & Services': ['SLB', 'HAL', 'BKR', 'NOV'],
        },
        'Midstream': {
            'Pipelines': ['KMI', 'WMB', 'OKE', 'ET'],
        },
    },

    # =========================================================================
    # MATERIALS SECTOR
    # =========================================================================
    'Materials': {
        'Chemicals': {
            'Diversified Chemicals': ['LIN', 'APD', 'DD', 'DOW', 'LYB', 'CE', 'EMN'],
            'Specialty Chemicals': ['SHW', 'PPG', 'ECL', 'IFF', 'ALB'],
            'Agricultural Chemicals': ['CF', 'MOS', 'NTR', 'CTVA'],
        },
        'Metals & Mining': {
            'Steel': ['NUE', 'STLD', 'CLF'],
            'Mining': ['FCX', 'NEM', 'AA'],
        },
        'Construction Materials': {
            'Building Materials': ['VMC', 'MLM', 'CX'],
        },
        'Containers & Packaging': {
            'Packaging': ['BALL', 'AVY', 'IP', 'PKG', 'SEE'],
        },
    },

    # =========================================================================
    # UTILITIES SECTOR
    # =========================================================================
    'Utilities': {
        'Electric Utilities': {
            'Electric': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'XEL', 'SRE', 'EXC', 'ED', 'PEG', 'EIX', 'WEC', 'ES', 'FE', 'DTE', 'AEE', 'CMS', 'PPL'],
        },
        'Gas Utilities': {
            'Gas': ['NI', 'ATO', 'OGS'],
        },
        'Multi-Utilities': {
            'Multi': ['PCG', 'AWK', 'AES'],
        },
    },

    # =========================================================================
    # REAL ESTATE SECTOR
    # =========================================================================
    'Real Estate': {
        'REITs': {
            'Retail REITs': ['SPG', 'O', 'VICI', 'KIM', 'REG', 'FRT'],
            'Industrial REITs': ['PLD', 'AMT', 'CCI', 'SBAC', 'DLR', 'EQIX'],
            'Residential REITs': ['AVB', 'EQR', 'ESS', 'MAA', 'UDR'],
            'Office REITs': ['BXP', 'VNO', 'SLG', 'HIW'],
            'Healthcare REITs': ['WELL', 'VTR', 'PEAK', 'HCP'],
            'Storage REITs': ['PSA', 'EXR', 'CUBE', 'LSI'],
        },
    },

    # =========================================================================
    # COMMUNICATION SERVICES SECTOR
    # =========================================================================
    'Communication Services': {
        'Media & Entertainment': {
            'Entertainment': ['DIS', 'NFLX', 'WBD', 'PARA', 'LYV', 'MTCH'],
            'Interactive Media': ['GOOGL', 'META'],
            'Games': ['EA', 'TTWO', 'ATVI'],
        },
        'Telecom': {
            'Telecom Services': ['T', 'VZ', 'TMUS'],
        },
        'Advertising': {
            'Advertising': ['OMC', 'IPG'],
        },
    },
}

# =============================================================================
# Create BigQuery Table
# =============================================================================
print("\n[1] Creating Stock Classification Table...")

create_table_query = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.stock_sector_classification` (
    symbol STRING NOT NULL,
    sector STRING NOT NULL,
    industry_group STRING NOT NULL,
    industry STRING NOT NULL,
    sector_code INT64,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""

try:
    bq_client.query(create_table_query).result()
    print("  Table created: stock_sector_classification")
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# Populate Classification Data
# =============================================================================
print("\n[2] Populating Classification Data...")

# Sector codes for ML encoding
SECTOR_CODES = {
    'Technology': 1,
    'Healthcare': 2,
    'Financials': 3,
    'Consumer Discretionary': 4,
    'Consumer Staples': 5,
    'Industrials': 6,
    'Energy': 7,
    'Materials': 8,
    'Utilities': 9,
    'Real Estate': 10,
    'Communication Services': 11,
}

# Build rows for insertion
rows = []
for sector, industry_groups in STOCK_CLASSIFICATION.items():
    sector_code = SECTOR_CODES[sector]
    for industry_group, industries in industry_groups.items():
        for industry, symbols in industries.items():
            for symbol in symbols:
                rows.append({
                    'symbol': symbol,
                    'sector': sector,
                    'industry_group': industry_group,
                    'industry': industry,
                    'sector_code': sector_code
                })

# Remove duplicates (some stocks appear in multiple categories)
seen = set()
unique_rows = []
for row in rows:
    if row['symbol'] not in seen:
        seen.add(row['symbol'])
        unique_rows.append(row)

print(f"  Total stocks classified: {len(unique_rows)}")

# Insert in batches
import pandas as pd
df = pd.DataFrame(unique_rows)
df['created_at'] = datetime.utcnow()

table_ref = f"{PROJECT_ID}.{ML_DATASET}.stock_sector_classification"
job = bq_client.load_table_from_dataframe(df, table_ref)
job.result()
print(f"  Inserted {len(unique_rows)} stock classifications")

# =============================================================================
# Summary by Sector
# =============================================================================
print("\n[3] Classification Summary by Sector...")
print("-" * 70)

summary_query = f"""
SELECT
    sector,
    sector_code,
    COUNT(DISTINCT symbol) as stock_count,
    COUNT(DISTINCT industry_group) as industry_groups,
    COUNT(DISTINCT industry) as industries
FROM `{PROJECT_ID}.{ML_DATASET}.stock_sector_classification`
GROUP BY sector, sector_code
ORDER BY sector_code
"""

results = list(bq_client.query(summary_query).result())
print(f"  {'Sector':30} | {'Code':>4} | {'Stocks':>7} | {'Groups':>7} | {'Industries':>10}")
print("  " + "-" * 75)
for row in results:
    print(f"  {row.sector:30} | {row.sector_code:>4} | {row.stock_count:>7} | {row.industry_groups:>7} | {row.industries:>10}")

print(f"\n  Total: {sum(r.stock_count for r in results)} stocks across {len(results)} sectors")

print("\n" + "=" * 70)
print("STOCK SECTOR CLASSIFICATION COMPLETE")
print("=" * 70)
print(f"\nCompleted: {datetime.now()}")
