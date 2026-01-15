"""
Signal Generator Agent
Analyzes market data and generates trading signals using technical indicators and AI
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentPriority

logger = logging.getLogger(__name__)


class SignalGeneratorAgent(BaseAgent):
    """
    Signal Generator Agent - Analyzes market data and generates trading signals

    Capabilities:
    - Technical indicator analysis (RSI, MACD, Bollinger Bands, etc.)
    - Trend detection and regime classification
    - Entry/exit signal generation
    - Multi-timeframe analysis
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        default_config = {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_signal_threshold': 0,
            'volume_spike_threshold': 2.0,
            'trend_ema_periods': [20, 50, 200],
            'min_confidence': 0.6,
            'supported_assets': ['stocks', 'crypto', 'etfs', 'forex'],
            'default_timeframe': 'daily'
        }

        merged_config = {**default_config, **(config or {})}

        super().__init__(
            agent_id=agent_id,
            name="SignalGenerator",
            description="Generates trading signals from market data analysis",
            config=merged_config
        )

        self.active_signals: List[Dict[str, Any]] = []

    def analyze_technical_indicators(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze technical indicators from market data"""
        if not data or len(data) < 2:
            return {'error': 'Insufficient data'}

        latest = data[0]
        prev = data[1]

        analysis = {
            'symbol': latest.get('symbol'),
            'datetime': str(latest.get('datetime')),
            'close': latest.get('close'),
            'indicators': {}
        }

        # RSI Analysis
        rsi = latest.get('rsi')
        if rsi:
            rsi_signal = 'neutral'
            if rsi < self.config['rsi_oversold']:
                rsi_signal = 'oversold'
            elif rsi > self.config['rsi_overbought']:
                rsi_signal = 'overbought'

            analysis['indicators']['rsi'] = {
                'value': rsi,
                'signal': rsi_signal,
                'prev_value': prev.get('rsi')
            }

        # MACD Analysis
        macd = latest.get('macd')
        macd_signal = latest.get('macd_signal')
        prev_macd = prev.get('macd')
        prev_macd_signal = prev.get('macd_signal')

        if macd is not None and macd_signal is not None:
            macd_histogram = macd - macd_signal
            crossover = None

            if prev_macd is not None and prev_macd_signal is not None:
                if prev_macd <= prev_macd_signal and macd > macd_signal:
                    crossover = 'bullish'
                elif prev_macd >= prev_macd_signal and macd < macd_signal:
                    crossover = 'bearish'

            analysis['indicators']['macd'] = {
                'macd': macd,
                'signal': macd_signal,
                'histogram': macd_histogram,
                'crossover': crossover
            }

        # Bollinger Bands Analysis
        bb_upper = latest.get('bollinger_upper') or latest.get('bb_upper')
        bb_lower = latest.get('bollinger_lower') or latest.get('bb_lower')
        bb_middle = latest.get('bollinger_middle') or latest.get('bb_middle')
        close = latest.get('close')

        if bb_upper and bb_lower and bb_middle and close:
            bb_position = 'middle'
            if close >= bb_upper:
                bb_position = 'above_upper'
            elif close <= bb_lower:
                bb_position = 'below_lower'
            elif close > bb_middle:
                bb_position = 'upper_half'
            else:
                bb_position = 'lower_half'

            bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle else 0

            analysis['indicators']['bollinger'] = {
                'upper': bb_upper,
                'middle': bb_middle,
                'lower': bb_lower,
                'position': bb_position,
                'width': bb_width
            }

        # Trend Analysis (EMAs)
        sma_20 = latest.get('sma_20')
        sma_50 = latest.get('sma_50')
        sma_200 = latest.get('sma_200')

        if sma_20 and sma_50 and sma_200 and close:
            trend = 'neutral'
            if close > sma_20 > sma_50 > sma_200:
                trend = 'strong_bullish'
            elif close > sma_20 > sma_50:
                trend = 'bullish'
            elif close < sma_20 < sma_50 < sma_200:
                trend = 'strong_bearish'
            elif close < sma_20 < sma_50:
                trend = 'bearish'

            analysis['indicators']['trend'] = {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'trend': trend,
                'above_sma20': close > sma_20,
                'above_sma50': close > sma_50,
                'above_sma200': close > sma_200
            }

        # Volume Analysis
        volume = latest.get('volume')
        if volume and len(data) >= 20:
            avg_volume = sum(d.get('volume', 0) for d in data[:20]) / 20
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1

            analysis['indicators']['volume'] = {
                'current': volume,
                'avg_20': avg_volume,
                'ratio': volume_ratio,
                'spike': volume_ratio > self.config['volume_spike_threshold']
            }

        return analysis

    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal from analysis"""
        indicators = analysis.get('indicators', {})

        buy_score = 0
        sell_score = 0
        reasons = []

        # RSI signals
        rsi_data = indicators.get('rsi', {})
        if rsi_data.get('signal') == 'oversold':
            buy_score += 2
            reasons.append('RSI oversold')
        elif rsi_data.get('signal') == 'overbought':
            sell_score += 2
            reasons.append('RSI overbought')

        # MACD signals
        macd_data = indicators.get('macd', {})
        if macd_data.get('crossover') == 'bullish':
            buy_score += 3
            reasons.append('MACD bullish crossover')
        elif macd_data.get('crossover') == 'bearish':
            sell_score += 3
            reasons.append('MACD bearish crossover')

        # Bollinger signals
        bb_data = indicators.get('bollinger', {})
        if bb_data.get('position') == 'below_lower':
            buy_score += 2
            reasons.append('Below lower Bollinger Band')
        elif bb_data.get('position') == 'above_upper':
            sell_score += 2
            reasons.append('Above upper Bollinger Band')

        # Trend signals
        trend_data = indicators.get('trend', {})
        trend = trend_data.get('trend', 'neutral')
        if trend in ['strong_bullish', 'bullish']:
            buy_score += 2
            reasons.append(f'Trend: {trend}')
        elif trend in ['strong_bearish', 'bearish']:
            sell_score += 2
            reasons.append(f'Trend: {trend}')

        # Volume confirmation
        volume_data = indicators.get('volume', {})
        if volume_data.get('spike'):
            if buy_score > sell_score:
                buy_score += 1
                reasons.append('Volume spike confirms bullish')
            elif sell_score > buy_score:
                sell_score += 1
                reasons.append('Volume spike confirms bearish')

        # Determine signal
        max_score = 10  # Maximum possible score
        buy_confidence = buy_score / max_score
        sell_confidence = sell_score / max_score

        signal = {
            'symbol': analysis.get('symbol'),
            'datetime': analysis.get('datetime'),
            'price': analysis.get('close'),
            'signal_type': 'hold',
            'direction': 'neutral',
            'confidence': 0,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'reasons': reasons,
            'generated_at': datetime.utcnow().isoformat()
        }

        min_confidence = self.config['min_confidence']

        if buy_confidence >= min_confidence and buy_score > sell_score:
            signal['signal_type'] = 'buy'
            signal['direction'] = 'long'
            signal['confidence'] = buy_confidence
        elif sell_confidence >= min_confidence and sell_score > buy_score:
            signal['signal_type'] = 'sell'
            signal['direction'] = 'short'
            signal['confidence'] = sell_confidence
        else:
            signal['confidence'] = max(buy_confidence, sell_confidence)

        return signal

    def scan_market(
        self,
        symbols: List[str],
        asset_type: str = 'stocks',
        timeframe: str = 'daily'
    ) -> List[Dict[str, Any]]:
        """Scan multiple symbols for trading signals"""
        signals = []

        for symbol in symbols:
            try:
                data = self.get_market_data(symbol, asset_type, timeframe, limit=50)
                if data:
                    analysis = self.analyze_technical_indicators(data)
                    signal = self.generate_signal(analysis)
                    signal['asset_type'] = asset_type
                    signal['timeframe'] = timeframe
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")

        # Sort by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)

        return signals

    def handle_message(self, message) -> Dict[str, Any]:
        """Handle incoming messages from other agents"""
        msg_type = message.message_type

        if msg_type == 'scan_request':
            symbols = message.payload.get('symbols', [])
            asset_type = message.payload.get('asset_type', 'stocks')
            signals = self.scan_market(symbols, asset_type)
            return {'signals': signals}

        elif msg_type == 'analyze_symbol':
            symbol = message.payload.get('symbol')
            asset_type = message.payload.get('asset_type', 'stocks')
            data = self.get_market_data(symbol, asset_type, 'daily', limit=50)
            if data:
                analysis = self.analyze_technical_indicators(data)
                signal = self.generate_signal(analysis)
                return {'analysis': analysis, 'signal': signal}
            return {'error': 'No data available'}

        return super().handle_message(message)

    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute signal generation"""
        context = context or {}

        symbols = context.get('symbols', ['AAPL', 'MSFT', 'NVDA', 'SPY', 'QQQ'])
        asset_type = context.get('asset_type', 'stocks')
        timeframe = context.get('timeframe', 'daily')

        signals = self.scan_market(symbols, asset_type, timeframe)

        # Filter actionable signals
        buy_signals = [s for s in signals if s['signal_type'] == 'buy']
        sell_signals = [s for s in signals if s['signal_type'] == 'sell']

        self.active_signals = signals
        self.log_execution('market_scan', {
            'symbols_scanned': len(symbols),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals)
        })

        return {
            'total_scanned': len(symbols),
            'signals': signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'top_buy': buy_signals[0] if buy_signals else None,
            'top_sell': sell_signals[0] if sell_signals else None
        }
