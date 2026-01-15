/**
 * Service Layer - Export all services
 * Orchestration between data sources and engines
 */

// Market Data Service
export { marketDataService } from './market-data-service';
export { default as MarketDataService } from './market-data-service';

// Trading Signal Service
export { tradingSignalService } from './trading-signal-service';
export { default as TradingSignalService } from './trading-signal-service';

// Service version
export const SERVICE_VERSION = "3.0.0";
