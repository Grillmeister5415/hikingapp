<template>
  <div>
    <div class="header">
      <h1>Meine Trips</h1>
      <div class="controls">
        <router-link to="/dashboard" class="btn btn-dashboard">Mein Dashboard</router-link>
        <router-link to="/trip/new" class="btn btn-new-trip">Neuen Trip erstellen +</router-link>
        <button @click="logout" class="btn btn-logout">Ausloggen</button>
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
    </div>

    <div v-if="isLoading">Lade Trips...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else>
      <p class="results-count">{{ trips.length }} Trip(s) gefunden.</p>
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
              <div class="participants" v-if="trip.participants.length">
                <strong>Teilnehmer:</strong>
                <router-link v-for="p in trip.participants" :key="p.id" :to="`/dashboard/${p.id}`" @click.stop class="participant-tag user-link">
                  {{ p.username }}
                </router-link>
              </div>
              <div class="huts" v-if="trip.huts.length">
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
          
          <button v-if="currentUser && currentUser.id === trip.creator.id" @click.stop="handleDeleteTrip(trip.id)" class="btn-delete" title="Trip löschen">🗑️</button>
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
    if (filters.value.search) params.append('search', filters.value.search);
    if (filters.value.participants.length > 0) {
      filters.value.participants.forEach(id => params.append('participants', id));
    }
    if (filters.value.from_date) params.append('from_date', filters.value.from_date);
    if (filters.value.to_date) params.append('to_date', filters.value.to_date);
    const response = await api.get(`/trips/?${params.toString()}`);
    trips.value = response.data;
  } catch (err) {
    error.value = "Fehler beim Laden der Trips.";
  } finally {
    isLoading.value = false;
  }
};

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/');
    allUsers.value = response.data;
  } catch (err) {
    console.error("Fehler beim Laden der Benutzerliste.");
  }
};

watch(filters, fetchTrips, { deep: true });

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
      trips.value = trips.value.filter(trip => trip.id !== tripId);
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
  return num.toLocaleString('de-CH');
};

const logout = () => {
  localStorage.clear();
  currentUser.value = null;
  router.push('/login');
};
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
.header > .controls { display: flex; gap: 1rem; }
.btn { display: inline-block; padding: 0.8rem 1.5rem; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; border: none; cursor: pointer; }
.btn-new-trip { background-color: #42b983; }
.btn-dashboard { background-color: #0d6efd; }
.btn-logout { background-color: #6c757d; }
.error-message { color: red; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 2rem; align-items: center; }
.search-input { flex-grow: 1; padding: 0.8rem 1rem; font-size: 1rem; border-radius: 8px; border: 1px solid #ccc; min-width: 200px; }
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; }
.filter-group input[type="date"] { padding: 0.7rem; border-radius: 8px; border: 1px solid #ccc; }
.btn-clear { background-color: #6c757d; color: white; border: none; padding: 0.8rem 1rem; border-radius: 8px; cursor: pointer; }
.results-count { text-align: right; color: #6c757d; margin-bottom: 0.5rem; }
.trip-list { list-style: none; padding: 0; }
.trip-card { display: flex; background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: box-shadow 0.2s ease-in-out; position: relative; }
.trip-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.card-content { padding: 1.5rem; width: 100%; }
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
</style>