/**
 * Auth Context - Global authentication state management
 *
 * Manages user authentication state, login/logout, and session persistence.
 *
 * @version 5.1.0
 */

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { API_CONFIG } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  isFirstLogin?: boolean;
  createdAt?: string;
  lastLogin?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<boolean>;
  clearError: () => void;
  refreshSession: () => Promise<void>;
}

interface AuthProviderProps {
  children: ReactNode;
}

// ============================================================================
// § 2. CONTEXT
// ============================================================================

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Storage keys
const AUTH_STORAGE_KEY = 'aialgotradehits-auth';
const SESSION_STORAGE_KEY = 'aialgotradehits-session';

// ============================================================================
// § 3. PROVIDER
// ============================================================================

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  // Initialize from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const stored = localStorage.getItem(AUTH_STORAGE_KEY);
        if (stored) {
          const user = JSON.parse(stored) as User;
          setState({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };
    initAuth();
  }, []);

  // Login function
  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.auth.login}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const user: User = {
          id: data.user?.id || email,
          email: data.user?.email || email,
          name: data.user?.name || email.split('@')[0],
          role: data.user?.role || 'user',
          isFirstLogin: data.user?.is_first_login || false,
          lastLogin: new Date().toISOString(),
        };

        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
        sessionStorage.setItem(SESSION_STORAGE_KEY, 'active');

        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });

        return true;
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: data.error || 'Login failed',
        }));
        return false;
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Network error',
      }));
      return false;
    }
  }, []);

  // Logout function
  const logout = useCallback(async (): Promise<void> => {
    try {
      await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.auth.logout}`, {
        method: 'POST',
      });
    } catch {
      // Continue with local logout even if API fails
    }

    localStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(SESSION_STORAGE_KEY);

    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  }, []);

  // Change password function
  const changePassword = useCallback(async (
    oldPassword: string,
    newPassword: string
  ): Promise<boolean> => {
    if (!state.user) return false;

    try {
      const response = await fetch(
        `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.auth.changePassword}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: state.user.email,
            old_password: oldPassword,
            new_password: newPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok && data.success) {
        // Update user to remove first login flag
        const updatedUser = { ...state.user, isFirstLogin: false };
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(updatedUser));
        setState(prev => ({ ...prev, user: updatedUser }));
        return true;
      }

      setState(prev => ({
        ...prev,
        error: data.error || 'Password change failed',
      }));
      return false;
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Network error',
      }));
      return false;
    }
  }, [state.user]);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Refresh session
  const refreshSession = useCallback(async () => {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      const user = JSON.parse(stored) as User;
      setState(prev => ({
        ...prev,
        user,
        isAuthenticated: true,
      }));
    }
  }, []);

  const value: AuthContextValue = {
    ...state,
    login,
    logout,
    changePassword,
    clearError,
    refreshSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================================
// § 4. HOOK
// ============================================================================

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
