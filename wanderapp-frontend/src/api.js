import axios from 'axios';
import router from './router';

// Die baseURL ist jetzt ein relativer Pfad. 
// Der Proxy in vue.config.js leitet alles unter /api an das Backend weiter.
const api = axios.create({
  baseURL: '/api',
});

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

// Interceptor für eingehende Antworten (Token Refresh)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          localStorage.clear();
          router.push('/login');
          return Promise.reject(error);
        }
        
        // WICHTIG: Dieser Aufruf nutzt jetzt auch den Proxy!
        const response = await api.post('/token/refresh/', {
          refresh: refreshToken,
        });

        const newAccessToken = response.data.access;
        localStorage.setItem('accessToken', newAccessToken);
        
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return api(originalRequest);

      } catch (refreshError) {
        localStorage.clear();
        router.push('/login');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;