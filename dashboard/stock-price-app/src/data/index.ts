/**
 * Data Layer - Data access and transformation
 *
 * Provides clean abstraction between API calls and business logic.
 * All data transformations happen here.
 *
 * @version 5.1.0
 */

export { marketDataService } from './market';
export { aiDataService } from './ai';
export { userDataService } from './user';

export type {
  MarketDataPoint,
  CandleData,
  SymbolInfo,
  TimeframeData,
} from './market';

export type {
  SignalData,
  PredictionData,
  GrowthData,
} from './ai';

export type {
  UserProfile,
  UserPreferences,
} from './user';
