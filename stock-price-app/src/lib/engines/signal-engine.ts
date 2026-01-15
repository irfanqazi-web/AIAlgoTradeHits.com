/**
 * SIGNAL ENGINE - Pure Calculation Functions
 * Trade signal generation and classification
 *
 * No side effects, no I/O, just math
 * @version 3.0.0
 */

import {
  TREND_REGIMES,
  EMA_CYCLES,
  RECOMMENDATIONS,
  INDICATOR_THRESHOLDS,
} from '@/lib/config/trading-config';
import type {
  TrendRegime,
  Recommendation,
  CandleWithIndicators,
  TradingSignal,
} from '@/types';

// ============================================================================
// § 1. TREND REGIME CLASSIFICATION
// ============================================================================

/**
 * Classify trend regime based on price and MAs
 * Pure function - no side effects
 */
export function classifyTrendRegime(
  close: number,
  sma50: number,
  sma200: number,
  adx: number
): TrendRegime {
  // Strong Uptrend: close > sma50, sma50 > sma200, adx > 25
  if (close > sma50 && sma50 > sma200 && adx > INDICATOR_THRESHOLDS.ADX.strong) {
    return "STRONG_UPTREND";
  }

  // Weak Uptrend: close > sma50 AND close > sma200
  if (close > sma50 && close > sma200) {
    return "WEAK_UPTREND";
  }

  // Strong Downtrend: close < sma50, sma50 < sma200, adx > 25
  if (close < sma50 && sma50 < sma200 && adx > INDICATOR_THRESHOLDS.ADX.strong) {
    return "STRONG_DOWNTREND";
  }

  // Weak Downtrend: close < sma50 AND close < sma200
  if (close < sma50 && close < sma200) {
    return "WEAK_DOWNTREND";
  }

  // Default: Consolidation
  return "CONSOLIDATION";
}

/**
 * Get trend regime details
 */
export function getTrendRegimeDetails(regime: TrendRegime) {
  return TREND_REGIMES[regime];
}

// ============================================================================
// § 2. EMA CYCLE DETECTION
// ============================================================================

/**
 * Detect if price is in rise cycle (EMA12 > EMA26)
 */
export function isInRiseCycle(ema12: number, ema26: number): boolean {
  return ema12 > ema26;
}

/**
 * Detect rise cycle start (crossover)
 */
export function isRiseCycleStart(
  currentEma12: number,
  currentEma26: number,
  prevEma12: number,
  prevEma26: number
): boolean {
  return currentEma12 > currentEma26 && prevEma12 <= prevEma26;
}

/**
 * Detect fall cycle start (crossunder)
 */
export function isFallCycleStart(
  currentEma12: number,
  currentEma26: number,
  prevEma12: number,
  prevEma26: number
): boolean {
  return currentEma12 < currentEma26 && prevEma12 >= prevEma26;
}

/**
 * Get EMA cycle status
 */
export function getEmaCycleStatus(
  currentEma12: number,
  currentEma26: number,
  prevEma12?: number,
  prevEma26?: number
): {
  inRiseCycle: boolean;
  cycleStart: "rise" | "fall" | null;
  signal: "BULLISH" | "BEARISH";
} {
  const inRiseCycle = isInRiseCycle(currentEma12, currentEma26);

  let cycleStart: "rise" | "fall" | null = null;
  if (prevEma12 !== undefined && prevEma26 !== undefined) {
    if (isRiseCycleStart(currentEma12, currentEma26, prevEma12, prevEma26)) {
      cycleStart = "rise";
    } else if (isFallCycleStart(currentEma12, currentEma26, prevEma12, prevEma26)) {
      cycleStart = "fall";
    }
  }

  return {
    inRiseCycle,
    cycleStart,
    signal: inRiseCycle ? "BULLISH" : "BEARISH",
  };
}

// ============================================================================
// § 3. RECOMMENDATION GENERATION
// ============================================================================

/**
 * Generate trade recommendation based on indicators
 * Pure function - no side effects
 */
export function generateRecommendation(data: {
  trendRegime: TrendRegime;
  rsi?: number;
  macdHistogram?: number;
  inRiseCycle?: boolean;
  growthScore?: number;
}): Recommendation {
  // Count bullish/bearish signals
  let bullishSignals = 0;
  let bearishSignals = 0;

  // Trend regime
  if (data.trendRegime === "STRONG_UPTREND") bullishSignals += 2;
  else if (data.trendRegime === "WEAK_UPTREND") bullishSignals += 1;
  else if (data.trendRegime === "STRONG_DOWNTREND") bearishSignals += 2;
  else if (data.trendRegime === "WEAK_DOWNTREND") bearishSignals += 1;

  // RSI
  if (data.rsi !== undefined) {
    if (data.rsi <= INDICATOR_THRESHOLDS.RSI.oversold) bullishSignals += 1;
    else if (data.rsi >= INDICATOR_THRESHOLDS.RSI.overbought) bearishSignals += 1;
  }

  // MACD
  if (data.macdHistogram !== undefined) {
    if (data.macdHistogram > 0) bullishSignals += 1;
    else if (data.macdHistogram < 0) bearishSignals += 1;
  }

  // EMA cycle
  if (data.inRiseCycle !== undefined) {
    if (data.inRiseCycle) bullishSignals += 1;
    else bearishSignals += 1;
  }

  // Growth score
  if (data.growthScore !== undefined) {
    if (data.growthScore >= 75) bullishSignals += 1;
    else if (data.growthScore <= 25) bearishSignals += 1;
  }

  // Calculate net signal
  const netSignal = bullishSignals - bearishSignals;

  if (netSignal >= 4) return "STRONG_BUY";
  if (netSignal >= 2) return "BUY";
  if (netSignal <= -4) return "STRONG_SELL";
  if (netSignal <= -2) return "SELL";
  return "HOLD";
}

/**
 * Get recommendation details
 */
export function getRecommendationDetails(recommendation: Recommendation) {
  return RECOMMENDATIONS[recommendation];
}

// ============================================================================
// § 4. SIGNAL CONFIDENCE
// ============================================================================

/**
 * Calculate signal confidence (0-100)
 */
export function calculateSignalConfidence(data: {
  trendRegime: TrendRegime;
  adx?: number;
  volumeRatio?: number;
  rsiExtreme?: boolean;
}): number {
  let confidence = 50; // Base confidence

  // Trend strength adds confidence
  if (data.trendRegime === "STRONG_UPTREND" || data.trendRegime === "STRONG_DOWNTREND") {
    confidence += 15;
  } else if (data.trendRegime === "CONSOLIDATION") {
    confidence -= 10;
  }

  // ADX strength
  if (data.adx !== undefined) {
    if (data.adx >= INDICATOR_THRESHOLDS.ADX.very_strong) confidence += 15;
    else if (data.adx >= INDICATOR_THRESHOLDS.ADX.strong) confidence += 10;
    else if (data.adx < INDICATOR_THRESHOLDS.ADX.weak) confidence -= 10;
  }

  // Volume confirmation
  if (data.volumeRatio !== undefined) {
    if (data.volumeRatio >= 2) confidence += 10;
    else if (data.volumeRatio >= 1.5) confidence += 5;
    else if (data.volumeRatio < 0.5) confidence -= 10;
  }

  // RSI extreme adds confidence for reversal signals
  if (data.rsiExtreme) {
    confidence += 10;
  }

  // Clamp to 0-100
  return Math.max(0, Math.min(100, confidence));
}

// ============================================================================
// § 5. COMPLETE SIGNAL GENERATION
// ============================================================================

/**
 * Generate complete trading signal from candle data
 */
export function generateTradingSignal(
  candle: CandleWithIndicators,
  symbol: string
): TradingSignal {
  // Get trend regime
  const trendRegime = classifyTrendRegime(
    candle.close,
    candle.sma_50 || candle.close,
    candle.sma_200 || candle.close,
    candle.adx || 0
  );

  // Get EMA cycle status
  const inRiseCycle = candle.ema_12 && candle.ema_26
    ? isInRiseCycle(candle.ema_12, candle.ema_26)
    : undefined;

  // Generate recommendation
  const recommendation = generateRecommendation({
    trendRegime,
    rsi: candle.rsi_14,
    macdHistogram: candle.macd_histogram,
    inRiseCycle,
    growthScore: candle.growth_score,
  });

  // Calculate confidence
  const confidence = calculateSignalConfidence({
    trendRegime,
    adx: candle.adx,
    rsiExtreme:
      candle.rsi_14 !== undefined &&
      (candle.rsi_14 <= 30 || candle.rsi_14 >= 70),
  });

  // Generate reason
  const reason = generateSignalReason(candle, trendRegime, recommendation);

  return {
    symbol,
    datetime: candle.datetime,
    signal: recommendation,
    confidence,
    reason,
    price: candle.close,
  };
}

/**
 * Generate human-readable reason for signal
 */
export function generateSignalReason(
  candle: CandleWithIndicators,
  trendRegime: TrendRegime,
  recommendation: Recommendation
): string {
  const reasons: string[] = [];

  // Trend reason
  const trendDetails = getTrendRegimeDetails(trendRegime);
  reasons.push(`Trend: ${trendDetails.label}`);

  // RSI reason
  if (candle.rsi_14 !== undefined) {
    if (candle.rsi_14 <= 30) reasons.push("RSI oversold");
    else if (candle.rsi_14 >= 70) reasons.push("RSI overbought");
    else if (candle.rsi_14 >= 50 && candle.rsi_14 <= 70) reasons.push("RSI in sweet spot");
  }

  // MACD reason
  if (candle.macd_histogram !== undefined) {
    if (candle.macd_histogram > 0) reasons.push("MACD bullish");
    else reasons.push("MACD bearish");
  }

  // Growth score reason
  if (candle.growth_score !== undefined) {
    if (candle.growth_score >= 75) reasons.push(`Growth Score: ${candle.growth_score} (Excellent)`);
    else if (candle.growth_score >= 50) reasons.push(`Growth Score: ${candle.growth_score} (Good)`);
  }

  return reasons.join("; ");
}

// ============================================================================
// § 6. BATCH SIGNAL GENERATION
// ============================================================================

/**
 * Generate signals for array of candles
 */
export function batchGenerateSignals(
  candles: CandleWithIndicators[],
  symbol: string
): TradingSignal[] {
  return candles.map((candle) => generateTradingSignal(candle, symbol));
}

/**
 * Filter signals by recommendation type
 */
export function filterSignalsByType(
  signals: TradingSignal[],
  types: Recommendation[]
): TradingSignal[] {
  return signals.filter((signal) => types.includes(signal.signal));
}

/**
 * Get buy signals only
 */
export function getBuySignals(signals: TradingSignal[]): TradingSignal[] {
  return filterSignalsByType(signals, ["STRONG_BUY", "BUY"]);
}

/**
 * Get sell signals only
 */
export function getSellSignals(signals: TradingSignal[]): TradingSignal[] {
  return filterSignalsByType(signals, ["STRONG_SELL", "SELL"]);
}
