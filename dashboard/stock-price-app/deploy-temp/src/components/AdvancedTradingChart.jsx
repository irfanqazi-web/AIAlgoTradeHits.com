import TradingViewChart from './TradingViewChart';

/**
 * Wrapper for TradingViewChart to maintain backward compatibility
 * Supports assetType for all 7 market types
 */
export default function AdvancedTradingChart({ symbol, marketType, assetType, timeframe, theme = 'dark' }) {
  return (
    <TradingViewChart
      symbol={symbol}
      marketType={marketType}
      assetType={assetType}
      timeframe={timeframe}
      theme={theme}
    />
  );
}
