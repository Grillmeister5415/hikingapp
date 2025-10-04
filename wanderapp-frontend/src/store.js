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

// Dashboard state management
export const dashboardCache = ref({});
export const selectedYear = ref(null); // null = all-time
export const availableYears = ref([]);

// Fetch dashboard overview with caching
export async function fetchDashboardOverview(userId = null, year = null) {
  const cacheKey = `${userId || 'me'}_${year || 'all'}`;

  // Return cached data if available
  if (dashboardCache.value[cacheKey]) {
    return dashboardCache.value[cacheKey];
  }

  // Build API URL
  const params = year ? `?year=${year}` : '';
  const url = userId
    ? `/dashboard/overview/${userId}/${params}`
    : `/dashboard/overview/${params}`;

  try {
    const response = await api.get(url);
    // Cache the response
    dashboardCache.value[cacheKey] = response.data;
    // Update available years
    if (response.data.available_years) {
      availableYears.value = response.data.available_years;
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard overview:', error);
    throw error;
  }
}

// Clear dashboard cache (useful when data changes)
export function clearDashboardCache() {
  dashboardCache.value = {};
}

// Set selected year and persist
export function setSelectedYear(year) {
  selectedYear.value = year;
  if (year) {
    localStorage.setItem('selectedYear', year);
  } else {
    localStorage.removeItem('selectedYear');
  }
}

// Load selected year from localStorage on init
const storedYear = localStorage.getItem('selectedYear');
if (storedYear) {
  selectedYear.value = parseInt(storedYear);
}