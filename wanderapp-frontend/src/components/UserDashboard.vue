<template>
  <div>
    <div class="header-with-controls">
      <h1>Dashboard von {{ username }}</h1>
      <BaseButton tag="router-link" :to="tripListRoute" variant="secondary" size="small">
        <span class="btn-text-desktop">← Zurück zur Trip-Liste</span>
        <span class="btn-text-mobile">Zurück</span>
      </BaseButton>
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

    <!-- Error Display -->
    <div v-if="error" class="error-section">
      <p class="error">{{ error }}</p>
    </div>

    <!-- Combined Dashboard (ALL tab) -->
    <template v-if="activeCategory === 'ALL'">
      <!-- HIKING GROUP -->
      <template v-if="totals.hiking && totals.hiking.count > 0">
        <!-- Hiking Statistics -->
        <div class="section">
          <h2 class="section-title">🥾 Hiking</h2>
          <div v-if="isLoadingTotals">Lade Statistiken...</div>
          <div v-else class="stats-grid">
            <div class="stat-card activity-hiking">
              <span class="value">{{ getHikingTripCount() }}</span>
              <span class="label">Trips</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.count) }}</span>
              <span class="label">Total Hikes</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.total_km) }} <small>km</small></span>
              <span class="label">Gesamtdistanz</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.total_elevation) }} <small>m</small></span>
              <span class="label">Gesamter Aufstieg</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.total_loss) }} <small>m</small></span>
              <span class="label">Gesamter Abstieg</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatDurationFromSeconds(totals.hiking.total_duration) }}</span>
              <span class="label">Gesamte Dauer</span>
            </div>
          </div>
        </div>

        <!-- Hiking Records -->
        <div v-if="details.hiking_records && (details.hiking_records.longest_by_km || details.hiking_records.highest_by_gain || details.hiking_records.longest_by_duration)" class="section">
          <h2 class="section-title">🥾 Hiking Rekorde</h2>
          <div v-if="isLoadingDetails">Lade Rekorde...</div>
          <div v-else class="stats-grid">
            <router-link v-if="details.hiking_records.longest_by_km" :to="`/trip/${details.hiking_records.longest_by_km.trip}`" class="stat-card record-link activity-hiking">
              <span class="value">{{ details.hiking_records.longest_by_km.calculated_length_km || details.hiking_records.longest_by_km.manual_length_km }} <small>km</small></span>
              <span class="label">Längste Wanderung</span>
              <span class="context">{{ details.hiking_records.longest_by_km.name }}</span>
            </router-link>
            <router-link v-if="details.hiking_records.highest_by_gain" :to="`/trip/${details.hiking_records.highest_by_gain.trip}`" class="stat-card record-link activity-hiking">
              <span class="value">{{ details.hiking_records.highest_by_gain.calculated_elevation_gain || details.hiking_records.highest_by_gain.manual_elevation_gain }} <small>m</small></span>
              <span class="label">Grösster Aufstieg</span>
              <span class="context">{{ details.hiking_records.highest_by_gain.name }}</span>
            </router-link>
            <router-link v-if="details.hiking_records.longest_by_duration" :to="`/trip/${details.hiking_records.longest_by_duration.trip}`" class="stat-card record-link activity-hiking">
              <span class="value">{{ formatDuration(details.hiking_records.longest_by_duration.calculated_duration || details.hiking_records.longest_by_duration.manual_duration) }}</span>
              <span class="label">Längste Dauer</span>
              <span class="context">{{ details.hiking_records.longest_by_duration.name }}</span>
            </router-link>
          </div>
        </div>

        <!-- Top Hiking Partners -->
        <div v-if="hikingDetails.top_partners && hikingDetails.top_partners.length > 0" class="section">
          <h2 class="section-title">👫 Top Wanderpartner</h2>
          <div v-if="isLoadingDetails">Lade Partner...</div>
          <ol v-else class="partners-list">
            <li v-for="(partner, index) in hikingDetails.top_partners" :key="partner.id">
              <router-link :to="`/dashboard/${partner.id}`" class="partner-link">
                <span class="partner-rank">{{ index + 1 }}.</span>
                <span class="partner-name">{{ partner.username }}</span>
                <span class="partner-count">{{ partner.hike_count }} gemeinsame Trips</span>
              </router-link>
            </li>
          </ol>
        </div>
      </template>

      <!-- SURFING GROUP -->
      <template v-if="totals.surfing && totals.surfing.count > 0">
        <!-- Surfing Statistics -->
        <div class="section">
          <h2 class="section-title">🏄‍♂️ Surfing</h2>
          <div v-if="isLoadingTotals">Lade Statistiken...</div>
          <div v-else class="stats-grid">
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatNumber(totals.surfing.count) }}</span>
              <span class="label">Total Sessions</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatDurationFromSeconds(totals.surfing.total_time_in_water) }}</span>
              <span class="label">Total Time in Water</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatNumber(totals.surfing.total_waves_caught) }}</span>
              <span class="label">Total Wavecount</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ totals.surfing.most_used_surfboard || 'N/A' }}</span>
              <span class="label">Most Surfed Surfboard</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatTemperature(totals.surfing.avg_water_temperature) }}</span>
              <span class="label">Average Water Temperature</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatTemperature(totals.surfing.min_water_temperature) }}</span>
              <span class="label">Coldest Water Temperature</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatTemperature(totals.surfing.max_water_temperature) }}</span>
              <span class="label">Hottest Water Temperature</span>
            </div>
          </div>
        </div>

        <!-- Surfing Records -->
        <div v-if="details.surfing_records && (details.surfing_records.longest_session || details.surfing_records.most_waves_caught || details.surfing_records.best_wave_quality)" class="section">
          <h2 class="section-title">🏄‍♂️ Surfing Rekorde</h2>
          <div v-if="isLoadingDetails">Lade Rekorde...</div>
          <div v-else class="stats-grid">
            <router-link v-if="details.surfing_records.longest_session" :to="`/trip/${details.surfing_records.longest_session.trip}`" class="stat-card record-link activity-surfing">
              <span class="value">{{ formatDuration(details.surfing_records.longest_session.time_in_water) }}</span>
              <span class="label">Längste Session</span>
              <span class="context">{{ details.surfing_records.longest_session.name }}</span>
            </router-link>
            <router-link v-if="details.surfing_records.most_waves_caught" :to="`/trip/${details.surfing_records.most_waves_caught.trip}`" class="stat-card record-link activity-surfing">
              <span class="value">{{ details.surfing_records.most_waves_caught.waves_caught }}</span>
              <span class="label">Meiste Wellen</span>
              <span class="context">{{ details.surfing_records.most_waves_caught.name }}</span>
            </router-link>
            <router-link v-if="details.surfing_records.best_wave_quality" :to="`/trip/${details.surfing_records.best_wave_quality.trip}`" class="stat-card record-link activity-surfing">
              <span class="value">{{ '⭐'.repeat(details.surfing_records.best_wave_quality.wave_quality) }}</span>
              <span class="label">Beste Wellenqualität</span>
              <span class="context">{{ details.surfing_records.best_wave_quality.name }}</span>
            </router-link>
          </div>
        </div>

        <!-- Top Surfing Partners -->
        <div v-if="surfingDetails.top_partners && surfingDetails.top_partners.length > 0" class="section">
          <h2 class="section-title">👫 Top Surf-Partners</h2>
          <div v-if="isLoadingDetails">Lade Partner...</div>
          <ol v-else class="partners-list">
            <li v-for="(partner, index) in surfingDetails.top_partners" :key="partner.id">
              <router-link :to="`/dashboard/${partner.id}`" class="partner-link">
                <span class="partner-rank">{{ index + 1 }}.</span>
                <span class="partner-name">{{ partner.username }}</span>
                <span class="partner-count">{{ partner.hike_count }} gemeinsame Surf-Trips</span>
              </router-link>
            </li>
          </ol>
        </div>
      </template>
    </template>

    <!-- Individual Activity Tabs -->
    <template v-else>
      <div class="section">
        <h2 class="section-title">{{ getSectionTitle() }}</h2>
        <div v-if="isLoadingTotals">Lade Statistiken...</div>
        <div v-else class="stats-grid">
          <!-- Hiking specific stats -->
          <template v-if="activeCategory === 'HIKING' && totals.hiking">
            <div class="stat-card activity-hiking">
              <span class="value">{{ getHikingTripCount() }}</span>
              <span class="label">Trips</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.count) }}</span>
              <span class="label">Total Hikes</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.total_km) }} <small>km</small></span>
              <span class="label">Gesamtdistanz</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.total_elevation) }} <small>m</small></span>
              <span class="label">Gesamter Aufstieg</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatNumber(totals.hiking.total_loss) }} <small>m</small></span>
              <span class="label">Gesamter Abstieg</span>
            </div>
            <div class="stat-card activity-hiking">
              <span class="value">{{ formatDurationFromSeconds(totals.hiking.total_duration) }}</span>
              <span class="label">Gesamte Dauer</span>
            </div>
          </template>
          
          <!-- Surfing specific stats -->
          <template v-else-if="activeCategory === 'SURFING' && totals.surfing">
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatNumber(totals.surfing.count) }}</span>
              <span class="label">Total Sessions</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatDurationFromSeconds(totals.surfing.total_time_in_water) }}</span>
              <span class="label">Total Time in Water</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatNumber(totals.surfing.total_waves_caught) }}</span>
              <span class="label">Total Wavecount</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ totals.surfing.most_used_surfboard || 'N/A' }}</span>
              <span class="label">Most Surfed Surfboard</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatTemperature(totals.surfing.avg_water_temperature) }}</span>
              <span class="label">Average Water Temperature</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatTemperature(totals.surfing.min_water_temperature) }}</span>
              <span class="label">Coldest Water Temperature</span>
            </div>
            <div class="stat-card activity-surfing">
              <span class="value">{{ formatTemperature(totals.surfing.max_water_temperature) }}</span>
              <span class="label">Hottest Water Temperature</span>
            </div>
          </template>
        </div>
      </div>
    </template>


    <!-- Personal Records - Only for individual activity tabs (not for surfing) -->
    <div v-if="activeCategory === 'HIKING' && details.longest_stage_by_km" class="section">
      <h2 class="section-title">{{ getRecordsTitle() }}</h2>
      <div v-if="isLoadingDetails">Lade Rekorde...</div>
      <div v-else class="stats-grid">
        <router-link v-if="details.longest_stage_by_km" :to="`/trip/${details.longest_stage_by_km.trip}`" class="stat-card record-link">
          <span class="value">{{ details.longest_stage_by_km.calculated_length_km || details.longest_stage_by_km.manual_length_km }} <small>km</small></span>
          <span class="label">Längste Etappe</span>
          <span class="context">{{ details.longest_stage_by_km.name }}</span>
        </router-link>
        <router-link v-if="details.highest_stage_by_gain" :to="`/trip/${details.highest_stage_by_gain.trip}`" class="stat-card record-link">
          <span class="value">{{ details.highest_stage_by_gain.calculated_elevation_gain || details.highest_stage_by_gain.manual_elevation_gain }} <small>m</small></span>
          <span class="label">Grösster Aufstieg</span>
          <span class="context">{{ details.highest_stage_by_gain.name }}</span>
        </router-link>
        <router-link v-if="details.longest_stage_by_duration" :to="`/trip/${details.longest_stage_by_duration.trip}`" class="stat-card record-link">
          <span class="value">{{ formatDuration(details.longest_stage_by_duration.calculated_duration || details.longest_stage_by_duration.manual_duration) }}</span>
          <span class="label">Längste Dauer</span>
          <span class="context">{{ details.longest_stage_by_duration.name }}</span>
        </router-link>
      </div>
    </div>

    
    <!-- Top Partners (for individual activity tabs only) -->
    <div v-if="activeCategory !== 'ALL'" class="section">
      <h2 v-if="activeCategory === 'SURFING'" class="section-title">Top Surf-Partners</h2>
      <h2 v-else class="section-title">Top Wanderpartner</h2>
      <div v-if="isLoadingDetails">Lade Partner...</div>
      <ol v-else-if="details.top_partners && details.top_partners.length" class="partners-list">
        <li v-for="(partner, index) in details.top_partners" :key="partner.id">
          <router-link :to="`/dashboard/${partner.id}`" class="partner-link">
            <span class="partner-rank">{{ index + 1 }}.</span>
            <span class="partner-name">{{ partner.username }}</span>
            <span v-if="activeCategory === 'SURFING'" class="partner-count">{{ partner.hike_count }} gemeinsame Surf-Trips</span>
            <span v-else class="partner-count">{{ partner.hike_count }} gemeinsame Trips</span>
          </router-link>
        </li>
      </ol>
      <p v-else><em>Sie waren bisher alleine unterwegs.</em></p>
    </div>

    <div v-if="activeCategory !== 'ALL'" class="export-section">
      <BaseButton @click="downloadCSV" :loading="isDownloading" variant="primary" size="large">
        {{ getExportButtonText() }}
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';
import { getTripListRoute } from '../utils/navigation.js';
import BaseButton from './base/BaseButton.vue';
import { formatDurationHoursMinutes, formatDurationFromSeconds as formatDurationFromSecondsUtil } from '../utils/duration.js';

const route = useRoute();

// Computed property for trip list navigation
const tripListRoute = computed(() => getTripListRoute());
const totals = ref({});
const details = ref({});
const hikingDetails = ref({});
const surfingDetails = ref({});
const isLoadingTotals = ref(true);
const isLoadingDetails = ref(true);
const error = ref(null);
const username = ref('Dir');
const isDownloading = ref(false);

// Category management
const activeCategory = ref('ALL');
const categories = ref([
  { value: 'ALL', label: 'Alle', icon: '📊' },
  { value: 'HIKING', label: 'Wandern', icon: '🥾' },
  { value: 'SURFING', label: 'Surfen', icon: '🏄‍♂️' }
]);

const fetchData = async () => {
  try {
    isLoadingTotals.value = true;
    isLoadingDetails.value = true;
    error.value = null;
    const userId = route.params.id;
    
    if (activeCategory.value === 'ALL') {
      // For ALL tab, fetch general stats plus specific activity details
      const [totalsResponse, detailsResponse, hikingDetailsResponse, surfingDetailsResponse] = await Promise.all([
        api.get(userId ? `/stats/${userId}` : `/stats`),
        api.get(userId ? `/dashboard-data/${userId}` : `/dashboard-data`),
        api.get(userId ? `/dashboard-data/${userId}?activity_type=HIKING` : `/dashboard-data?activity_type=HIKING`),
        api.get(userId ? `/dashboard-data/${userId}?activity_type=SURFING` : `/dashboard-data?activity_type=SURFING`)
      ]);
      
      // Structure the totals data for the template
      const rawTotals = totalsResponse.data;
      totals.value = {
        hiking: rawTotals.hiking,
        surfing: rawTotals.surfing,
        trip_count: rawTotals.trip_count,
        stage_count: rawTotals.stage_count,
        total_km: rawTotals.total_km,
        total_elevation: rawTotals.total_elevation,
        total_loss: rawTotals.total_loss,
        total_duration: rawTotals.total_duration
      };
      
      details.value = detailsResponse.data;
      hikingDetails.value = hikingDetailsResponse.data;
      surfingDetails.value = surfingDetailsResponse.data;
      username.value = rawTotals.username;
    } else {
      // For individual activity tabs, use activity filter
      const queryParams = new URLSearchParams();
      queryParams.append('activity_type', activeCategory.value);
      const queryString = queryParams.toString();
      const urlSuffix = `?${queryString}`;
      
      const [totalsResponse, detailsResponse] = await Promise.all([
        api.get(userId ? `/stats/${userId}${urlSuffix}` : `/stats${urlSuffix}`),
        api.get(userId ? `/dashboard-data/${userId}${urlSuffix}` : `/dashboard-data${urlSuffix}`)
      ]);
      
      // Structure the totals data for the template
      const rawTotals = totalsResponse.data;
      totals.value = {
        hiking: rawTotals.hiking,
        surfing: rawTotals.surfing,
        trip_count: rawTotals.trip_count,
        stage_count: rawTotals.stage_count,
        total_km: rawTotals.total_km,
        total_elevation: rawTotals.total_elevation,
        total_loss: rawTotals.total_loss,
        total_duration: rawTotals.total_duration
      };
      
      details.value = detailsResponse.data;
      username.value = rawTotals.username;
    }
  } catch (err) {
    console.error('Dashboard fetch error:', err);
    error.value = "Fehler beim Laden der Dashboard-Daten: " + (err.response?.data?.detail || err.message);
  } finally {
    isLoadingTotals.value = false;
    isLoadingDetails.value = false;
  }
};

// Category management
const setActiveCategory = (category) => {
  activeCategory.value = category;
  fetchData();
};

const getSectionTitle = () => {
  switch (activeCategory.value) {
    case 'HIKING':
      return '🥾 Hiking Statistiken';
    case 'SURFING':
      return '🏄‍♂️ Surfing Statistiken';
    default:
      return 'Total';
  }
};

const getRecordsTitle = () => {
  switch (activeCategory.value) {
    case 'HIKING':
      return '🥾 Hiking Rekorde';
    case 'SURFING':
      return '🏄‍♂️ Surfing Rekorde';
    default:
      return 'Persönliche Rekorde';
  }
};

onMounted(fetchData);
watch(() => route.params.id, fetchData);

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString('de-CH');
};

const formatDuration = formatDurationHoursMinutes;
const formatDurationFromSeconds = (seconds) => formatDurationFromSecondsUtil(seconds || 0);

const formatTemperature = (temp) => {
  if (temp === null || temp === undefined) return 'N/A';
  return `${temp}°C`;
};

const getHikingTripCount = () => {
  if (!totals.value || !totals.value.trip_count) return 0;
  return totals.value.trip_count;
};

const getExportButtonText = () => {
  switch (activeCategory.value) {
    case 'HIKING':
      return 'Hiking-Trips als CSV exportieren';
    case 'SURFING':
      return 'Surf-Sessions als CSV exportieren';
    default:
      return 'Alle Aktivitäten als CSV exportieren';
  }
};

const downloadCSV = async () => {
  isDownloading.value = true;
  try {
    // Build API endpoint with activity type filter if applicable
    let apiEndpoint = '/trips/';
    if (activeCategory.value !== 'ALL') {
      apiEndpoint += `?activity_type=${activeCategory.value}`;
    }

    const response = await api.get(apiEndpoint);
    const tripsList = response.data.results || response.data;

    // Check if trips is valid
    if (!tripsList || !Array.isArray(tripsList)) {
      throw new Error('Keine Trips gefunden oder ungültige Datenstruktur');
    }

    // Fetch detailed data for each trip (to get stages)
    const tripDetailsPromises = tripsList.map(trip => api.get(`/trips/${trip.id}/`));
    const tripDetailsResponses = await Promise.all(tripDetailsPromises);
    const trips = tripDetailsResponses.map(response => response.data);

    let csvContent = "data:text/csv;charset=utf-8,";

    // Generate headers and filename based on activity type
    let headers = [];
    let filename = '';

    if (activeCategory.value === 'HIKING') {
      headers = ["Trip Name", "Trip Start Date", "Trip End Date", "Stage Name", "Stage Date", "Distance (km)", "Elevation Gain (m)", "Elevation Loss (m)", "Duration", "Stage Description", "Creator", "Participants"];
      filename = "hiking_export.csv";
    } else if (activeCategory.value === 'SURFING') {
      headers = ["Trip Name", "Trip Start Date", "Trip End Date", "Country", "Stage Name", "Stage Date", "Surf Spot", "Time in Water", "Waves Caught", "Surfboard Used", "Wave Quality", "Wave Height (m)", "Water Temp (°C)", "Tide Stage", "Tide Movement", "Swell Direction", "Wind Direction", "Wave Energy", "Stage Description", "Creator", "Participants"];
      filename = "surfing_export.csv";
    } else {
      // Combined export includes all fields
      headers = ["Trip Name", "Trip Start Date", "Trip End Date", "Country", "Stage Name", "Stage Date", "Activity Type", "Distance (km)", "Elevation Gain (m)", "Elevation Loss (m)", "Duration", "Surf Spot", "Time in Water", "Waves Caught", "Surfboard Used", "Wave Quality", "Wave Height (m)", "Water Temp (°C)", "Tide Stage", "Tide Movement", "Swell Direction", "Wind Direction", "Wave Energy", "Stage Description", "Creator", "Participants"];
      filename = "all_activities_export.csv";
    }

    csvContent += headers.join(',') + "\r\n";

    trips.forEach(trip => {
      if (trip && trip.stages && Array.isArray(trip.stages) && trip.stages.length > 0) {
        trip.stages.forEach(stage => {
          const participants = (trip.participants && Array.isArray(trip.participants))
            ? trip.participants.map(p => p.username).join('; ')
            : '';
          let row = [];

          if (activeCategory.value === 'HIKING') {
            const distance = stage.calculated_length_km || stage.manual_length_km || 0;
            const gain = stage.calculated_elevation_gain || stage.manual_elevation_gain || 0;
            const loss = stage.calculated_elevation_loss || 0;
            const duration = stage.calculated_duration || stage.manual_duration || '00:00:00';

            row = [
              `"${trip.name}"`,
              trip.start_date,
              trip.end_date,
              `"${stage.name}"`,
              stage.date,
              distance,
              gain,
              loss,
              duration,
              `"${stage.description || ''}"`,
              `"${trip.creator ? trip.creator.username : ''}"`,
              `"${participants}"`
            ];
          } else if (activeCategory.value === 'SURFING') {
            const timeInWater = stage.time_in_water || '00:00:00';
            const waveQuality = stage.wave_quality ? '⭐'.repeat(stage.wave_quality) : '';

            row = [
              `"${trip.name}"`,
              trip.start_date,
              trip.end_date,
              `"${trip.country || ''}"`,
              `"${stage.name}"`,
              stage.date,
              `"${stage.surf_spot || ''}"`,
              timeInWater,
              stage.waves_caught || 0,
              `"${stage.surfboard?.name || stage.surfboard_used || ''}"`,
              waveQuality,
              stage.wave_height || '',
              stage.water_temperature || '',
              stage.tide_stage || '',
              stage.tide_movement || '',
              stage.swell_direction || '',
              stage.wind_direction || '',
              stage.wave_energy || '',
              `"${stage.description || ''}"`,
              `"${trip.creator ? trip.creator.username : ''}"`,
              `"${participants}"`
            ];
          } else {
            // Combined export - include all fields
            const distance = stage.calculated_length_km || stage.manual_length_km || 0;
            const gain = stage.calculated_elevation_gain || stage.manual_elevation_gain || 0;
            const loss = stage.calculated_elevation_loss || 0;
            const duration = stage.calculated_duration || stage.manual_duration || '00:00:00';
            const timeInWater = stage.time_in_water || '00:00:00';
            const waveQuality = stage.wave_quality ? '⭐'.repeat(stage.wave_quality) : '';

            row = [
              `"${trip.name}"`,
              trip.start_date,
              trip.end_date,
              `"${trip.country || ''}"`,
              `"${stage.name}"`,
              stage.date,
              stage.activity_type || 'HIKING',
              distance,
              gain,
              loss,
              duration,
              `"${stage.surf_spot || ''}"`,
              timeInWater,
              stage.waves_caught || 0,
              `"${stage.surfboard?.name || stage.surfboard_used || ''}"`,
              waveQuality,
              stage.wave_height || '',
              stage.water_temperature || '',
              stage.tide_stage || '',
              stage.tide_movement || '',
              stage.swell_direction || '',
              stage.wind_direction || '',
              stage.wave_energy || '',
              `"${stage.description || ''}"`,
              `"${trip.creator ? trip.creator.username : ''}"`,
              `"${participants}"`
            ];
          }

          csvContent += row.join(',') + "\r\n";
        });
      }
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    alert("Fehler beim Exportieren: " + err.message);
  } finally {
    isDownloading.value = false;
  }
};
</script>

<style scoped>
/* UserDashboard - Migrated to Design System */
.header-with-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  gap: var(--space-4);
}

.header-with-controls h1 {
  margin: 0;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  min-width: 0;
  flex: 1;
}

.btn-text-mobile {
  display: none;
}

.btn-text-desktop {
  display: inline;
}

.section {
  margin-bottom: var(--space-10);
}

.section-title {
  margin-bottom: var(--space-6);
  font-size: var(--text-2xl);
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border-medium);
  padding-bottom: var(--space-2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-6);
}

.stat-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  display: flex;
  flex-direction: column;
}

.record-link {
  text-decoration: none;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.record-link:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.value {
  font-size: var(--text-4xl);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.value small {
  font-size: var(--text-xl);
  font-weight: var(--font-normal);
  color: var(--color-text-secondary);
}

.label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

.context {
  font-size: var(--text-base);
  color: var(--color-text-primary);
  margin-top: var(--space-4);
  font-style: italic;
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--space-4);
}

.partners-list {
  list-style: none;
  padding: 0;
}

.partner-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-secondary);
  margin-bottom: var(--space-2);
  text-decoration: none;
  color: inherit;
  transition: background-color var(--transition-fast);
}

.partner-link:hover {
  background-color: var(--color-bg-tertiary);
}

.partner-rank {
  font-weight: var(--font-bold);
  color: var(--color-text-secondary);
  margin-right: var(--space-4);
}

.partner-name {
  font-weight: var(--font-medium);
  flex-grow: 1;
}

.partner-count {
  color: var(--color-text-secondary);
}

.export-section {
  text-align: center;
  margin-top: var(--space-10);
}

.error {
  color: var(--color-error);
}

.error-section {
  margin-bottom: var(--space-6);
}

.error-section .error {
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
}

/* Activity-specific styling */
.activity-hiking {
  border-left: 4px solid var(--color-hiking);
}

.activity-running {
  border-left: 4px solid var(--color-running);
}

.activity-surfing {
  border-left: 4px solid var(--color-surfing);
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
  border: 1px solid transparent;
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

/* Mobile responsive category tabs */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr; /* Stack cards on mobile */
    gap: var(--space-4);
  }

  .stat-card {
    padding: var(--space-5);
  }

  .value {
    font-size: var(--text-3xl); /* Slightly smaller on mobile */
  }

  .label {
    margin-top: var(--space-2); /* More space between value and label */
  }

  .context {
    margin-top: var(--space-3);
    padding-top: var(--space-3);
    font-size: var(--text-sm); /* Smaller to prevent awkward wrapping */
  }
}

@media (max-width: 768px) {
  /* Show mobile text, hide desktop text */
  .btn-text-mobile {
    display: inline;
  }

  .btn-text-desktop {
    display: none;
  }

  .header-with-controls {
    flex-direction: column-reverse;
    align-items: stretch;
    gap: var(--space-4);
    margin: 0 0.5rem var(--space-8) 0.5rem;
  }

  .header-with-controls h1 {
    font-size: var(--text-2xl); /* Smaller heading on mobile */
  }

  .section {
    margin: 0 0.5rem var(--space-8) 0.5rem;
  }
}

@media (max-width: 600px) {
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
    min-height: 44px; /* Ensure proper touch target */
  }

  .stat-card {
    padding: var(--space-4); /* Reduce padding on smaller mobile */
  }

  .partners-list {
    margin: 0 0.5rem;
  }

  .records-grid {
    grid-template-columns: 1fr; /* Stack record cards on mobile */
    gap: var(--space-4);
  }
}
</style>
