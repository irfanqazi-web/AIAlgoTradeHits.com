/**
 * API Layer - Unified API exports
 *
 * Single entry point for all API functionality.
 * Provides route-based handlers organized by domain.
 *
 * @version 5.1.0
 */

// ============================================================================
// § 1. CLIENT
// ============================================================================

export { apiClient, type ApiResponse, type RequestConfig } from './client';

// ============================================================================
// § 2. ROUTE HANDLERS
// ============================================================================

// Market API
export { marketApi } from './market';
export type { Symbol, Candle, LivePrice, SearchResult } from './market';

// AI API
export { aiApi } from './ai';
export type {
  TradingSignal,
  NestedSignal,
  RiseCycleCandidate,
  MLPrediction,
  GrowthScreenerResult,
  TextToSQLResponse,
  PatternRecognition,
} from './ai';

// Auth API
export { authApi } from './auth';
export type {
  LoginRequest,
  LoginResponse,
  ChangePasswordRequest,
  RegisterRequest,
  SessionInfo,
} from './auth';

// Admin API
export { adminApi } from './admin';
export type {
  AdminUser,
  CreateUserRequest,
  UpdateUserRequest,
  SystemHealth,
  TableCount,
  SchedulerJob,
  AuditLogEntry,
} from './admin';

// Data API
export { dataApi } from './data';
export type {
  DataExportRequest,
  DataExportResponse,
  DataGap,
  DataQualityReport,
  MLTrainingData,
  ReconciliationResult,
} from './data';

// ============================================================================
// § 3. UNIFIED API OBJECT
// ============================================================================

import { marketApi } from './market';
import { aiApi } from './ai';
import { authApi } from './auth';
import { adminApi } from './admin';
import { dataApi } from './data';

/**
 * Unified API object for convenient access
 *
 * @example
 * import { api } from '@/api';
 *
 * // Market data
 * const symbols = await api.market.getSymbols();
 * const history = await api.market.getHistory('AAPL');
 *
 * // AI signals
 * const signals = await api.ai.getTradingSignals();
 *
 * // Auth
 * const result = await api.auth.login({ email, password });
 *
 * // Admin
 * const users = await api.admin.getUsers();
 *
 * // Data
 * const gaps = await api.data.getDataGaps();
 */
export const api = {
  market: marketApi,
  ai: aiApi,
  auth: authApi,
  admin: adminApi,
  data: dataApi,
} as const;

export default api;
