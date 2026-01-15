"""
Gemini Financial Analyst for AIAlgoTradeHits.com
Based on: gemini-financial-analysis-modes.html

This module provides multiple AI-powered financial analysis modes:
1. Technical Analysis Mode - Indicator interpretation
2. Fundamental Analysis Mode - Financial metrics analysis
3. Sentiment Analysis Mode - Market sentiment evaluation
4. Risk Assessment Mode - Risk/reward analysis
5. Portfolio Analysis Mode - Portfolio optimization suggestions
6. Trade Recommendation Mode - Entry/exit recommendations
"""

from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
LOCATION = 'us-central1'

# Initialize
bq_client = bigquery.Client(project=PROJECT_ID)
vertexai.init(project=PROJECT_ID, location=LOCATION)


def fmt(value, decimals=2, prefix=''):
    """Format a value with specified decimals, or return N/A if None"""
    if value is None:
        return 'N/A'
    return f"{prefix}{value:.{decimals}f}"


class GeminiFinancialAnalyst:
    """Multi-mode financial analysis using Gemini LLM"""

    def __init__(self):
        # Try multiple model versions
        self.model = None
        model_versions = [
            "gemini-2.0-flash-001",
            "gemini-1.5-pro-002",
            "gemini-1.5-flash-002",
            "gemini-pro"
        ]

        for model_name in model_versions:
            try:
                self.model = GenerativeModel(model_name)
                print(f"Initialized with model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to initialize {model_name}: {e}")
                continue

        if self.model is None:
            print("Warning: No Gemini model available, falling back to rule-based analysis")

        self.generation_config = GenerationConfig(
            temperature=0.3,
            top_p=0.8,
            max_output_tokens=2048
        )

    def _fetch_market_data(self, symbol: str, asset_type: str = 'stocks', days: int = 30) -> Dict:
        """Fetch market data for analysis"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
        AND datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY))
        ORDER BY datetime DESC
        """

        df = bq_client.query(query).to_dataframe()

        if df.empty:
            return {'error': f'No data found for {symbol}'}

        latest = df.iloc[0]

        # Calculate summary statistics
        data = {
            'symbol': symbol,
            'asset_type': asset_type,
            'latest': {
                'date': str(latest['datetime']),
                'price': float(latest['close']) if pd.notna(latest['close']) else None,
                'open': float(latest['open']) if pd.notna(latest['open']) else None,
                'high': float(latest['high']) if pd.notna(latest['high']) else None,
                'low': float(latest['low']) if pd.notna(latest['low']) else None,
                'volume': float(latest['volume']) if pd.notna(latest['volume']) else None
            },
            'indicators': {
                'rsi': float(latest['rsi']) if pd.notna(latest.get('rsi')) else None,
                'macd': float(latest['macd']) if pd.notna(latest.get('macd')) else None,
                'macd_signal': float(latest['macd_signal']) if pd.notna(latest.get('macd_signal')) else None,
                'adx': float(latest['adx']) if pd.notna(latest.get('adx')) else None,
                'atr': float(latest['atr']) if pd.notna(latest.get('atr')) else None,
                'sma_20': float(latest['sma_20']) if pd.notna(latest.get('sma_20')) else None,
                'sma_50': float(latest['sma_50']) if pd.notna(latest.get('sma_50')) else None,
                'sma_200': float(latest['sma_200']) if pd.notna(latest.get('sma_200')) else None,
                'bollinger_upper': float(latest['bollinger_upper']) if pd.notna(latest.get('bollinger_upper')) else None,
                'bollinger_lower': float(latest['bollinger_lower']) if pd.notna(latest.get('bollinger_lower')) else None
            },
            'signals': {
                'trend_regime': int(latest['trend_regime']) if pd.notna(latest.get('trend_regime')) else 0,
                'cycle_type': int(latest['cycle_type']) if pd.notna(latest.get('cycle_type')) else 0,
                'golden_cross': int(latest['golden_cross']) if pd.notna(latest.get('golden_cross')) else 0,
                'death_cross': int(latest['death_cross']) if pd.notna(latest.get('death_cross')) else 0,
                'buy_pressure_pct': float(latest['buy_pressure_pct']) if pd.notna(latest.get('buy_pressure_pct')) else 50,
                'sell_pressure_pct': float(latest['sell_pressure_pct']) if pd.notna(latest.get('sell_pressure_pct')) else 50
            },
            'patterns': {
                'hammer': int(latest['hammer']) if pd.notna(latest.get('hammer')) else 0,
                'shooting_star': int(latest['shooting_star']) if pd.notna(latest.get('shooting_star')) else 0,
                'bullish_engulfing': int(latest['bullish_engulfing']) if pd.notna(latest.get('bullish_engulfing')) else 0,
                'bearish_engulfing': int(latest['bearish_engulfing']) if pd.notna(latest.get('bearish_engulfing')) else 0,
                'doji': int(latest['doji']) if pd.notna(latest.get('doji')) else 0
            },
            'statistics': {
                'period_high': float(df['high'].max()),
                'period_low': float(df['low'].min()),
                'avg_volume': float(df['volume'].mean()),
                'price_change_pct': float((df.iloc[0]['close'] - df.iloc[-1]['close']) / df.iloc[-1]['close'] * 100),
                'volatility': float(df['close'].std() / df['close'].mean() * 100)
            }
        }

        return data

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini model with prompt"""

        if self.model is None:
            return json.dumps({'error': 'Gemini model not available'})

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            return response.text
        except Exception as e:
            return json.dumps({'error': str(e)})

    def technical_analysis(self, symbol: str, asset_type: str = 'stocks') -> Dict:
        """
        Mode 1: Technical Analysis
        Interprets technical indicators and provides trading signals
        """

        data = self._fetch_market_data(symbol, asset_type)
        if 'error' in data:
            return data

        prompt = f"""You are a professional technical analyst. Analyze the following market data and provide a comprehensive technical analysis.

SYMBOL: {symbol}
ASSET TYPE: {asset_type.upper()}

PRICE DATA:
- Current Price: ${data['latest']['price']:.2f}
- Period High: ${data['statistics']['period_high']:.2f}
- Period Low: ${data['statistics']['period_low']:.2f}
- Price Change (30d): {data['statistics']['price_change_pct']:.2f}%

TECHNICAL INDICATORS:
- RSI: {fmt(data['indicators']['rsi'], 1)}
- MACD: {fmt(data['indicators']['macd'], 4)}
- MACD Signal: {fmt(data['indicators']['macd_signal'], 4)}
- ADX: {fmt(data['indicators']['adx'], 1)}
- ATR: {fmt(data['indicators']['atr'], 2, '$')}

MOVING AVERAGES:
- SMA 20: {fmt(data['indicators']['sma_20'], 2, '$')}
- SMA 50: {fmt(data['indicators']['sma_50'], 2, '$')}
- SMA 200: {fmt(data['indicators']['sma_200'], 2, '$')}

SIGNALS:
- Trend Regime: {data['signals']['trend_regime']} (1=bullish, -1=bearish, 0=neutral)
- Buy Pressure: {data['signals']['buy_pressure_pct']:.1f}%
- Sell Pressure: {data['signals']['sell_pressure_pct']:.1f}%
- Golden Cross: {'Yes' if data['signals']['golden_cross'] else 'No'}
- Death Cross: {'Yes' if data['signals']['death_cross'] else 'No'}

CANDLESTICK PATTERNS:
- Hammer: {'Detected' if data['patterns']['hammer'] else 'None'}
- Shooting Star: {'Detected' if data['patterns']['shooting_star'] else 'None'}
- Bullish Engulfing: {'Detected' if data['patterns']['bullish_engulfing'] else 'None'}
- Bearish Engulfing: {'Detected' if data['patterns']['bearish_engulfing'] else 'None'}

Provide your analysis in JSON format:
{{
    "trend_direction": "BULLISH" or "BEARISH" or "NEUTRAL",
    "trend_strength": "STRONG" or "MODERATE" or "WEAK",
    "momentum": "INCREASING" or "DECREASING" or "STABLE",
    "support_levels": [price1, price2],
    "resistance_levels": [price1, price2],
    "key_signals": ["signal1", "signal2", "signal3"],
    "recommendation": "BUY" or "SELL" or "HOLD",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "summary": "Brief analysis summary"
}}
"""

        response = self._call_gemini(prompt)

        try:
            # Extract JSON from response
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]

            result = json.loads(response)
            result['mode'] = 'TECHNICAL_ANALYSIS'
            result['symbol'] = symbol
            result['data'] = data
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                'mode': 'TECHNICAL_ANALYSIS',
                'symbol': symbol,
                'error': 'Failed to parse response',
                'raw_response': response[:500]
            }

    def risk_assessment(self, symbol: str, asset_type: str = 'stocks',
                        position_size: float = 10000) -> Dict:
        """
        Mode 2: Risk Assessment
        Evaluates risk/reward and provides position sizing recommendations
        """

        data = self._fetch_market_data(symbol, asset_type)
        if 'error' in data:
            return data

        prompt = f"""You are a professional risk manager. Analyze the following market data and provide a comprehensive risk assessment.

SYMBOL: {symbol}
ASSET TYPE: {asset_type.upper()}
PROPOSED POSITION SIZE: ${position_size:,.2f}

PRICE DATA:
- Current Price: ${data['latest']['price']:.2f}
- 30-Day High: ${data['statistics']['period_high']:.2f}
- 30-Day Low: ${data['statistics']['period_low']:.2f}
- Volatility (CV): {data['statistics']['volatility']:.2f}%

RISK INDICATORS:
- ATR (Average True Range): {fmt(data['indicators']['atr'], 2, '$')}
- ADX (Trend Strength): {fmt(data['indicators']['adx'], 1)}
- RSI: {fmt(data['indicators']['rsi'], 1)}

BOLLINGER BANDS:
- Upper: {fmt(data['indicators']['bollinger_upper'], 2, '$')}
- Lower: {fmt(data['indicators']['bollinger_lower'], 2, '$')}

Provide your risk assessment in JSON format:
{{
    "risk_level": "HIGH" or "MEDIUM" or "LOW",
    "max_position_size": recommended_amount,
    "suggested_stop_loss": stop_loss_price,
    "suggested_take_profit": take_profit_price,
    "risk_reward_ratio": ratio,
    "max_daily_loss": amount,
    "volatility_assessment": "HIGH" or "MEDIUM" or "LOW",
    "risk_factors": ["factor1", "factor2"],
    "mitigation_strategies": ["strategy1", "strategy2"],
    "summary": "Brief risk assessment"
}}
"""

        response = self._call_gemini(prompt)

        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]

            result = json.loads(response)
            result['mode'] = 'RISK_ASSESSMENT'
            result['symbol'] = symbol
            result['position_size_input'] = position_size
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                'mode': 'RISK_ASSESSMENT',
                'symbol': symbol,
                'error': 'Failed to parse response',
                'raw_response': response[:500]
            }

    def sentiment_analysis(self, symbol: str, asset_type: str = 'stocks') -> Dict:
        """
        Mode 3: Sentiment Analysis
        Analyzes market sentiment based on technical indicators
        """

        data = self._fetch_market_data(symbol, asset_type)
        if 'error' in data:
            return data

        prompt = f"""You are a market sentiment analyst. Analyze the following technical data to assess market sentiment for {symbol}.

PRICE ACTION:
- Price Change (30d): {data['statistics']['price_change_pct']:.2f}%
- Current vs 200-day MA: {'Above' if data['latest']['price'] > (data['indicators']['sma_200'] or 0) else 'Below'}
- Volatility: {data['statistics']['volatility']:.2f}%

SENTIMENT INDICATORS:
- RSI: {fmt(data['indicators']['rsi'], 1)} (>70 overbought, <30 oversold)
- Buy Pressure: {data['signals']['buy_pressure_pct']:.1f}%
- Sell Pressure: {data['signals']['sell_pressure_pct']:.1f}%
- Trend Regime: {data['signals']['trend_regime']}

VOLUME:
- Recent Volume vs Average: {f"{data['latest']['volume'] / data['statistics']['avg_volume']:.2f}x" if data['statistics']['avg_volume'] and data['statistics']['avg_volume'] > 0 else 'N/A'}

Provide sentiment analysis in JSON format:
{{
    "overall_sentiment": "BULLISH" or "BEARISH" or "NEUTRAL",
    "sentiment_strength": 1-10,
    "fear_greed_indicator": "EXTREME_FEAR" or "FEAR" or "NEUTRAL" or "GREED" or "EXTREME_GREED",
    "institutional_bias": "ACCUMULATING" or "DISTRIBUTING" or "NEUTRAL",
    "retail_bias": "BULLISH" or "BEARISH" or "NEUTRAL",
    "momentum_sentiment": "POSITIVE" or "NEGATIVE" or "NEUTRAL",
    "key_sentiment_drivers": ["driver1", "driver2"],
    "contrarian_signals": ["signal1"],
    "summary": "Brief sentiment summary"
}}
"""

        response = self._call_gemini(prompt)

        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]

            result = json.loads(response)
            result['mode'] = 'SENTIMENT_ANALYSIS'
            result['symbol'] = symbol
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                'mode': 'SENTIMENT_ANALYSIS',
                'symbol': symbol,
                'error': 'Failed to parse response',
                'raw_response': response[:500]
            }

    def trade_recommendation(self, symbol: str, asset_type: str = 'stocks') -> Dict:
        """
        Mode 4: Trade Recommendation
        Provides specific entry/exit recommendations
        """

        data = self._fetch_market_data(symbol, asset_type)
        if 'error' in data:
            return data

        prompt = f"""You are a professional trader. Based on the following data, provide specific trade recommendations for {symbol}.

CURRENT STATE:
- Price: ${data['latest']['price']:.2f}
- Trend: {data['signals']['trend_regime']} (1=up, -1=down, 0=sideways)
- RSI: {fmt(data['indicators']['rsi'], 1)}
- MACD vs Signal: {'Bullish' if (data['indicators']['macd'] or 0) > (data['indicators']['macd_signal'] or 0) else 'Bearish'}
- ADX: {fmt(data['indicators']['adx'], 1)}

KEY LEVELS:
- SMA 20: {fmt(data['indicators']['sma_20'], 2, '$')}
- SMA 50: {fmt(data['indicators']['sma_50'], 2, '$')}
- Bollinger Upper: {fmt(data['indicators']['bollinger_upper'], 2, '$')}
- Bollinger Lower: {fmt(data['indicators']['bollinger_lower'], 2, '$')}
- ATR: {fmt(data['indicators']['atr'], 2, '$')}

PATTERNS:
- Golden Cross: {'Yes' if data['signals']['golden_cross'] else 'No'}
- Death Cross: {'Yes' if data['signals']['death_cross'] else 'No'}
- Candlestick Patterns: {', '.join([k for k, v in data['patterns'].items() if v]) or 'None'}

Provide trade recommendations in JSON format:
{{
    "action": "BUY" or "SELL" or "HOLD" or "WAIT",
    "entry_price": recommended_entry_price,
    "stop_loss": stop_loss_price,
    "take_profit_1": first_target,
    "take_profit_2": second_target,
    "position_size_pct": recommended_portfolio_percentage,
    "time_horizon": "INTRADAY" or "SWING" or "POSITION",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "entry_conditions": ["condition1", "condition2"],
    "exit_conditions": ["condition1", "condition2"],
    "risk_per_trade_pct": percentage,
    "reasoning": "Brief explanation of the trade setup"
}}
"""

        response = self._call_gemini(prompt)

        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]

            result = json.loads(response)
            result['mode'] = 'TRADE_RECOMMENDATION'
            result['symbol'] = symbol
            result['current_price'] = data['latest']['price']
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                'mode': 'TRADE_RECOMMENDATION',
                'symbol': symbol,
                'error': 'Failed to parse response',
                'raw_response': response[:500]
            }

    def portfolio_analysis(self, symbols: List[str], asset_type: str = 'stocks') -> Dict:
        """
        Mode 5: Portfolio Analysis
        Analyzes a portfolio of assets and provides optimization suggestions
        """

        portfolio_data = []
        for symbol in symbols:
            data = self._fetch_market_data(symbol, asset_type, days=30)
            if 'error' not in data:
                portfolio_data.append({
                    'symbol': symbol,
                    'price': data['latest']['price'],
                    'rsi': data['indicators']['rsi'],
                    'trend': data['signals']['trend_regime'],
                    'volatility': data['statistics']['volatility'],
                    'change_30d': data['statistics']['price_change_pct']
                })

        if not portfolio_data:
            return {'error': 'No valid data for any symbol'}

        portfolio_summary = "\n".join([
            f"- {p['symbol']}: Price=${p['price']:.2f}, RSI={fmt(p['rsi'], 1)}, "
            f"Trend={p['trend']}, Vol={p['volatility']:.2f}%, 30d Change={p['change_30d']:.2f}%"
            for p in portfolio_data
        ])

        prompt = f"""You are a portfolio manager. Analyze the following portfolio and provide optimization recommendations.

PORTFOLIO HOLDINGS:
{portfolio_summary}

TOTAL SYMBOLS: {len(portfolio_data)}

Provide portfolio analysis in JSON format:
{{
    "overall_health": "STRONG" or "MODERATE" or "WEAK",
    "diversification_score": 1-10,
    "risk_level": "HIGH" or "MEDIUM" or "LOW",
    "correlation_concern": true or false,
    "rebalancing_needed": true or false,
    "top_performers": ["symbol1", "symbol2"],
    "underperformers": ["symbol1", "symbol2"],
    "add_recommendations": ["symbol1", "symbol2"],
    "reduce_recommendations": ["symbol1"],
    "sector_exposure": "Brief sector analysis",
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "summary": "Brief portfolio assessment"
}}
"""

        response = self._call_gemini(prompt)

        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]

            result = json.loads(response)
            result['mode'] = 'PORTFOLIO_ANALYSIS'
            result['symbols_analyzed'] = symbols
            result['portfolio_data'] = portfolio_data
            result['timestamp'] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                'mode': 'PORTFOLIO_ANALYSIS',
                'symbols': symbols,
                'error': 'Failed to parse response',
                'raw_response': response[:500]
            }

    def full_analysis(self, symbol: str, asset_type: str = 'stocks') -> Dict:
        """
        Run all analysis modes and combine results
        """

        print(f"\nRunning full analysis for {symbol}...")

        results = {
            'symbol': symbol,
            'asset_type': asset_type,
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }

        print("  1/4 Technical Analysis...")
        results['analyses']['technical'] = self.technical_analysis(symbol, asset_type)

        print("  2/4 Risk Assessment...")
        results['analyses']['risk'] = self.risk_assessment(symbol, asset_type)

        print("  3/4 Sentiment Analysis...")
        results['analyses']['sentiment'] = self.sentiment_analysis(symbol, asset_type)

        print("  4/4 Trade Recommendation...")
        results['analyses']['trade'] = self.trade_recommendation(symbol, asset_type)

        # Generate summary
        results['summary'] = {
            'overall_bias': results['analyses'].get('technical', {}).get('recommendation', 'UNKNOWN'),
            'risk_level': results['analyses'].get('risk', {}).get('risk_level', 'UNKNOWN'),
            'sentiment': results['analyses'].get('sentiment', {}).get('overall_sentiment', 'UNKNOWN'),
            'recommended_action': results['analyses'].get('trade', {}).get('action', 'UNKNOWN')
        }

        return results


def main():
    """Test the Gemini Financial Analyst"""

    print("=" * 80)
    print("GEMINI FINANCIAL ANALYST - MULTI-MODE ANALYSIS")
    print("=" * 80)
    print(f"Started: {datetime.now()}")

    analyst = GeminiFinancialAnalyst()

    # Test with AAPL
    print("\n--- TESTING ANALYSIS MODES ---")

    # Technical Analysis
    print("\n1. TECHNICAL ANALYSIS (AAPL)")
    tech = analyst.technical_analysis('AAPL', 'stocks')
    if 'error' not in tech:
        print(f"   Trend: {tech.get('trend_direction', 'N/A')}")
        print(f"   Recommendation: {tech.get('recommendation', 'N/A')}")
        print(f"   Confidence: {tech.get('confidence', 'N/A')}")
    else:
        print(f"   Error: {tech.get('error')}")

    # Risk Assessment
    print("\n2. RISK ASSESSMENT (AAPL)")
    risk = analyst.risk_assessment('AAPL', 'stocks', 10000)
    if 'error' not in risk:
        print(f"   Risk Level: {risk.get('risk_level', 'N/A')}")
        print(f"   Max Position: ${risk.get('max_position_size', 'N/A'):,.2f}" if isinstance(risk.get('max_position_size'), (int, float)) else f"   Max Position: {risk.get('max_position_size', 'N/A')}")
        print(f"   Risk/Reward: {risk.get('risk_reward_ratio', 'N/A')}")
    else:
        print(f"   Error: {risk.get('error')}")

    # Sentiment Analysis
    print("\n3. SENTIMENT ANALYSIS (AAPL)")
    sentiment = analyst.sentiment_analysis('AAPL', 'stocks')
    if 'error' not in sentiment:
        print(f"   Overall: {sentiment.get('overall_sentiment', 'N/A')}")
        print(f"   Strength: {sentiment.get('sentiment_strength', 'N/A')}/10")
        print(f"   Fear/Greed: {sentiment.get('fear_greed_indicator', 'N/A')}")
    else:
        print(f"   Error: {sentiment.get('error')}")

    # Trade Recommendation
    print("\n4. TRADE RECOMMENDATION (AAPL)")
    trade = analyst.trade_recommendation('AAPL', 'stocks')
    if 'error' not in trade:
        print(f"   Action: {trade.get('action', 'N/A')}")
        print(f"   Entry: ${trade.get('entry_price', 'N/A')}" if isinstance(trade.get('entry_price'), (int, float)) else f"   Entry: {trade.get('entry_price', 'N/A')}")
        print(f"   Stop Loss: ${trade.get('stop_loss', 'N/A')}" if isinstance(trade.get('stop_loss'), (int, float)) else f"   Stop Loss: {trade.get('stop_loss', 'N/A')}")
        print(f"   Confidence: {trade.get('confidence', 'N/A')}")
    else:
        print(f"   Error: {trade.get('error')}")

    # Portfolio Analysis
    print("\n5. PORTFOLIO ANALYSIS")
    portfolio = analyst.portfolio_analysis(['AAPL', 'MSFT', 'GOOGL', 'NVDA'], 'stocks')
    if 'error' not in portfolio:
        print(f"   Health: {portfolio.get('overall_health', 'N/A')}")
        print(f"   Risk: {portfolio.get('risk_level', 'N/A')}")
        print(f"   Diversification: {portfolio.get('diversification_score', 'N/A')}/10")
    else:
        print(f"   Error: {portfolio.get('error')}")

    # Crypto test
    print("\n--- CRYPTO ANALYSIS (BTC/USD) ---")
    btc_analysis = analyst.full_analysis('BTC/USD', 'crypto')
    print(f"   Summary: {btc_analysis.get('summary', {})}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
