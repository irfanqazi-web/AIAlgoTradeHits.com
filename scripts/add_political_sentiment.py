"""
Political/Trump Sentiment Integration for Rise Cycle
"""

from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client(project='aialgotradehits')

print("=" * 70)
print("POLITICAL/TRUMP SENTIMENT INTEGRATION")
print("=" * 70)

# Create sample political sentiment data
print("\nStep 1: Creating sample political sentiment entries...")

sample_data = """
INSERT INTO `aialgotradehits.ml_models.political_sentiment`
(date, headline, source, sentiment_score, impact_sectors, trump_related, tariff_related, fed_related, china_related, market_impact, confidence, created_at)
VALUES
('2026-01-08', 'Trump threatens new China tariffs on tech imports', 'Reuters', -0.7, ['Technology', 'Semiconductors'], TRUE, TRUE, FALSE, TRUE, 'NEGATIVE', 0.85, CURRENT_TIMESTAMP()),
('2026-01-07', 'Trump signals softer stance on chip exports to China', 'Bloomberg', 0.4, ['Semiconductors'], TRUE, FALSE, FALSE, TRUE, 'POSITIVE', 0.75, CURRENT_TIMESTAMP()),
('2026-01-06', 'Trump administration increases defense spending proposal', 'WSJ', 0.8, ['Industrials'], TRUE, FALSE, FALSE, FALSE, 'POSITIVE', 0.9, CURRENT_TIMESTAMP()),
('2026-01-05', 'Fed signals potential rate cuts in Q2', 'CNBC', 0.6, ['Financials'], FALSE, FALSE, TRUE, FALSE, 'POSITIVE', 0.8, CURRENT_TIMESTAMP()),
('2026-01-04', 'Trump trade war rhetoric spooks markets', 'FT', -0.5, ['Technology', 'Semiconductors', 'Industrials'], TRUE, TRUE, FALSE, TRUE, 'NEGATIVE', 0.7, CURRENT_TIMESTAMP())
"""

try:
    client.query(sample_data).result()
    print("  Sample political sentiment data inserted")
except Exception as e:
    print(f"  Note: {e}")

# Create sector-specific Trump impact mapping
print("\nStep 2: Creating Trump impact sector mapping...")

trump_impact_table = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.trump_sector_impact` AS
SELECT * FROM UNNEST([
    STRUCT('Semiconductors' as sector, 'HIGH' as tariff_sensitivity, 'NEGATIVE' as china_tariff_impact, -0.6 as typical_impact_score, 'China exports, supply chain' as risk_factors),
    STRUCT('Technology' as sector, 'MEDIUM' as tariff_sensitivity, 'NEGATIVE' as china_tariff_impact, -0.4 as typical_impact_score, 'Global supply chain, China revenue' as risk_factors),
    STRUCT('Industrials' as sector, 'LOW' as tariff_sensitivity, 'POSITIVE' as china_tariff_impact, 0.3 as typical_impact_score, 'Defense spending benefits' as risk_factors),
    STRUCT('Financials' as sector, 'LOW' as tariff_sensitivity, 'NEUTRAL' as china_tariff_impact, 0.1 as typical_impact_score, 'Deregulation benefits' as risk_factors),
    STRUCT('Defense' as sector, 'NONE' as tariff_sensitivity, 'POSITIVE' as china_tariff_impact, 0.7 as typical_impact_score, 'Increased spending' as risk_factors)
])
"""
client.query(trump_impact_table).result()
print("  Trump sector impact table created")

# Create view with political sentiment integrated
print("\nStep 3: Creating enhanced view with political sentiment...")

political_enhanced_view = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_rise_cycle_with_sentiment` AS
WITH latest_political AS (
    SELECT
        sector,
        AVG(sentiment_score) as avg_political_sentiment,
        SUM(CASE WHEN trump_related THEN 1 ELSE 0 END) as trump_news_count,
        SUM(CASE WHEN tariff_related THEN 1 ELSE 0 END) as tariff_news_count,
        MAX(CASE WHEN market_impact = 'POSITIVE' THEN 1 WHEN market_impact = 'NEGATIVE' THEN -1 ELSE 0 END) as latest_market_impact
    FROM `aialgotradehits.ml_models.political_sentiment` p,
    UNNEST(impact_sectors) as sector
    WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    GROUP BY sector
),
enhanced_signals AS (
    SELECT
        e.*,
        t.tariff_sensitivity,
        t.china_tariff_impact,
        t.typical_impact_score as trump_sector_bias,
        COALESCE(p.avg_political_sentiment, 0) as political_sentiment,
        COALESCE(p.trump_news_count, 0) as trump_news_count,
        COALESCE(p.tariff_news_count, 0) as tariff_news_count,
        COALESCE(p.latest_market_impact, 0) as political_market_impact
    FROM `aialgotradehits.ml_models.v_rise_cycle_enhanced_signals` e
    LEFT JOIN `aialgotradehits.ml_models.trump_sector_impact` t ON e.sector = t.sector
    LEFT JOIN latest_political p ON e.sector = p.sector
)
SELECT
    *,
    -- Adjusted signal based on political sentiment
    CASE
        WHEN signal = 'ULTRA_BUY' AND political_sentiment > 0 THEN 'ULTRA_BUY'
        WHEN signal = 'ULTRA_BUY' AND political_sentiment < -0.3 AND tariff_sensitivity = 'HIGH' THEN 'STRONG_BUY'
        WHEN signal = 'STRONG_BUY' AND political_sentiment > 0.3 THEN 'ULTRA_BUY'
        WHEN signal = 'STRONG_BUY' AND political_sentiment < -0.5 AND tariff_sensitivity = 'HIGH' THEN 'BUY'
        WHEN signal = 'BUY' AND political_sentiment > 0.5 AND trump_sector_bias > 0 THEN 'STRONG_BUY'
        ELSE signal
    END as adjusted_signal,
    -- Political risk flag
    CASE
        WHEN tariff_sensitivity = 'HIGH' AND tariff_news_count > 0 THEN 'HIGH_RISK'
        WHEN political_sentiment < -0.3 THEN 'ELEVATED_RISK'
        WHEN political_sentiment > 0.3 THEN 'FAVORABLE'
        ELSE 'NEUTRAL'
    END as political_risk,
    -- Final combined score
    enhanced_score +
        CAST(ROUND(COALESCE(political_sentiment, 0) * 2) AS INT64) +
        CAST(ROUND(COALESCE(trump_sector_bias, 0) * 2) AS INT64) as final_score
FROM enhanced_signals
"""

client.query(political_enhanced_view).result()
print("  Political sentiment view created")

# Show current signals
print("\nCurrent Signals with Political Sentiment:")
print("-" * 110)
signals = list(client.query("""
    SELECT
        signal_date, symbol, ROUND(current_price, 2) as price, base_score, enhanced_score,
        final_score, signal, adjusted_signal, sector, political_risk,
        ROUND(political_sentiment, 2) as pol_sent, trump_news_count
    FROM `aialgotradehits.ml_models.v_rise_cycle_with_sentiment`
    WHERE adjusted_signal IN ('ULTRA_BUY', 'STRONG_BUY', 'BUY')
      AND signal_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    ORDER BY final_score DESC, signal_date DESC
    LIMIT 15
""").result())

if signals:
    print(f"{'Date':<12} {'Sym':<6} {'Price':>8} {'Base':>5} {'Enh':>4} {'Final':>5} {'Signal':<12} {'Adj Signal':<12} {'Sector':<14} {'PolRisk':<12}")
    print("-" * 110)
    for s in signals:
        print(f"{str(s.signal_date):<12} {s.symbol:<6} {s.price:>8.2f} {s.base_score:>5} {s.enhanced_score:>4} {s.final_score:>5} {s.signal:<12} {s.adjusted_signal:<12} {s.sector:<14} {s.political_risk:<12}")

print("\n" + "=" * 70)
print("POLITICAL SENTIMENT INTEGRATION COMPLETE")
print("=" * 70)
print("""
Trump/Political Impact Rules:
- Semiconductors: HIGH tariff sensitivity, NEGATIVE China impact (-0.6)
- Technology: MEDIUM tariff sensitivity, NEGATIVE China impact (-0.4)
- Industrials: LOW sensitivity, POSITIVE Trump impact (+0.3) - Defense spending
- Financials: LOW sensitivity, NEUTRAL (+0.1) - Deregulation benefits
- Defense: NONE sensitivity, POSITIVE Trump impact (+0.7) - Increased spending

Signal Adjustments:
- ULTRA_BUY downgraded to STRONG_BUY if negative sentiment + HIGH tariff risk
- STRONG_BUY upgraded to ULTRA_BUY if positive sentiment + favorable sector
- BUY upgraded to STRONG_BUY if strong positive sentiment + Trump-favorable sector

Political Risk Levels:
- HIGH_RISK: High tariff sensitivity sector with recent tariff news
- ELEVATED_RISK: Political sentiment < -0.3
- FAVORABLE: Political sentiment > 0.3
- NEUTRAL: Default
""")
