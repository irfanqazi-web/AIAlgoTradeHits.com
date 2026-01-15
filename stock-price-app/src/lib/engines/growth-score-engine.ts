/**
 * GROWTH SCORE ENGINE - Pure Calculation Functions
 * No side effects, no I/O, just math
 *
 * Based on masterquery.md v4.0
 * @version 3.0.0
 */

import {
  GROWTH_SCORE_RULES,
  GROWTH_SCORE_THRESHOLDS,
  INDICATOR_THRESHOLDS,
} from '@/lib/config/trading-config';
import type { GrowthScoreBreakdown, CandleWithIndicators } from '@/types';

// ============================================================================
// § 1. GROWTH SCORE CALCULATION (0-100)
// ============================================================================

/**
 * Calculate Growth Score breakdown
 * Pure function - no side effects
 */
export function calculateGrowthScoreBreakdown(data: {
  rsi_14?: number;
  macd_histogram?: number;
  adx?: number;
  close?: number;
  sma_200?: number;
}): GrowthScoreBreakdown {
  let rsi_component = 0;
  let macd_component = 0;
  let adx_component = 0;
  let sma_component = 0;

  // RSI sweet spot (50-70) = 25 points
  if (data.rsi_14 !== undefined) {
    const [low, high] = GROWTH_SCORE_RULES.rsi_sweet_spot.range;
    if (data.rsi_14 >= low && data.rsi_14 <= high) {
      rsi_component = GROWTH_SCORE_RULES.rsi_sweet_spot.points;
    }
  }

  // MACD histogram positive = 25 points
  if (data.macd_histogram !== undefined && data.macd_histogram > 0) {
    macd_component = GROWTH_SCORE_RULES.macd_positive.points;
  }

  // Strong trend (ADX > 25) = 25 points
  if (data.adx !== undefined && data.adx > GROWTH_SCORE_RULES.strong_trend.threshold) {
    adx_component = GROWTH_SCORE_RULES.strong_trend.points;
  }

  // Above SMA200 = 25 points
  if (data.close !== undefined && data.sma_200 !== undefined && data.close > data.sma_200) {
    sma_component = GROWTH_SCORE_RULES.above_sma200.points;
  }

  return {
    total: rsi_component + macd_component + adx_component + sma_component,
    rsi_component,
    macd_component,
    adx_component,
    sma_component,
  };
}

/**
 * Calculate Growth Score (0-100)
 * Convenience function that returns just the total
 */
export function calculateGrowthScore(data: {
  rsi_14?: number;
  macd_histogram?: number;
  adx?: number;
  close?: number;
  sma_200?: number;
}): number {
  return calculateGrowthScoreBreakdown(data).total;
}

/**
 * Get Growth Score category
 */
export function getGrowthScoreCategory(
  score: number
): "EXCELLENT" | "GOOD" | "MODERATE" | "POOR" {
  if (score >= GROWTH_SCORE_THRESHOLDS.EXCELLENT) return "EXCELLENT";
  if (score >= GROWTH_SCORE_THRESHOLDS.GOOD) return "GOOD";
  if (score >= GROWTH_SCORE_THRESHOLDS.MODERATE) return "MODERATE";
  return "POOR";
}

// ============================================================================
// § 2. SENTIMENT SCORE CALCULATION
// ============================================================================

/**
 * Calculate simple sentiment score (0-1)
 * Based on price momentum and volume
 */
export function calculateSentimentScore(data: {
  close: number;
  open: number;
  volume: number;
  avg_volume?: number;
  rsi_14?: number;
}): number {
  let score = 0.5; // Start neutral

  // Price direction component (0-0.3)
  const priceChange = (data.close - data.open) / data.open;
  if (priceChange > 0.02) score += 0.3;
  else if (priceChange > 0.01) score += 0.2;
  else if (priceChange > 0) score += 0.1;
  else if (priceChange < -0.02) score -= 0.3;
  else if (priceChange < -0.01) score -= 0.2;
  else if (priceChange < 0) score -= 0.1;

  // Volume component (0-0.2)
  if (data.avg_volume && data.avg_volume > 0) {
    const volumeRatio = data.volume / data.avg_volume;
    if (volumeRatio > 2 && priceChange > 0) score += 0.2;
    else if (volumeRatio > 1.5 && priceChange > 0) score += 0.1;
    else if (volumeRatio > 2 && priceChange < 0) score -= 0.2;
    else if (volumeRatio > 1.5 && priceChange < 0) score -= 0.1;
  }

  // Clamp to 0-1 range
  return Math.max(0, Math.min(1, score));
}

// ============================================================================
// § 3. RSI ANALYSIS
// ============================================================================

/**
 * Analyze RSI status
 */
export function analyzeRSI(rsi: number): {
  status: "oversold" | "overbought" | "sweet_spot" | "neutral";
  score: number;
  signal: "BUY" | "SELL" | "HOLD";
} {
  const thresholds = INDICATOR_THRESHOLDS.RSI;

  if (rsi <= thresholds.oversold) {
    return { status: "oversold", score: 1, signal: "BUY" };
  }
  if (rsi >= thresholds.overbought) {
    return { status: "overbought", score: -1, signal: "SELL" };
  }
  if (rsi >= thresholds.sweet_spot[0] && rsi <= thresholds.sweet_spot[1]) {
    return { status: "sweet_spot", score: 0.5, signal: "HOLD" };
  }
  return { status: "neutral", score: 0, signal: "HOLD" };
}

// ============================================================================
// § 4. ADX ANALYSIS
// ============================================================================

/**
 * Analyze ADX trend strength
 */
export function analyzeADX(adx: number): {
  strength: "weak" | "moderate" | "strong" | "very_strong";
  score: number;
  tradeable: boolean;
} {
  const thresholds = INDICATOR_THRESHOLDS.ADX;

  if (adx >= thresholds.very_strong) {
    return { strength: "very_strong", score: 1, tradeable: true };
  }
  if (adx >= thresholds.strong) {
    return { strength: "strong", score: 0.75, tradeable: true };
  }
  if (adx >= thresholds.weak) {
    return { strength: "moderate", score: 0.5, tradeable: true };
  }
  return { strength: "weak", score: 0.25, tradeable: false };
}

// ============================================================================
// § 5. VOLUME ANALYSIS
// ============================================================================

/**
 * Analyze volume surge
 */
export function analyzeVolume(
  currentVolume: number,
  averageVolume: number
): {
  ratio: number;
  surge: boolean;
  high_volume: boolean;
  signal: "CONFIRM" | "NEUTRAL" | "WEAK";
} {
  if (averageVolume === 0) {
    return { ratio: 0, surge: false, high_volume: false, signal: "NEUTRAL" };
  }

  const ratio = currentVolume / averageVolume;
  const thresholds = INDICATOR_THRESHOLDS.VOLUME;

  return {
    ratio,
    surge: ratio >= thresholds.surge_multiplier,
    high_volume: ratio >= thresholds.high_volume_multiplier,
    signal:
      ratio >= thresholds.high_volume_multiplier
        ? "CONFIRM"
        : ratio >= thresholds.surge_multiplier
        ? "NEUTRAL"
        : "WEAK",
  };
}

// ============================================================================
// § 6. COMPOSITE SCORE
// ============================================================================

/**
 * Calculate composite trading score
 * Combines multiple indicators into a single score (-100 to +100)
 */
export function calculateCompositeScore(data: CandleWithIndicators): number {
  let score = 0;
  let components = 0;

  // RSI component (-25 to +25)
  if (data.rsi_14 !== undefined) {
    const rsiAnalysis = analyzeRSI(data.rsi_14);
    score += rsiAnalysis.score * 25;
    components++;
  }

  // MACD component (-25 to +25)
  if (data.macd_histogram !== undefined) {
    if (data.macd_histogram > 0) score += 25;
    else if (data.macd_histogram < 0) score -= 25;
    components++;
  }

  // ADX component (0 to +25)
  if (data.adx !== undefined) {
    const adxAnalysis = analyzeADX(data.adx);
    score += adxAnalysis.score * 25;
    components++;
  }

  // Trend component (-25 to +25)
  if (data.close !== undefined && data.sma_200 !== undefined) {
    if (data.close > data.sma_200) score += 25;
    else score -= 25;
    components++;
  }

  // Normalize if we have components
  if (components > 0) {
    return Math.round((score / components) * (4 / components));
  }

  return 0;
}

// ============================================================================
// § 7. BATCH PROCESSING
// ============================================================================

/**
 * Calculate growth scores for an array of candles
 */
export function batchCalculateGrowthScores(
  candles: CandleWithIndicators[]
): Array<CandleWithIndicators & { growth_score: number }> {
  return candles.map((candle) => ({
    ...candle,
    growth_score: calculateGrowthScore(candle),
  }));
}

/**
 * Find high growth score candidates
 */
export function findHighGrowthCandidates(
  candles: CandleWithIndicators[],
  minScore: number = 75
): CandleWithIndicators[] {
  return candles.filter((candle) => calculateGrowthScore(candle) >= minScore);
}
