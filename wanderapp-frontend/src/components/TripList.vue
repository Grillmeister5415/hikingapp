<template>
  <div>
    <div class="header">
      <h1>Meine Trips</h1>
      <div class="controls">
        <router-link to="/dashboard" class="btn btn-dashboard">Dashboard</router-link>
        <router-link :to="getAddTripRoute()" class="btn btn-new-trip">
          {{ getAddTripLabel() }}
        </router-link>
        <button @click="logout" class="btn btn-logout">Logout</button>
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
      <input type="text" v-model="filters.search" placeholder="Suche nach Name, Ort..." class="search-input" />
      <div class="filter-group">
        <label>Teilnehmer:</label>
        <MultiSelectDropdown
          :options="allUsers"
          v-model="filters.participants"
          placeholder="Alle Teilnehmer"
        />
      </div>
      <div class="filter-group">
        <label>Von:</label>
        <input type="date" v-model="filters.from_date" />
      </div>
      <div class="filter-group">
        <label>Bis:</label>
        <input type="date" v-model="filters.to_date" />
      </div>
      <button
        v-if="activeCategory === 'SURFING' || activeCategory === 'HIKING'"
        @click="showAdvancedFilters = !showAdvancedFilters"
        class="btn-clear btn-advanced"
        :class="{ active: showAdvancedFilters }"
      >
        {{ showAdvancedFilters ? 'Erweiterte Filter ausblenden' : 'Erweiterte Filter' }}
      </button>
      <button @click="clearFilters" class="btn-clear">Filter zurücksetzen</button>
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
                <span class="stat-value">{{ getSurfStageCount(trip) }}</span>
                <label>Sessions</label>
              </div>
              <span class="stat-separator" v-if="trip.country_display">|</span>
              <div class="stat-item" v-if="trip.country_display">
                <span class="stat-value">{{ getCountryWithFlag(trip) }}</span>
                <label>Land</label>
              </div>
            </div>

            <div class="tags-container">
              <div class="participants" v-if="trip.participants?.length > 0">
                <strong>Teilnehmer:</strong>
                <router-link v-for="p in trip.participants" :key="p.id" :to="`/dashboard/${p.id}`" @click.stop class="participant-tag user-link">
                  {{ p.username }}
                </router-link>
              </div>
              <!-- Show huts for hiking trips -->
              <div class="huts" v-if="trip.activity_type === 'HIKING' && trip.huts?.length > 0">
                <strong>🏔️ Hütten:</strong>
                <template v-for="hut in trip.huts" :key="hut.id">
                  <a v-if="hut.link" :href="hut.link" target="_blank" @click.stop class="hut-tag">
                    {{ hut.name }} 🔗
                  </a>
                  <span v-else class="hut-tag">{{ hut.name }}</span>
                </template>
              </div>
              
              <!-- Show country for surf trips -->
              <div class="country" v-if="trip.activity_type === 'SURFING' && trip.country_display">
                <strong>🌍 Land:</strong>
                <span class="country-tag">{{ getCountryWithFlag(trip) }}</span>
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
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import { currentUser, setCurrentTab } from '../store';
import MultiSelectDropdown from './MultiSelectDropdown.vue';
import AdvancedSearch from './AdvancedSearch.vue';
import HikingAdvancedSearch from './HikingAdvancedSearch.vue';

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
      filters.value.participants.forEach(id => params.append('participants', id));
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
  // Merge advanced filters with existing filters
  const combinedParams = new URLSearchParams();

  // Add basic filters
  if (filters.value.search) combinedParams.append('search', filters.value.search);
  if (filters.value.participants.length > 0) {
    filters.value.participants.forEach(id => combinedParams.append('participants', id));
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
  // Merge advanced hiking filters with existing filters
  const combinedParams = new URLSearchParams();
  // Add basic filters
  if (filters.value.search) combinedParams.append('search', filters.value.search);
  if (filters.value.participants.length > 0) {
    filters.value.participants.forEach(id => combinedParams.append('participants', id));
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
  const category = categories.value.find(cat => cat.value === activeCategory.value);
  return `${category?.icon} ${category?.label} hinzufügen`;
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
};

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
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('de-DE', options);
};

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return Math.round(num).toLocaleString('de-CH');
};

const formatDuration = (duration) => {
  if (!duration) return '0h 0m';
  
  let totalSeconds;
  if (typeof duration === 'string') {
    if (duration.includes('day')) {
      const dayMatch = duration.match(/(\d+)\s*day/);
      const days = dayMatch ? parseInt(dayMatch[1]) : 0;
      
      const timeMatch = duration.match(/(\d{1,2}):(\d{2}):(\d{2})/);
      if (timeMatch) {
        const hours = parseInt(timeMatch[1]) + (days * 24);
        const minutes = parseInt(timeMatch[2]);
        return `${hours}h ${minutes}m`;
      }
      return `${days * 24}h 0m`;
    } else {
      const timeParts = duration.split(':');
      if (timeParts.length >= 2) {
        const hours = parseInt(timeParts[0]);
        const minutes = parseInt(timeParts[1]);
        return `${hours}h ${minutes}m`;
      }
    }
  } else if (typeof duration === 'number') {
    totalSeconds = duration;
  }
  
  if (totalSeconds !== undefined) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
  
  return '0h 0m';
};

const logout = () => {
  // Use centralized logout from api.js
  import('../api').then(module => {
    module.logout();
  });
};


// Surf-specific helper functions
const getSurfStageCount = (trip) => {
  return trip.surf_session_count || trip.stage_count || '0';
};

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
/* Your original CSS from GitHub with additions for pagination */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1.5rem; }

/* Category tabs styling */
.category-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: transparent;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.2s ease;
}

.category-tab:hover {
  background-color: rgba(255, 255, 255, 0.7);
  color: #495057;
}

.category-tab.active {
  background-color: white;
  color: #333;
  border-color: #0d6efd;
  box-shadow: 0 2px 8px rgba(13, 110, 253, 0.15);
}

.category-icon {
  font-size: 1.2rem;
}
.header > .controls { display: flex; gap: 1rem; flex-wrap: wrap; }
.btn { display: inline-block; padding: 0.8rem 1.5rem; color: white; text-decoration: none; border-radius: 12px; font-weight: bold; border: none; cursor: pointer; font-size: 0.95rem; }
.btn-new-trip { background-color: #42b983; }
.btn-dashboard { background-color: #0d6efd; }
.btn-logout { background-color: #6c757d; }
.error-message { color: red; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem; align-items: center; }
.search-input { flex-grow: 1; padding: 0.8rem 1rem; font-size: 1rem; border-radius: 8px; border: 1px solid #ccc; min-width: 200px; }
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; }
.filter-group input[type="date"] { padding: 0.7rem; border-radius: 8px; border: 1px solid #ccc; }
.btn-clear { background-color: #6c757d; color: white; border: none; padding: 1rem 1.5rem; border-radius: 12px; cursor: pointer; font-size: 1rem; }
.btn-advanced { background-color: #42b983; transition: background-color 0.2s ease; }
.btn-advanced:hover { background-color: #369870; }
.btn-advanced.active { background-color: #28a745; }
.trip-list { list-style: none; padding: 0; }
.trip-card { display: flex; background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: box-shadow 0.2s ease-in-out; position: relative; }
.trip-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.card-content { padding: 1.5rem; width: 100%; padding-right: 2.5rem; }
.trip-info h2 { margin: 0 0 0.25rem 0; }
.trip-link { text-decoration: none; color: inherit; }
.trip-link:hover h2 { color: #0d6efd; }
.meta-info { display: flex; align-items: center; gap: 0.5rem; color: #6c757d; font-size: 0.9rem; margin-bottom: 1rem; flex-wrap: wrap; }
.user-link { color: #0d6efd; text-decoration: none; font-weight: 500; }
.user-link:hover { text-decoration: underline; }
.trip-stats { display: flex; align-items: baseline; gap: 1rem; padding: 1rem 0; border-top: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0; }
.stat-item { text-align: left; }
.stat-value { font-size: 1.5rem; font-weight: 500; color: #333; }
.stat-value small { font-size: 0.9rem; font-weight: 400; color: #6c757d; margin-left: 0.25rem; }
.stat-item label { font-size: 0.8rem; color: #6c757d; display: block; margin-top: -5px; }
.stat-separator { color: #e0e0e0; font-size: 1.5rem; }
.tags-container { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; font-size: 0.9rem; }
.participants, .huts, .country { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
.participant-tag, .hut-tag, .country-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; margin-right: 0.5rem; margin-top: 0.25rem; }
.participant-tag { background-color: #e9ecef; color: #495057; }
.hut-tag { background-color: #d1ecf1; color: #0c5460; text-decoration: none; }
.country-tag { background-color: #20b2aa; color: white; font-weight: 500; }

/* Surf-specific styling */
.surf-stats {
  border-color: #20b2aa;
}
.surf-stats .stat-value {
  color: #20b2aa;
}

.btn-delete { position: absolute; top: 1rem; right: 1rem; background-color: transparent; border: none; color: #aaa; cursor: pointer; font-size: 1.2rem; }
.btn-delete:hover { color: #dc3545; }
.pagination-controls { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; align-items: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-top: -1rem; margin-bottom: 2rem; }
.page-navigation { display: flex; align-items: center; gap: 1rem; }
.page-navigation button { padding: 0.5rem 1rem; border: 1px solid #ccc; border-radius: 4px; }
.page-navigation button:disabled { opacity: 0.5; cursor: not-allowed; }
.results-count { text-align: right; color: #6c757d; margin: 0; }
.filter-bar .results-count { margin-left: auto; font-weight: 500; }
.results-summary { padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem; text-align: center; }
.results-summary .results-count { text-align: center; font-weight: 500; color: #20b2aa; }

/* Infinite scroll styles */
.infinite-scroll-status {
  text-align: center;
  padding: 2rem 0;
}

.loading-more {
  color: #6c757d;
  font-style: italic;
  padding: 1rem;
}

.no-more-trips {
  color: #6c757d;
  font-size: 0.9rem;
  padding: 1rem;
  border-top: 1px solid #f0f0f0;
  margin-top: 1rem;
}

.scroll-sentinel {
  height: 1px;
  width: 100%;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    margin: 0 0.5rem 2rem 0.5rem;
  }
  
  .header > .controls {
    justify-content: center;
    gap: 0.5rem;
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
    padding: 0.75rem;
    gap: 0.5rem;
    margin: 0 0.5rem 1rem 0.5rem;
  }
  
  .search-input {
    min-width: auto;
    width: 100%;
    padding: 0.6rem 0.8rem;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
  }
  
  .filter-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  /* Special layout for date filters to appear on same line */
  .filter-group:nth-of-type(3), .filter-group:nth-of-type(4) {
    display: inline-flex;
    width: calc(50% - 0.25rem);
  }
  
  .filter-group label {
    font-size: 0.85rem;
    margin: 0;
  }
  
  .filter-group input[type="date"] {
    padding: 0.5rem;
    font-size: 0.9rem;
  }
  
  .btn-clear {
    padding: 0.8rem 1rem;
    font-size: 0.95rem;
    margin-top: 0.25rem;
    border-radius: 10px;
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
    padding: 0.6rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .category-icon {
    font-size: 1rem;
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
    gap: 0.5rem;
  }
  
  .stat-value {
    font-size: 1.2rem;
  }
}
</style>