/**
 * NESTED ML ENGINE - Pure Calculation Functions
 * Multi-timeframe signal calculations for 66.2% UP accuracy model
 *
 * No side effects, no I/O, just math
 * @version 3.0.0
 */

import {
  NESTED_SIGNAL_THRESHOLDS,
  NESTED_ACTION_STATUS,
} from '@/lib/config/trading-config';
import type {
  NestedSignal,
  ActionStatus,
  NestedTradingSignal,
} from '@/types';

// ============================================================================
// § 1. NESTED SIGNAL CLASSIFICATION
// ============================================================================

/**
 * Classify nested signal based on multi-timeframe scores
 * Pure function - no side effects
 */
export function classifyNestedSignal(scores: {
  daily: number;
  hourly: number;
  fivemin: number;
  alignedPct: number;
}): NestedSignal {
  const { daily, hourly, fivemin, alignedPct } = scores;

  // ULTRA_BUY: All TFs aligned (>60%), scores 5+/6+/5+
  const ultraBuy = NESTED_SIGNAL_THRESHOLDS.ULTRA_BUY;
  if (
    alignedPct >= ultraBuy.aligned_pct &&
    daily >= ultraBuy.min_scores.daily &&
    hourly >= ultraBuy.min_scores.hourly &&
    fivemin >= ultraBuy.min_scores.fivemin
  ) {
    return "ULTRA_BUY";
  }

  // STRONG_BUY: All TFs aligned (>50%), scores 4+/5+/4+
  const strongBuy = NESTED_SIGNAL_THRESHOLDS.STRONG_BUY;
  if (
    alignedPct >= strongBuy.aligned_pct &&
    daily >= strongBuy.min_scores.daily &&
    hourly >= strongBuy.min_scores.hourly &&
    fivemin >= strongBuy.min_scores.fivemin
  ) {
    return "STRONG_BUY";
  }

  // BUY: Daily + Hourly aligned, scores 4+/4+
  const buy = NESTED_SIGNAL_THRESHOLDS.BUY;
  if (daily >= buy.min_scores.daily && hourly >= buy.min_scores.hourly) {
    return "BUY";
  }

  // WEAK_BUY: Daily bullish only, score 4+
  const weakBuy = NESTED_SIGNAL_THRESHOLDS.WEAK_BUY;
  if (daily >= weakBuy.min_score) {
    return "WEAK_BUY";
  }

  // Default: HOLD
  return "HOLD";
}

/**
 * Get nested signal details
 */
export function getNestedSignalDetails(signal: NestedSignal) {
  return NESTED_SIGNAL_THRESHOLDS[signal];
}

// ============================================================================
// § 2. ACTION STATUS DETERMINATION
// ============================================================================

/**
 * Determine action status based on alignment and scores
 * Pure function - no side effects
 */
export function determineActionStatus(data: {
  allTfAligned: boolean;
  fiveMinUpPct: number;
  fiveMinEmaPct: number;
  avgScore: number;
}): ActionStatus {
  const { allTfAligned, fiveMinUpPct, fiveMinEmaPct, avgScore } = data;

  // EXECUTE: All TF aligned + 5min up pct >= 50% + score >= 4
  if (allTfAligned && fiveMinUpPct >= 50 && avgScore >= 4) {
    return "EXECUTE";
  }

  // READY: All TF aligned + 5min EMA >= 50%
  if (allTfAligned && fiveMinEmaPct >= 50) {
    return "READY";
  }

  // WATCH: Any partial alignment
  if (allTfAligned) {
    return "WATCH";
  }

  // WAIT: No alignment
  return "WAIT";
}

/**
 * Get action status details
 */
export function getActionStatusDetails(status: ActionStatus) {
  return NESTED_ACTION_STATUS[status];
}

// ============================================================================
// § 3. ALIGNMENT CALCULATIONS
// ============================================================================

/**
 * Check if all timeframes are aligned (EMA bullish)
 */
export function checkAllTimeframeAlignment(
  dailyEmaBullish: boolean,
  hourlyEmaBullish: boolean,
  fiveMinEmaBullish: boolean
): boolean {
  return dailyEmaBullish && hourlyEmaBullish && fiveMinEmaBullish;
}

/**
 * Check if daily and hourly are aligned
 */
export function checkDailyHourlyAlignment(
  dailyEmaBullish: boolean,
  hourlyEmaBullish: boolean
): boolean {
  return dailyEmaBullish && hourlyEmaBullish;
}

/**
 * Check if hourly and 5min are aligned
 */
export function checkHourlyFiveMinAlignment(
  hourlyEmaBullish: boolean,
  fiveMinEmaBullish: boolean
): boolean {
  return hourlyEmaBullish && fiveMinEmaBullish;
}

/**
 * Calculate alignment percentage
 */
export function calculateAlignmentPercentage(
  fiveMinBullishBars: number,
  totalBars: number
): number {
  if (totalBars === 0) return 0;
  return (fiveMinBullishBars / totalBars) * 100;
}

/**
 * Get full alignment status
 */
export function getAlignmentStatus(data: {
  dailyEmaBullish: boolean;
  hourlyEmaBullish: boolean;
  fiveMinEmaBullish: boolean;
  fiveMinBullishBars?: number;
  totalBars?: number;
}): {
  allTfAligned: boolean;
  dailyHourlyAligned: boolean;
  hourlyFiveMinAligned: boolean;
  alignmentPct: number;
} {
  return {
    allTfAligned: checkAllTimeframeAlignment(
      data.dailyEmaBullish,
      data.hourlyEmaBullish,
      data.fiveMinEmaBullish
    ),
    dailyHourlyAligned: checkDailyHourlyAlignment(
      data.dailyEmaBullish,
      data.hourlyEmaBullish
    ),
    hourlyFiveMinAligned: checkHourlyFiveMinAlignment(
      data.hourlyEmaBullish,
      data.fiveMinEmaBullish
    ),
    alignmentPct:
      data.fiveMinBullishBars !== undefined && data.totalBars !== undefined
        ? calculateAlignmentPercentage(data.fiveMinBullishBars, data.totalBars)
        : 0,
  };
}

// ============================================================================
// § 4. SCORE CALCULATIONS
// ============================================================================

/**
 * Calculate daily rise cycle score (0-8)
 * Based on: EMA alignment, MACD, trend, SMA50, SMA200
 */
export function calculateDailyScore(data: {
  emaBullish: boolean;
  macdBullish: boolean;
  strongTrend: boolean;
  aboveSma50: boolean;
  aboveSma200: boolean;
  rsiSweet: boolean;
  volumeSurge: boolean;
  priceUp: boolean;
}): number {
  let score = 0;

  if (data.emaBullish) score += 1;
  if (data.macdBullish) score += 1;
  if (data.strongTrend) score += 1;
  if (data.aboveSma50) score += 1;
  if (data.aboveSma200) score += 1;
  if (data.rsiSweet) score += 1;
  if (data.volumeSurge) score += 1;
  if (data.priceUp) score += 1;

  return score;
}

/**
 * Calculate hourly score (0-10)
 */
export function calculateHourlyScore(data: {
  emaBullish: boolean;
  macdBullish: boolean;
  strongTrend: boolean;
  rsiSweet: boolean;
  volumeSurge: boolean;
  priceUp: boolean;
  aboveDailyEma: boolean;
  momentumPositive: boolean;
  volumeAboveAvg: boolean;
  trendContinuation: boolean;
}): number {
  let score = 0;

  if (data.emaBullish) score += 1;
  if (data.macdBullish) score += 1;
  if (data.strongTrend) score += 1;
  if (data.rsiSweet) score += 1;
  if (data.volumeSurge) score += 1;
  if (data.priceUp) score += 1;
  if (data.aboveDailyEma) score += 1;
  if (data.momentumPositive) score += 1;
  if (data.volumeAboveAvg) score += 1;
  if (data.trendContinuation) score += 1;

  return score;
}

/**
 * Calculate average 5-minute score from aggregated data
 */
export function calculateAvgFiveMinScore(
  fiveMinScores: number[]
): number {
  if (fiveMinScores.length === 0) return 0;
  const sum = fiveMinScores.reduce((a, b) => a + b, 0);
  return sum / fiveMinScores.length;
}

// ============================================================================
// § 5. COMPLETE NESTED SIGNAL GENERATION
// ============================================================================

/**
 * Generate complete nested trading signal
 */
export function generateNestedSignal(data: {
  symbol: string;
  tradeDate: string;
  tradeHour: number;
  dailyScore: number;
  hourlyScore: number;
  fiveMinScore: number;
  dailyEmaBullish: boolean;
  hourlyEmaBullish: boolean;
  fiveMinEmaBullish: boolean;
  fiveMinUpPct: number;
  fiveMinEmaPct: number;
  actualOutcome?: "UP" | "DOWN";
  hourPctChange?: number;
}): NestedTradingSignal {
  // Calculate alignment
  const alignment = getAlignmentStatus({
    dailyEmaBullish: data.dailyEmaBullish,
    hourlyEmaBullish: data.hourlyEmaBullish,
    fiveMinEmaBullish: data.fiveMinEmaBullish,
  });

  // Classify nested signal
  const nestedSignal = classifyNestedSignal({
    daily: data.dailyScore,
    hourly: data.hourlyScore,
    fivemin: data.fiveMinScore,
    alignedPct: data.fiveMinEmaPct,
  });

  // Determine action status
  const avgScore = (data.dailyScore + data.hourlyScore + data.fiveMinScore) / 3;
  const actionStatus = determineActionStatus({
    allTfAligned: alignment.allTfAligned,
    fiveMinUpPct: data.fiveMinUpPct,
    fiveMinEmaPct: data.fiveMinEmaPct,
    avgScore,
  });

  return {
    symbol: data.symbol,
    trade_date: data.tradeDate,
    trade_hour: data.tradeHour,
    nested_signal: nestedSignal,
    action_status: actionStatus,
    scores: {
      daily: data.dailyScore,
      hourly: data.hourlyScore,
      fivemin: data.fiveMinScore,
    },
    alignment: {
      all_tf_aligned: alignment.allTfAligned,
      daily_hourly_aligned: alignment.dailyHourlyAligned,
      hourly_5min_aligned: alignment.hourlyFiveMinAligned,
    },
    actual_outcome: data.actualOutcome,
    hour_pct_change: data.hourPctChange,
  };
}

// ============================================================================
// § 6. FILTERING & SORTING
// ============================================================================

/**
 * Filter nested signals by action status
 */
export function filterByActionStatus(
  signals: NestedTradingSignal[],
  status: ActionStatus
): NestedTradingSignal[] {
  return signals.filter((signal) => signal.action_status === status);
}

/**
 * Filter nested signals by aligned only
 */
export function filterAlignedOnly(
  signals: NestedTradingSignal[]
): NestedTradingSignal[] {
  return signals.filter((signal) => signal.alignment.all_tf_aligned);
}

/**
 * Sort signals by combined score (descending)
 */
export function sortByScore(
  signals: NestedTradingSignal[]
): NestedTradingSignal[] {
  return [...signals].sort((a, b) => {
    const scoreA = a.scores.daily + a.scores.hourly + a.scores.fivemin;
    const scoreB = b.scores.daily + b.scores.hourly + b.scores.fivemin;
    return scoreB - scoreA;
  });
}

/**
 * Get top signals (EXECUTE and READY only)
 */
export function getTopSignals(
  signals: NestedTradingSignal[],
  limit: number = 10
): NestedTradingSignal[] {
  return sortByScore(
    signals.filter(
      (s) => s.action_status === "EXECUTE" || s.action_status === "READY"
    )
  ).slice(0, limit);
}

// ============================================================================
// § 7. MODEL METRICS
// ============================================================================

/**
 * Model performance constants (from validation)
 */
export const MODEL_METRICS = {
  UP_ACCURACY: 66.2,
  DOWN_ACCURACY: 70.6,
  OVERALL_ACCURACY: 68.4,
  ROC_AUC: 0.777,
  F1_SCORE: 0.678,
  IMPROVEMENT_VS_BASELINE: 6.2, // 6.2x better than single-TF
} as const;

/**
 * Feature importance (from model training)
 */
export const FEATURE_IMPORTANCE = {
  fivemin_price_up_pct: 0.0665,
  fivemin_ema_pct: 0.0373,
  avg_5min_score: 0.0355,
  fivemin_macd_pct: 0.0275,
  max_5min_score: 0.0134,
  daily_score: 0.0030,
} as const;
