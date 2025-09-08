<template>
  <div>
    <div class="header">
      <h1>Meine Trips</h1>
      <div class="controls">
        <router-link to="/dashboard" class="btn btn-dashboard">Dashboard</router-link>
        <router-link to="/trip/new" class="btn btn-new-trip">Add Trip</router-link>
        <button @click="logout" class="btn btn-logout">Logout</button>
      </div>
    </div>

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
      <button @click="clearFilters" class="btn-clear">Filter zurücksetzen</button>
      <p class="results-count">{{ totalTrips }} Trip(s) gefunden.</p>
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
      <div class="page-navigation">
        <button @click="prevPage" :disabled="!previousPageUrl || isLoading">‹</button>
        <span>Seite {{ currentPage }}</span>
        <button @click="nextPage" :disabled="!nextPageUrl || isLoading">›</button>
      </div>
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
            
            <div class="trip-stats">
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

            <div class="tags-container">
              <div class="participants" v-if="trip.participants?.length > 0">
                <strong>Teilnehmer:</strong>
                <router-link v-for="p in trip.participants" :key="p.id" :to="`/dashboard/${p.id}`" @click.stop class="participant-tag user-link">
                  {{ p.username }}
                </router-link>
              </div>
              <div class="huts" v-if="trip.huts?.length > 0">
                <strong>Hütten:</strong>
                <template v-for="hut in trip.huts" :key="hut.id">
                  <a v-if="hut.link" :href="hut.link" target="_blank" @click.stop class="hut-tag">
                    {{ hut.name }} 🔗
                  </a>
                  <span v-else class="hut-tag">{{ hut.name }}</span>
                </template>
              </div>
            </div>
          </div>
          
          <button v-if="currentUser && currentUser.id === trip.creator?.id" @click.stop="handleDeleteTrip(trip.id)" class="btn-delete" title="Trip löschen">🗑️</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { currentUser } from '../store';
import MultiSelectDropdown from './MultiSelectDropdown.vue';

const router = useRouter();
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

const filters = ref({
  search: '',
  participants: [],
  from_date: '',
  to_date: ''
});

const fetchTrips = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    const params = new URLSearchParams();

    // --- Add filter parameters ---
    if (filters.value.search) params.append('search', filters.value.search);
    if (filters.value.participants.length > 0) {
      filters.value.participants.forEach(id => params.append('participants', id));
    }
    if (filters.value.from_date) params.append('from_date', filters.value.from_date);
    if (filters.value.to_date) params.append('to_date', filters.value.to_date);
    
    // --- Add pagination parameters ---
    params.append('page', currentPage.value);
    params.append('page_size', pageSize.value);

    const response = await api.get(`/trips/`, { params });

    // --- CORRECTLY HANDLE PAGINATED RESPONSE ---
    trips.value = response.data.results;
    totalTrips.value = response.data.count;
    nextPageUrl.value = response.data.next;
    previousPageUrl.value = response.data.previous;

  } catch (err) {
    console.error("API Error:", err.response?.data || err.message);
    error.value = "Fehler beim Laden der Trips. Bitte versuchen Sie es später erneut.";
  } finally {
    isLoading.value = false;
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

// --- Watcher resets to page 1 on any filter change ---
const onFilterChange = () => {
  currentPage.value = 1;
  fetchTrips();
};

watch(filters, onFilterChange, { deep: true });
watch(pageSize, onFilterChange);


onMounted(() => {
  fetchTrips();
  fetchUsers();
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
  localStorage.clear();
  currentUser.value = null;
  router.push('/login');
};

// --- NEW: Pagination methods ---
const nextPage = () => {
  if (nextPageUrl.value) {
    currentPage.value++;
    fetchTrips();
  }
};

const prevPage = () => {
  if (previousPageUrl.value) {
    currentPage.value--;
    fetchTrips();
  }
};

</script>

<style scoped>
/* Your original CSS from GitHub with additions for pagination */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem; flex-wrap: wrap; gap: 1.5rem; }
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
.participants, .huts { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
.participant-tag, .hut-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; margin-right: 0.5rem; margin-top: 0.25rem; }
.participant-tag { background-color: #e9ecef; color: #495057; }
.hut-tag { background-color: #d1ecf1; color: #0c5460; text-decoration: none; }
.btn-delete { position: absolute; top: 1rem; right: 1rem; background-color: transparent; border: none; color: #aaa; cursor: pointer; font-size: 1.2rem; }
.btn-delete:hover { color: #dc3545; }
.pagination-controls { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; align-items: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-top: -1rem; margin-bottom: 2rem; }
.page-navigation { display: flex; align-items: center; gap: 1rem; }
.page-navigation button { padding: 0.5rem 1rem; border: 1px solid #ccc; border-radius: 4px; }
.page-navigation button:disabled { opacity: 0.5; cursor: not-allowed; }
.results-count { text-align: right; color: #6c757d; margin: 0; }
.filter-bar .results-count { margin-left: auto; font-weight: 500; }

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