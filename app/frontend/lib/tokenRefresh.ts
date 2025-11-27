/**
 * Proactive token refresh mechanism
 * Refreshes tokens before they expire to prevent automatic logout
 */

let refreshTimer: NodeJS.Timeout | null = null;

/**
 * Start proactive token refresh
 * Refreshes token 5 minutes before expiration
 */
export function startTokenRefresh() {
  // Clear any existing timer
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }

  // Refresh token every 7 hours (8 hour expiration - 1 hour buffer)
  // This ensures we refresh before expiration
  const REFRESH_INTERVAL = 7 * 60 * 60 * 1000; // 7 hours in milliseconds

  refreshTimer = setInterval(async () => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        console.log('✅ Token refreshed proactively');
      } else {
        console.warn('⚠️ Token refresh failed, user may need to login');
      }
    } catch (error) {
      console.error('❌ Error refreshing token:', error);
    }
  }, REFRESH_INTERVAL);
}

/**
 * Stop proactive token refresh
 */
export function stopTokenRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

