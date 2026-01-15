/**
 * Technical Analysis Utilities
 * Functions for calculating Fibonacci, Elliott Wave, Support/Resistance, Supply/Demand, and Pivot Points
 */

/**
 * Calculate automatic Fibonacci retracement levels
 * Finds the highest high and lowest low in the data range and calculates retracement levels
 */
export function calculateFibonacciLevels(data, lookbackPeriod = 100) {
  if (!data || data.length < 2) return null;

  // Use the last N candles for calculation
  const recentData = data.slice(-lookbackPeriod);

  // Find swing high and swing low
  let swingHigh = -Infinity;
  let swingLow = Infinity;
  let swingHighTime = null;
  let swingLowTime = null;

  recentData.forEach(item => {
    const high = Number(item.high || 0);
    const low = Number(item.low || 0);
    const time = Number(item.time);

    if (high > swingHigh) {
      swingHigh = high;
      swingHighTime = time;
    }
    if (low < swingLow) {
      swingLow = low;
      swingLowTime = time;
    }
  });

  if (swingHigh === -Infinity || swingLow === Infinity) return null;

  const diff = swingHigh - swingLow;

  // Determine if it's an uptrend or downtrend based on which came first
  const isUptrend = swingLowTime < swingHighTime;

  // Calculate Fibonacci levels
  const levels = {
    '0': isUptrend ? swingLow : swingHigh,
    '23.6': isUptrend ? swingLow + diff * 0.236 : swingHigh - diff * 0.236,
    '38.2': isUptrend ? swingLow + diff * 0.382 : swingHigh - diff * 0.382,
    '50': isUptrend ? swingLow + diff * 0.5 : swingHigh - diff * 0.5,
    '61.8': isUptrend ? swingLow + diff * 0.618 : swingHigh - diff * 0.618,
    '78.6': isUptrend ? swingLow + diff * 0.786 : swingHigh - diff * 0.786,
    '100': isUptrend ? swingHigh : swingLow,
  };

  return {
    levels,
    swingHigh,
    swingLow,
    swingHighTime,
    swingLowTime,
    isUptrend,
    range: diff,
  };
}

/**
 * Detect pivot points (swing highs and lows)
 * A pivot high is a high that is higher than N bars before and after
 * A pivot low is a low that is lower than N bars before and after
 */
export function detectPivotPoints(data, leftBars = 5, rightBars = 5) {
  if (!data || data.length < leftBars + rightBars + 1) return { pivotHighs: [], pivotLows: [] };

  const pivotHighs = [];
  const pivotLows = [];

  for (let i = leftBars; i < data.length - rightBars; i++) {
    const currentHigh = Number(data[i].high || 0);
    const currentLow = Number(data[i].low || 0);
    const time = Number(data[i].time);

    // Check for pivot high
    let isPivotHigh = true;
    for (let j = i - leftBars; j <= i + rightBars; j++) {
      if (j === i) continue;
      if (Number(data[j].high || 0) >= currentHigh) {
        isPivotHigh = false;
        break;
      }
    }

    if (isPivotHigh) {
      pivotHighs.push({
        time,
        price: currentHigh,
        index: i,
      });
    }

    // Check for pivot low
    let isPivotLow = true;
    for (let j = i - leftBars; j <= i + rightBars; j++) {
      if (j === i) continue;
      if (Number(data[j].low || 0) <= currentLow) {
        isPivotLow = false;
        break;
      }
    }

    if (isPivotLow) {
      pivotLows.push({
        time,
        price: currentLow,
        index: i,
      });
    }
  }

  return { pivotHighs, pivotLows };
}

/**
 * Detect Support and Resistance levels
 * Based on pivot points and price clusters
 */
export function detectSupportResistance(data, tolerance = 0.002) {
  const { pivotHighs, pivotLows } = detectPivotPoints(data);

  // Cluster pivot points into support/resistance levels
  const resistanceLevels = clusterPrices(pivotHighs.map(p => p.price), tolerance);
  const supportLevels = clusterPrices(pivotLows.map(p => p.price), tolerance);

  // Get the most recent time for drawing lines
  const endTime = data.length > 0 ? Number(data[data.length - 1].time) : null;
  const startTime = data.length > 50 ? Number(data[data.length - 50].time) :
                    data.length > 0 ? Number(data[0].time) : null;

  return {
    resistance: resistanceLevels.map(price => ({
      price,
      startTime,
      endTime,
      type: 'resistance',
    })),
    support: supportLevels.map(price => ({
      price,
      startTime,
      endTime,
      type: 'support',
    })),
  };
}

/**
 * Helper function to cluster prices within a tolerance
 */
function clusterPrices(prices, tolerance) {
  if (prices.length === 0) return [];

  const sorted = [...prices].sort((a, b) => a - b);
  const clusters = [];
  let currentCluster = [sorted[0]];

  for (let i = 1; i < sorted.length; i++) {
    const priceDiff = Math.abs(sorted[i] - sorted[i - 1]) / sorted[i - 1];

    if (priceDiff <= tolerance) {
      currentCluster.push(sorted[i]);
    } else {
      // Calculate average of cluster
      const avg = currentCluster.reduce((sum, p) => sum + p, 0) / currentCluster.length;
      if (currentCluster.length >= 2) { // Only keep clusters with at least 2 touches
        clusters.push(avg);
      }
      currentCluster = [sorted[i]];
    }
  }

  // Add the last cluster
  if (currentCluster.length >= 2) {
    const avg = currentCluster.reduce((sum, p) => sum + p, 0) / currentCluster.length;
    clusters.push(avg);
  }

  return clusters;
}

/**
 * Detect Supply and Demand Zones
 * Supply zones: areas where price reversed down (resistance zones)
 * Demand zones: areas where price reversed up (support zones)
 */
export function detectSupplyDemandZones(data, minZoneStrength = 2) {
  if (!data || data.length < 10) return { supplyZones: [], demandZones: [] };

  const supplyZones = [];
  const demandZones = [];

  // Look for strong reversals
  for (let i = 5; i < data.length - 5; i++) {
    const current = data[i];
    const close = Number(current.close || 0);
    const open = Number(current.open || 0);
    const high = Number(current.high || 0);
    const low = Number(current.low || 0);
    const time = Number(current.time);

    // Check for supply zone (reversal down)
    // Look for a candle with strong move up followed by reversal down
    if (i >= 3) {
      const prev1 = data[i - 1];
      const prev2 = data[i - 2];
      const prev3 = data[i - 3];

      const prevClose1 = Number(prev1.close || 0);
      const prevClose2 = Number(prev2.close || 0);
      const prevClose3 = Number(prev3.close || 0);

      // Strong upward movement followed by reversal
      if (prevClose1 > prevClose2 && prevClose2 > prevClose3 && close < open) {
        const bodySize = Math.abs(close - open);
        const candleRange = high - low;

        // Strong bearish candle (body is at least 60% of range)
        if (bodySize / candleRange > 0.6) {
          supplyZones.push({
            top: high,
            bottom: Math.max(close, open),
            time,
            strength: minZoneStrength,
          });
        }
      }
    }

    // Check for demand zone (reversal up)
    if (i >= 3) {
      const prev1 = data[i - 1];
      const prev2 = data[i - 2];
      const prev3 = data[i - 3];

      const prevClose1 = Number(prev1.close || 0);
      const prevClose2 = Number(prev2.close || 0);
      const prevClose3 = Number(prev3.close || 0);

      // Strong downward movement followed by reversal
      if (prevClose1 < prevClose2 && prevClose2 < prevClose3 && close > open) {
        const bodySize = Math.abs(close - open);
        const candleRange = high - low;

        // Strong bullish candle
        if (bodySize / candleRange > 0.6) {
          demandZones.push({
            top: Math.max(close, open),
            bottom: low,
            time,
            strength: minZoneStrength,
          });
        }
      }
    }
  }

  // Filter out overlapping zones, keep the strongest
  const filteredSupply = filterOverlappingZones(supplyZones);
  const filteredDemand = filterOverlappingZones(demandZones);

  return {
    supplyZones: filteredSupply,
    demandZones: filteredDemand,
  };
}

/**
 * Filter overlapping zones, keep only the most recent
 */
function filterOverlappingZones(zones) {
  if (zones.length === 0) return [];

  const filtered = [];
  const sorted = [...zones].sort((a, b) => b.time - a.time); // Most recent first

  sorted.forEach(zone => {
    const overlaps = filtered.some(existing => {
      return !(zone.top < existing.bottom || zone.bottom > existing.top);
    });

    if (!overlaps) {
      filtered.push(zone);
    }
  });

  return filtered;
}

/**
 * Simple Elliott Wave detection
 * Identifies potential 5-wave impulse patterns
 */
export function detectElliottWaves(data) {
  if (!data || data.length < 50) return null;

  const { pivotHighs, pivotLows } = detectPivotPoints(data, 5, 5);

  // Need at least 3 pivot highs and 2 pivot lows for a basic pattern
  if (pivotHighs.length < 3 || pivotLows.length < 2) return null;

  // Take the most recent pivots
  const recentHighs = pivotHighs.slice(-3);
  const recentLows = pivotLows.slice(-2);

  // Sort by time
  const allPivots = [
    ...recentHighs.map(p => ({ ...p, type: 'high' })),
    ...recentLows.map(p => ({ ...p, type: 'low' })),
  ].sort((a, b) => a.time - b.time);

  // Check if we have an alternating pattern (high-low-high-low-high)
  if (allPivots.length >= 5) {
    // Look for 5-wave impulse pattern
    // Wave 1: low to high
    // Wave 2: high to low (retracement, should not go below wave 1 start)
    // Wave 3: low to high (strongest, should exceed wave 1 high)
    // Wave 4: high to low (retracement, should not overlap wave 1)
    // Wave 5: low to high (final push)

    const waves = [];

    // Try to identify the pattern from most recent pivots
    for (let i = 0; i <= allPivots.length - 5; i++) {
      const p1 = allPivots[i];
      const p2 = allPivots[i + 1];
      const p3 = allPivots[i + 2];
      const p4 = allPivots[i + 3];
      const p5 = allPivots[i + 4];

      // Check alternating pattern
      if (p1.type === 'low' && p2.type === 'high' && p3.type === 'low' &&
          p4.type === 'high' && p5.type === 'low') {

        // Check Elliott Wave rules
        // Rule 1: Wave 2 should not retrace more than 100% of wave 1
        if (p3.price >= p1.price) {
          // Rule 2: Wave 3 should be longer than wave 1 (strongest wave)
          const wave1Height = p2.price - p1.price;
          const wave3Height = p4.price - p3.price;

          if (wave3Height > wave1Height) {
            waves.push({
              wave1: { time: p1.time, price: p1.price, position: 'start', label: '1' },
              wave2: { time: p2.time, price: p2.price, position: 'high', label: '2' },
              wave3: { time: p3.time, price: p3.price, position: 'low', label: '3' },
              wave4: { time: p4.time, price: p4.price, position: 'high', label: '4' },
              wave5: { time: p5.time, price: p5.price, position: 'low', label: '5' },
            });
          }
        }
      }
    }

    return waves.length > 0 ? waves[waves.length - 1] : null; // Return most recent pattern
  }

  return null;
}

/**
 * Calculate Classic Pivot Points
 * Used for intraday trading support/resistance
 */
export function calculatePivotPoints(data) {
  if (!data || data.length === 0) return null;

  // Use the previous period's data (last complete candle)
  const lastCandle = data[data.length - 1];
  const high = Number(lastCandle.high || 0);
  const low = Number(lastCandle.low || 0);
  const close = Number(lastCandle.close || 0);

  // Pivot Point
  const pp = (high + low + close) / 3;

  // Support and Resistance levels
  const r1 = 2 * pp - low;
  const s1 = 2 * pp - high;
  const r2 = pp + (high - low);
  const s2 = pp - (high - low);
  const r3 = high + 2 * (pp - low);
  const s3 = low - 2 * (high - pp);

  return {
    pp,    // Pivot Point
    r1, r2, r3,  // Resistance levels
    s1, s2, s3,  // Support levels
  };
}
