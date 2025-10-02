<template>
  <div>
    <div class="header">
      <h1>Meine Trips</h1>
      <div class="controls">
        <BaseButton tag="router-link" to="/dashboard" variant="secondary" size="small">Dashboard</BaseButton>
        <BaseButton tag="router-link" :to="getAddTripRoute()" variant="primary" size="small">
          {{ getAddTripLabel() }}
        </BaseButton>
        <BaseButton @click="logout" variant="secondary" size="small">Logout</BaseButton>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="category-tabs">
      <button 
        v-for="category in categories" 
        :key="category.value"
        @click="setActiveCategory(category.value)"
        :class="['category-tab', { active: activeCategory === category.value }]"
      >
        <span class="category-icon">{{ category.icon }}</span>
        {{ category.label }}
      </button>
    </div>

    <!-- Enhanced Search for Surfing -->
    <AdvancedSearch
      v-if="activeCategory === 'SURFING'"
      :showAdvancedFilters="showAdvancedFilters"
      @search="handleAdvancedSearch"
    />

    <!-- Enhanced Search for Hiking -->
    <HikingAdvancedSearch
      v-if="activeCategory === 'HIKING'"
      :showAdvancedFilters="showAdvancedFilters"
      @search="handleHikingAdvancedSearch"
    />

    <!-- Basic Search Bar -->
    <div class="filter-bar">
      <BaseInput
        id="search-filter"
        type="text"
        v-model="filters.search"
        placeholder="Suche nach Name, Ort..."
      />
      <div class="filter-group">
        <FilterParticipantSelector
          v-model="filters.participants"
        />
      </div>
      <div class="filter-group">
        <label>Von:</label>
        <BaseInput
          id="from-date-filter"
          type="date"
          v-model="filters.from_date"
        />
      </div>
      <div class="filter-group">
        <label>Bis:</label>
        <BaseInput
          id="to-date-filter"
          type="date"
          v-model="filters.to_date"
        />
      </div>
      <BaseButton
        v-if="activeCategory === 'SURFING' || activeCategory === 'HIKING'"
        @click="showAdvancedFilters = !showAdvancedFilters"
        :variant="showAdvancedFilters || activeAdvancedFiltersCount > 0 ? 'primary' : 'ghost'"
        size="small"
      >
        {{ showAdvancedFilters ? 'Filter ausblenden' : 'Erweiterte Filter' }}
        <BaseBadge
          v-if="activeAdvancedFiltersCount > 0 && !showAdvancedFilters"
          variant="primary"
          size="small"
          style="margin-left: var(--space-2);"
        >
          {{ activeAdvancedFiltersCount }}
        </BaseBadge>
      </BaseButton>
      <BaseButton v-if="hasActiveFilters" @click="clearFilters" variant="ghost" size="small">Filter zurücksetzen</BaseButton>
    </div>


    <div class="pagination-controls">
      <div class="page-size-selector">
        <label for="pageSize">Pro Seite:</label>
        <select id="pageSize" v-model="pageSize">
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
      </div>
      <p class="results-count">{{ totalTrips }} Trip(s) gefunden.</p>
    </div>

    <div v-if="isLoading">Lade Trips...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else>
      <ul class="trip-list">
        <li v-for="trip in trips" :key="trip.id" class="trip-card">
          <div class="card-content">
            <div class="trip-info">
              <router-link :to="`/trip/${trip.id}`" class="trip-link">
                <h2>{{ trip.name }}</h2>
              </router-link>
              <div class="meta-info">
                <span>{{ formatDate(trip.start_date) }} - {{ formatDate(trip.end_date) }}</span>
                <span class="separator" v-if="trip.creator">•</span>
                <span v-if="trip.creator">
                  Erstellt von: 
                  <router-link :to="`/dashboard/${trip.creator.id}`" @click.stop class="user-link">
                    {{ trip.creator.username }}
                  </router-link>
                </span>
              </div>
            </div>
            
            <!-- Hiking/Running Stats -->
            <div v-if="trip.activity_type !== 'SURFING'" class="trip-stats">
              <div class="stat-item">
                <span class="stat-value">{{ formatDuration(trip.total_duration) }}</span>
                <label>Dauer</label>
              </div>
              <span class="stat-separator">|</span>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(trip.total_distance) }} <small>km</small></span>
                <label>Distanz</label>
              </div>
              <span class="stat-separator">|</span>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(trip.total_gain) }} <small>m</small></span>
                <label>Aufstieg</label>
              </div>
              <span class="stat-separator">|</span>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(trip.total_loss) }} <small>m</small></span>
                <label>Abstieg</label>
              </div>
            </div>

            <!-- Surf Stats -->
            <div v-if="trip.activity_type === 'SURFING'" class="trip-stats surf-stats">
              <div class="stat-item">
                <span class="stat-value">{{ formatDuration(trip.total_surf_time) }}</span>
                <label>Total Surftime</label>
              </div>
              <span class="stat-separator">|</span>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(trip.total_wave_count) }}</span>
                <label>Total Wavecount</label>
              </div>
              <span class="stat-separator">|</span>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(trip.unique_surf_spots_count) }}</span>
                <label>Spots Surfed</label>
              </div>
            </div>

            <div class="tags-container">
              <div class="participants" v-if="trip.participants?.length > 0">
                <strong>Teilnehmer:</strong>
                <router-link v-for="p in trip.participants" :key="p.id" :to="`/dashboard/${p.id}`" @click.stop class="user-link">
                  <BaseBadge variant="default" size="medium">{{ p.username }}</BaseBadge>
                </router-link>
              </div>
              <!-- Show huts for hiking trips -->
              <div class="huts" v-if="trip.activity_type === 'HIKING' && trip.huts?.length > 0">
                <strong>Hütten:</strong>
                <template v-for="hut in trip.huts" :key="hut.id">
                  <a v-if="hut.link" :href="hut.link" target="_blank" @click.stop>
                    <BaseBadge variant="info" size="medium">{{ hut.name }} 🔗</BaseBadge>
                  </a>
                  <BaseBadge v-else variant="info" size="medium">{{ hut.name }}</BaseBadge>
                </template>
              </div>

              <!-- Show country for surf trips -->
              <div class="country" v-if="trip.activity_type === 'SURFING' && trip.country_display">
                <strong>🌍 Land:</strong>
                <BaseBadge variant="surfing" size="medium">{{ getCountryWithFlag(trip) }}</BaseBadge>
              </div>
            </div>
          </div>
          
          <button v-if="currentUser && currentUser.id === trip.creator?.id" @click.stop="handleDeleteTrip(trip.id)" class="btn-delete" title="Trip löschen">🗑️</button>
        </li>
      </ul>

      <!-- Infinite scroll loading states -->
      <div class="infinite-scroll-status">
        <div v-if="isLoadingMore" class="loading-more">
          Lade weitere Trips...
        </div>
        <div v-else-if="!hasMoreTrips && allTrips.length > 0" class="no-more-trips">
          Alle Trips wurden geladen
        </div>
        <!-- Sentinel element for intersection observer -->
        <div ref="sentinel" class="scroll-sentinel"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import { currentUser, setCurrentTab } from '../store';
import FilterParticipantSelector from './FilterParticipantSelector.vue';
import AdvancedSearch from './AdvancedSearch.vue';
import HikingAdvancedSearch from './HikingAdvancedSearch.vue';
import BaseButton from './base/BaseButton.vue';
import BaseBadge from './base/BaseBadge.vue';
import { formatDurationHoursMinutes } from '../utils/duration.js';
import BaseInput from './base/BaseInput.vue';

// Accept props for default category
const props = defineProps({
  defaultCategory: {
    type: String,
    default: null
  }
});

const router = useRouter();
const route = useRoute();
const trips = ref([]);
const isLoading = ref(true);
const error = ref(null);
const allUsers = ref([]);

// --- NEW & UPDATED STATE FOR PAGINATION ---
const totalTrips = ref(0);
const currentPage = ref(1);
const pageSize = ref('10'); // Default page size
const nextPageUrl = ref(null);
const previousPageUrl = ref(null);

// --- INFINITE SCROLL STATE ---
const allTrips = ref([]); // Accumulates all loaded trips
const isLoadingMore = ref(false); // Loading additional trips
const hasMoreTrips = ref(true); // Whether more trips are available
const observer = ref(null); // Intersection observer instance
const sentinel = ref(null); // Template ref for sentinel element

// Category management
const activeCategory = ref(props.defaultCategory || 'HIKING');
const categories = ref([
  { value: 'HIKING', label: 'Wandern', icon: '🥾' },
  { value: 'SURFING', label: 'Surfen', icon: '🏄‍♂️' }
]);

const filters = ref({
  search: '',
  participants: [],
  from_date: '',
  to_date: ''
});

const showAdvancedFilters = ref(false);
const activeAdvancedFilters = ref({});

const fetchTrips = async (isInfiniteScroll = false) => {
  try {
    // Set appropriate loading state
    if (isInfiniteScroll) {
      isLoadingMore.value = true;
    } else {
      isLoading.value = true;
    }
    error.value = null;

    const params = new URLSearchParams();

    // --- Add filter parameters ---
    if (filters.value.search) params.append('search', filters.value.search);
    if (filters.value.participants.length > 0) {
      filters.value.participants.forEach(participant => params.append('participants', participant.id));
    }
    if (filters.value.from_date) params.append('from_date', filters.value.from_date);
    if (filters.value.to_date) params.append('to_date', filters.value.to_date);

    // --- Add activity type filter based on active category ---
    params.append('activity_type', activeCategory.value);

    // --- Add pagination parameters ---
    params.append('page', currentPage.value);
    params.append('page_size', pageSize.value);

    const response = await api.get(`/trips/`, { params });

    // --- HANDLE RESPONSE: APPEND FOR INFINITE SCROLL, REPLACE FOR INITIAL/FILTER LOADS ---
    if (isInfiniteScroll) {
      // Append new results to existing trips
      allTrips.value.push(...response.data.results);
    } else {
      // Replace trips (initial load or filter change)
      allTrips.value = response.data.results;
    }

    // Keep original trips ref for backward compatibility
    trips.value = allTrips.value;

    totalTrips.value = response.data.count;
    nextPageUrl.value = response.data.next;
    previousPageUrl.value = response.data.previous;
    hasMoreTrips.value = !!response.data.next; // Has more trips if next URL exists

  } catch (err) {
    console.error("API Error:", err.response?.data || err.message);
    error.value = "Fehler beim Laden der Trips. Bitte versuchen Sie es später erneut.";
  } finally {
    if (isInfiniteScroll) {
      isLoadingMore.value = false;
    } else {
      isLoading.value = false;
    }
  }
};

// --- THIS IS YOUR ORIGINAL, WORKING VERSION ---
const fetchUsers = async () => {
  try {
    const response = await api.get('/users/');
    allUsers.value = response.data;
  } catch (err) {
    console.error("Fehler beim Laden der Benutzerliste.");
  }
};

// --- INFINITE SCROLL FUNCTIONS ---
const loadMoreTrips = async () => {
  // Prevent multiple simultaneous loads
  if (isLoadingMore.value || !hasMoreTrips.value) return;

  currentPage.value++;
  await fetchTrips(true); // true = infinite scroll mode
};

const setupIntersectionObserver = () => {
  // Create observer to watch sentinel element
  observer.value = new IntersectionObserver(
    (entries) => {
      const [entry] = entries;
      console.log('Intersection observed:', {
        isIntersecting: entry.isIntersecting,
        hasMoreTrips: hasMoreTrips.value,
        isLoadingMore: isLoadingMore.value,
        currentPage: currentPage.value
      });

      if (entry.isIntersecting && hasMoreTrips.value && !isLoadingMore.value) {
        console.log('Loading more trips...');
        loadMoreTrips();
      }
    },
    {
      rootMargin: '100px', // Start loading 100px before reaching bottom
      threshold: 0.1,
    }
  );
};

const observeSentinel = (element) => {
  if (observer.value && element) {
    observer.value.observe(element);
  }
};

const cleanupIntersectionObserver = () => {
  if (observer.value) {
    observer.value.disconnect();
    observer.value = null;
  }
};

const handleAdvancedSearch = (advancedFilters) => {
  // Store active advanced filters for badge display
  activeAdvancedFilters.value = advancedFilters;

  // Merge advanced filters with existing filters
  const combinedParams = new URLSearchParams();

  // Add basic filters
  if (filters.value.search) combinedParams.append('search', filters.value.search);
  if (filters.value.participants.length > 0) {
    filters.value.participants.forEach(participant => combinedParams.append('participants', participant.id));
  }
  if (filters.value.from_date) combinedParams.append('from_date', filters.value.from_date);
  if (filters.value.to_date) combinedParams.append('to_date', filters.value.to_date);

  // Add advanced filters
  Object.keys(advancedFilters).forEach(key => {
    if (advancedFilters[key] !== '' && advancedFilters[key] !== null) {
      combinedParams.append(key, advancedFilters[key]);
    }
  });

  // Add activity type and pagination
  combinedParams.append('activity_type', activeCategory.value);
  combinedParams.append('page', 1);
  combinedParams.append('page_size', pageSize.value);

  // Make API call with combined filters
  fetchTripsWithAdvancedParams(combinedParams);
};

const handleHikingAdvancedSearch = (advancedFilters) => {
  // Store active advanced filters for badge display
  activeAdvancedFilters.value = advancedFilters;
  // Merge advanced hiking filters with existing filters
  const combinedParams = new URLSearchParams();
  // Add basic filters
  if (filters.value.search) combinedParams.append('search', filters.value.search);
  if (filters.value.participants.length > 0) {
    filters.value.participants.forEach(participant => combinedParams.append('participants', participant.id));
  }
  if (filters.value.from_date) combinedParams.append('from_date', filters.value.from_date);
  if (filters.value.to_date) combinedParams.append('to_date', filters.value.to_date);
  // Add hiking advanced filters
  Object.keys(advancedFilters).forEach(key => {
    if (advancedFilters[key] !== '' && advancedFilters[key] !== null) {
      combinedParams.append(key, advancedFilters[key]);
    }
  });
  // Add activity type and pagination
  combinedParams.append('activity_type', activeCategory.value);
  combinedParams.append('page', 1);
  combinedParams.append('page_size', pageSize.value);
  // Make API call with combined filters
  fetchTripsWithAdvancedParams(combinedParams);
};

const fetchTripsWithAdvancedParams = async (params) => {
  try {
    isLoading.value = true;
    error.value = null;
    currentPage.value = 1;
    allTrips.value = []; // Clear accumulated trips for new search
    hasMoreTrips.value = true; // Reset has more trips flag

    const response = await api.get(`/trips/`, { params });

    // Use the same logic as fetchTrips for consistency
    allTrips.value = response.data.results;
    trips.value = allTrips.value;

    totalTrips.value = response.data.count;
    nextPageUrl.value = response.data.next;
    previousPageUrl.value = response.data.previous;
    hasMoreTrips.value = !!response.data.next;

  } catch (err) {
    console.error("Advanced Search API Error:", err.response?.data || err.message);
    error.value = "Fehler beim Laden der gefilterten Trips.";
  } finally {
    isLoading.value = false;
  }
};

// --- Category management ---
const setActiveCategory = (category) => {
  // Navigate to category-specific URL - the route watcher will handle the data refresh
  const categoryRoutes = {
    'HIKING': '/hiking',
    'SURFING': '/surfing'
  };

  const targetRoute = categoryRoutes[category];
  if (targetRoute && route.path !== targetRoute) {
    router.push(targetRoute);
  } else {
    // Fallback: if we're already on the correct route, refresh manually
    activeCategory.value = category;
    activeAdvancedFilters.value = {}; // Clear advanced filters when category changes
    setCurrentTab(category);
    currentPage.value = 1;
    allTrips.value = []; // Clear accumulated trips for new category
    hasMoreTrips.value = true; // Reset has more trips flag
    fetchTrips();
  }
};

const getAddTripRoute = () => {
  return `/trip/new?activity_type=${activeCategory.value}`;
};

const getAddTripLabel = () => {
  switch (activeCategory.value) {
    case 'HIKING':
      return 'Add Hike';
    case 'SURFING':
      return 'Add Surf';
    default:
      return 'Add Trip';
  }
};

// --- Watcher resets to page 1 and clears accumulated trips on any filter change ---
const onFilterChange = async () => {
  currentPage.value = 1;
  allTrips.value = []; // Clear accumulated trips
  hasMoreTrips.value = true; // Reset has more trips flag
  await fetchTrips(); // This will be a fresh load, not infinite scroll

  // Re-observe sentinel after content changes
  await nextTick();
  if (sentinel.value && observer.value) {
    observer.value.disconnect();
    observeSentinel(sentinel.value);
  }
};

watch(filters, onFilterChange, { deep: true });
watch(pageSize, onFilterChange);

// Helper function to extract category from route path
const getCategoryFromRoute = (routePath) => {
  const categoryMap = {
    '/hiking': 'HIKING',
    '/surfing': 'SURFING'
  };
  return categoryMap[routePath] || 'HIKING';
};

// Watch for route changes to update category and refresh data
watch(route, async (newRoute) => {
  const newCategory = getCategoryFromRoute(newRoute.path);
  if (newCategory !== activeCategory.value) {
    activeCategory.value = newCategory;
    activeAdvancedFilters.value = {}; // Clear advanced filters when category changes
    setCurrentTab(newCategory);
    currentPage.value = 1;
    allTrips.value = []; // Clear accumulated trips for new category
    hasMoreTrips.value = true; // Reset has more trips flag
    await fetchTrips();

    // Re-observe sentinel after content changes
    await nextTick();
    if (sentinel.value && observer.value) {
      observer.value.disconnect();
      observeSentinel(sentinel.value);
    }
  }
}, { immediate: true });

onMounted(async () => {
  await fetchTrips();
  fetchUsers();
  setupIntersectionObserver();

  // Start observing the sentinel element after DOM is fully rendered and trips are loaded
  await nextTick();
  if (sentinel.value && observer.value) {
    observeSentinel(sentinel.value);
  }
});

onBeforeUnmount(() => {
  cleanupIntersectionObserver();
});

const clearFilters = () => {
  filters.value = {
    search: '',
    participants: [],
    from_date: '',
    to_date: ''
  };
  activeAdvancedFilters.value = {};
};

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return (
    filters.value.search !== '' ||
    filters.value.participants.length > 0 ||
    filters.value.from_date !== '' ||
    filters.value.to_date !== ''
  );
});

// Computed property to count active advanced filters
const activeAdvancedFiltersCount = computed(() => {
  return Object.keys(activeAdvancedFilters.value).filter(
    key => activeAdvancedFilters.value[key] !== '' && activeAdvancedFilters.value[key] !== null
  ).length;
});

const handleDeleteTrip = async (tripId) => {
  if (window.confirm("Sind Sie sicher, dass Sie diesen Trip endgültig löschen möchten?")) {
    try {
      await api.delete(`/trips/${tripId}/`);
      fetchTrips(); // Reload the list after deletion
    } catch (err) {
      alert("Fehler beim Löschen des Trips.");
    }
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
};

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return Math.round(num).toLocaleString('de-CH');
};

const formatDuration = formatDurationHoursMinutes;

const logout = () => {
  // Use centralized logout from api.js
  import('../api').then(module => {
    module.logout();
  });
};


// Surf-specific helper functions
const getCountryWithFlag = (trip) => {
  if (!trip.country || !trip.country_display) return '';
  
  // Generate flag emoji for country code
  const getCountryFlag = (countryCode) => {
    if (!countryCode || countryCode.length !== 2) return '🌍';
    return countryCode
      .toUpperCase()
      .split('')
      .map(char => String.fromCodePoint(char.charCodeAt(0) + 127397))
      .join('');
  };
  
  const flag = getCountryFlag(trip.country);
  return `${flag} ${trip.country_display}`;
};

</script>

<style scoped>
/* TripList - Migrated to Design System */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  flex-wrap: wrap;
  gap: var(--space-6);
}

/* Category tabs styling */
.category-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  padding: var(--space-2);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.category-tab {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background-color: transparent;
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.category-tab:hover {
  background-color: rgba(255, 255, 255, 0.7);
  color: var(--color-text-primary);
}

.category-tab.active {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  border-color: var(--color-blue);
  box-shadow: var(--shadow-sm);
}

.category-icon {
  font-size: var(--text-lg);
}

.header > .controls {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.error-message {
  color: var(--color-error);
}
/* Filter bar */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  align-items: flex-start;
}

/* Vertically center buttons in filter bar */
.filter-bar > button {
  align-self: center;
}

/* Search input (BaseInput) in filter bar */
.filter-bar > .input-wrapper {
  flex-grow: 1;
  min-width: 200px;
  margin-bottom: 0; /* Override BaseInput default margin */
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* Force Von filter to start on new line */
.filter-bar > .filter-group:nth-of-type(2) {
  flex-basis: 100%;
}

.filter-group label {
  font-weight: var(--font-medium);
  white-space: nowrap;
}

/* Date inputs (BaseInput) in filter groups */
.filter-group .input-wrapper {
  margin-bottom: 0; /* Override BaseInput default margin */
  max-width: 160px;
}

/* Trip list */
.trip-list {
  list-style: none;
  padding: 0;
}

.trip-card {
  display: flex;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-fast);
  position: relative;
}

.trip-card:hover {
  box-shadow: var(--shadow-md);
}

.card-content {
  padding: var(--space-6);
  width: 100%;
  padding-right: var(--space-10);
  min-width: 0;
  overflow: hidden;
}

.trip-info {
  min-width: 0;
  overflow: hidden;
}

.trip-info h2 {
  margin: 0 0 var(--space-1) 0;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

.trip-link {
  text-decoration: none;
  color: inherit;
}

.trip-link:hover h2 {
  color: var(--color-blue);
}

.meta-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  min-width: 0;
}

.user-link {
  color: var(--color-blue);
  text-decoration: none;
  font-weight: var(--font-medium);
}

.user-link:hover {
  text-decoration: underline;
}
/* Trip stats */
.trip-stats {
  display: flex;
  align-items: baseline;
  gap: var(--space-4);
  padding: var(--space-4) 0;
  border-top: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
}

.stat-item {
  text-align: left;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.stat-value small {
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  color: var(--color-text-secondary);
  margin-left: var(--space-1);
}

.stat-item label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  display: block;
  margin-top: -5px;
}

.stat-separator {
  color: var(--color-border-light);
  font-size: var(--text-2xl);
}

/* Tags container */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-top: var(--space-4);
  font-size: var(--text-sm);
  min-width: 0;
}

.participants,
.huts,
.country {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3); /* Increased from 8px to 12px for better badge spacing */
}

/* Surf-specific styling */
.surf-stats {
  border-color: var(--color-surfing);
}

.surf-stats .stat-value {
  color: var(--color-surfing);
}

/* Delete button */
.btn-delete {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  background-color: transparent;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  font-size: var(--text-lg);
}

.btn-delete:hover {
  color: var(--color-error);
}

/* Pagination controls */
.pagination-controls {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-top: -var(--space-4);
  margin-bottom: var(--space-8);
}

.page-navigation {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.page-navigation button {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-sm);
}

.page-navigation button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results-count {
  text-align: right;
  color: var(--color-text-secondary);
  margin: 0;
}

.filter-bar .results-count {
  margin-left: auto;
  font-weight: var(--font-medium);
}

.results-summary {
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  text-align: center;
}

.results-summary .results-count {
  text-align: center;
  font-weight: var(--font-medium);
  color: var(--color-surfing);
}

/* Infinite scroll styles */
.infinite-scroll-status {
  text-align: center;
  padding: 2rem 0;
}

.loading-more {
  color: var(--color-text-secondary);
  font-style: italic;
  padding: 1rem;
}

.no-more-trips {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  padding: 1rem;
  border-top: 1px solid var(--color-border-light);
  margin-top: 1rem;
}

.scroll-sentinel {
  height: 1px;
  width: 100%;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .header {
    flex-direction: column-reverse;
    align-items: stretch;
    gap: 0.75rem;
    margin: 0 0.5rem 2rem 0.5rem;
  }

  .header > .controls {
    flex-direction: row;
    gap: var(--space-2);
    width: 100%;
    flex-wrap: wrap;
  }

  .header > .controls > * {
    font-size: var(--text-sm);
    flex: 1;
    min-width: max-content;
  }

  .btn {
    padding: 0.7rem 1rem;
    font-size: 0.9rem;
    font-weight: 600;
    flex: 1;
    min-width: 90px;
    max-width: 110px;
    text-align: center;
    border-radius: 10px;
  }
  
  .filter-bar {
    padding: var(--space-4);
    gap: var(--space-6); /* Increased from 8px to 24px for better breathing room */
    margin: 0 0.5rem 1rem 0.5rem;
    flex-direction: column; /* Stack all filter elements vertically */
    align-items: stretch;
  }

  /* Search input (BaseInput) on mobile */
  .filter-bar > .input-wrapper {
    min-width: auto;
    width: 100%;
    margin-bottom: 0;
    box-sizing: border-box;
  }

  .filter-bar > .input-wrapper .input-field {
    box-sizing: border-box;
  }

  .filter-group {
    display: flex;
    flex-direction: column; /* Stack label and input vertically */
    align-items: stretch;
    gap: var(--space-2);
    width: 100%;
  }

  /* Override special layout - stack date filters vertically on mobile */
  /* Note: counting .filter-group children only - participants is 1st, Von is 2nd, Bis is 3rd */
  .filter-group:nth-of-type(2), .filter-group:nth-of-type(3) {
    display: flex;
    width: 100%;
    flex: 0 0 100%; /* Explicitly force full width and prevent flex shrinking */
    overflow: hidden; /* Only prevent overflow for date input groups */
  }

  .filter-group label {
    font-size: 0.85rem;
    margin: 0;
  }

  /* Date inputs (BaseInput) on mobile */
  .filter-group .input-wrapper {
    width: 100%;
    max-width: none;
    margin-bottom: 0;
    box-sizing: border-box;
  }

  .filter-group .input-field {
    box-sizing: border-box;
  }

  .btn-clear {
    padding: 0.8rem 1rem;
    font-size: 0.95rem;
    margin-top: 0;
    border-radius: 10px;
    width: 100%;
  }

  /* Override button constraints for filter buttons */
  .filter-bar .btn {
    max-width: none;
    min-width: auto;
    width: auto;
    flex: 0 1 auto;
  }
  
  /* Mobile responsive category tabs */
  .category-tabs {
    margin: 0 0.5rem 1.5rem 0.5rem;
    padding: 0.4rem;
    gap: 0.3rem;
  }
  
  .category-tab {
    flex: 1;
    justify-content: center;
    padding: 0.75rem 1rem; /* Increased for better touch targets (min 44px) */
    font-size: 0.9rem;
    min-height: 44px; /* Ensure minimum touch target size */
  }
  
  .category-icon {
    font-size: 1rem;
  }

  /* Increase delete button touch targets on mobile */
  .btn-delete {
    font-size: var(--text-xl); /* Larger icon */
    padding: var(--space-2); /* Add padding for larger touch area */
    min-width: 44px;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Hide page size selector on mobile (desktop-oriented control) */
  .page-size-selector {
    display: none;
  }

  .results-count {
    text-align: center !important;
    font-size: 0.85rem;
    margin-top: 0.25rem;
  }
  
  .pagination-controls {
    flex-direction: column;
    gap: 0.75rem;
    margin: 0 0.5rem 2rem 0.5rem;
  }
  
  .trip-list {
    margin: 0 0.5rem;
  }
  
  .trip-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
    padding: var(--space-4);
  }

  .stat-separator {
    display: none;
  }

  .stat-value {
    font-size: 1.2rem;
  }

  /* Enhanced word-breaking for mobile */
  .trip-info h2 {
    font-size: 1.3rem;
    line-height: 1.3;
  }

  .card-content {
    padding: 1rem;
    padding-right: 2rem;
  }

  /* Badge sizing and overflow handling on mobile */
  .participants a,
  .huts a,
  .huts > span,
  .country > span {
    max-width: 150px;
  }

  /* Ensure BaseBadge content truncates properly - use deep selector for scoped child component */
  .participants :deep(.badge),
  .huts :deep(.badge),
  .country :deep(.badge) {
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
  }
}
</style>
