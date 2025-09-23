// src/store.js
import { ref, computed } from 'vue';
import api from './api';

// Reactive auth state
export const currentUser = ref(null);
export const isAuthLoading = ref(false);
export const authMessage = ref(null);

// Computed auth status
export const isAuthenticated = computed(() => {
  return !!(currentUser.value && localStorage.getItem('accessToken'));
});

// Display auth message temporarily
export function showAuthMessage(message, type = 'info', duration = 5000) {
  authMessage.value = { text: message, type };
  setTimeout(() => {
    if (authMessage.value?.text === message) {
      authMessage.value = null;
    }
  }, duration);
}

// Fetch current user with loading state
export async function fetchCurrentUser() {
  const token = localStorage.getItem('accessToken');
  if (token && !currentUser.value && !isAuthLoading.value) {
    isAuthLoading.value = true;
    try {
      const response = await api.get('/users/me/');
      currentUser.value = response.data;
    } catch (error) {
      console.error("Could not fetch user.", error);
      currentUser.value = null;

      // Show user-friendly message for auth errors
      if (error.response?.status === 401) {
        showAuthMessage('Session expired. Please log in again.', 'warning');
      } else {
        showAuthMessage('Unable to verify login status.', 'error');
      }
    } finally {
      isAuthLoading.value = false;
    }
  }
}

// Clear auth state (called from logout)
export function clearAuthState() {
  currentUser.value = null;
  isAuthLoading.value = false;
  authMessage.value = null;
}

// Tab state management
export const currentTab = ref(localStorage.getItem('currentTab') || 'HIKING');

// Set current tab and persist to localStorage
export function setCurrentTab(tab) {
  currentTab.value = tab;
  localStorage.setItem('currentTab', tab);
}

// Get route path for current tab
export function getCurrentTabRoute() {
  switch (currentTab.value) {
    case 'SURFING':
      return '/surfing';
    case 'HIKING':
      return '/hiking';
    default:
      return '/hiking';
  }
}