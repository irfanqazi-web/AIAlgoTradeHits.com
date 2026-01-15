"""
ADK-Based Trading Agent System for AIAlgoTradeHits
Multi-Agent Architecture for Mathematical, Data Engineering, and Analytical Trading Capabilities

Developer: irfan.qazi@aialgotradehits.com
Documentation: https://google.github.io/adk-docs/
GitHub: https://github.com/google/adk-python

This module implements a sophisticated multi-agent trading analytics system using
Google's Agent Development Kit (ADK) with Gemini 2.5 for:
- Text-to-SQL conversion for trading queries
- Technical analysis and indicator calculations
- Market scanning and opportunity detection
- Quantitative analysis and statistical computations
- Risk assessment and position sizing
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import numpy as np

# Google ADK imports
try:
    from google.adk.agents import Agent, LlmAgent
    from google.adk.tools import FunctionTool
    from google.adk.runners import Runner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Install ADK: pip install google-adk")

# Google GenAI for standalone Gemini usage
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# BigQuery for data access
from google.cloud import bigquery

# Numerical computing
import pandas as pd

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
GEMINI_MODEL = 'gemini-2.5-flash'

# ==============================================================================
# TOOL DEFINITIONS - Custom Tools for Trading Agents
# ==============================================================================

@dataclass
class TradingContext:
    """Context for trading operations"""
    asset_type: str = 'stocks'
    period: str = 'daily'
    symbols: List[str] = None
    start_date: str = None
    end_date: str = None


class BigQueryTool:
    """Tool for executing BigQuery queries"""

    def __init__(self):
        self.client = bigquery.Client(project=PROJECT_ID)

    def execute_sql(self, sql: str, limit: int = 100) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            query_job = self.client.query(sql)
            results = list(query_job.result())

            data = []
            for row in results[:limit]:
                row_dict = dict(row)
                for key, value in row_dict.items():
                    if hasattr(value, 'isoformat'):
                        row_dict[key] = value.isoformat()
                    elif isinstance(value, (np.float64, np.float32)):
                        row_dict[key] = float(value)
                    elif isinstance(value, (np.int64, np.int32)):
                        row_dict[key] = int(value)
                data.append(row_dict)

            return {'success': True, 'data': data, 'count': len(data)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': []}

    def get_latest_data(self, table: str, symbol: str = None, limit: int = 100) -> Dict:
        """Get latest data from a table"""
        where_clause = f"WHERE symbol = '{symbol}'" if symbol else ""
        sql = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        {where_clause}
        ORDER BY datetime DESC
        LIMIT {limit}
        """
        return self.execute_sql(sql)


class TechnicalAnalysisTool:
    """Tool for calculating technical indicators"""

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict[str, float]:
        """Calculate MACD (12, 26, 9)"""
        if len(prices) < 26:
            return {'macd': None, 'signal': None, 'histogram': None}

        prices_arr = np.array(prices)

        # Calculate EMAs
        ema_12 = pd.Series(prices_arr).ewm(span=12).mean().iloc[-1]
        ema_26 = pd.Series(prices_arr).ewm(span=26).mean().iloc[-1]

        macd = ema_12 - ema_26

        # Signal line (9-period EMA of MACD)
        macd_series = pd.Series(prices_arr).ewm(span=12).mean() - pd.Series(prices_arr).ewm(span=26).mean()
        signal = macd_series.ewm(span=9).mean().iloc[-1]

        return {
            'macd': round(macd, 4),
            'signal': round(signal, 4),
            'histogram': round(macd - signal, 4)
        }

    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': None, 'middle': None, 'lower': None}

        prices_arr = np.array(prices[-period:])
        middle = np.mean(prices_arr)
        std = np.std(prices_arr)

        return {
            'upper': round(middle + (std_dev * std), 4),
            'middle': round(middle, 4),
            'lower': round(middle - (std_dev * std), 4)
        }

    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return None

        true_ranges = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            true_ranges.append(tr)

        return round(np.mean(true_ranges[-period:]), 4)

    @staticmethod
    def detect_trend(prices: List[float], sma_short: int = 20, sma_long: int = 50) -> Dict[str, Any]:
        """Detect trend direction and strength"""
        if len(prices) < sma_long:
            return {'trend': 'unknown', 'strength': 0}

        prices_arr = np.array(prices)
        sma_short_val = np.mean(prices_arr[-sma_short:])
        sma_long_val = np.mean(prices_arr[-sma_long:])

        current_price = prices[-1]

        if current_price > sma_short_val > sma_long_val:
            trend = 'uptrend'
            strength = min(100, ((current_price - sma_long_val) / sma_long_val) * 100)
        elif current_price < sma_short_val < sma_long_val:
            trend = 'downtrend'
            strength = min(100, ((sma_long_val - current_price) / sma_long_val) * 100)
        else:
            trend = 'sideways'
            strength = 0

        return {'trend': trend, 'strength': round(strength, 2)}


class QuantitativeAnalysisTool:
    """Tool for quantitative analysis and statistical computations"""

    @staticmethod
    def calculate_returns(prices: List[float]) -> Dict[str, float]:
        """Calculate various return metrics"""
        if len(prices) < 2:
            return {}

        prices_arr = np.array(prices)
        returns = np.diff(prices_arr) / prices_arr[:-1]

        return {
            'total_return': round((prices[-1] - prices[0]) / prices[0] * 100, 2),
            'mean_return': round(np.mean(returns) * 100, 4),
            'std_dev': round(np.std(returns) * 100, 4),
            'sharpe_ratio': round(np.mean(returns) / np.std(returns) * np.sqrt(252), 2) if np.std(returns) > 0 else 0,
            'max_drawdown': round(QuantitativeAnalysisTool._calculate_max_drawdown(prices_arr) * 100, 2)
        }

    @staticmethod
    def _calculate_max_drawdown(prices: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        peak = prices[0]
        max_dd = 0

        for price in prices:
            if price > peak:
                peak = price
            dd = (peak - price) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> Dict[str, float]:
        """Calculate volatility metrics"""
        if len(prices) < period:
            return {}

        returns = np.diff(prices) / prices[:-1]

        return {
            'daily_volatility': round(np.std(returns[-period:]) * 100, 4),
            'annualized_volatility': round(np.std(returns[-period:]) * np.sqrt(252) * 100, 2),
            'variance': round(np.var(returns[-period:]) * 10000, 6)
        }

    @staticmethod
    def calculate_correlation(prices1: List[float], prices2: List[float]) -> float:
        """Calculate correlation between two price series"""
        if len(prices1) != len(prices2) or len(prices1) < 2:
            return None

        returns1 = np.diff(prices1) / prices1[:-1]
        returns2 = np.diff(prices2) / prices2[:-1]

        return round(np.corrcoef(returns1, returns2)[0, 1], 4)

    @staticmethod
    def calculate_beta(asset_prices: List[float], market_prices: List[float]) -> float:
        """Calculate beta relative to market"""
        if len(asset_prices) != len(market_prices) or len(asset_prices) < 2:
            return None

        asset_returns = np.diff(asset_prices) / asset_prices[:-1]
        market_returns = np.diff(market_prices) / market_prices[:-1]

        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)

        return round(covariance / market_variance, 4) if market_variance > 0 else 1.0


class RiskAssessmentTool:
    """Tool for risk assessment and position sizing"""

    @staticmethod
    def calculate_position_size(
        account_balance: float,
        risk_percent: float,
        entry_price: float,
        stop_loss: float
    ) -> Dict[str, Any]:
        """Calculate position size based on risk management"""
        risk_amount = account_balance * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)

        if price_risk == 0:
            return {'error': 'Stop loss cannot equal entry price'}

        shares = int(risk_amount / price_risk)
        position_value = shares * entry_price

        return {
            'shares': shares,
            'position_value': round(position_value, 2),
            'risk_amount': round(risk_amount, 2),
            'max_loss': round(shares * price_risk, 2),
            'risk_reward_ratio': None  # Will be calculated with take profit
        }

    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if len(returns) < 10:
            return None

        returns_arr = np.array(returns)
        var = np.percentile(returns_arr, (1 - confidence) * 100)
        return round(var * 100, 4)

    @staticmethod
    def calculate_expected_value(
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> Dict[str, float]:
        """Calculate expected value of trading system"""
        ev = (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
        profit_factor = (win_rate * avg_win) / ((1 - win_rate) * abs(avg_loss)) if avg_loss != 0 else float('inf')

        return {
            'expected_value': round(ev, 4),
            'profit_factor': round(profit_factor, 4),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }


# ==============================================================================
# AGENT DEFINITIONS - ADK-Based Trading Agents
# ==============================================================================

class TextToSQLAgent:
    """
    Agent for converting natural language to SQL queries.
    Uses Gemini 2.5 for intelligent query parsing.
    """

    def __init__(self):
        self.bq_tool = BigQueryTool()
        if GENAI_AVAILABLE:
            self.client = genai.Client()
        else:
            self.client = None

        self.schema_context = self._build_schema_context()

    def _build_schema_context(self) -> str:
        """Build schema context for SQL generation"""
        return """
TABLES:
- v2_stocks_daily: Daily stock data (symbol, name, sector, close, percent_change, rsi, macd, adx, volume, week_52_high, week_52_low)
- v2_crypto_daily: Daily crypto data (symbol, name, close, percent_change, rsi, macd, volume)
- v2_forex_daily: Daily forex data (symbol, close, percent_change, rsi, atr)
- v2_etfs_daily: Daily ETF data (symbol, name, close, percent_change, rsi, volume)
- v2_indices_daily: Daily index data (symbol, name, close, percent_change, rsi)
- v2_commodities_daily: Daily commodity data (symbol, name, close, percent_change, rsi, atr)

KEY COLUMNS: symbol, name, datetime, open, high, low, close, volume, percent_change, rsi, macd, macd_signal, sma_20, sma_50, sma_200, adx, atr, bollinger_upper, bollinger_lower, week_52_high, week_52_low, sector

TRADING TERMS:
- oversold = RSI < 30
- overbought = RSI > 70
- strong trend = ADX > 25
- bullish MACD = MACD > MACD_SIGNAL
- breakout = close near week_52_high
"""

    def generate_sql(self, query: str, context: TradingContext = None) -> Dict[str, Any]:
        """Generate SQL from natural language"""
        if not self.client:
            return {'success': False, 'error': 'GenAI client not available'}

        context = context or TradingContext()

        prompt = f"""Generate BigQuery SQL for: "{query}"

{self.schema_context}

CONTEXT: asset_type={context.asset_type}, period={context.period}

RULES:
1. Use: `aialgotradehits.crypto_trading_data.table_name`
2. Include ORDER BY and LIMIT
3. SELECT only

SQL:"""

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(temperature=0.1)
            )
            sql = self._extract_sql(response.text)
            return {'success': True, 'sql': sql}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _extract_sql(self, text: str) -> str:
        """Extract SQL from response"""
        import re
        sql = re.sub(r'```sql?\n?', '', text)
        sql = re.sub(r'```', '', sql).strip()
        return sql

    def query(self, natural_language: str, context: TradingContext = None) -> Dict[str, Any]:
        """Full pipeline: generate and execute SQL"""
        result = self.generate_sql(natural_language, context)
        if not result['success']:
            return result

        execution = self.bq_tool.execute_sql(result['sql'])
        result['data'] = execution.get('data', [])
        result['count'] = execution.get('count', 0)
        return result


class MarketScannerAgent:
    """
    Agent for scanning markets and finding trading opportunities.
    """

    def __init__(self):
        self.bq_tool = BigQueryTool()

    def scan_gainers(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find top gainers"""
        table = f"v2_{asset_type}_daily"
        sql = f"""
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        )
        SELECT symbol, name, close, percent_change, volume, rsi
        FROM latest WHERE rn = 1
        ORDER BY percent_change DESC NULLS LAST
        LIMIT {limit}
        """
        result = self.bq_tool.execute_sql(sql)
        return result.get('data', [])

    def scan_losers(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find top losers"""
        table = f"v2_{asset_type}_daily"
        sql = f"""
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        )
        SELECT symbol, name, close, percent_change, volume, rsi
        FROM latest WHERE rn = 1
        ORDER BY percent_change ASC NULLS LAST
        LIMIT {limit}
        """
        result = self.bq_tool.execute_sql(sql)
        return result.get('data', [])

    def scan_oversold(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find oversold assets (RSI < 30)"""
        table = f"v2_{asset_type}_daily"
        sql = f"""
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        )
        SELECT symbol, name, close, percent_change, rsi, macd, adx
        FROM latest WHERE rn = 1 AND rsi < 30 AND rsi IS NOT NULL
        ORDER BY rsi ASC
        LIMIT {limit}
        """
        result = self.bq_tool.execute_sql(sql)
        return result.get('data', [])

    def scan_breakouts(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find assets breaking 52-week highs"""
        table = f"v2_{asset_type}_daily"
        sql = f"""
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        )
        SELECT symbol, name, close, percent_change, week_52_high,
               ROUND(close / week_52_high * 100, 2) as pct_of_high, volume, rsi
        FROM latest
        WHERE rn = 1 AND close >= week_52_high * 0.95 AND week_52_high IS NOT NULL
        ORDER BY pct_of_high DESC
        LIMIT {limit}
        """
        result = self.bq_tool.execute_sql(sql)
        return result.get('data', [])

    def scan_strong_trends(self, asset_type: str = 'stocks', limit: int = 20) -> List[Dict]:
        """Find assets with strong trends (ADX > 25)"""
        table = f"v2_{asset_type}_daily"
        sql = f"""
        WITH latest AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        )
        SELECT symbol, name, close, percent_change, adx, macd, rsi
        FROM latest
        WHERE rn = 1 AND adx > 25 AND adx IS NOT NULL
        ORDER BY adx DESC
        LIMIT {limit}
        """
        result = self.bq_tool.execute_sql(sql)
        return result.get('data', [])


class TechnicalAnalysisAgent:
    """
    Agent for technical analysis calculations.
    """

    def __init__(self):
        self.bq_tool = BigQueryTool()
        self.ta_tool = TechnicalAnalysisTool()

    def analyze_symbol(self, symbol: str, asset_type: str = 'stocks') -> Dict[str, Any]:
        """Perform comprehensive technical analysis on a symbol"""
        table = f"v2_{asset_type}_daily"

        # Get historical data
        sql = f"""
        SELECT datetime, open, high, low, close, volume,
               rsi, macd, macd_signal, adx, atr, sma_20, sma_50, sma_200,
               bollinger_upper, bollinger_middle, bollinger_lower
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT 200
        """

        result = self.bq_tool.execute_sql(sql)
        if not result.get('data'):
            return {'error': f'No data found for {symbol}'}

        data = result['data']
        closes = [float(d['close']) for d in reversed(data) if d.get('close')]
        highs = [float(d['high']) for d in reversed(data) if d.get('high')]
        lows = [float(d['low']) for d in reversed(data) if d.get('low')]

        latest = data[0]

        # Calculate indicators
        analysis = {
            'symbol': symbol,
            'current_price': latest.get('close'),
            'rsi': latest.get('rsi'),
            'macd': {
                'value': latest.get('macd'),
                'signal': latest.get('macd_signal'),
                'histogram': latest.get('macd') - latest.get('macd_signal') if latest.get('macd') and latest.get('macd_signal') else None
            },
            'adx': latest.get('adx'),
            'atr': latest.get('atr'),
            'moving_averages': {
                'sma_20': latest.get('sma_20'),
                'sma_50': latest.get('sma_50'),
                'sma_200': latest.get('sma_200')
            },
            'bollinger_bands': {
                'upper': latest.get('bollinger_upper'),
                'middle': latest.get('bollinger_middle'),
                'lower': latest.get('bollinger_lower')
            },
            'trend': self.ta_tool.detect_trend(closes),
            'signals': self._generate_signals(latest, closes)
        }

        return analysis

    def _generate_signals(self, latest: Dict, closes: List[float]) -> List[str]:
        """Generate trading signals based on indicators"""
        signals = []

        rsi = latest.get('rsi')
        if rsi:
            if rsi < 30:
                signals.append('OVERSOLD - Potential buy signal')
            elif rsi > 70:
                signals.append('OVERBOUGHT - Potential sell signal')

        macd = latest.get('macd')
        macd_signal = latest.get('macd_signal')
        if macd and macd_signal:
            if macd > macd_signal and macd > 0:
                signals.append('BULLISH MACD - Upward momentum')
            elif macd < macd_signal:
                signals.append('BEARISH MACD - Downward momentum')

        adx = latest.get('adx')
        if adx and adx > 25:
            signals.append(f'STRONG TREND - ADX at {adx:.1f}')

        price = latest.get('close')
        bb_lower = latest.get('bollinger_lower')
        bb_upper = latest.get('bollinger_upper')
        if price and bb_lower and bb_upper:
            if price < bb_lower:
                signals.append('BELOW LOWER BOLLINGER - Oversold')
            elif price > bb_upper:
                signals.append('ABOVE UPPER BOLLINGER - Overbought')

        return signals


class QuantitativeAnalysisAgent:
    """
    Agent for quantitative analysis and statistical computations.
    """

    def __init__(self):
        self.bq_tool = BigQueryTool()
        self.quant_tool = QuantitativeAnalysisTool()

    def analyze_returns(self, symbol: str, asset_type: str = 'stocks', period: int = 100) -> Dict[str, Any]:
        """Analyze returns for a symbol"""
        table = f"v2_{asset_type}_daily"
        sql = f"""
        SELECT close FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {period}
        """

        result = self.bq_tool.execute_sql(sql)
        if not result.get('data'):
            return {'error': f'No data for {symbol}'}

        prices = [float(d['close']) for d in reversed(result['data'])]

        return {
            'symbol': symbol,
            'period': len(prices),
            'returns': self.quant_tool.calculate_returns(prices),
            'volatility': self.quant_tool.calculate_volatility(prices)
        }

    def calculate_correlation_matrix(self, symbols: List[str], asset_type: str = 'stocks') -> Dict[str, Any]:
        """Calculate correlation matrix for multiple symbols"""
        table = f"v2_{asset_type}_daily"

        # Get data for all symbols
        prices_data = {}
        for symbol in symbols:
            sql = f"""
            SELECT close FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE symbol = '{symbol}'
            ORDER BY datetime DESC
            LIMIT 100
            """
            result = self.bq_tool.execute_sql(sql)
            if result.get('data'):
                prices_data[symbol] = [float(d['close']) for d in reversed(result['data'])]

        # Calculate correlations
        correlations = {}
        for i, sym1 in enumerate(symbols):
            if sym1 not in prices_data:
                continue
            correlations[sym1] = {}
            for sym2 in symbols:
                if sym2 not in prices_data:
                    continue
                corr = self.quant_tool.calculate_correlation(prices_data[sym1], prices_data[sym2])
                correlations[sym1][sym2] = corr

        return {'symbols': symbols, 'correlations': correlations}


# ==============================================================================
# MASTER ORCHESTRATOR - Coordinates All Agents
# ==============================================================================

class TradingOrchestrator:
    """
    Master orchestrator that coordinates all trading agents.
    """

    def __init__(self):
        self.text_to_sql = TextToSQLAgent()
        self.scanner = MarketScannerAgent()
        self.technical = TechnicalAnalysisAgent()
        self.quant = QuantitativeAnalysisAgent()
        self.risk = RiskAssessmentTool()

        if GENAI_AVAILABLE:
            self.gemini = genai.Client()
        else:
            self.gemini = None

    def process_query(self, query: str, context: TradingContext = None) -> Dict[str, Any]:
        """
        Process a user query through the appropriate agents.
        """
        context = context or TradingContext()
        query_lower = query.lower()

        # Route based on query intent
        if any(word in query_lower for word in ['sql', 'query', 'select', 'from']):
            # Direct SQL generation
            return self.text_to_sql.query(query, context)

        elif any(word in query_lower for word in ['gainers', 'winners', 'top performers']):
            return {
                'type': 'scan',
                'scan_type': 'gainers',
                'data': self.scanner.scan_gainers(context.asset_type)
            }

        elif any(word in query_lower for word in ['losers', 'decliners', 'worst']):
            return {
                'type': 'scan',
                'scan_type': 'losers',
                'data': self.scanner.scan_losers(context.asset_type)
            }

        elif any(word in query_lower for word in ['oversold', 'rsi below', 'undervalued']):
            return {
                'type': 'scan',
                'scan_type': 'oversold',
                'data': self.scanner.scan_oversold(context.asset_type)
            }

        elif any(word in query_lower for word in ['breakout', '52 week', 'new high']):
            return {
                'type': 'scan',
                'scan_type': 'breakouts',
                'data': self.scanner.scan_breakouts(context.asset_type)
            }

        elif any(word in query_lower for word in ['analyze', 'technical', 'indicators']):
            # Extract symbol
            import re
            symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
            if symbols:
                return {
                    'type': 'technical_analysis',
                    'data': self.technical.analyze_symbol(symbols[0], context.asset_type)
                }

        elif any(word in query_lower for word in ['correlation', 'compare', 'relationship']):
            import re
            symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
            if len(symbols) >= 2:
                return {
                    'type': 'correlation',
                    'data': self.quant.calculate_correlation_matrix(symbols, context.asset_type)
                }

        # Default: use Text-to-SQL
        return self.text_to_sql.query(query, context)


# ==============================================================================
# MAIN - Interactive CLI
# ==============================================================================

def main():
    """Interactive CLI for testing the trading agents"""

    print("=" * 70)
    print("AIAlgoTradeHits ADK Trading Agent System")
    print("=" * 70)
    print("\nAgents Available:")
    print("  1. Text-to-SQL Agent - Convert natural language to SQL")
    print("  2. Market Scanner Agent - Scan for trading opportunities")
    print("  3. Technical Analysis Agent - Analyze indicators")
    print("  4. Quantitative Analysis Agent - Statistical analysis")
    print("\nExample queries:")
    print("  - 'Show me oversold tech stocks'")
    print("  - 'Top 10 crypto gainers'")
    print("  - 'Analyze AAPL technical indicators'")
    print("  - 'Calculate correlation between AAPL MSFT GOOGL'")
    print("\nType 'quit' to exit\n")

    orchestrator = TradingOrchestrator()

    while True:
        try:
            query = input("Query> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if not query:
                continue

            print("\nProcessing...")
            result = orchestrator.process_query(query)

            if result.get('success') or result.get('data'):
                if 'sql' in result:
                    print(f"\nSQL: {result['sql'][:200]}...")
                if 'data' in result:
                    data = result['data']
                    if isinstance(data, list):
                        print(f"\nResults ({len(data)} items):")
                        for item in data[:5]:
                            if isinstance(item, dict):
                                symbol = item.get('symbol', 'N/A')
                                price = item.get('close', item.get('current_price', 'N/A'))
                                change = item.get('percent_change', 'N/A')
                                print(f"  {symbol}: ${price} ({change}%)")
                    else:
                        print(f"\n{json.dumps(data, indent=2, default=str)[:500]}...")
            else:
                print(f"\nError: {result.get('error', 'Unknown error')}")

            print()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
