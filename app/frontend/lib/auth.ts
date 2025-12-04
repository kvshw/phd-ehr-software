/**
 * Authentication utilities and API calls
 */
import { apiClient } from './apiClient';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  role: 'clinician' | 'researcher' | 'admin' | 'nurse' | 'doctor';
  specialty?: string;
  first_name?: string;
  last_name?: string;
  title?: string;
  department?: string;
  heti_number?: string;
  license_number?: string;
  workplace_municipality?: string;
  primary_workplace?: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * Login user and store tokens
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
  
  // Store tokens in HTTP-only cookies via API route
  if (typeof window !== 'undefined') {
    await fetch('/api/auth/set-tokens', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
      }),
    });
  }
  
  return response.data;
}

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const response = await apiClient.get<User>('/auth/me', {
      withCredentials: true,
      timeout: 15000, // 15 second timeout
    });
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error('Unauthorized');
    }
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error('Request timeout - backend may not be running');
    }
    if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      throw new Error('Network error - cannot connect to backend');
    }
    throw error;
  }
}

/**
 * Refresh access token
 */
export async function refreshToken(refreshToken: string): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  
  // Update tokens in HTTP-only cookies
  if (typeof window !== 'undefined') {
    await fetch('/api/auth/set-tokens', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
      }),
    });
  }
  
  return response.data;
}

/**
 * Logout user - calls backend to clear cookies
 */
export async function logout(): Promise<void> {
  try {
    // Call backend logout endpoint to clear cookies
    // Use fetch directly to ensure credentials are sent
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    await fetch(`${apiUrl}/api/v1/auth/logout`, {
      method: 'POST',
      credentials: 'include', // Important: send cookies
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error: any) {
    // Even if the request fails, continue with logout
    console.warn('Logout request failed, but continuing with logout:', error);
  }
  
  // Always redirect to login page, even if API call failed
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * Get redirect path based on user role
 */
export function getRedirectPath(role: string): string {
  switch (role) {
    case 'clinician':
    case 'doctor':
      return '/dashboard';
    case 'researcher':
      return '/researcher/dashboard';
    case 'admin':
      return '/admin/controls';
    case 'nurse':
      return '/nurse/dashboard';
    default:
      return '/dashboard';
  }
}

