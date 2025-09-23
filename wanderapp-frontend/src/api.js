import axios from 'axios';
import router from './router';

// Die baseURL ist jetzt ein relativer Pfad.
// Der Proxy in vue.config.js leitet alles unter /api an das Backend weiter.
const api = axios.create({
  baseURL: '/api',
});

// Global state to prevent race conditions
let isRefreshing = false;
let failedQueue = [];
let isLoggingOut = false;

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  failedQueue = [];
};

// Centralized logout function
export const logout = () => {
  if (isLoggingOut) return;
  isLoggingOut = true;

  // Clear all auth data
  localStorage.clear();

  // Reset global state
  isRefreshing = false;
  failedQueue = [];

  // Clear auth state using store function
  try {
    const { clearAuthState, showAuthMessage } = require('./store');
    clearAuthState();
    showAuthMessage('You have been logged out.', 'info');
  } catch (e) {
    // Store not available, continue
  }

  // Navigate to login only if not already there
  if (router.currentRoute.value.path !== '/login') {
    router.push('/login').finally(() => {
      isLoggingOut = false;
    });
  } else {
    isLoggingOut = false;
  }
};

// Interceptor für ausgehende Anfragen
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor für eingehende Antworten (Token Refresh mit Queue)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {

      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refreshToken');

      if (!refreshToken) {
        processQueue(error, null);
        logout();
        return Promise.reject(error);
      }

      try {
        // Use fresh axios instance to avoid interceptor loops
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken,
        });

        const newAccessToken = response.data.access;
        localStorage.setItem('accessToken', newAccessToken);

        // Update authorization header for original request
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

        // Process all queued requests
        processQueue(null, newAccessToken);
        isRefreshing = false;

        // Retry original request
        return api(originalRequest);

      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;