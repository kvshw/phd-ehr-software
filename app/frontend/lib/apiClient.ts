/**
 * API client with cookie-based authentication
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Client-side API client (uses cookies automatically via withCredentials)
export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for sending cookies
  timeout: 30000, // 30 second timeout (increased for slow database queries)
});

// Helper to get cookie value
function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

// Request interceptor to add auth token from cookies as Authorization header
apiClient.interceptors.request.use(
  (config) => {
    // Try to get access token from cookie and add as Authorization header
    // This works across subdomains (unlike cookies)
    const accessToken = getCookie('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    // Cookies are also sent with withCredentials: true (for same-domain requests)
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Track if we're currently refreshing to avoid infinite loops
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response interceptor to handle errors and automatic token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Suppress 404 errors for adaptation endpoint (expected when no plan exists)
    const isAdaptationEndpoint = error.config?.url?.includes('/mape-k/adaptation/latest');
    if (error.response?.status === 404 && isAdaptationEndpoint) {
      // Return a resolved promise with a proper axios response structure
      // This prevents console errors for expected 404s
      return Promise.resolve({
        data: null,
        status: 404,
        statusText: 'Not Found',
        headers: error.response?.headers || {},
        config: error.config,
        request: error.request,
      });
    }
    
    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Try to refresh the token via API route
        const refreshResponse = await fetch('/api/auth/refresh', {
          method: 'POST',
          credentials: 'include',
        });

        if (refreshResponse.ok) {
          // Token refreshed successfully, retry original request
          // The new token is now in cookies, so the request will work
          isRefreshing = false;
          processQueue(null, null);
          return apiClient(originalRequest);
        } else {
          // Refresh failed - user needs to login again
          throw new Error('Token refresh failed');
        }
      } catch (refreshError) {
        // Refresh failed - clear auth and redirect to login
        isRefreshing = false;
        processQueue(refreshError, null);
        
        if (typeof window !== 'undefined') {
          // Clear cookies
          document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          
          // Only redirect if not already on login page
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

