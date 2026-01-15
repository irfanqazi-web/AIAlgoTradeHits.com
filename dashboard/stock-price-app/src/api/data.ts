/**
 * Data API - Data warehouse route handlers
 *
 * Handles all data-related API calls for exports, downloads,
 * and data warehouse operations.
 *
 * @version 5.1.0
 */

import { apiClient, ApiResponse } from './client';
import { API_CONFIG, AssetType, Timeframe } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface DataExportRequest {
  assetType: AssetType;
  symbols: string[];
  timeframe: Timeframe;
  startDate: string;
  endDate: string;
  fields: string[];
  format: 'csv' | 'json' | 'xlsx';
}

export interface DataExportResponse {
  exportId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  downloadUrl?: string;
  rowCount?: number;
  fileSize?: number;
  expiresAt?: string;
}

export interface DataGap {
  symbol: string;
  assetType: AssetType;
  timeframe: Timeframe;
  startDate: string;
  endDate: string;
  missingDays: number;
}

export interface DataQualityReport {
  table: string;
  totalRows: number;
  nullCounts: Record<string, number>;
  duplicateCount: number;
  dateRange: {
    min: string;
    max: string;
  };
  lastUpdated: string;
}

export interface MLTrainingData {
  symbol: string;
  features: Record<string, number>[];
  labels: string[];
  metadata: {
    featureNames: string[];
    rowCount: number;
    dateRange: { start: string; end: string };
  };
}

export interface ReconciliationResult {
  table: string;
  expectedCount: number;
  actualCount: number;
  discrepancy: number;
  status: 'ok' | 'warning' | 'error';
}

// ============================================================================
// § 2. EXPORT FUNCTIONS
// ============================================================================

/**
 * Request data export
 */
export async function requestExport(
  request: DataExportRequest
): Promise<ApiResponse<DataExportResponse>> {
  return apiClient.post<DataExportResponse>(API_CONFIG.endpoints.data.export, request);
}

/**
 * Get export status
 */
export async function getExportStatus(
  exportId: string
): Promise<ApiResponse<DataExportResponse>> {
  return apiClient.get<DataExportResponse>(`${API_CONFIG.endpoints.data.export}/${exportId}`);
}

/**
 * Download exported data
 */
export async function downloadExport(
  exportId: string
): Promise<ApiResponse<Blob>> {
  return apiClient.get<Blob>(`${API_CONFIG.endpoints.data.download}/${exportId}`);
}

/**
 * Get ML training data
 */
export async function getMLTrainingData(
  symbol: string,
  assetType: AssetType = 'stocks',
  days = 365
): Promise<ApiResponse<MLTrainingData>> {
  const params = {
    symbol,
    asset_type: assetType,
    days,
  };
  return apiClient.get<MLTrainingData>(API_CONFIG.endpoints.data.mlTraining, params);
}

// ============================================================================
// § 3. DATA QUALITY FUNCTIONS
// ============================================================================

/**
 * Get data gaps
 */
export async function getDataGaps(
  assetType?: AssetType
): Promise<ApiResponse<DataGap[]>> {
  const params: Record<string, string> = {};
  if (assetType) {
    params.asset_type = assetType;
  }
  return apiClient.get<DataGap[]>(API_CONFIG.endpoints.data.gaps, params);
}

/**
 * Get data quality report
 */
export async function getDataQualityReport(
  table?: string
): Promise<ApiResponse<DataQualityReport[]>> {
  const params: Record<string, string> = {};
  if (table) {
    params.table = table;
  }
  return apiClient.get<DataQualityReport[]>(API_CONFIG.endpoints.data.quality, params);
}

/**
 * Run data reconciliation
 */
export async function runReconciliation(): Promise<ApiResponse<ReconciliationResult[]>> {
  return apiClient.post<ReconciliationResult[]>(API_CONFIG.endpoints.data.reconciliation);
}

/**
 * Trigger data backfill
 */
export async function triggerBackfill(
  assetType: AssetType,
  symbols: string[],
  startDate: string,
  endDate: string
): Promise<ApiResponse<{ jobId: string; status: string }>> {
  return apiClient.post<{ jobId: string; status: string }>(API_CONFIG.endpoints.data.backfill, {
    asset_type: assetType,
    symbols,
    start_date: startDate,
    end_date: endDate,
  });
}

// ============================================================================
// § 4. WAREHOUSE OPERATIONS
// ============================================================================

/**
 * Get warehouse statistics
 */
export async function getWarehouseStats(): Promise<ApiResponse<{
  totalTables: number;
  totalRows: number;
  storageBytes: number;
  lastSync: string;
}>> {
  return apiClient.get(API_CONFIG.endpoints.data.warehouseStats);
}

/**
 * Get available fields for a table
 */
export async function getTableFields(
  table: string
): Promise<ApiResponse<{ name: string; type: string; description: string }[]>> {
  return apiClient.get(`${API_CONFIG.endpoints.data.tableFields}/${table}`);
}

// ============================================================================
// § 5. EXPORT
// ============================================================================

export const dataApi = {
  // Exports
  requestExport,
  getExportStatus,
  downloadExport,
  getMLTrainingData,
  // Data quality
  getDataGaps,
  getDataQualityReport,
  runReconciliation,
  triggerBackfill,
  // Warehouse
  getWarehouseStats,
  getTableFields,
};

export default dataApi;
