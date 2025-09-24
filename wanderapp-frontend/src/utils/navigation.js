// src/utils/navigation.js
import { useRouter } from 'vue-router';
import { getCurrentTabRoute } from '../store.js';

/**
 * Navigate to the trip list while preserving the current tab context
 * @param {Object} router - Vue router instance
 */
export function navigateToTripList(router) {
  const tabRoute = getCurrentTabRoute();
  router.push(tabRoute);
}

/**
 * Get the appropriate route for navigation back to trip list
 * Used for router-link :to attribute
 * @returns {string} Route path for current tab
 */
export function getTripListRoute() {
  return getCurrentTabRoute();
}

/**
 * Composable for tab-aware navigation
 * Provides router and navigation helpers
 * @returns {Object} Navigation utilities
 */
export function useTabAwareNavigation() {
  const router = useRouter();

  return {
    router,
    navigateToTripList: () => navigateToTripList(router),
    getTripListRoute,
  };
}