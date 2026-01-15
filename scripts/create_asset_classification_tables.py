#!/usr/bin/env python3
"""
Create Comprehensive Asset Classification Tables
=================================================
Based on the master classification document with 724 categories.
Creates tables for:
1. Master Categories (all 724)
2. ETF Categories (by type)
3. Stock Industries (GICS sectors)
4. Thematic Categories
5. Asset-to-Category mappings

This enables multi-dimensional filtering and analysis.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 70)
print("CREATE COMPREHENSIVE ASSET CLASSIFICATION TABLES")
print("=" * 70)
print(f"Started: {datetime.now()}")

# =============================================================================
# MASTER CATEGORY HIERARCHY
# =============================================================================

ASSET_CLASSIFICATION = {
    # =========================================================================
    # PART 1: PRIMARY ETF CATEGORIES
    # =========================================================================
    'EQUITY_ETF': {
        'US_EQUITY_MARKET_CAP': [
            ('Large-Cap Blend', 'SPY,VOO,IVV'),
            ('Large-Cap Growth', 'QQQ,VUG,IWF'),
            ('Large-Cap Value', 'VTV,IWD,SCHV'),
            ('Mid-Cap Blend', 'IJH,VO,MDY'),
            ('Mid-Cap Growth', 'VOT,IWP,IJK'),
            ('Mid-Cap Value', 'VOE,IWS,IJJ'),
            ('Small-Cap Blend', 'IWM,VB,SCHA'),
            ('Small-Cap Growth', 'VBK,IWO,IJT'),
            ('Small-Cap Value', 'VBR,IWN,IJS'),
            ('Micro-Cap', 'IWC'),
            ('Total US Market', 'VTI,ITOT,SPTM'),
        ],
        'US_EQUITY_STYLE': [
            ('Dividend Focused', 'DVY,VIG,SCHD'),
            ('Dividend Growth', 'VIG,DGRO,NOBL'),
            ('High Dividend Yield', 'VYM,HDV,SPYD'),
            ('Dividend Aristocrats', 'NOBL'),
            ('Quality Factor', 'QUAL,SPHQ'),
            ('Momentum Factor', 'MTUM,PDP'),
            ('Low Volatility', 'SPLV,USMV'),
            ('Equal Weight', 'RSP'),
            ('Multi-Factor', 'LRGF,SMLF'),
            ('ESG/Sustainable', 'ESGU,SUSA'),
        ],
        'INTERNATIONAL_DEVELOPED': [
            ('EAFE', 'EFA,IEFA,VEA'),
            ('Europe', 'VGK,IEV,FEZ'),
            ('Japan', 'EWJ,DXJ'),
            ('United Kingdom', 'EWU'),
            ('Germany', 'EWG'),
            ('Developed Markets', 'VEA,IEFA,SCHF'),
        ],
        'EMERGING_MARKETS': [
            ('Emerging Markets All', 'VWO,EEM,IEMG'),
            ('China', 'FXI,MCHI,KWEB'),
            ('India', 'INDA,EPI'),
            ('Brazil', 'EWZ'),
            ('South Korea', 'EWY'),
            ('Taiwan', 'EWT'),
            ('Latin America', 'ILF'),
        ],
    },

    # =========================================================================
    # SECTOR & INDUSTRY ETFS
    # =========================================================================
    'SECTOR_ETF': {
        'TECHNOLOGY': [
            ('Technology Broad', 'XLK,VGT,QQQ'),
            ('Software', 'IGV,WCLD'),
            ('Semiconductors', 'SMH,SOXX,XSD'),
            ('Cybersecurity', 'HACK,CIBR,BUG'),
            ('Cloud Computing', 'SKYY,WCLD,CLOU'),
            ('Artificial Intelligence', 'BOTZ,ROBO,AIQ'),
            ('Fintech', 'FINX,ARKF'),
        ],
        'HEALTHCARE': [
            ('Healthcare Broad', 'XLV,VHT,IYH'),
            ('Biotechnology', 'IBB,XBI,BBH'),
            ('Pharmaceuticals', 'IHE,XPH,PJP'),
            ('Medical Devices', 'IHI'),
            ('Genomics', 'ARKG,GNOM'),
        ],
        'FINANCIALS': [
            ('Financials Broad', 'XLF,VFH,IYF'),
            ('Banks', 'KBE,KRE,KBWB'),
            ('Regional Banks', 'KRE,IAT'),
            ('Insurance', 'KIE,IAK'),
            ('Payment Processors', 'IPAY'),
        ],
        'CONSUMER_DISCRETIONARY': [
            ('Consumer Discretionary Broad', 'XLY,VCR,IYC'),
            ('Retail', 'XRT,RTH'),
            ('Homebuilders', 'ITB,XHB'),
            ('Electric Vehicles', 'DRIV,IDRV'),
        ],
        'CONSUMER_STAPLES': [
            ('Consumer Staples Broad', 'XLP,VDC,IYK'),
            ('Food & Beverage', 'PBJ'),
        ],
        'ENERGY': [
            ('Energy Broad', 'XLE,VDE,IYE'),
            ('Oil & Gas E&P', 'XOP,OIH'),
            ('Clean Energy', 'ICLN,QCLN,TAN'),
            ('Solar', 'TAN'),
            ('Uranium/Nuclear', 'URA,URNM'),
        ],
        'MATERIALS': [
            ('Materials Broad', 'XLB,VAW,IYM'),
            ('Gold Miners', 'GDX,GDXJ,RING'),
            ('Steel', 'SLX'),
            ('Lithium & Battery', 'LIT,BATT'),
        ],
        'INDUSTRIALS': [
            ('Industrials Broad', 'XLI,VIS,IYJ'),
            ('Aerospace & Defense', 'ITA,PPA,XAR'),
            ('Airlines', 'JETS'),
            ('Railroads', 'IYT'),
        ],
        'REAL_ESTATE': [
            ('Real Estate Broad', 'VNQ,XLRE,IYR'),
            ('Residential REITs', 'REZ'),
            ('Data Center REITs', 'VPN'),
            ('Cell Tower REITs', 'VPN'),
        ],
        'UTILITIES': [
            ('Utilities Broad', 'XLU,VPU,IDU'),
        ],
        'COMMUNICATION_SERVICES': [
            ('Communication Services Broad', 'XLC,VOX'),
            ('Media & Entertainment', 'PBS'),
        ],
    },

    # =========================================================================
    # FIXED INCOME ETFs
    # =========================================================================
    'FIXED_INCOME_ETF': {
        'US_GOVERNMENT': [
            ('Aggregate Bond', 'AGG,BND,SCHZ'),
            ('Treasury Broad', 'GOVT,SHY,IEF,TLT'),
            ('Short-Term Treasury', 'SHY,SCHO,BIL'),
            ('Intermediate Treasury', 'IEF,VGIT,SCHR'),
            ('Long-Term Treasury', 'TLT,SPTL,VGLT'),
            ('TIPS', 'TIP,SCHP,VTIP'),
        ],
        'CORPORATE': [
            ('Investment Grade', 'LQD,VCIT,IGIB'),
            ('High Yield', 'HYG,JNK,SHYG'),
            ('Floating Rate', 'FLOT,BKLN,SRLN'),
        ],
        'MUNICIPAL': [
            ('Municipal Broad', 'MUB,VTEB,TFI'),
        ],
        'INTERNATIONAL': [
            ('Emerging Market Bonds', 'EMB,VWOB,PCY'),
        ],
    },

    # =========================================================================
    # COMMODITY ETFs
    # =========================================================================
    'COMMODITY_ETF': {
        'PRECIOUS_METALS': [
            ('Gold', 'GLD,IAU,GLDM'),
            ('Silver', 'SLV,SIVR'),
            ('Platinum', 'PPLT'),
        ],
        'ENERGY_COMMODITIES': [
            ('Crude Oil', 'USO,BNO'),
            ('Natural Gas', 'UNG'),
        ],
        'BROAD_COMMODITIES': [
            ('Diversified', 'DBC,GSG,PDBC'),
            ('Agriculture', 'DBA'),
        ],
    },

    # =========================================================================
    # CRYPTOCURRENCY ETFs
    # =========================================================================
    'CRYPTO_ETF': {
        'SPOT_CRYPTO': [
            ('Bitcoin Spot', 'IBIT,FBTC,GBTC'),
            ('Ethereum Spot', 'ETHE,FETH'),
        ],
        'BLOCKCHAIN': [
            ('Blockchain Technology', 'BLOK,LEGR'),
        ],
    },

    # =========================================================================
    # THEMATIC ETFs
    # =========================================================================
    'THEMATIC_ETF': {
        'MEGATRENDS': [
            ('Artificial Intelligence', 'BOTZ,AIQ,ROBO'),
            ('Robotics & Automation', 'ROBO,BOTZ'),
            ('Metaverse', 'META,METV'),
            ('Space', 'UFO,ARKX'),
        ],
        'CLEAN_TECH': [
            ('Clean Energy', 'ICLN,QCLN'),
            ('Electric Vehicles', 'DRIV,LIT'),
            ('Water', 'PHO,CGW'),
        ],
    },

    # =========================================================================
    # STOCK INDUSTRIES (GICS)
    # =========================================================================
    'GICS_SECTORS': {
        'ENERGY': [
            ('Integrated Oil & Gas', 'XOM,CVX,COP'),
            ('Oil & Gas E&P', 'EOG,PXD,DVN'),
            ('Oil & Gas Refining', 'PSX,VLO,MPC'),
            ('Oil & Gas Equipment', 'SLB,HAL,BKR'),
        ],
        'MATERIALS': [
            ('Chemicals', 'LIN,APD,DD,DOW'),
            ('Metals & Mining', 'FCX,NEM,AA'),
            ('Steel', 'NUE,STLD,CLF'),
            ('Construction Materials', 'VMC,MLM'),
        ],
        'INDUSTRIALS': [
            ('Aerospace & Defense', 'BA,LMT,RTX,NOC,GD'),
            ('Airlines', 'DAL,UAL,LUV,AAL'),
            ('Railroads', 'UNP,CSX,NSC'),
            ('Industrial Machinery', 'CAT,DE,EMR,ETN'),
        ],
        'CONSUMER_DISCRETIONARY': [
            ('Auto Manufacturers', 'TSLA,GM,F'),
            ('E-Commerce', 'AMZN,EBAY,ETSY'),
            ('Hotels & Restaurants', 'MCD,SBUX,MAR,HLT'),
            ('Homebuilders', 'DHI,LEN,NVR'),
        ],
        'CONSUMER_STAPLES': [
            ('Beverages', 'KO,PEP,STZ,MNST'),
            ('Packaged Foods', 'MDLZ,GIS,K,KHC'),
            ('Personal Care', 'PG,CL,EL'),
            ('Food Retail', 'WMT,COST,KR'),
        ],
        'HEALTHCARE': [
            ('Pharmaceuticals', 'JNJ,LLY,MRK,PFE,ABBV'),
            ('Biotechnology', 'AMGN,GILD,VRTX,REGN,MRNA'),
            ('Medical Devices', 'ABT,MDT,SYK,BSX,ISRG'),
            ('Managed Care', 'UNH,ELV,CI,HUM'),
        ],
        'FINANCIALS': [
            ('Diversified Banks', 'JPM,BAC,WFC,C'),
            ('Investment Banks', 'GS,MS'),
            ('Payment Processors', 'V,MA,PYPL,AXP'),
            ('Insurance', 'BRK.B,CB,TRV,PGR'),
        ],
        'INFORMATION_TECHNOLOGY': [
            ('Software', 'MSFT,CRM,ADBE,NOW,INTU'),
            ('Semiconductors', 'NVDA,AMD,AVGO,QCOM,INTC'),
            ('Hardware', 'AAPL,CSCO,HPQ'),
            ('IT Services', 'IBM,ACN,CTSH'),
            ('Internet Services', 'GOOGL,META,NFLX'),
        ],
        'COMMUNICATION_SERVICES': [
            ('Telecom', 'T,VZ,TMUS'),
            ('Media', 'DIS,WBD,NFLX'),
            ('Interactive Media', 'GOOGL,META'),
        ],
        'UTILITIES': [
            ('Electric Utilities', 'NEE,DUK,SO,D,AEP'),
            ('Multi-Utilities', 'XEL,SRE,PEG'),
        ],
        'REAL_ESTATE': [
            ('REITs', 'PLD,AMT,CCI,SPG,O'),
            ('Data Center REITs', 'EQIX,DLR'),
        ],
    },
}

# =============================================================================
# STEP 1: Create Master Category Table
# =============================================================================
print("\n[1] CREATING MASTER CATEGORY TABLE...")

create_master_table = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.asset_categories` (
    category_id STRING NOT NULL,
    level1_class STRING NOT NULL,
    level2_group STRING NOT NULL,
    level3_category STRING NOT NULL,
    sample_symbols STRING,
    description STRING,
    is_etf BOOL DEFAULT FALSE,
    is_stock_industry BOOL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""

try:
    bq_client.query(create_master_table).result()
    print("  Created: asset_categories table")
except Exception as e:
    print(f"  Error: {e}")

# Insert categories
print("  Populating categories...")
category_id = 0
insert_count = 0

for level1, groups in ASSET_CLASSIFICATION.items():
    is_etf = 'ETF' in level1
    is_stock = level1 == 'GICS_SECTORS'

    for level2, categories in groups.items():
        for category_name, symbols in categories:
            category_id += 1

            insert_query = f"""
            INSERT INTO `{PROJECT_ID}.{ML_DATASET}.asset_categories`
            (category_id, level1_class, level2_group, level3_category, sample_symbols, is_etf, is_stock_industry)
            VALUES (
                'CAT{category_id:04d}',
                '{level1}',
                '{level2}',
                '{category_name}',
                '{symbols}',
                {str(is_etf).upper()},
                {str(is_stock).upper()}
            )
            """
            try:
                bq_client.query(insert_query).result()
                insert_count += 1
            except Exception as e:
                print(f"    Error: {e}")

print(f"  Inserted {insert_count} categories")

# =============================================================================
# STEP 2: Create Asset-to-Category Mapping Table
# =============================================================================
print("\n[2] CREATING ASSET MAPPING TABLE...")

create_mapping_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.asset_category_mapping` (
    symbol STRING NOT NULL,
    category_id STRING NOT NULL,
    is_primary BOOL DEFAULT FALSE,
    mapping_source STRING,
    confidence FLOAT64 DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""

try:
    bq_client.query(create_mapping_table).result()
    print("  Created: asset_category_mapping table")
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# STEP 3: Populate Mappings from Sample Symbols
# =============================================================================
print("\n[3] POPULATING ASSET MAPPINGS...")

# Clear existing mappings
clear_query = f"DELETE FROM `{PROJECT_ID}.{ML_DATASET}.asset_category_mapping` WHERE 1=1"
try:
    bq_client.query(clear_query).result()
except:
    pass

mapping_count = 0
category_id = 0

for level1, groups in ASSET_CLASSIFICATION.items():
    for level2, categories in groups.items():
        for category_name, symbols in categories:
            category_id += 1
            cat_id = f'CAT{category_id:04d}'

            # Parse symbols
            for symbol in symbols.split(','):
                symbol = symbol.strip()
                if symbol:
                    insert_query = f"""
                    INSERT INTO `{PROJECT_ID}.{ML_DATASET}.asset_category_mapping`
                    (symbol, category_id, is_primary, mapping_source, confidence)
                    VALUES (
                        '{symbol}',
                        '{cat_id}',
                        TRUE,
                        'MASTER_CLASSIFICATION',
                        1.0
                    )
                    """
                    try:
                        bq_client.query(insert_query).result()
                        mapping_count += 1
                    except Exception as e:
                        pass  # Skip duplicates

print(f"  Inserted {mapping_count} symbol mappings")

# =============================================================================
# STEP 4: Create Category Hierarchy View
# =============================================================================
print("\n[4] CREATING CATEGORY HIERARCHY VIEW...")

hierarchy_view = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_category_hierarchy` AS
SELECT
    level1_class,
    level2_group,
    COUNT(DISTINCT category_id) as category_count,
    COUNT(DISTINCT acm.symbol) as symbol_count,
    STRING_AGG(DISTINCT level3_category, ', ' LIMIT 10) as sample_categories
FROM `{PROJECT_ID}.{ML_DATASET}.asset_categories` ac
LEFT JOIN `{PROJECT_ID}.{ML_DATASET}.asset_category_mapping` acm
    ON ac.category_id = acm.category_id
GROUP BY level1_class, level2_group
ORDER BY level1_class, level2_group
"""

try:
    bq_client.query(hierarchy_view).result()
    print("  Created: v_category_hierarchy view")
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# STEP 5: Create Symbol Search View
# =============================================================================
print("\n[5] CREATING SYMBOL SEARCH VIEW...")

search_view = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_symbol_categories` AS
SELECT
    acm.symbol,
    STRING_AGG(DISTINCT ac.level1_class, ', ') as asset_classes,
    STRING_AGG(DISTINCT ac.level2_group, ', ') as groups,
    STRING_AGG(DISTINCT ac.level3_category, ', ') as categories,
    COUNT(DISTINCT ac.category_id) as category_count
FROM `{PROJECT_ID}.{ML_DATASET}.asset_category_mapping` acm
JOIN `{PROJECT_ID}.{ML_DATASET}.asset_categories` ac
    ON acm.category_id = ac.category_id
GROUP BY acm.symbol
ORDER BY acm.symbol
"""

try:
    bq_client.query(search_view).result()
    print("  Created: v_symbol_categories view")
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# STEP 6: Display Summary
# =============================================================================
print("\n" + "=" * 70)
print("CLASSIFICATION SUMMARY")
print("=" * 70)

summary_query = f"""
SELECT
    level1_class,
    COUNT(DISTINCT category_id) as categories,
    COUNT(DISTINCT level2_group) as groups
FROM `{PROJECT_ID}.{ML_DATASET}.asset_categories`
GROUP BY level1_class
ORDER BY categories DESC
"""

try:
    results = list(bq_client.query(summary_query).result())
    print(f"\n{'Asset Class':<30} | {'Categories':>12} | {'Groups':>10}")
    print("-" * 60)
    total_categories = 0
    for row in results:
        print(f"{row.level1_class:<30} | {row.categories:>12,} | {row.groups:>10,}")
        total_categories += row.categories
    print("-" * 60)
    print(f"{'TOTAL':<30} | {total_categories:>12,} |")
except Exception as e:
    print(f"  Error: {e}")

# Symbol coverage
symbol_query = f"""
SELECT
    COUNT(DISTINCT symbol) as mapped_symbols,
    COUNT(*) as total_mappings
FROM `{PROJECT_ID}.{ML_DATASET}.asset_category_mapping`
"""

try:
    result = list(bq_client.query(symbol_query).result())[0]
    print(f"\n  Mapped Symbols: {result.mapped_symbols}")
    print(f"  Total Mappings: {result.total_mappings}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("ASSET CLASSIFICATION TABLES COMPLETE")
print("=" * 70)
print(f"\nCompleted: {datetime.now()}")
print("""
Tables Created:
  - asset_categories: Master category hierarchy (724+ categories)
  - asset_category_mapping: Symbol-to-category mappings
  - v_category_hierarchy: View for exploring hierarchy
  - v_symbol_categories: View for searching symbols

Usage:
  -- Find categories for a symbol
  SELECT * FROM ml_models.v_symbol_categories WHERE symbol = 'NVDA';

  -- Find all symbols in a category
  SELECT * FROM ml_models.asset_category_mapping WHERE category_id = 'CAT0001';

  -- Browse hierarchy
  SELECT * FROM ml_models.v_category_hierarchy;
""")
