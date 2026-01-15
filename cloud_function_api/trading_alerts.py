"""
Trading Alert System for AIAlgoTradeHits.com
Detects price anomalies, volume surges, and generates trading alerts

Based on: gcp-timeseries-bigquery-implementation.html
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Alert thresholds
ALERT_THRESHOLDS = {
    'price_spike_pct': 3.0,        # 3% price move
    'volume_surge_ratio': 2.5,     # 2.5x average volume
    'rsi_overbought': 75,          # RSI overbought
    'rsi_oversold': 25,            # RSI oversold
    'macd_cross_strength': 0.5,    # MACD cross strength
    'bb_breakout_pct': 1.0,        # Bollinger Band breakout
    'adx_strong_trend': 30,        # Strong trend threshold
}


class TradingAlertSystem:
    """Comprehensive trading alert detection system"""

    def __init__(self, project_id=PROJECT_ID, dataset_id=DATASET_ID):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.thresholds = ALERT_THRESHOLDS.copy()

    def detect_price_anomalies(self, asset_type='stocks', lookback_days=20):
        """Detect significant price movements"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        query = f"""
        WITH latest_data AS (
            SELECT
                symbol,
                datetime,
                close,
                open,
                high,
                low,
                volume,
                rsi,
                macd,
                macd_signal,
                adx,
                bollinger_upper,
                bollinger_lower,
                sma_20,
                sma_50,
                golden_cross,
                death_cross,
                cycle_type,
                cycle_pnl_pct,
                LAG(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close,
                AVG(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as avg_close_20d,
                STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as std_close_20d
            FROM `{self.project_id}.{self.dataset_id}.{table}`
            WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days + 5} DAY)
        ),
        anomalies AS (
            SELECT
                symbol,
                datetime,
                close,
                prev_close,
                ROUND((close - prev_close) / prev_close * 100, 2) as price_change_pct,
                ROUND((close - avg_close_20d) / std_close_20d, 2) as zscore,
                rsi,
                macd,
                macd_signal,
                adx,
                bollinger_upper,
                bollinger_lower,
                golden_cross,
                death_cross,
                cycle_type,
                cycle_pnl_pct,
                CASE
                    WHEN ABS((close - prev_close) / prev_close * 100) >= {self.thresholds['price_spike_pct']} THEN 'PRICE_SPIKE'
                    WHEN close > bollinger_upper THEN 'BB_UPPER_BREAKOUT'
                    WHEN close < bollinger_lower THEN 'BB_LOWER_BREAKOUT'
                    WHEN rsi >= {self.thresholds['rsi_overbought']} THEN 'RSI_OVERBOUGHT'
                    WHEN rsi <= {self.thresholds['rsi_oversold']} THEN 'RSI_OVERSOLD'
                    WHEN golden_cross = 1 THEN 'GOLDEN_CROSS'
                    WHEN death_cross = 1 THEN 'DEATH_CROSS'
                    ELSE NULL
                END as alert_type
            FROM latest_data
            WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
        )
        SELECT *
        FROM anomalies
        WHERE alert_type IS NOT NULL
        ORDER BY datetime DESC, ABS(price_change_pct) DESC
        LIMIT 100
        """

        try:
            df = self.client.query(query).to_dataframe()
            alerts = []

            for _, row in df.iterrows():
                alert = {
                    'symbol': row['symbol'],
                    'datetime': row['datetime'].isoformat() if hasattr(row['datetime'], 'isoformat') else str(row['datetime']),
                    'alert_type': row['alert_type'],
                    'price': float(row['close']),
                    'price_change_pct': float(row['price_change_pct']) if pd.notna(row['price_change_pct']) else 0,
                    'zscore': float(row['zscore']) if pd.notna(row['zscore']) else 0,
                    'rsi': float(row['rsi']) if pd.notna(row['rsi']) else 50,
                    'adx': float(row['adx']) if pd.notna(row['adx']) else 0,
                    'severity': self._calculate_severity(row),
                    'recommendation': self._generate_recommendation(row)
                }
                alerts.append(alert)

            return alerts

        except Exception as e:
            logger.error(f"Error detecting price anomalies: {e}")
            return []

    def detect_volume_surges(self, asset_type='stocks'):
        """Detect unusual volume activity"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        query = f"""
        WITH volume_analysis AS (
            SELECT
                symbol,
                datetime,
                close,
                volume,
                AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as avg_volume_20d,
                ROUND(volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING), 0), 2) as volume_ratio,
                (close - LAG(close, 1) OVER (PARTITION BY symbol ORDER BY datetime)) / NULLIF(LAG(close, 1) OVER (PARTITION BY symbol ORDER BY datetime), 0) * 100 as price_change_pct,
                rsi,
                adx,
                buy_pressure_pct,
                sell_pressure_pct
            FROM `{self.project_id}.{self.dataset_id}.{table}`
            WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 25 DAY)
        )
        SELECT
            symbol,
            datetime,
            close,
            volume,
            avg_volume_20d,
            volume_ratio,
            price_change_pct,
            rsi,
            adx,
            buy_pressure_pct,
            sell_pressure_pct,
            CASE
                WHEN volume_ratio >= {self.thresholds['volume_surge_ratio']} AND price_change_pct > 0 THEN 'VOLUME_SURGE_BULLISH'
                WHEN volume_ratio >= {self.thresholds['volume_surge_ratio']} AND price_change_pct < 0 THEN 'VOLUME_SURGE_BEARISH'
                WHEN volume_ratio >= {self.thresholds['volume_surge_ratio']} THEN 'VOLUME_SURGE'
                ELSE NULL
            END as alert_type
        FROM volume_analysis
        WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
          AND volume_ratio >= {self.thresholds['volume_surge_ratio']}
        ORDER BY datetime DESC, volume_ratio DESC
        LIMIT 50
        """

        try:
            df = self.client.query(query).to_dataframe()
            alerts = []

            for _, row in df.iterrows():
                alert = {
                    'symbol': row['symbol'],
                    'datetime': row['datetime'].isoformat() if hasattr(row['datetime'], 'isoformat') else str(row['datetime']),
                    'alert_type': row['alert_type'],
                    'price': float(row['close']),
                    'volume': int(row['volume']),
                    'avg_volume': int(row['avg_volume_20d']) if pd.notna(row['avg_volume_20d']) else 0,
                    'volume_ratio': float(row['volume_ratio']),
                    'price_change_pct': float(row['price_change_pct']) if pd.notna(row['price_change_pct']) else 0,
                    'buy_pressure': float(row['buy_pressure_pct']) if pd.notna(row['buy_pressure_pct']) else 50,
                    'sell_pressure': float(row['sell_pressure_pct']) if pd.notna(row['sell_pressure_pct']) else 50,
                    'severity': 'HIGH' if row['volume_ratio'] > 4 else 'MEDIUM' if row['volume_ratio'] > 3 else 'LOW',
                    'recommendation': self._generate_volume_recommendation(row)
                }
                alerts.append(alert)

            return alerts

        except Exception as e:
            logger.error(f"Error detecting volume surges: {e}")
            return []

    def detect_technical_signals(self, asset_type='stocks'):
        """Detect technical trading signals"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        query = f"""
        SELECT
            symbol,
            datetime,
            close,
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            adx,
            plus_di,
            minus_di,
            golden_cross,
            death_cross,
            cycle_type,
            cycle_pnl_pct,
            hammer,
            shooting_star,
            bullish_engulfing,
            bearish_engulfing,
            doji,
            trend_regime,
            CASE
                WHEN golden_cross = 1 THEN 'GOLDEN_CROSS'
                WHEN death_cross = 1 THEN 'DEATH_CROSS'
                WHEN hammer = 1 AND rsi < 40 THEN 'HAMMER_OVERSOLD'
                WHEN shooting_star = 1 AND rsi > 60 THEN 'SHOOTING_STAR_OVERBOUGHT'
                WHEN bullish_engulfing = 1 THEN 'BULLISH_ENGULFING'
                WHEN bearish_engulfing = 1 THEN 'BEARISH_ENGULFING'
                WHEN macd > macd_signal AND LAG(macd, 1) OVER (PARTITION BY symbol ORDER BY datetime) <= LAG(macd_signal, 1) OVER (PARTITION BY symbol ORDER BY datetime) THEN 'MACD_BULLISH_CROSS'
                WHEN macd < macd_signal AND LAG(macd, 1) OVER (PARTITION BY symbol ORDER BY datetime) >= LAG(macd_signal, 1) OVER (PARTITION BY symbol ORDER BY datetime) THEN 'MACD_BEARISH_CROSS'
                WHEN adx > {self.thresholds['adx_strong_trend']} AND plus_di > minus_di THEN 'STRONG_UPTREND'
                WHEN adx > {self.thresholds['adx_strong_trend']} AND minus_di > plus_di THEN 'STRONG_DOWNTREND'
                ELSE NULL
            END as signal_type
        FROM `{self.project_id}.{self.dataset_id}.{table}`
        WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)
        HAVING signal_type IS NOT NULL
        ORDER BY datetime DESC
        LIMIT 100
        """

        try:
            df = self.client.query(query).to_dataframe()
            signals = []

            for _, row in df.iterrows():
                signal = {
                    'symbol': row['symbol'],
                    'datetime': row['datetime'].isoformat() if hasattr(row['datetime'], 'isoformat') else str(row['datetime']),
                    'signal_type': row['signal_type'],
                    'price': float(row['close']),
                    'rsi': float(row['rsi']) if pd.notna(row['rsi']) else 50,
                    'macd': float(row['macd']) if pd.notna(row['macd']) else 0,
                    'adx': float(row['adx']) if pd.notna(row['adx']) else 0,
                    'trend_regime': int(row['trend_regime']) if pd.notna(row['trend_regime']) else 0,
                    'cycle_pnl': float(row['cycle_pnl_pct']) if pd.notna(row['cycle_pnl_pct']) else 0,
                    'direction': 'BULLISH' if row['signal_type'] in ['GOLDEN_CROSS', 'HAMMER_OVERSOLD', 'BULLISH_ENGULFING', 'MACD_BULLISH_CROSS', 'STRONG_UPTREND'] else 'BEARISH',
                    'strength': self._calculate_signal_strength(row)
                }
                signals.append(signal)

            return signals

        except Exception as e:
            logger.error(f"Error detecting technical signals: {e}")
            return []

    def get_market_summary(self):
        """Get overall market summary with alerts"""

        # Get stock alerts
        stock_price_alerts = self.detect_price_anomalies('stocks')
        stock_volume_alerts = self.detect_volume_surges('stocks')
        stock_signals = self.detect_technical_signals('stocks')

        # Get crypto alerts
        crypto_price_alerts = self.detect_price_anomalies('crypto')
        crypto_volume_alerts = self.detect_volume_surges('crypto')
        crypto_signals = self.detect_technical_signals('crypto')

        # Aggregate stats
        summary = {
            'timestamp': datetime.now().isoformat(),
            'stocks': {
                'price_alerts': len(stock_price_alerts),
                'volume_alerts': len(stock_volume_alerts),
                'technical_signals': len(stock_signals),
                'bullish_signals': len([s for s in stock_signals if s.get('direction') == 'BULLISH']),
                'bearish_signals': len([s for s in stock_signals if s.get('direction') == 'BEARISH']),
                'top_alerts': stock_price_alerts[:5],
                'top_volume': stock_volume_alerts[:5],
                'top_signals': stock_signals[:5]
            },
            'crypto': {
                'price_alerts': len(crypto_price_alerts),
                'volume_alerts': len(crypto_volume_alerts),
                'technical_signals': len(crypto_signals),
                'bullish_signals': len([s for s in crypto_signals if s.get('direction') == 'BULLISH']),
                'bearish_signals': len([s for s in crypto_signals if s.get('direction') == 'BEARISH']),
                'top_alerts': crypto_price_alerts[:5],
                'top_volume': crypto_volume_alerts[:5],
                'top_signals': crypto_signals[:5]
            },
            'market_sentiment': self._calculate_market_sentiment(stock_signals + crypto_signals)
        }

        return summary

    def _calculate_severity(self, row):
        """Calculate alert severity based on multiple factors"""
        score = 0

        if pd.notna(row.get('price_change_pct')):
            if abs(row['price_change_pct']) > 5:
                score += 3
            elif abs(row['price_change_pct']) > 3:
                score += 2
            else:
                score += 1

        if pd.notna(row.get('zscore')):
            if abs(row['zscore']) > 3:
                score += 2
            elif abs(row['zscore']) > 2:
                score += 1

        if pd.notna(row.get('adx')) and row['adx'] > 30:
            score += 1

        if score >= 4:
            return 'CRITICAL'
        elif score >= 3:
            return 'HIGH'
        elif score >= 2:
            return 'MEDIUM'
        return 'LOW'

    def _generate_recommendation(self, row):
        """Generate trading recommendation based on alert"""
        alert_type = row.get('alert_type', '')

        recommendations = {
            'PRICE_SPIKE': 'Significant price movement detected. Monitor for continuation or reversal.',
            'BB_UPPER_BREAKOUT': 'Price above upper Bollinger Band. Watch for potential pullback or momentum continuation.',
            'BB_LOWER_BREAKOUT': 'Price below lower Bollinger Band. Watch for bounce or further breakdown.',
            'RSI_OVERBOUGHT': 'RSI indicates overbought conditions. Consider taking profits or tightening stops.',
            'RSI_OVERSOLD': 'RSI indicates oversold conditions. Watch for potential bounce.',
            'GOLDEN_CROSS': 'Bullish MA crossover signal. Consider long positions with proper risk management.',
            'DEATH_CROSS': 'Bearish MA crossover signal. Consider reducing exposure or hedging.',
        }

        return recommendations.get(alert_type, 'Monitor price action and volume for confirmation.')

    def _generate_volume_recommendation(self, row):
        """Generate recommendation for volume surge"""
        if row.get('price_change_pct', 0) > 0:
            return 'High volume on up move suggests institutional buying. Watch for continuation.'
        elif row.get('price_change_pct', 0) < 0:
            return 'High volume on down move suggests distribution. Consider defensive positioning.'
        return 'Unusual volume activity. Wait for directional confirmation.'

    def _calculate_signal_strength(self, row):
        """Calculate signal strength (1-10)"""
        strength = 5  # Base

        if pd.notna(row.get('adx')) and row['adx'] > 30:
            strength += 2
        elif pd.notna(row.get('adx')) and row['adx'] > 25:
            strength += 1

        if pd.notna(row.get('rsi')):
            if row['rsi'] < 30 or row['rsi'] > 70:
                strength += 1

        if pd.notna(row.get('trend_regime')) and row['trend_regime'] != 0:
            strength += 1

        return min(10, strength)

    def _calculate_market_sentiment(self, signals):
        """Calculate overall market sentiment"""
        if not signals:
            return {'sentiment': 'NEUTRAL', 'score': 50}

        bullish = len([s for s in signals if s.get('direction') == 'BULLISH'])
        bearish = len([s for s in signals if s.get('direction') == 'BEARISH'])
        total = bullish + bearish

        if total == 0:
            return {'sentiment': 'NEUTRAL', 'score': 50}

        score = int((bullish / total) * 100)

        if score > 65:
            sentiment = 'BULLISH'
        elif score < 35:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'

        return {
            'sentiment': sentiment,
            'score': score,
            'bullish_count': bullish,
            'bearish_count': bearish
        }


# Singleton instance
_alert_system = None

def get_alert_system():
    """Get singleton instance of alert system"""
    global _alert_system
    if _alert_system is None:
        _alert_system = TradingAlertSystem()
    return _alert_system
