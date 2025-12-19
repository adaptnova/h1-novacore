import { INFRASTRUCTURE_CONFIG } from '../config/infrastructure';

// Generate a unique request ID
export const generateRequestId = () => {
  return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

// OAuth token management
let currentToken = null;
let tokenExpiry = null;

export const getAuthToken = async () => {
  // Check if we have a valid token
  if (currentToken && tokenExpiry && Date.now() < tokenExpiry) {
    return currentToken;
  }

  try {
    const { host, port, ssl, endpoints } = INFRASTRUCTURE_CONFIG.auth.oauth2;
    const protocol = ssl ? 'https' : 'http';
    const response = await fetch(`${protocol}://${host}:${port}${endpoints.token}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: process.env.REACT_APP_OAUTH_CLIENT_ID,
        client_secret: process.env.REACT_APP_OAUTH_CLIENT_SECRET,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to obtain auth token');
    }

    const data = await response.json();
    currentToken = data.access_token;
    // Set expiry 5 minutes before actual expiry to ensure token freshness
    tokenExpiry = Date.now() + (data.expires_in - 300) * 1000;

    return currentToken;
  } catch (error) {
    console.error('Auth token acquisition failed:', error);
    throw error;
  }
};

// Token refresh scheduler
let refreshInterval;

export const startTokenRefresh = () => {
  // Clear any existing refresh interval
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }

  // Set up automatic token refresh
  refreshInterval = setInterval(async () => {
    try {
      await getAuthToken();
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
  }, 840000); // 14 minutes (leaving 1-minute buffer for token expiry)
};

export const stopTokenRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
};

// Auth state management
export const isAuthenticated = () => {
  return !!currentToken && !!tokenExpiry && Date.now() < tokenExpiry;
};

// Request headers with auth
export const getAuthHeaders = async () => {
  const token = await getAuthToken();
  return {
    'Authorization': `Bearer ${token}`,
    'X-Request-ID': generateRequestId(),
    'Content-Type': 'application/json',
  };
};

// Error handling
export class AuthError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AuthError';
  }
}

// Initialize auth
export const initializeAuth = async () => {
  try {
    await getAuthToken();
    startTokenRefresh();
    return true;
  } catch (error) {
    console.error('Auth initialization failed:', error);
    return false;
  }
};

// Cleanup
export const cleanupAuth = () => {
  stopTokenRefresh();
  currentToken = null;
  tokenExpiry = null;
};
