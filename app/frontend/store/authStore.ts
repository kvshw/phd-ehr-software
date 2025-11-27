/**
 * Authentication store using Zustand
 */
import { create } from 'zustand';
import { User, login as loginApi, getCurrentUser, logout as logoutApi } from '@/lib/auth';
import { getRedirectPath } from '@/lib/auth';
import { startTokenRefresh, stopTokenRefresh } from '@/lib/tokenRefresh';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string, preferredRole?: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

// Flag to prevent multiple concurrent checkAuth calls
let isCheckingAuth = false;

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string, preferredRole?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await loginApi({ email, password });
      const user = await getCurrentUser();
      
      // Validate role if preferred role was selected
      if (preferredRole && user.role !== preferredRole) {
        set({
          isLoading: false,
          error: `This account does not have ${preferredRole} access. Your role is ${user.role}.`,
          isAuthenticated: false,
          user: null,
        });
        return;
      }
      
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      // Start proactive token refresh
      if (typeof window !== 'undefined') {
        startTokenRefresh();
      }

      // Redirect based on role
      const redirectPath = getRedirectPath(user.role);
      if (typeof window !== 'undefined') {
        window.location.href = redirectPath;
      }
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Login failed. Please check your credentials.',
        isAuthenticated: false,
        user: null,
      });
    }
  },

  logout: async () => {
    set({ isLoading: true });
    
    // Stop token refresh
    stopTokenRefresh();
    
    try {
      await logoutApi();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  },

  checkAuth: async () => {
    // Prevent multiple concurrent calls
    if (isCheckingAuth) {
      return;
    }
    
    // If already authenticated with user data, skip the check
    const state = get();
    if (state.isAuthenticated && state.user) {
      return;
    }
    
    isCheckingAuth = true;
    set({ isLoading: true });
    
    try {
      const user = await getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      
      // Start proactive token refresh if authenticated
      if (typeof window !== 'undefined') {
        startTokenRefresh();
      }
    } catch (error: any) {
      console.error('Auth check failed:', error?.message);
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
      // Stop token refresh on auth failure
      if (typeof window !== 'undefined') {
        stopTokenRefresh();
      }
    } finally {
      isCheckingAuth = false;
    }
  },

  clearError: () => set({ error: null }),
}));

