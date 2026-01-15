/**
 * Admin API - Administrative route handlers
 *
 * Handles all admin-related API calls for user management,
 * system monitoring, and configuration.
 *
 * @version 5.1.0
 */

import { apiClient, ApiResponse } from './client';
import { API_CONFIG } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  status: 'active' | 'inactive' | 'pending';
  createdAt: string;
  lastLogin?: string;
}

export interface CreateUserRequest {
  email: string;
  name: string;
  password: string;
  role: 'admin' | 'user' | 'viewer';
}

export interface UpdateUserRequest {
  name?: string;
  role?: 'admin' | 'user' | 'viewer';
  status?: 'active' | 'inactive';
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    name: string;
    status: 'up' | 'down';
    latency?: number;
    lastCheck: string;
  }[];
  uptime: number;
  version: string;
}

export interface TableCount {
  table: string;
  count: number;
  lastUpdated: string;
  schema: string;
}

export interface SchedulerJob {
  name: string;
  schedule: string;
  lastRun?: string;
  nextRun: string;
  status: 'active' | 'paused' | 'failed';
  lastResult?: 'success' | 'failure';
}

export interface AuditLogEntry {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: string;
  details?: Record<string, unknown>;
}

// ============================================================================
// § 2. USER MANAGEMENT
// ============================================================================

/**
 * Get all users
 */
export async function getUsers(): Promise<ApiResponse<AdminUser[]>> {
  return apiClient.get<AdminUser[]>(API_CONFIG.endpoints.admin.users);
}

/**
 * Get user by ID
 */
export async function getUserById(userId: string): Promise<ApiResponse<AdminUser>> {
  return apiClient.get<AdminUser>(`${API_CONFIG.endpoints.admin.users}/${userId}`);
}

/**
 * Create new user
 */
export async function createUser(
  data: CreateUserRequest
): Promise<ApiResponse<AdminUser>> {
  return apiClient.post<AdminUser>(API_CONFIG.endpoints.admin.users, data);
}

/**
 * Update user
 */
export async function updateUser(
  userId: string,
  data: UpdateUserRequest
): Promise<ApiResponse<AdminUser>> {
  return apiClient.put<AdminUser>(`${API_CONFIG.endpoints.admin.users}/${userId}`, data);
}

/**
 * Delete user
 */
export async function deleteUser(
  userId: string
): Promise<ApiResponse<{ success: boolean }>> {
  return apiClient.delete<{ success: boolean }>(`${API_CONFIG.endpoints.admin.users}/${userId}`);
}

/**
 * Reset user password
 */
export async function resetUserPassword(
  userId: string
): Promise<ApiResponse<{ temporaryPassword: string }>> {
  return apiClient.post<{ temporaryPassword: string }>(
    `${API_CONFIG.endpoints.admin.users}/${userId}/reset-password`
  );
}

// ============================================================================
// § 3. SYSTEM MONITORING
// ============================================================================

/**
 * Get system health status
 */
export async function getSystemHealth(): Promise<ApiResponse<SystemHealth>> {
  return apiClient.get<SystemHealth>(API_CONFIG.endpoints.admin.health);
}

/**
 * Get table counts
 */
export async function getTableCounts(): Promise<ApiResponse<TableCount[]>> {
  return apiClient.get<TableCount[]>(API_CONFIG.endpoints.admin.tableCounts);
}

/**
 * Get scheduler jobs
 */
export async function getSchedulerJobs(): Promise<ApiResponse<SchedulerJob[]>> {
  return apiClient.get<SchedulerJob[]>(API_CONFIG.endpoints.admin.schedulers);
}

/**
 * Trigger scheduler job manually
 */
export async function triggerSchedulerJob(
  jobName: string
): Promise<ApiResponse<{ triggered: boolean; jobId: string }>> {
  return apiClient.post<{ triggered: boolean; jobId: string }>(
    `${API_CONFIG.endpoints.admin.schedulers}/${jobName}/trigger`
  );
}

/**
 * Get audit logs
 */
export async function getAuditLogs(
  limit = 100,
  offset = 0
): Promise<ApiResponse<AuditLogEntry[]>> {
  return apiClient.get<AuditLogEntry[]>(API_CONFIG.endpoints.admin.logs, { limit, offset });
}

// ============================================================================
// § 4. CONFIGURATION
// ============================================================================

/**
 * Get system configuration
 */
export async function getConfig(): Promise<ApiResponse<Record<string, unknown>>> {
  return apiClient.get<Record<string, unknown>>(API_CONFIG.endpoints.admin.config);
}

/**
 * Update system configuration
 */
export async function updateConfig(
  config: Record<string, unknown>
): Promise<ApiResponse<{ success: boolean }>> {
  return apiClient.put<{ success: boolean }>(API_CONFIG.endpoints.admin.config, config);
}

// ============================================================================
// § 5. EXPORT
// ============================================================================

export const adminApi = {
  // User management
  getUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser,
  resetUserPassword,
  // System monitoring
  getSystemHealth,
  getTableCounts,
  getSchedulerJobs,
  triggerSchedulerJob,
  getAuditLogs,
  // Configuration
  getConfig,
  updateConfig,
};

export default adminApi;
