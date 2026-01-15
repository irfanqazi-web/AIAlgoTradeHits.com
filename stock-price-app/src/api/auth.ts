/**
 * Auth API - Authentication route handlers
 *
 * Handles all authentication-related API calls.
 *
 * @version 5.1.0
 */

import { apiClient, ApiResponse } from './client';
import { API_CONFIG } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: {
    id: string;
    email: string;
    name: string;
    role: 'admin' | 'user' | 'viewer';
  };
  token: string;
  expiresAt: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface SessionInfo {
  userId: string;
  email: string;
  role: string;
  isValid: boolean;
  expiresAt: string;
}

// ============================================================================
// § 2. API FUNCTIONS
// ============================================================================

/**
 * Login user
 */
export async function login(
  credentials: LoginRequest
): Promise<ApiResponse<LoginResponse>> {
  return apiClient.post<LoginResponse>(API_CONFIG.endpoints.auth.login, credentials);
}

/**
 * Logout user
 */
export async function logout(): Promise<ApiResponse<{ success: boolean }>> {
  return apiClient.post<{ success: boolean }>(API_CONFIG.endpoints.auth.logout);
}

/**
 * Change password
 */
export async function changePassword(
  data: ChangePasswordRequest
): Promise<ApiResponse<{ success: boolean }>> {
  return apiClient.post<{ success: boolean }>(API_CONFIG.endpoints.auth.changePassword, data);
}

/**
 * Register new user
 */
export async function register(
  data: RegisterRequest
): Promise<ApiResponse<LoginResponse>> {
  return apiClient.post<LoginResponse>(API_CONFIG.endpoints.auth.register, data);
}

/**
 * Get current session info
 */
export async function getSession(): Promise<ApiResponse<SessionInfo>> {
  return apiClient.get<SessionInfo>(API_CONFIG.endpoints.auth.session);
}

/**
 * Refresh session token
 */
export async function refreshSession(): Promise<ApiResponse<{ token: string; expiresAt: string }>> {
  return apiClient.post<{ token: string; expiresAt: string }>(API_CONFIG.endpoints.auth.refresh);
}

/**
 * Request password reset
 */
export async function requestPasswordReset(
  email: string
): Promise<ApiResponse<{ success: boolean; message: string }>> {
  return apiClient.post<{ success: boolean; message: string }>(
    API_CONFIG.endpoints.auth.resetPassword,
    { email }
  );
}

// ============================================================================
// § 3. EXPORT
// ============================================================================

export const authApi = {
  login,
  logout,
  changePassword,
  register,
  getSession,
  refreshSession,
  requestPasswordReset,
};

export default authApi;
