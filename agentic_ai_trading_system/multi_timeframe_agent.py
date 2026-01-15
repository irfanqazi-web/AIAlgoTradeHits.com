"""
Multi-Timeframe Agentic AI Trading System
=========================================

Architecture:
- DailyScreenerAgent: Identifies high Growth Score opportunities
- HourlyCycleAgent: Detects EMA 12/26 rise/fall cycles
- ExecutionAgent: Monitors 5-min for optimal entry/exit
- OrchestratorAgent: Coordinates all agents and generates signals

Based on validated XGBoost model with 68.5% UP accuracy
Key Features: Pivot flags (100% in top 3), Growth Score, EMA Cycles
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from google.cloud import bigquery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

class Signal(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class Action(Enum):
    EXECUTE_BUY = "EXECUTE_BUY"
    PREPARE_BUY = "PREPARE_BUY"
    MONITOR = "MONITOR"
    PREPARE_SELL = "PREPARE_SELL"
    EXECUTE_SELL = "EXECUTE_SELL"
    STAY_OUT = "STAY_OUT"

@dataclass
class TradeSignal:
    symbol: str
    timeframe: str
    signal: Signal
    strength: float  # 0-100
    confidence: float  # 0-1
    factors: List[str]
    metrics: Dict[str, Any]
    timestamp: str

    def to_dict(self):
        return {
            **asdict(self),
            'signal': self.signal.value,
        }

@dataclass
class CombinedSignal:
    symbol: str
    daily_signal: Optional[TradeSignal]
    hourly_signal: Optional[TradeSignal]
    fivemin_signal: Optional[TradeSignal]
    combined_strength: float
    recommendation: Signal
    action: Action
    alignment: Dict[str, bool]
    factors: List[str]
    timestamp: str

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'daily_signal': self.daily_signal.to_dict() if self.daily_signal else None,
            'hourly_signal': self.hourly_signal.to_dict() if self.hourly_signal else None,
            'fivemin_signal': self.fivemin_signal.to_dict() if self.fivemin_signal else None,
            'combined_strength': self.combined_strength,
            'recommendation': self.recommendation.value,
            'action': self.action.value,
            'alignment': self.alignment,
            'factors': self.factors,
            'timestamp': self.timestamp
        }

# =============================================================================
# BASE AGENT CLASS
# =============================================================================

class BaseAgent:
    """Base class for all trading agents"""

    def __init__(self, name: str):
        self.name = name
        self.client = bigquery.Client(project=PROJECT_ID)
        self.logger = logging.getLogger(f"Agent.{name}")

    async def fetch_data(self, table: str, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Fetch data from BigQuery"""
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE symbol = @symbol
        ORDER BY datetime DESC
        LIMIT @limit
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )

        try:
            df = self.client.query(query, job_config=job_config).to_dataframe()
            return df.sort_values('datetime', ascending=True).reset_index(drop=True)
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()

    def calculate_signal_strength(self, factors: List[Tuple[str, float]]) -> float:
        """Calculate overall signal strength from factors"""
        if not factors:
            return 50.0

        total = sum(weight for _, weight in factors)
        return min(max(total, 0), 100)

    def determine_signal(self, strength: float) -> Signal:
        """Determine signal type from strength"""
        if strength >= 80:
            return Signal.STRONG_BUY
        elif strength >= 60:
            return Signal.BUY
        elif strength >= 40:
            return Signal.HOLD
        elif strength >= 20:
            return Signal.SELL
        else:
            return Signal.STRONG_SELL

# =============================================================================
# DAILY SCREENER AGENT
# =============================================================================

class DailyScreenerAgent(BaseAgent):
    """
    Agent responsible for daily opportunity screening

    Strategy:
    1. Look for Growth Score >= 75 (validated 68.5% UP accuracy)
    2. RSI between 40-65 (sweet spot per validation)
    3. MACD histogram positive
    4. Price above SMA 200 (trend confirmation)
    5. Watch for pivot_low_flag signals (100% in top 3 features)
    """

    def __init__(self):
        super().__init__("DailyScreener")

    async def analyze(self, symbol: str) -> Optional[TradeSignal]:
        """Analyze daily data for trading opportunity"""

        df = await self.fetch_data('stocks_daily_clean', symbol, 100)

        if df.empty or len(df) < 2:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        factors = []
        factor_details = []

        # 1. Growth Score (40 points max - most important per validation)
        growth_score = float(latest.get('growth_score', 0) or 0)
        if growth_score >= 75:
            factors.append(("growth_score_high", 40))
            factor_details.append(f"Growth Score {growth_score:.0f} (EXCELLENT)")
        elif growth_score >= 50:
            factors.append(("growth_score_medium", 25))
            factor_details.append(f"Growth Score {growth_score:.0f} (GOOD)")
        elif growth_score >= 25:
            factors.append(("growth_score_low", 10))
            factor_details.append(f"Growth Score {growth_score:.0f} (FAIR)")

        # 2. RSI Sweet Spot (20 points)
        rsi = float(latest.get('rsi', latest.get('rsi_14', 50)) or 50)
        if 40 <= rsi <= 65:
            factors.append(("rsi_sweet_spot", 20))
            factor_details.append(f"RSI {rsi:.1f} (Sweet Spot)")
        elif rsi < 30:
            factors.append(("rsi_oversold", 15))
            factor_details.append(f"RSI {rsi:.1f} (Oversold)")
        elif rsi > 70:
            factors.append(("rsi_overbought", -10))
            factor_details.append(f"RSI {rsi:.1f} (Overbought)")

        # 3. MACD Histogram (15 points)
        macd_hist = float(latest.get('macd_histogram', latest.get('macd_hist', 0)) or 0)
        if macd_hist > 0:
            factors.append(("macd_bullish", 15))
            factor_details.append("MACD Histogram Positive")
        elif macd_hist < 0:
            factors.append(("macd_bearish", -10))
            factor_details.append("MACD Histogram Negative")

        # 4. EMA Rise Cycle (15 points)
        ema_12 = float(latest.get('ema_12', 0) or 0)
        ema_26 = float(latest.get('ema_26', 0) or 0)
        if ema_12 > 0 and ema_26 > 0:
            if ema_12 > ema_26:
                factors.append(("ema_rise_cycle", 15))
                factor_details.append("EMA 12/26 Rise Cycle")
            else:
                factors.append(("ema_fall_cycle", -10))
                factor_details.append("EMA 12/26 Fall Cycle")

        # 5. Pivot Low Flag (10 points - KEY FEATURE per validation)
        pivot_low = int(latest.get('pivot_low_flag', 0) or 0)
        if pivot_low == 1:
            factors.append(("pivot_low", 10))
            factor_details.append("PIVOT LOW SIGNAL!")

        # 6. Above SMA 200 (bonus confirmation)
        close = float(latest.get('close', 0) or 0)
        sma_200 = float(latest.get('sma_200', 0) or 0)
        if close > 0 and sma_200 > 0 and close > sma_200:
            factors.append(("above_sma200", 5))
            factor_details.append("Above 200 SMA")

        # Calculate final strength
        strength = self.calculate_signal_strength(factors)
        signal = self.determine_signal(strength)

        # Calculate confidence based on factor count
        confidence = min(len([f for f in factors if f[1] > 0]) / 6.0, 1.0)

        return TradeSignal(
            symbol=symbol,
            timeframe="daily",
            signal=signal,
            strength=strength,
            confidence=confidence,
            factors=factor_details,
            metrics={
                'growth_score': growth_score,
                'rsi': rsi,
                'macd_histogram': macd_hist,
                'ema_12': ema_12,
                'ema_26': ema_26,
                'in_rise_cycle': ema_12 > ema_26 if ema_12 > 0 and ema_26 > 0 else False,
                'pivot_low': pivot_low == 1,
                'close': close,
                'sma_200': sma_200
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )

# =============================================================================
# HOURLY CYCLE AGENT
# =============================================================================

class HourlyCycleAgent(BaseAgent):
    """
    Agent responsible for hourly cycle detection

    Strategy:
    1. Detect EMA 12/26 crossovers (rise cycle start)
    2. Confirm with volume spike (1.5x average)
    3. RSI momentum above 50
    4. MACD acceleration
    """

    def __init__(self):
        super().__init__("HourlyCycle")

    async def analyze(self, symbol: str) -> Optional[TradeSignal]:
        """Analyze hourly data for cycle timing"""

        df = await self.fetch_data('stocks_hourly_clean', symbol, 100)

        if df.empty or len(df) < 3:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        prev2 = df.iloc[-3]

        factors = []
        factor_details = []

        # 1. EMA Cycle Detection (30 points)
        ema_12 = float(latest.get('ema_12', 0) or 0)
        ema_26 = float(latest.get('ema_26', 0) or 0)
        prev_ema_12 = float(prev.get('ema_12', 0) or 0)
        prev_ema_26 = float(prev.get('ema_26', 0) or 0)

        in_rise_cycle = ema_12 > ema_26 if ema_12 > 0 and ema_26 > 0 else False
        rise_cycle_start = in_rise_cycle and prev_ema_12 <= prev_ema_26
        fall_cycle_start = not in_rise_cycle and prev_ema_12 >= prev_ema_26

        if rise_cycle_start:
            factors.append(("rise_cycle_start", 30))
            factor_details.append("RISE CYCLE START!")
        elif in_rise_cycle:
            factors.append(("in_rise_cycle", 15))
            factor_details.append("In Rise Cycle")
        elif fall_cycle_start:
            factors.append(("fall_cycle_start", -30))
            factor_details.append("Fall Cycle Start")
        else:
            factors.append(("in_fall_cycle", -15))
            factor_details.append("In Fall Cycle")

        # 2. Volume Spike (10 points)
        volume = float(latest.get('volume', 0) or 0)
        avg_volume = df['volume'].tail(20).mean() if 'volume' in df.columns else 0
        volume_spike = volume > avg_volume * 1.5 if avg_volume > 0 else False

        if volume_spike and in_rise_cycle:
            factors.append(("volume_spike", 10))
            factor_details.append("Volume Spike (1.5x)")

        # 3. RSI Momentum (15 points)
        rsi = float(latest.get('rsi', latest.get('rsi_14', 50)) or 50)
        if 50 < rsi < 70:
            factors.append(("rsi_bullish", 15))
            factor_details.append(f"RSI Bullish ({rsi:.1f})")
        elif rsi < 30:
            factors.append(("rsi_oversold", 10))
            factor_details.append(f"RSI Oversold ({rsi:.1f})")
        elif rsi > 70:
            factors.append(("rsi_overbought", -15))
            factor_details.append(f"RSI Overbought ({rsi:.1f})")

        # 4. MACD Acceleration (10 points)
        macd_hist = float(latest.get('macd_histogram', latest.get('macd_hist', 0)) or 0)
        prev_macd_hist = float(prev.get('macd_histogram', prev.get('macd_hist', 0)) or 0)

        if macd_hist > 0 and macd_hist > prev_macd_hist:
            factors.append(("macd_accelerating", 10))
            factor_details.append("MACD Accelerating")
        elif macd_hist > 0:
            factors.append(("macd_positive", 5))
            factor_details.append("MACD Positive")

        # Calculate final strength (start from 50 for neutral)
        base_strength = 50
        strength = base_strength + sum(weight for _, weight in factors)
        strength = min(max(strength, 0), 100)
        signal = self.determine_signal(strength)

        confidence = 0.7 if rise_cycle_start else 0.5

        return TradeSignal(
            symbol=symbol,
            timeframe="hourly",
            signal=signal,
            strength=strength,
            confidence=confidence,
            factors=factor_details,
            metrics={
                'ema_12': ema_12,
                'ema_26': ema_26,
                'in_rise_cycle': in_rise_cycle,
                'rise_cycle_start': rise_cycle_start,
                'fall_cycle_start': fall_cycle_start,
                'rsi': rsi,
                'volume_spike': volume_spike,
                'macd_histogram': macd_hist,
                'close': float(latest.get('close', 0) or 0)
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )

# =============================================================================
# EXECUTION AGENT (5-MINUTE)
# =============================================================================

class ExecutionAgent(BaseAgent):
    """
    Agent responsible for 5-minute execution timing

    Strategy:
    1. Wait for micro EMA crossover (9/21)
    2. Enter when RSI oversold (30-35)
    3. Buy below VWAP for value
    4. Exit on overbought RSI (65+)
    """

    def __init__(self):
        super().__init__("Execution")

    async def analyze(self, symbol: str) -> Optional[TradeSignal]:
        """Analyze 5-minute data for execution timing"""

        df = await self.fetch_data('stocks_5min_clean', symbol, 100)

        if df.empty or len(df) < 5:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        factors = []
        factor_details = []
        entry_signal = None

        # Calculate short-term EMAs if not present
        if 'ema_9' not in df.columns:
            df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        if 'ema_21' not in df.columns:
            df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 1. Micro EMA Cross (25 points)
        ema_9 = float(latest.get('ema_9', latest.get('ema_12', latest['close'])))
        ema_21 = float(latest.get('ema_21', latest.get('ema_26', latest['close'])))
        prev_ema_9 = float(prev.get('ema_9', prev.get('ema_12', prev['close'])))
        prev_ema_21 = float(prev.get('ema_21', prev.get('ema_26', prev['close'])))

        micro_trend_up = ema_9 > ema_21
        micro_cross_up = micro_trend_up and prev_ema_9 <= prev_ema_21
        micro_cross_down = not micro_trend_up and prev_ema_9 >= prev_ema_21

        if micro_cross_up:
            factors.append(("micro_cross_up", 25))
            factor_details.append("MICRO BUY SIGNAL!")
            entry_signal = "BUY_NOW"
        elif micro_cross_down:
            factors.append(("micro_cross_down", -25))
            factor_details.append("MICRO SELL SIGNAL!")
            entry_signal = "SELL_NOW"
        elif micro_trend_up:
            factors.append(("micro_uptrend", 10))
            factor_details.append("Micro Uptrend")
        else:
            factors.append(("micro_downtrend", -10))
            factor_details.append("Micro Downtrend")

        # 2. RSI Timing (15 points)
        rsi = float(latest.get('rsi', latest.get('rsi_14', 50)) or 50)
        if rsi < 35:
            factors.append(("rsi_oversold_entry", 15))
            factor_details.append(f"Oversold Entry ({rsi:.1f})")
            if not entry_signal:
                entry_signal = "CONSIDER_BUY"
        elif rsi > 65:
            factors.append(("rsi_overbought_exit", -15))
            factor_details.append(f"Overbought Exit ({rsi:.1f})")
            if not entry_signal:
                entry_signal = "CONSIDER_SELL"

        # 3. VWAP Position (10 points)
        close = float(latest.get('close', 0) or 0)
        vwap = float(latest.get('vwap_daily', latest.get('vwap', 0)) or 0)

        if vwap > 0 and close > 0:
            price_vs_vwap = (close / vwap - 1) * 100
            if price_vs_vwap < -0.5:
                factors.append(("below_vwap", 10))
                factor_details.append(f"Below VWAP ({price_vs_vwap:.2f}%)")
            elif price_vs_vwap > 0.5:
                factors.append(("above_vwap", -5))
                factor_details.append(f"Above VWAP ({price_vs_vwap:.2f}%)")
        else:
            price_vs_vwap = 0

        # Calculate final strength
        base_strength = 50
        strength = base_strength + sum(weight for _, weight in factors)
        strength = min(max(strength, 0), 100)
        signal = self.determine_signal(strength)

        confidence = 0.8 if entry_signal in ["BUY_NOW", "SELL_NOW"] else 0.5

        return TradeSignal(
            symbol=symbol,
            timeframe="5min",
            signal=signal,
            strength=strength,
            confidence=confidence,
            factors=factor_details,
            metrics={
                'micro_trend_up': micro_trend_up,
                'micro_cross_up': micro_cross_up,
                'micro_cross_down': micro_cross_down,
                'rsi': rsi,
                'price_vs_vwap': price_vs_vwap,
                'close': close,
                'vwap': vwap,
                'entry_signal': entry_signal
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )

# =============================================================================
# ORCHESTRATOR AGENT
# =============================================================================

class OrchestratorAgent(BaseAgent):
    """
    Master agent that coordinates all sub-agents and generates final signals

    Weighting:
    - Daily: 50% (identifies opportunity)
    - Hourly: 30% (timing the entry)
    - 5-Minute: 20% (execution precision)
    """

    def __init__(self):
        super().__init__("Orchestrator")
        self.daily_agent = DailyScreenerAgent()
        self.hourly_agent = HourlyCycleAgent()
        self.execution_agent = ExecutionAgent()

    async def analyze_symbol(self, symbol: str) -> CombinedSignal:
        """Run full multi-timeframe analysis on a symbol"""

        # Run all agents in parallel
        daily_signal, hourly_signal, fivemin_signal = await asyncio.gather(
            self.daily_agent.analyze(symbol),
            self.hourly_agent.analyze(symbol),
            self.execution_agent.analyze(symbol)
        )

        # Weight the signals
        weights = {'daily': 0.5, 'hourly': 0.3, 'fivemin': 0.2}

        total_strength = 0
        active_timeframes = 0
        factors = []

        if daily_signal:
            total_strength += daily_signal.strength * weights['daily']
            active_timeframes += 1
            if daily_signal.signal in [Signal.STRONG_BUY, Signal.BUY]:
                factors.append(f"Daily: {daily_signal.factors[0] if daily_signal.factors else 'Bullish'}")

        if hourly_signal:
            total_strength += hourly_signal.strength * weights['hourly']
            active_timeframes += 1
            if hourly_signal.metrics.get('rise_cycle_start'):
                factors.append("Hourly: Rise Cycle Start!")

        if fivemin_signal:
            total_strength += fivemin_signal.strength * weights['fivemin']
            active_timeframes += 1
            if fivemin_signal.metrics.get('entry_signal') == 'BUY_NOW':
                factors.append("5min: Buy Signal Active!")

        # Calculate combined strength
        combined_strength = total_strength / active_timeframes if active_timeframes > 0 else 50

        # Check alignment
        daily_bullish = daily_signal and daily_signal.signal in [Signal.STRONG_BUY, Signal.BUY]
        hourly_bullish = hourly_signal and hourly_signal.signal in [Signal.STRONG_BUY, Signal.BUY]
        fivemin_bullish = fivemin_signal and fivemin_signal.signal in [Signal.STRONG_BUY, Signal.BUY]
        all_aligned = daily_bullish and hourly_bullish and fivemin_bullish

        # Determine final recommendation and action
        if all_aligned and combined_strength >= 60:
            recommendation = Signal.STRONG_BUY
            action = Action.EXECUTE_BUY
            factors.append("ALL TIMEFRAMES ALIGNED!")
        elif daily_bullish and hourly_bullish and combined_strength >= 55:
            recommendation = Signal.BUY
            action = Action.PREPARE_BUY
        elif combined_strength >= 45:
            recommendation = Signal.HOLD
            action = Action.MONITOR
        elif combined_strength >= 35:
            recommendation = Signal.SELL
            action = Action.PREPARE_SELL
        else:
            recommendation = Signal.STRONG_SELL
            action = Action.STAY_OUT

        return CombinedSignal(
            symbol=symbol,
            daily_signal=daily_signal,
            hourly_signal=hourly_signal,
            fivemin_signal=fivemin_signal,
            combined_strength=combined_strength,
            recommendation=recommendation,
            action=action,
            alignment={
                'daily': daily_bullish,
                'hourly': hourly_bullish,
                'fivemin': fivemin_bullish,
                'all_aligned': all_aligned
            },
            factors=factors,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    async def screen_hot_stocks(self, min_growth_score: int = 50, limit: int = 20) -> List[Dict]:
        """Screen for high growth score opportunities"""

        query = f"""
        SELECT
            symbol,
            growth_score,
            rsi,
            macd_histogram,
            ema_12,
            ema_26,
            close,
            volume,
            pivot_low_flag,
            pivot_high_flag,
            sentiment_score,
            recommendation
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
          AND growth_score >= @min_score
        ORDER BY growth_score DESC, datetime DESC
        LIMIT @limit
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("min_score", "INT64", min_growth_score),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )

        try:
            df = self.client.query(query, job_config=job_config).to_dataframe()
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error screening stocks: {e}")
            return []

    async def run_full_analysis(self, symbols: List[str] = None) -> Dict[str, CombinedSignal]:
        """Run full analysis on multiple symbols"""

        if symbols is None:
            # Get hot stocks
            hot_stocks = await self.screen_hot_stocks()
            symbols = list(set([s['symbol'] for s in hot_stocks]))[:10]

        results = {}

        for symbol in symbols:
            try:
                signal = await self.analyze_symbol(symbol)
                results[symbol] = signal
                self.logger.info(f"{symbol}: {signal.recommendation.value} ({signal.combined_strength:.1f}%)")
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")

        return results

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for the Agentic AI Trading System"""

    print("=" * 80)
    print("AGENTIC AI MULTI-TIMEFRAME TRADING SYSTEM")
    print("=" * 80)
    print()

    orchestrator = OrchestratorAgent()

    # Test with SPY
    print("Analyzing SPY across all timeframes...")
    signal = await orchestrator.analyze_symbol("SPY")

    print(f"\nSPY Combined Signal:")
    print(f"  Recommendation: {signal.recommendation.value}")
    print(f"  Action: {signal.action.value}")
    print(f"  Strength: {signal.combined_strength:.1f}%")
    print(f"  Alignment: Daily={signal.alignment['daily']}, Hourly={signal.alignment['hourly']}, 5min={signal.alignment['fivemin']}")
    print(f"  Factors: {', '.join(signal.factors)}")

    # Screen hot stocks
    print("\n\nScreening for hot stocks (Growth Score >= 50)...")
    hot_stocks = await orchestrator.screen_hot_stocks(min_growth_score=50, limit=10)

    print(f"\nFound {len(hot_stocks)} hot stocks:")
    for stock in hot_stocks[:5]:
        print(f"  {stock['symbol']}: GS={stock['growth_score']}, RSI={stock.get('rsi', 'N/A')}")

    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
