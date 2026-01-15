/**
 * TradingViewChart Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { marketDataService } from '@/lib/services';
import themes from '../../theme';
import {
  calculateFibonacciLevels,
  detectPivotPoints,
  detectSupportResistance,
  detectSupplyDemandZones,
  detectElliottWaves,
  calculatePivotPoints,
} from '../../utils/technicalAnalysis';

/**
 * TradingView-style chart with RSI and MACD panels below
 * Matches Screen format 6.jpg layout
 * Supports all 7 asset types: stocks, crypto, forex, etfs, indices, commodities, interest_rates
 */
export default function TradingViewChart({ symbol, marketType = 'stocks', assetType, timeframe = 'daily', theme = 'dark' }) {
  // Use assetType if provided, otherwise fall back to marketType for backwards compatibility
  const effectiveAssetType = assetType || (marketType === 'crypto' ? 'crypto' : 'stocks');
  const mainChartRef = useRef(null);
  const rsiChartRef = useRef(null);
  const tradesChartRef = useRef(null);
  const macdChartRef = useRef(null);

  const mainContainerRef = useRef(null);
  const rsiContainerRef = useRef(null);
  const tradesContainerRef = useRef(null);
  const macdContainerRef = useRef(null);

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [latestData, setLatestData] = useState(null);

  // Indicator visibility toggles
  const [showSMA20, setShowSMA20] = useState(true);
  const [showSMA50, setShowSMA50] = useState(true);
  const [showEMA12, setShowEMA12] = useState(true);
  const [showBB, setShowBB] = useState(true);
  const [showFib, setShowFib] = useState(true); // On by default
  const [showElliott, setShowElliott] = useState(true); // On by default
  const [showRSI, setShowRSI] = useState(true);
  const [showMACD, setShowMACD] = useState(true);
  const [showSupportResistance, setShowSupportResistance] = useState(true);
  const [showSupplyDemand, setShowSupplyDemand] = useState(true);
  const [showPivotPoints, setShowPivotPoints] = useState(true);
  const [showPivotHL, setShowPivotHL] = useState(true); // Pivot High/Low markers

  // Chart height controls - reduced for compact view
  const [mainHeight, setMainHeight] = useState(250);
  const [rsiHeight, setRsiHeight] = useState(80);
  const [volumeHeight, setVolumeHeight] = useState(150);
  const [macdHeight, setMacdHeight] = useState(120);

  // Store series refs for toggling visibility
  const sma20SeriesRef = useRef(null);
  const sma50SeriesRef = useRef(null);
  const ema12SeriesRef = useRef(null);
  const bbSeriesRefs = useRef({ upper: null, middle: null, lower: null });
  const fibSeriesRefs = useRef([]);
  const candlestickSeriesRef = useRef(null);
  const tradeMarkersRef = useRef([]);
  const elliottMarkersRef = useRef([]);
  const supportResistanceRefs = useRef([]);
  const supplyDemandRefs = useRef([]);
  const pivotPointRefs = useRef([]);
  const pivotHLMarkersRef = useRef([]);

  const currentTheme = themes[theme];

  // Fetch data
  useEffect(() => {
    if (!symbol) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        let chartData;
        // TEMPORARY: Reduce daily limit to test if size is the issue
        const limit = timeframe === 'daily' ? 100 : 500;

        console.log(`🔍 Fetching ${timeframe} data for ${symbol} (${effectiveAssetType}), limit: ${limit}`);

        // Use universal getData method that supports all asset types
        chartData = await marketDataService.getData(symbol, effectiveAssetType, timeframe, limit);

        console.log(`✅ TradingView chart loaded ${chartData.length} candles for ${symbol} (${timeframe})`);
        console.log(`📊 First candle:`, chartData[0]);
        console.log(`📊 Last candle:`, chartData[chartData.length - 1]);

        if (chartData.length === 0) {
          console.error(`❌ No data available for ${symbol}`);
          setError(`No data available for ${symbol}`);
        } else {
          setData(chartData);
          setLatestData(chartData[chartData.length - 1]);
        }
      } catch (err) {
        console.error('❌ Error fetching chart data:', err);
        setError(err.message || 'Failed to load chart data');
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, effectiveAssetType, timeframe]);

  // Create charts
  useEffect(() => {
    if (!data || data.length === 0) return;

    // Clean up existing charts
    try {
      if (mainChartRef.current) {
        mainChartRef.current.remove();
        mainChartRef.current = null;
      }
    } catch (err) {
      console.error('Error cleaning up main chart:', err);
    }

    try {
      if (rsiChartRef.current) {
        rsiChartRef.current.remove();
        rsiChartRef.current = null;
      }
    } catch (err) {
      console.error('Error cleaning up RSI chart:', err);
    }

    try {
      if (tradesChartRef.current) {
        tradesChartRef.current.remove();
        tradesChartRef.current = null;
      }
    } catch (err) {
      console.error('Error cleaning up trades chart:', err);
    }

    try {
      if (macdChartRef.current) {
        macdChartRef.current.remove();
        macdChartRef.current = null;
      }
    } catch (err) {
      console.error('Error cleaning up MACD chart:', err);
    }

    // Chart options
    const chartOptions = {
      layout: {
        background: { type: 'solid', color: currentTheme.chart.background },
        textColor: currentTheme.chart.textColor,
      },
      grid: {
        vertLines: { color: currentTheme.chart.gridColor },
        horzLines: { color: currentTheme.chart.gridColor },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: currentTheme.textSecondary,
          labelBackgroundColor: currentTheme.primary,
        },
        horzLine: {
          color: currentTheme.textSecondary,
          labelBackgroundColor: currentTheme.primary,
        },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: currentTheme.chart.borderColor,
      },
      rightPriceScale: {
        borderColor: currentTheme.chart.borderColor,
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
    };

    // ========== MAIN PRICE CHART ==========
    try {
      if (mainContainerRef.current) {
        const containerWidth = mainContainerRef.current.clientWidth;
        console.log(`Creating main chart for ${symbol}: width=${containerWidth}, data points=${data.length}`);

        if (containerWidth === 0) {
          console.warn('Container width is 0, chart may not render properly');
        }

        // Use full container width, chart library handles price scale internally
        const chartWidth = containerWidth || 800;

        const mainChart = createChart(mainContainerRef.current, {
          ...chartOptions,
          width: chartWidth,
          height: mainHeight,
        });

        mainChartRef.current = mainChart;

        // Candlestick series
        const candlestickSeries = mainChart.addCandlestickSeries({
          upColor: currentTheme.chart.upColor,
          downColor: currentTheme.chart.downColor,
          borderVisible: false,
          wickUpColor: currentTheme.chart.upColor,
          wickDownColor: currentTheme.chart.downColor,
        });
        candlestickSeriesRef.current = candlestickSeries;

        const candlestickData = data
          .map(item => ({
            time: Number(item.time || 0),
            open: Number(item.open || item.close || 0),
            high: Number(item.high || item.close || 0),
            low: Number(item.low || item.close || 0),
            close: Number(item.close || 0),
          }))
          .filter(item => {
            // Filter out invalid candles
            const hasValidPrice = item.close > 0 && item.open > 0 && item.high > 0 && item.low > 0;
            const hasValidTime = item.time > 0;
            const isValidCandle = item.high >= item.low && item.high >= item.close && item.high >= item.open && item.low <= item.close && item.low <= item.open;

            return hasValidPrice && hasValidTime && isValidCandle;
          })
          .sort((a, b) => a.time - b.time);

        console.log(`✅ Candlestick data for ${symbol}: ${candlestickData.length} candles`);
        if (candlestickData.length > 0) {
          console.log('📊 First candle:', candlestickData[0]);
          console.log('📊 Last candle:', candlestickData[candlestickData.length - 1]);
          console.log('📊 Time range:', new Date(candlestickData[0].time * 1000).toISOString(), 'to', new Date(candlestickData[candlestickData.length - 1].time * 1000).toISOString());

          // Check indicator availability
          const hasRSI = data.some(d => d.rsi != null);
          const hasMACD = data.some(d => d.macd != null);
          const hasSMA = data.some(d => d.sma_20 != null);
          console.log('📈 Indicators available:', { hasRSI, hasMACD, hasSMA });
        } else {
          console.error('❌ NO VALID CANDLESTICK DATA! Raw data sample:', data[0]);
          throw new Error('No valid candlestick data to display');
        }

        if (candlestickData.length === 0) {
          throw new Error('No valid candles after filtering');
        }

        candlestickSeries.setData(candlestickData);
        console.log('✅ Candlestick series data set successfully');

        // Volume overlay (bottom 20%)
        const volumeSeries = mainChart.addHistogramSeries({
          color: currentTheme.textMuted,
          priceFormat: {
            type: 'volume',
          },
          priceScaleId: 'volume',
        });

        mainChart.priceScale('volume').applyOptions({
          scaleMargins: {
            top: 0.8,
            bottom: 0,
          },
        });

        const volumeData = data
          .map(item => ({
            time: Number(item.time || 0),
            value: Number(item.volume || 0),
            color: (Number(item.close) || 0) >= (Number(item.open) || 0) ? currentTheme.chart.volumeUpColor : currentTheme.chart.volumeDownColor,
          }))
          .filter(item => item.time > 0)
          .sort((a, b) => a.time - b.time);

        volumeSeries.setData(volumeData);

        // Add SMAs
        const hasSMA20 = data.some(item => item.sma_20 != null);
        console.log('Has SMA 20?', hasSMA20, 'showSMA20:', showSMA20);
        if (hasSMA20) {
          const sma20Series = mainChart.addLineSeries({
            color: currentTheme.indicators.sma20,
            lineWidth: 2,
            title: 'SMA 20',
            priceLineVisible: false,
            lastValueVisible: true,
            visible: showSMA20,
          });
          sma20SeriesRef.current = sma20Series;

          const sma20Data = data
            .filter(item => item.sma_20 != null && item.time)
            .map(item => ({
              time: Number(item.time),
              value: Number(item.sma_20),
            }))
            .sort((a, b) => a.time - b.time);

          sma20Series.setData(sma20Data);
        }

        const hasSMA50 = data.some(item => item.sma_50 != null);
        console.log('Has SMA 50?', hasSMA50, 'showSMA50:', showSMA50);
        if (hasSMA50) {
          const sma50Series = mainChart.addLineSeries({
            color: currentTheme.indicators.sma50,
            lineWidth: 2,
            title: 'SMA 50',
            priceLineVisible: false,
            lastValueVisible: true,
            visible: showSMA50,
          });
          sma50SeriesRef.current = sma50Series;

          const sma50Data = data
            .filter(item => item.sma_50 != null && item.time)
            .map(item => ({
              time: Number(item.time),
              value: Number(item.sma_50),
            }))
            .sort((a, b) => a.time - b.time);

          sma50Series.setData(sma50Data);
        }

        if (data[0]?.ema_12) {
          const ema12Series = mainChart.addLineSeries({
            color: currentTheme.indicators.ema12,
            lineWidth: 1,
            title: 'EMA 12',
            priceLineVisible: false,
            lastValueVisible: true,
            visible: showEMA12,
          });
          ema12SeriesRef.current = ema12Series;

          const ema12Data = data
            .filter(item => item.ema_12 != null && item.time)
            .map(item => ({
              time: Number(item.time),
              value: Number(item.ema_12),
            }))
            .sort((a, b) => a.time - b.time);

          ema12Series.setData(ema12Data);
        }

        // Add Bollinger Bands
        const hasBB = data.some(item => item.bb_upper != null && item.bb_middle != null && item.bb_lower != null);
        if (hasBB) {
          console.log('Adding Bollinger Bands to chart');
          // Upper band
          const bbUpperSeries = mainChart.addLineSeries({
            color: '#60a5fa',
            lineWidth: 1,
            title: 'BB Upper',
            priceLineVisible: false,
            lastValueVisible: false,
            lineStyle: 2, // dashed
            visible: showBB,
          });
          bbSeriesRefs.current.upper = bbUpperSeries;

          const bbUpperData = data
            .filter(item => item.bb_upper != null && item.time)
            .map(item => ({
              time: Number(item.time),
              value: Number(item.bb_upper),
            }))
            .sort((a, b) => a.time - b.time);

          bbUpperSeries.setData(bbUpperData);

          // Middle band
          const bbMiddleSeries = mainChart.addLineSeries({
            color: '#93c5fd',
            lineWidth: 1,
            title: 'BB Middle',
            priceLineVisible: false,
            lastValueVisible: false,
            visible: showBB,
          });
          bbSeriesRefs.current.middle = bbMiddleSeries;

          const bbMiddleData = data
            .filter(item => item.bb_middle != null && item.time)
            .map(item => ({
              time: Number(item.time),
              value: Number(item.bb_middle),
            }))
            .sort((a, b) => a.time - b.time);

          bbMiddleSeries.setData(bbMiddleData);

          // Lower band
          const bbLowerSeries = mainChart.addLineSeries({
            color: '#60a5fa',
            lineWidth: 1,
            title: 'BB Lower',
            priceLineVisible: false,
            lastValueVisible: false,
            lineStyle: 2, // dashed
            visible: showBB,
          });
          bbSeriesRefs.current.lower = bbLowerSeries;

          const bbLowerData = data
            .filter(item => item.bb_lower != null && item.time)
            .map(item => ({
              time: Number(item.time),
              value: Number(item.bb_lower),
            }))
            .sort((a, b) => a.time - b.time);

          bbLowerSeries.setData(bbLowerData);
        }

        // Add Fibonacci Retracement Levels
        const hasFib = data.some(item => item.fib_618 != null || item.fib_382 != null || item.fib_500 != null);
        console.log('Fibonacci check - Has data?', hasFib, 'showFib:', showFib);
        console.log('Sample Fib data:', data.slice(-5).map(d => ({ fib_618: d.fib_618, fib_382: d.fib_382, fib_500: d.fib_500 })));
        if (hasFib && showFib) {
          console.log('Adding Fibonacci levels to chart');
          fibSeriesRefs.current = []; // Reset refs
          const fibLevels = [
            { key: 'fib_0', color: '#6366f1', label: '0%' },
            { key: 'fib_236', color: '#8b5cf6', label: '23.6%' },
            { key: 'fib_382', color: '#a855f7', label: '38.2%' },
            { key: 'fib_500', color: '#c084fc', label: '50%' },
            { key: 'fib_618', color: '#d8b4fe', label: '61.8%' },
            { key: 'fib_786', color: '#e9d5ff', label: '78.6%' },
            { key: 'fib_100', color: '#f3e8ff', label: '100%' },
          ];

          fibLevels.forEach(({ key, color, label }) => {
            const hasLevel = data.some(item => item[key] != null);
            if (hasLevel) {
              const fibSeries = mainChart.addLineSeries({
                color: color,
                lineWidth: 1,
                title: `Fib ${label}`,
                priceLineVisible: false,
                lastValueVisible: false,
                lineStyle: 2, // dashed
                visible: showFib,
              });
              fibSeriesRefs.current.push(fibSeries);

              const fibData = data
                .filter(item => item[key] != null && item.time)
                .map(item => ({
                  time: Number(item.time),
                  value: Number(item[key]),
                }))
                .sort((a, b) => a.time - b.time);

              if (fibData.length > 0) {
                fibSeries.setData(fibData);
              }
            }
          });
        }

        // Add AUTOMATIC Fibonacci Retracement Levels (calculated)
        if (showFib && data.length >= 20) {
          const fibResult = calculateFibonacciLevels(data, 100);
          if (fibResult) {
            console.log('Automatic Fibonacci levels calculated:', fibResult);

            const fibColors = {
              '0': '#6366f1',
              '23.6': '#8b5cf6',
              '38.2': '#a855f7',
              '50': '#c084fc',
              '61.8': '#d8b4fe',
              '78.6': '#e9d5ff',
              '100': '#f3e8ff',
            };

            // Draw each Fibonacci level as a horizontal line
            Object.entries(fibResult.levels).forEach(([label, price]) => {
              const fibSeries = mainChart.addLineSeries({
                color: fibColors[label] || '#a855f7',
                lineWidth: 2,
                title: `Fib ${label}%`,
                priceLineVisible: true,
                lastValueVisible: true,
                lineStyle: 2, // dashed
              });

              // Create line data spanning visible range
              const fibLineData = data
                .slice(-50) // Last 50 candles
                .filter(item => item.time)
                .map(item => ({
                  time: Number(item.time),
                  value: price,
                }))
                .sort((a, b) => a.time - b.time);

              fibSeries.setData(fibLineData);
              fibSeriesRefs.current.push(fibSeries);
            });
          }
        }

        // Add Support and Resistance Levels (automatic)
        if (showSupportResistance && data.length >= 20) {
          const srLevels = detectSupportResistance(data, 0.002);
          console.log('Support/Resistance levels:', srLevels);

          // Draw resistance levels
          srLevels.resistance.forEach((level, idx) => {
            const resSeries = mainChart.addLineSeries({
              color: '#ef4444',
              lineWidth: 2,
              title: `Resistance ${idx + 1}`,
              priceLineVisible: true,
              lastValueVisible: true,
              lineStyle: 0, // solid
            });

            const resData = data
              .slice(-50)
              .filter(item => item.time)
              .map(item => ({
                time: Number(item.time),
                value: level.price,
              }))
              .sort((a, b) => a.time - b.time);

            resSeries.setData(resData);
            supportResistanceRefs.current.push(resSeries);
          });

          // Draw support levels
          srLevels.support.forEach((level, idx) => {
            const supSeries = mainChart.addLineSeries({
              color: '#22c55e',
              lineWidth: 2,
              title: `Support ${idx + 1}`,
              priceLineVisible: true,
              lastValueVisible: true,
              lineStyle: 0, // solid
            });

            const supData = data
              .slice(-50)
              .filter(item => item.time)
              .map(item => ({
                time: Number(item.time),
                value: level.price,
              }))
              .sort((a, b) => a.time - b.time);

            supSeries.setData(supData);
            supportResistanceRefs.current.push(supSeries);
          });
        }

        // Add Classical Pivot Points
        if (showPivotPoints && data.length > 0) {
          const pivots = calculatePivotPoints(data);
          if (pivots) {
            console.log('Pivot Points:', pivots);

            const pivotLevels = [
              { label: 'PP', value: pivots.pp, color: '#f59e0b' },
              { label: 'R1', value: pivots.r1, color: '#ef4444' },
              { label: 'R2', value: pivots.r2, color: '#dc2626' },
              { label: 'R3', value: pivots.r3, color: '#991b1b' },
              { label: 'S1', value: pivots.s1, color: '#22c55e' },
              { label: 'S2', value: pivots.s2, color: '#16a34a' },
              { label: 'S3', value: pivots.s3, color: '#15803d' },
            ];

            pivotLevels.forEach(({ label, value, color }) => {
              const pivotSeries = mainChart.addLineSeries({
                color,
                lineWidth: 1,
                title: label,
                priceLineVisible: true,
                lastValueVisible: true,
                lineStyle: 3, // dotted
              });

              const pivotData = data
                .slice(-30)
                .filter(item => item.time)
                .map(item => ({
                  time: Number(item.time),
                  value,
                }))
                .sort((a, b) => a.time - b.time);

              pivotSeries.setData(pivotData);
              pivotPointRefs.current.push(pivotSeries);
            });
          }
        }

        // Add Pivot High/Low Markers
        if (showPivotHL && data.length >= 20) {
          const { pivotHighs, pivotLows } = detectPivotPoints(data, 5, 5);
          console.log(`Detected ${pivotHighs.length} pivot highs, ${pivotLows.length} pivot lows`);

          const pivotMarkers = [];

          // Add pivot high markers
          pivotHighs.slice(-20).forEach(pivot => {
            pivotMarkers.push({
              time: pivot.time,
              position: 'aboveBar',
              color: '#ef4444',
              shape: 'arrowDown',
              text: 'PH',
              size: 0.5,
            });
          });

          // Add pivot low markers
          pivotLows.slice(-20).forEach(pivot => {
            pivotMarkers.push({
              time: pivot.time,
              position: 'belowBar',
              color: '#22c55e',
              shape: 'arrowUp',
              text: 'PL',
              size: 0.5,
            });
          });

          pivotHLMarkersRef.current = pivotMarkers;
        }

        // Add Supply and Demand Zones
        if (showSupplyDemand && data.length >= 20) {
          const { supplyZones, demandZones } = detectSupplyDemandZones(data, 2);
          console.log(`Detected ${supplyZones.length} supply zones, ${demandZones.length} demand zones`);

          // Draw supply zones (resistance/sell zones) - red zones
          supplyZones.slice(-5).forEach((zone, idx) => {
            // Top of zone
            const supplyTopSeries = mainChart.addLineSeries({
              color: '#ef4444',
              lineWidth: 2,
              title: `Supply ${idx + 1} Top`,
              priceLineVisible: false,
              lastValueVisible: false,
              lineStyle: 0, // solid
            });

            // Bottom of zone
            const supplyBottomSeries = mainChart.addLineSeries({
              color: '#ef4444',
              lineWidth: 2,
              title: `Supply ${idx + 1} Bottom`,
              priceLineVisible: false,
              lastValueVisible: false,
              lineStyle: 0, // solid
            });

            // Create zone data from zone time to end
            const zoneStartIndex = data.findIndex(d => Number(d.time) >= zone.time);
            const zoneData = data
              .slice(Math.max(0, zoneStartIndex - 5))
              .filter(item => item.time)
              .map(item => ({ time: Number(item.time) }))
              .sort((a, b) => a.time - b.time);

            const topData = zoneData.map(item => ({ ...item, value: zone.top }));
            const bottomData = zoneData.map(item => ({ ...item, value: zone.bottom }));

            supplyTopSeries.setData(topData);
            supplyBottomSeries.setData(bottomData);

            supplyDemandRefs.current.push(supplyTopSeries, supplyBottomSeries);
          });

          // Draw demand zones (support/buy zones) - green zones
          demandZones.slice(-5).forEach((zone, idx) => {
            // Top of zone
            const demandTopSeries = mainChart.addLineSeries({
              color: '#22c55e',
              lineWidth: 2,
              title: `Demand ${idx + 1} Top`,
              priceLineVisible: false,
              lastValueVisible: false,
              lineStyle: 0, // solid
            });

            // Bottom of zone
            const demandBottomSeries = mainChart.addLineSeries({
              color: '#22c55e',
              lineWidth: 2,
              title: `Demand ${idx + 1} Bottom`,
              priceLineVisible: false,
              lastValueVisible: false,
              lineStyle: 0, // solid
            });

            // Create zone data from zone time to end
            const zoneStartIndex = data.findIndex(d => Number(d.time) >= zone.time);
            const zoneData = data
              .slice(Math.max(0, zoneStartIndex - 5))
              .filter(item => item.time)
              .map(item => ({ time: Number(item.time) }))
              .sort((a, b) => a.time - b.time);

            const topData = zoneData.map(item => ({ ...item, value: zone.top }));
            const bottomData = zoneData.map(item => ({ ...item, value: zone.bottom }));

            demandTopSeries.setData(topData);
            demandBottomSeries.setData(bottomData);

            supplyDemandRefs.current.push(demandTopSeries, demandBottomSeries);
          });
        }

        // Add Elliott Wave Markers
        const hasElliott = data.some(item => item.wave_position != null || item.wave_1_high != null);
        console.log('Elliott Wave check - Has data?', hasElliott, 'showElliott:', showElliott);
        console.log('Sample Elliott data:', data.slice(-5).map(d => ({
          wave_position: d.wave_position,
          wave_1_high: d.wave_1_high,
          wave_3_high: d.wave_3_high,
          wave_5_high: d.wave_5_high,
          high: d.high
        })));

        // Add AUTOMATIC Elliott Wave detection
        if (showElliott && data.length >= 50) {
          const elliottWaves = detectElliottWaves(data);
          if (elliottWaves) {
            console.log('Automatic Elliott Waves detected:', elliottWaves);
            const autoElliottMarkers = [
              {
                time: elliottWaves.wave1.time,
                position: 'belowBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '1',
                size: 1,
              },
              {
                time: elliottWaves.wave2.time,
                position: 'aboveBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '2',
                size: 1,
              },
              {
                time: elliottWaves.wave3.time,
                position: 'belowBar',
                color: '#f97316',
                shape: 'circle',
                text: '3',
                size: 2,
              },
              {
                time: elliottWaves.wave4.time,
                position: 'aboveBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '4',
                size: 1,
              },
              {
                time: elliottWaves.wave5.time,
                position: 'belowBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '5',
                size: 1,
              },
            ];
            elliottMarkersRef.current.push(...autoElliottMarkers);
          }
        }

        if (showElliott && hasElliott) {
          console.log('Adding Elliott Wave markers to chart');
          const elliottMarkers = [];

          // Find the most recent data points with Elliott Wave data
          const recentData = data.slice(-100); // Look at last 100 candles

          recentData.forEach((item, idx) => {
            // Mark Wave 1 (peak)
            if (item.wave_1_high && item.high === item.wave_1_high) {
              elliottMarkers.push({
                time: Number(item.time),
                position: 'aboveBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '1',
                size: 1,
              });
            }

            // Mark Wave 2 (trough)
            if (item.wave_2_low && item.low === item.wave_2_low) {
              elliottMarkers.push({
                time: Number(item.time),
                position: 'belowBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '2',
                size: 1,
              });
            }

            // Mark Wave 3 (peak - usually the strongest)
            if (item.wave_3_high && item.high === item.wave_3_high) {
              elliottMarkers.push({
                time: Number(item.time),
                position: 'aboveBar',
                color: '#f97316',
                shape: 'circle',
                text: '3',
                size: 2,
              });
            }

            // Mark Wave 4 (trough)
            if (item.wave_4_low && item.low === item.wave_4_low) {
              elliottMarkers.push({
                time: Number(item.time),
                position: 'belowBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '4',
                size: 1,
              });
            }

            // Mark Wave 5 (peak)
            if (item.wave_5_high && item.high === item.wave_5_high) {
              elliottMarkers.push({
                time: Number(item.time),
                position: 'aboveBar',
                color: '#fbbf24',
                shape: 'circle',
                text: '5',
                size: 1,
              });
            }
          });

          // Store Elliott markers
          elliottMarkersRef.current = elliottMarkers;
        } else {
          elliottMarkersRef.current = [];
        }

        // Merge and apply all markers to candlestick series
        if (candlestickSeriesRef.current) {
          const allMarkers = [
            ...tradeMarkersRef.current,
            ...elliottMarkersRef.current,
            ...pivotHLMarkersRef.current,
          ];
          if (allMarkers.length > 0) {
            // Sort markers by time in ascending order (required by lightweight-charts)
            const sortedMarkers = allMarkers.sort((a, b) => a.time - b.time);
            candlestickSeriesRef.current.setMarkers(sortedMarkers);
          }
        }

        mainChart.timeScale().fitContent();
      }
    } catch (err) {
      console.error('Error creating main price chart:', err);
    }

    // ========== RSI CHART ==========
    try {
      const hasRSI = data.some(item => item.rsi != null);
      if (rsiContainerRef.current && hasRSI) {
        const rsiWidth = rsiContainerRef.current.clientWidth || 800;
        console.log(`Creating RSI chart: width=${rsiWidth}`);

        const rsiChart = createChart(rsiContainerRef.current, {
          ...chartOptions,
          width: rsiWidth,
          height: rsiHeight,
        });

        rsiChartRef.current = rsiChart;

        const rsiSeries = rsiChart.addLineSeries({
          color: '#a855f7',
          lineWidth: 2,
          priceLineVisible: false,
        });

        const rsiData = data
          .filter(item => item.rsi != null && item.time)
          .map(item => ({
            time: Number(item.time),
            value: Number(item.rsi),
          }))
          .sort((a, b) => a.time - b.time);

        if (rsiData.length > 0) {
          rsiSeries.setData(rsiData);

          // Add horizontal lines at 30 and 70 - use full data range for sync
          const overboughtLine = rsiChart.addLineSeries({
            color: '#ef4444',
            lineWidth: 1,
            lineStyle: 2, // dashed
            priceLineVisible: false,
          });
          // Use all data points, not just RSI data points
          const allTimePoints = data
            .filter(item => item.time)
            .map(item => ({ time: Number(item.time), value: 70 }))
            .sort((a, b) => a.time - b.time);
          overboughtLine.setData(allTimePoints);

          const oversoldLine = rsiChart.addLineSeries({
            color: '#10b981',
            lineWidth: 1,
            lineStyle: 2, // dashed
            priceLineVisible: false,
          });
          oversoldLine.setData(allTimePoints.map(item => ({ ...item, value: 30 })));

          rsiChart.timeScale().fitContent();
          rsiChart.priceScale('right').applyOptions({
            scaleMargins: {
              top: 0.1,
              bottom: 0.1,
            },
          });
        }
      }
    } catch (err) {
      console.error('Error creating RSI chart:', err);
    }

    // ========== VOLUME CHART ==========
    try {
      const hasVolume = data.some(item => item.volume != null);
      console.log('Volume - Has data?', hasVolume, 'Data length:', data.length);
      if (tradesContainerRef.current && hasVolume) {
        const volumeChartWidth = tradesContainerRef.current.clientWidth || 800;

        const volumeChart = createChart(tradesContainerRef.current, {
          ...chartOptions,
          width: volumeChartWidth,
          height: volumeHeight,
        });

        tradesChartRef.current = volumeChart;

        // Create histogram series for volume bars
        const volumeSeries = volumeChart.addHistogramSeries({
          priceFormat: {
            type: 'volume',
          },
          priceLineVisible: false,
        });

        // Prepare volume data with positive (buy) above center, negative (sell) below center
        const volumeData = data
          .map(item => {
            const volume = Number(item.volume || 0);
            const isBullish = (Number(item.close) || 0) >= (Number(item.open) || 0);

            return {
              time: Number(item.time || 0),
              // Positive for buy trades (above center), negative for sell trades (below center)
              value: isBullish ? volume : -volume,
              // Green for buy (above), Yellow for sell (below) - high contrast
              color: isBullish ? '#22c55e' : '#fbbf24',
            };
          })
          .filter(item => item.time > 0)
          .sort((a, b) => a.time - b.time);

        console.log('Volume data prepared:', volumeData.length, 'bars');

        if (volumeData.length > 0) {
          volumeSeries.setData(volumeData);
        }

        // Add zero center line
        const zeroLineSeries = volumeChart.addLineSeries({
          color: currentTheme.textMuted,
          lineWidth: 1,
          lineStyle: 2, // dashed
          priceLineVisible: false,
        });

        const zeroLineData = data
          .filter(item => item.time)
          .map(item => ({
            time: Number(item.time),
            value: 0,
          }))
          .sort((a, b) => a.time - b.time);

        if (zeroLineData.length > 0) {
          zeroLineSeries.setData(zeroLineData);
        }

        // Calculate trade signals for markers on main chart
        const markers = [];
        for (let i = 1; i < data.length; i++) {
          const prev = data[i - 1];
          const curr = data[i];

          if (!prev.macd || !prev.macd_signal || !curr.macd || !curr.macd_signal) continue;
          if (!prev.time || !curr.time) continue;

          const prevMACD = Number(prev.macd);
          const prevSignal = Number(prev.macd_signal);
          const currMACD = Number(curr.macd);
          const currSignal = Number(curr.macd_signal);

          // Bullish crossover: MACD crosses above Signal
          if (prevMACD <= prevSignal && currMACD > currSignal) {
            markers.push({
              time: Number(curr.time),
              position: 'belowBar',
              color: currentTheme.chart.upColor,
              shape: 'arrowUp',
              text: 'Buy',
            });
          }

          // Bearish crossover: MACD crosses below Signal
          if (prevMACD >= prevSignal && currMACD < currSignal) {
            markers.push({
              time: Number(curr.time),
              position: 'aboveBar',
              color: currentTheme.chart.downColor,
              shape: 'arrowDown',
              text: 'Sell',
            });
          }
        }

        // Store trade markers for merging with Elliott markers
        tradeMarkersRef.current = markers;

        // Apply buy/sell markers to the MAIN CHART candlestick series
        if (candlestickSeriesRef.current) {
          try {
            const allMarkers = [...tradeMarkersRef.current, ...elliottMarkersRef.current];
            console.log('Applying', allMarkers.length, 'markers to main chart (', tradeMarkersRef.current.length, 'trade +', elliottMarkersRef.current.length, 'elliott)');
            if (allMarkers.length > 0) {
              // Sort markers by time in ascending order (required by lightweight-charts)
              const sortedMarkers = allMarkers.sort((a, b) => a.time - b.time);
              candlestickSeriesRef.current.setMarkers(sortedMarkers);
            }
          } catch (err) {
            console.error('Error setting trade markers:', err);
          }
        }

        volumeChart.timeScale().fitContent();
        volumeChart.priceScale('right').applyOptions({
          scaleMargins: {
            top: 0.05,
            bottom: 0.05,
          },
        });
      }
    } catch (err) {
      console.error('Error creating volume chart:', err);
    }

    // ========== MACD HISTOGRAM CHART ==========
    try {
      const hasMACD = data.some(item => item.macd != null && item.macd_signal != null);
      if (macdContainerRef.current && hasMACD) {
        const macdWidth = macdContainerRef.current.clientWidth || 800;

        const macdChart = createChart(macdContainerRef.current, {
          ...chartOptions,
          width: macdWidth,
          height: macdHeight,
        });

        macdChartRef.current = macdChart;

        // MACD Histogram (MACD - Signal line difference)
        const macdHistogramSeries = macdChart.addHistogramSeries({
          priceFormat: {
            type: 'price',
            precision: 4,
          },
          priceLineVisible: false,
        });

        // Calculate MACD histogram values with positive/negative around zero
        const macdHistogramData = data
          .filter(item => item.macd != null && item.macd_signal != null && item.time)
          .map(item => {
            const macdValue = Number(item.macd);
            const signalValue = Number(item.macd_signal);
            const histValue = macdValue - signalValue;

            return {
              time: Number(item.time),
              value: histValue,
              // Green if positive (MACD above signal), Red if negative (MACD below signal)
              color: histValue >= 0 ? currentTheme.chart.volumeUpColor : currentTheme.chart.volumeDownColor,
            };
          })
          .sort((a, b) => a.time - b.time);

        if (macdHistogramData.length > 0) {
          macdHistogramSeries.setData(macdHistogramData);
        }

        // MACD Fast Line (blue)
        const macdLineSeries = macdChart.addLineSeries({
          color: '#2196f3',
          lineWidth: 2,
          priceLineVisible: false,
          title: 'MACD',
        });

        const macdLineData = data
          .filter(item => item.macd != null && item.time)
          .map(item => ({
            time: Number(item.time),
            value: Number(item.macd),
          }))
          .sort((a, b) => a.time - b.time);

        if (macdLineData.length > 0) {
          macdLineSeries.setData(macdLineData);
        }

        // MACD Signal line (orange)
        const macdSignalSeries = macdChart.addLineSeries({
          color: '#ff9800',
          lineWidth: 2,
          priceLineVisible: false,
          title: 'Signal',
        });

        const macdSignalData = data
          .filter(item => item.macd_signal != null && item.time)
          .map(item => ({
            time: Number(item.time),
            value: Number(item.macd_signal),
          }))
          .sort((a, b) => a.time - b.time);

        if (macdSignalData.length > 0) {
          macdSignalSeries.setData(macdSignalData);
        }

        // Add zero line for reference
        const zeroLineSeries = macdChart.addLineSeries({
          color: currentTheme.textMuted,
          lineWidth: 1,
          lineStyle: 2, // dashed
          priceLineVisible: false,
        });

        const zeroLineData = data
          .filter(item => item.time)
          .map(item => ({
            time: Number(item.time),
            value: 0,
          }))
          .sort((a, b) => a.time - b.time);

        if (zeroLineData.length > 0) {
          zeroLineSeries.setData(zeroLineData);
        }

        macdChart.timeScale().fitContent();
        macdChart.priceScale('right').applyOptions({
          scaleMargins: {
            top: 0.2,
            bottom: 0.2,
          },
        });
      }
    } catch (err) {
      console.error('Error creating MACD chart:', err);
    }

    // Sync time scales
    const handleTimeScaleChange = () => {
      try {
        const visibleLogicalRange = mainChartRef.current?.timeScale()?.getVisibleLogicalRange();
        if (visibleLogicalRange && rsiChartRef.current) {
          try {
            rsiChartRef.current.timeScale().setVisibleLogicalRange(visibleLogicalRange);
          } catch (err) {
            console.error('Error syncing RSI timescale:', err);
          }
        }
        if (visibleLogicalRange && tradesChartRef.current) {
          try {
            tradesChartRef.current.timeScale().setVisibleLogicalRange(visibleLogicalRange);
          } catch (err) {
            console.error('Error syncing Volume timescale:', err);
          }
        }
        if (visibleLogicalRange && macdChartRef.current) {
          try {
            macdChartRef.current.timeScale().setVisibleLogicalRange(visibleLogicalRange);
          } catch (err) {
            console.error('Error syncing MACD timescale:', err);
          }
        }
      } catch (err) {
        console.error('Error in time scale change handler:', err);
      }
    };

    try {
      if (mainChartRef.current) {
        mainChartRef.current.timeScale().subscribeVisibleLogicalRangeChange(handleTimeScaleChange);

        // Initial synchronization: set all charts to match main chart's time range
        // Use a longer delay to ensure all charts are fully rendered
        setTimeout(() => {
          try {
            const visibleLogicalRange = mainChartRef.current?.timeScale()?.getVisibleLogicalRange();
            console.log('Initial sync - visible range:', visibleLogicalRange);
            if (visibleLogicalRange) {
              if (rsiChartRef.current) {
                console.log('Syncing RSI chart to main chart time range');
                rsiChartRef.current.timeScale().setVisibleLogicalRange(visibleLogicalRange);
              }
              if (tradesChartRef.current) {
                console.log('Syncing Volume chart to main chart time range');
                tradesChartRef.current.timeScale().setVisibleLogicalRange(visibleLogicalRange);
              }
              if (macdChartRef.current) {
                console.log('Syncing MACD chart to main chart time range');
                macdChartRef.current.timeScale().setVisibleLogicalRange(visibleLogicalRange);
              }
            }
          } catch (err) {
            console.error('Error in initial time scale sync:', err);
          }
        }, 500);
      }
    } catch (err) {
      console.error('Error subscribing to time scale changes:', err);
    }

    // Handle resize
    const handleResize = () => {
      try {
        if (mainContainerRef.current && mainChartRef.current) {
          mainChartRef.current.applyOptions({
            width: mainContainerRef.current.clientWidth,
          });
        }
      } catch (err) {
        console.error('Error resizing main chart:', err);
      }

      try {
        if (rsiContainerRef.current && rsiChartRef.current) {
          rsiChartRef.current.applyOptions({
            width: rsiContainerRef.current.clientWidth,
          });
        }
      } catch (err) {
        console.error('Error resizing RSI chart:', err);
      }

      try {
        if (macdContainerRef.current && macdChartRef.current) {
          macdChartRef.current.applyOptions({
            width: macdContainerRef.current.clientWidth,
          });
        }
      } catch (err) {
        console.error('Error resizing MACD chart:', err);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      try {
        window.removeEventListener('resize', handleResize);
      } catch (err) {
        console.error('Error removing resize listener:', err);
      }

      try {
        if (mainChartRef.current) {
          mainChartRef.current.remove();
          mainChartRef.current = null;
        }
      } catch (err) {
        console.error('Error cleaning up main chart on unmount:', err);
      }

      try {
        if (rsiChartRef.current) {
          rsiChartRef.current.remove();
          rsiChartRef.current = null;
        }
      } catch (err) {
        console.error('Error cleaning up RSI chart on unmount:', err);
      }

      try {
        if (macdChartRef.current) {
          macdChartRef.current.remove();
          macdChartRef.current = null;
        }
      } catch (err) {
        console.error('Error cleaning up MACD chart on unmount:', err);
      }
    };
  }, [data, theme, showSMA20, showSMA50, showEMA12, showBB, showFib, showElliott, showSupportResistance, showSupplyDemand, showPivotPoints, showPivotHL, mainHeight, rsiHeight, volumeHeight, macdHeight]);

  if (loading) {
    return (
      <div style={{
        padding: '48px',
        textAlign: 'center',
        color: currentTheme.textSecondary,
      }}>
        Loading chart data...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '48px',
        textAlign: 'center',
        background: currentTheme.cardBg,
        borderRadius: '12px',
        border: `1px solid ${currentTheme.cardBorder}`,
      }}>
        <div style={{ color: '#ef4444', fontSize: '18px', marginBottom: '12px' }}>
          ⚠️ Error Loading Chart
        </div>
        <div style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: currentTheme.cardBg,
      borderRadius: '12px',
      border: `1px solid ${currentTheme.cardBorder}`,
      overflow: 'hidden',
    }}>
      {/* Header with symbol info, controls, and legend */}
      <div style={{
        padding: '16px 24px',
        borderBottom: `1px solid ${currentTheme.cardBorder}`,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        {/* Left: Symbol and OHLC */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <h2 style={{
            color: currentTheme.text,
            fontSize: '20px',
            margin: 0,
            fontWeight: '600',
            textAlign: 'left',
          }}>
            {symbol}
          </h2>
          {latestData && (
            <div style={{ display: 'flex', gap: '16px', fontSize: '14px' }}>
              <span style={{ color: currentTheme.textSecondary }}>
                O: <strong style={{ color: currentTheme.text }}>${latestData.open?.toFixed(2)}</strong>
              </span>
              <span style={{ color: currentTheme.textSecondary }}>
                H: <strong style={{ color: '#10b981' }}>${latestData.high?.toFixed(2)}</strong>
              </span>
              <span style={{ color: currentTheme.textSecondary }}>
                L: <strong style={{ color: '#ef4444' }}>${latestData.low?.toFixed(2)}</strong>
              </span>
              <span style={{ color: currentTheme.textSecondary }}>
                C: <strong style={{ color: currentTheme.text }}>${latestData.close?.toFixed(2)}</strong>
              </span>
            </div>
          )}
        </div>

        {/* Center: Zoom Controls */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button
            onClick={() => mainChartRef.current?.timeScale().resetTimeScale()}
            style={{
              padding: '6px 12px',
              background: currentTheme.cardBg,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '6px',
              color: currentTheme.text,
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: '600',
            }}
            title="Reset zoom"
          >
            Reset
          </button>
          <button
            onClick={() => mainChartRef.current?.timeScale().scrollToPosition(5, false)}
            style={{
              padding: '6px 10px',
              background: currentTheme.cardBg,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '6px',
              color: currentTheme.text,
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
            }}
            title="Zoom out"
          >
            −
          </button>
          <button
            onClick={() => mainChartRef.current?.timeScale().scrollToPosition(-5, false)}
            style={{
              padding: '6px 10px',
              background: currentTheme.cardBg,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '6px',
              color: currentTheme.text,
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
            }}
            title="Zoom in"
          >
            +
          </button>
        </div>

        {/* Right: Indicator toggles */}
        <div style={{
          display: 'flex',
          gap: '12px',
          fontSize: '12px',
          textAlign: 'left',
          alignItems: 'center',
        }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showSMA20}
              onChange={(e) => {
                setShowSMA20(e.target.checked);
                if (sma20SeriesRef.current) {
                  sma20SeriesRef.current.applyOptions({ visible: e.target.checked });
                }
              }}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: currentTheme.indicators.sma20 }} />
            <span style={{ color: currentTheme.textSecondary }}>SMA 20</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showSMA50}
              onChange={(e) => {
                setShowSMA50(e.target.checked);
                if (sma50SeriesRef.current) {
                  sma50SeriesRef.current.applyOptions({ visible: e.target.checked });
                }
              }}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: currentTheme.indicators.sma50 }} />
            <span style={{ color: currentTheme.textSecondary }}>SMA 50</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showEMA12}
              onChange={(e) => {
                setShowEMA12(e.target.checked);
                if (ema12SeriesRef.current) {
                  ema12SeriesRef.current.applyOptions({ visible: e.target.checked });
                }
              }}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: currentTheme.indicators.ema12 }} />
            <span style={{ color: currentTheme.textSecondary }}>EMA 12</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showBB}
              onChange={(e) => {
                setShowBB(e.target.checked);
                if (bbSeriesRefs.current.upper) {
                  bbSeriesRefs.current.upper.applyOptions({ visible: e.target.checked });
                }
                if (bbSeriesRefs.current.middle) {
                  bbSeriesRefs.current.middle.applyOptions({ visible: e.target.checked });
                }
                if (bbSeriesRefs.current.lower) {
                  bbSeriesRefs.current.lower.applyOptions({ visible: e.target.checked });
                }
              }}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#60a5fa' }} />
            <span style={{ color: currentTheme.textSecondary }}>Bollinger</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showFib}
              onChange={(e) => {
                setShowFib(e.target.checked);
                fibSeriesRefs.current.forEach(series => {
                  if (series) {
                    series.applyOptions({ visible: e.target.checked });
                  }
                });
              }}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#a855f7' }} />
            <span style={{ color: currentTheme.textSecondary }}>Fibonacci</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showElliott}
              onChange={(e) => {
                setShowElliott(e.target.checked);
                // Elliott waves use markers, which require recreating the chart
                // For now, just update state and let the chart recreate on next render
              }}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#fbbf24' }} />
            <span style={{ color: currentTheme.textSecondary }}>Elliott Wave</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showSupportResistance}
              onChange={(e) => setShowSupportResistance(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#ef4444' }} />
            <span style={{ color: currentTheme.textSecondary }}>Support/Resistance</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showSupplyDemand}
              onChange={(e) => setShowSupplyDemand(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#22c55e' }} />
            <span style={{ color: currentTheme.textSecondary }}>Supply/Demand</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showPivotPoints}
              onChange={(e) => setShowPivotPoints(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#f59e0b' }} />
            <span style={{ color: currentTheme.textSecondary }}>Pivot Points</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showPivotHL}
              onChange={(e) => setShowPivotHL(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            <div style={{ width: '16px', height: '2px', background: '#3b82f6' }} />
            <span style={{ color: currentTheme.textSecondary }}>Pivot H/L</span>
          </label>
        </div>
      </div>

      {/* Main Price Chart */}
      <div style={{ position: 'relative' }}>
        <div style={{
          position: 'absolute',
          top: '8px',
          left: '12px',
          fontSize: '11px',
          color: currentTheme.textSecondary,
          fontWeight: '600',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          <span>PRICE CHART</span>
          <select
            value={mainHeight}
            onChange={(e) => setMainHeight(Number(e.target.value))}
            style={{
              fontSize: '10px',
              padding: '2px 6px',
              background: currentTheme.background,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            <option value={300}>300px</option>
            <option value={400}>400px</option>
            <option value={500}>500px</option>
            <option value={600}>600px</option>
            <option value={700}>700px</option>
            <option value={800}>800px</option>
          </select>
        </div>
        <div ref={mainContainerRef} style={{ width: '100%', maxWidth: '100%', height: `${mainHeight}px`, overflow: 'hidden' }} />
      </div>

      {/* RSI Panel */}
      {data.some(item => item.rsi != null) && (
        <div style={{
          borderTop: `1px solid ${currentTheme.cardBorder}`,
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute',
            top: '8px',
            left: '12px',
            fontSize: '11px',
            color: currentTheme.textSecondary,
            fontWeight: '600',
            zIndex: 10,
            textAlign: 'left',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            <span>RSI {latestData?.rsi ? `(${latestData.rsi.toFixed(2)})` : ''}</span>
            <select
              value={rsiHeight}
              onChange={(e) => setRsiHeight(Number(e.target.value))}
              style={{
                fontSize: '10px',
                padding: '2px 6px',
                background: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.cardBorder}`,
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              <option value={80}>80px</option>
              <option value={100}>100px</option>
              <option value={120}>120px</option>
              <option value={150}>150px</option>
              <option value={180}>180px</option>
              <option value={200}>200px</option>
            </select>
          </div>
          <div ref={rsiContainerRef} style={{ width: '100%', maxWidth: '100%', height: `${rsiHeight}px`, overflow: 'hidden' }} />
        </div>
      )}

      {/* Trade Signals Panel */}
      {data.some(item => item.macd != null && item.macd_signal != null) && (
        <div style={{
          borderTop: `1px solid ${currentTheme.cardBorder}`,
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute',
            top: '8px',
            left: '12px',
            fontSize: '11px',
            color: currentTheme.textSecondary,
            fontWeight: '600',
            zIndex: 10,
            textAlign: 'left',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            <span>VOLUME</span>
            <select
              value={volumeHeight}
              onChange={(e) => setVolumeHeight(Number(e.target.value))}
              style={{
                fontSize: '10px',
                padding: '2px 6px',
                background: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.cardBorder}`,
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              <option value={150}>150px</option>
              <option value={200}>200px</option>
              <option value={250}>250px</option>
              <option value={300}>300px</option>
              <option value={350}>350px</option>
              <option value={400}>400px</option>
            </select>
          </div>
          <div ref={tradesContainerRef} style={{ width: '100%', maxWidth: '100%', height: `${volumeHeight}px`, overflow: 'hidden' }} />
        </div>
      )}

      {/* MACD Panel */}
      {data.some(item => item.macd != null) && (
        <div style={{
          borderTop: `1px solid ${currentTheme.cardBorder}`,
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute',
            top: '8px',
            left: '12px',
            fontSize: '11px',
            color: currentTheme.textSecondary,
            fontWeight: '600',
            zIndex: 10,
            textAlign: 'left',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            <span>
              MACD {latestData?.macd ? `(${latestData.macd.toFixed(4)})` : ''}
              {latestData?.macd_signal && (
                <span style={{ marginLeft: '8px', color: currentTheme.indicators.sma50 }}>
                  Signal: {latestData.macd_signal.toFixed(4)}
                </span>
              )}
            </span>
            <select
              value={macdHeight}
              onChange={(e) => setMacdHeight(Number(e.target.value))}
              style={{
                fontSize: '10px',
                padding: '2px 6px',
                background: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.cardBorder}`,
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              <option value={150}>150px</option>
              <option value={180}>180px</option>
              <option value={200}>200px</option>
              <option value={250}>250px</option>
              <option value={300}>300px</option>
              <option value={350}>350px</option>
            </select>
          </div>
          <div ref={macdContainerRef} style={{ width: '100%', maxWidth: '100%', height: `${macdHeight}px`, overflow: 'hidden' }} />
        </div>
      )}
    </div>
  );
}
