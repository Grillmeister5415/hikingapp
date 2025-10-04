<template>
  <div>
    <div class="header-with-controls">
      <h1>Dashboard von {{ username }}</h1>
      <BaseButton tag="router-link" :to="tripListRoute" variant="secondary" size="small">
        <span class="btn-text-desktop">← Zurück zur Trip-Liste</span>
        <span class="btn-text-mobile">Zurück</span>
      </BaseButton>
    </div>

    <!-- Year Filter -->
    <div class="year-filter">
      <label for="year-select">Jahr:</label>
      <select id="year-select" v-model="selectedYear" @change="onYearChange" class="year-select">
        <option :value="null">Alle Jahre</option>
        <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
      </select>
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
    <div v-if="error" class="error-banner">
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <span class="error-message">{{ error }}</span>
      </div>
      <button @click="error = null" class="error-dismiss" aria-label="Fehler schließen">×</button>
    </div>

    <!-- Combined Dashboard (ALL tab) - Simplified Overview -->
    <template v-if="activeCategory === 'ALL'">
      <!-- Quick Overview -->
      <div class="section">
        <h2 class="section-title">Übersicht {{ selectedYear ? selectedYear : '' }}</h2>
        <div v-if="isLoadingTotals" class="loading-container">
          <div class="loading-spinner"></div>
          <span>Lade Statistiken...</span>
        </div>
        <div v-else class="quick-overview-grid">
          <div class="stat-card" v-if="totals.trip_count">
            <span class="value">{{ formatNumber(totals.trip_count) }}</span>
            <span class="label">Total Trips</span>
          </div>
          <div class="stat-card activity-hiking" v-if="totals.hiking && totals.hiking.trip_count > 0">
            <span class="value">{{ formatNumber(totals.hiking.trip_count) }}</span>
            <span class="label">Hiking Trips • {{ formatNumber(totals.hiking.total_km) }} km</span>
          </div>
          <div class="stat-card activity-surfing" v-if="totals.surfing && totals.surfing.trip_count > 0">
            <span class="value">{{ formatNumber(totals.surfing.trip_count) }}</span>
            <span class="label">Surf Trips • {{ formatDurationFromSeconds(totals.surfing.total_time_in_water) }}</span>
          </div>
        </div>
      </div>

      <!-- Recent Highlights -->
      <div class="section" v-if="details.last_hike || details.last_surf || (hikingDetails.top_partners && hikingDetails.top_partners.length > 0)">
        <h2 class="section-title">Highlights</h2>
        <div class="highlights-list">
          <router-link v-if="details.last_hike" :to="`/trip/${details.last_hike.trip_id}`" class="highlight-item">
            <span class="highlight-icon">🥾</span>
            <div class="highlight-content">
              <span class="highlight-label">Letzte Wanderung</span>
              <span class="highlight-value">{{ details.last_hike.name }} • {{ formatDate(details.last_hike.date) }}</span>
            </div>
          </router-link>
          <router-link v-if="details.last_surf" :to="`/trip/${details.last_surf.trip_id}`" class="highlight-item">
            <span class="highlight-icon">🏄‍♂️</span>
            <div class="highlight-content">
              <span class="highlight-label">Letzte Session</span>
              <span class="highlight-value">{{ details.last_surf.name }} • {{ formatDate(details.last_surf.date) }}</span>
            </div>
          </router-link>
          <router-link v-if="hikingDetails.top_partners && hikingDetails.top_partners.length > 0" :to="`/dashboard/${hikingDetails.top_partners[0].id}`" class="highlight-item">
            <span class="highlight-icon">👫</span>
            <div class="highlight-content">
              <span class="highlight-label">Top Partner</span>
              <span class="highlight-value">{{ hikingDetails.top_partners[0].username }} • {{ getTotalTripsForPartner(hikingDetails.top_partners[0]) }} Trips</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Deep Dive Links -->
      <div class="section">
        <div class="deep-dive-links">
          <BaseButton @click="setActiveCategory('HIKING')" variant="secondary" size="large" v-if="totals.hiking && totals.hiking.count > 0">
            🥾 Hiking Details →
          </BaseButton>
          <BaseButton @click="setActiveCategory('SURFING')" variant="secondary" size="large" v-if="totals.surfing && totals.surfing.count > 0">
            🏄‍♂️ Surfing Details →
          </BaseButton>
        </div>
      </div>
    </template>

    <!-- Individual Activity Tabs -->
    <template v-else>
      <!-- Empty state for activities with no data -->
      <div v-if="!isLoadingTotals && ((activeCategory === 'HIKING' && (!totals.hiking || totals.hiking.count === 0)) || (activeCategory === 'SURFING' && (!totals.surfing || totals.surfing.count === 0)))" class="empty-state">
        <div class="empty-state-icon">{{ activeCategory === 'HIKING' ? '🥾' : '🏄‍♂️' }}</div>
        <h2 class="empty-state-title">
          {{ activeCategory === 'HIKING' ? 'Noch keine Wanderungen' : 'Noch keine Surf-Sessions' }}
          {{ selectedYear ? `in ${selectedYear}` : '' }}
        </h2>
        <p class="empty-state-text">
          {{ activeCategory === 'HIKING'
            ? 'Starten Sie Ihre erste Wanderung und verfolgen Sie Ihre Fortschritte mit detaillierten Statistiken und Rekorden.'
            : 'Protokollieren Sie Ihre erste Session und sehen Sie Wellenstatistiken, Wassertemperaturen und Surfboard-Analysen.'
          }}
        </p>
        <BaseButton
          tag="router-link"
          :to="activeCategory === 'HIKING' ? '/trip/new' : '/trip/new?activity_type=SURFING'"
          variant="primary"
          size="large"
        >
          {{ activeCategory === 'HIKING' ? '+ Wanderung hinzufügen' : '+ Session hinzufügen' }}
        </BaseButton>
      </div>

      <!-- Stats section (only show if there's data) -->
      <div v-else class="section">
        <h2 class="section-title">{{ getSectionTitle() }}</h2>
        <div v-if="isLoadingTotals" class="loading-container">
          <div class="loading-spinner"></div>
          <span>Lade Statistiken...</span>
        </div>
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
              <span class="value">{{ formatNumber(totals.surfing.trip_count || 0) }}</span>
              <span class="label">Trips</span>
            </div>
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
      <div v-if="isLoadingDetails" class="loading-container">
        <div class="loading-spinner"></div>
        <span>Lade Rekorde...</span>
      </div>
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
      <div v-if="isLoadingDetails" class="loading-container">
        <div class="loading-spinner"></div>
        <span>Lade Partner...</span>
      </div>
      <div v-else-if="details.top_partners && details.top_partners.length" class="partners-enhanced-list">
        <router-link
          v-for="(partner, index) in details.top_partners"
          :key="partner.id"
          :to="`/dashboard/${partner.id}`"
          class="partner-card-enhanced"
        >
          <div class="partner-card-header">
            <span class="partner-rank">{{ index + 1 }}.</span>
            <span class="partner-name">{{ partner.username }}</span>
            <span class="partner-separator">-</span>
            <span v-if="activeCategory === 'SURFING'" class="partner-count">{{ getTotalTripsForPartner(partner) }} Trips together</span>
            <span v-else class="partner-count">{{ getTotalTripsForPartner(partner) }} Trips together</span>
          </div>
          <div v-if="partner.last_together" class="partner-card-footer">
            <span class="partner-last-together">Last Trip: {{ partner.last_together.trip_name }} - {{ formatDate(partner.last_together.date) }}</span>
          </div>
        </router-link>
      </div>
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
import { selectedYear, setSelectedYear, availableYears, fetchDashboardOverview } from '../store.js';

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
    const year = selectedYear.value;

    if (activeCategory.value === 'ALL') {
      // For ALL tab, use the new overview endpoint
      try {
        const overviewData = await fetchDashboardOverview(userId, year);

        // Map overview data to existing template structure
        totals.value = overviewData.totals;
        username.value = overviewData.user.username;

        // Map records to details format
        details.value = {
          hiking_records: overviewData.records.hiking,
          surfing_records: overviewData.records.surfing,
          last_hike: overviewData.recent_activity.last_hike,
          last_surf: overviewData.recent_activity.last_surf
        };

        // Map partners
        hikingDetails.value = {
          top_partners: overviewData.top_partners
        };
        surfingDetails.value = {
          top_partners: overviewData.top_partners
        };
      } catch (err) {
        console.error('Failed to fetch overview, falling back to old method:', err);
        // Fallback to old method
        const yearParam = year ? `&year=${year}` : '';
        const [totalsResponse, detailsResponse, hikingDetailsResponse, surfingDetailsResponse] = await Promise.all([
          api.get(userId ? `/stats/${userId}?${yearParam}` : `/stats?${yearParam}`),
          api.get(userId ? `/dashboard-data/${userId}?${yearParam}` : `/dashboard-data?${yearParam}`),
          api.get(userId ? `/dashboard-data/${userId}?activity_type=HIKING${yearParam}` : `/dashboard-data?activity_type=HIKING${yearParam}`),
          api.get(userId ? `/dashboard-data/${userId}?activity_type=SURFING${yearParam}` : `/dashboard-data?activity_type=SURFING${yearParam}`)
        ]);

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
      }
    } else {
      // For individual activity tabs, use activity filter
      const queryParams = new URLSearchParams();
      queryParams.append('activity_type', activeCategory.value);
      if (year) {
        queryParams.append('year', year);
      }
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

// Year change handler
const onYearChange = () => {
  setSelectedYear(selectedYear.value);
  fetchData();
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

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('de-CH', { day: '2-digit', month: 'short', year: 'numeric' });
};

const getTotalTripsForPartner = (partner) => {
  if (!partner) return 0;
  const hiking = partner.hiking_count || 0;
  const surfing = partner.surfing_count || 0;
  return hiking + surfing;
};

const getHikingTripCount = () => {
  if (!totals.value || !totals.value.hiking) return 0;
  return totals.value.hiking.trip_count || 0;
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

/* Enhanced Partner Cards */
.partners-enhanced-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.partner-card-enhanced {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-secondary);
  text-decoration: none;
  color: inherit;
  transition: background-color var(--transition-fast), transform var(--transition-fast), box-shadow var(--transition-fast);
  border: 1px solid var(--color-border-light);
}

.partner-card-enhanced:hover {
  background-color: var(--color-bg-tertiary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.partner-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.partner-card-header .partner-rank {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.partner-card-header .partner-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.partner-card-header .partner-separator {
  color: var(--color-text-secondary);
}

.partner-card-header .partner-count {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.partner-card-footer {
  padding-left: calc(var(--text-base) + var(--space-2) * 2);
  margin-top: var(--space-2);
}

.partner-last-together {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  font-style: italic;
}

.export-section {
  text-align: center;
  margin-top: var(--space-10);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-12) var(--space-6);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  margin: var(--space-8) 0;
}

.empty-state-icon {
  font-size: 64px;
  margin-bottom: var(--space-6);
  opacity: 0.6;
}

.empty-state-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.empty-state-text {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  max-width: 500px;
  margin-bottom: var(--space-8);
  line-height: 1.6;
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

/* Quick Overview Grid */
.quick-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-6);
}

/* Highlights List */
.highlights-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.highlight-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: inherit;
  transition: background-color var(--transition-fast), transform var(--transition-fast);
}

.highlight-item:hover {
  background-color: var(--color-bg-tertiary);
  transform: translateX(4px);
}

.highlight-icon {
  font-size: var(--text-2xl);
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.highlight-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  flex: 1;
}

.highlight-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
}

.highlight-value {
  font-size: var(--text-base);
  color: var(--color-text-primary);
}

/* Deep Dive Links */
.deep-dive-links {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
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

/* Year filter styling */
.year-filter {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.year-filter label {
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.year-select {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-size: var(--text-base);
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.year-select:hover {
  border-color: var(--color-primary);
}

.year-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
  .year-filter {
    flex-direction: column;
    align-items: stretch;
    margin: 0 0.5rem var(--space-6) 0.5rem;
  }

  .year-select {
    width: 100%;
  }

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

  .error-banner {
    padding: var(--space-3);
    margin: 0 0.5rem var(--space-4) 0.5rem;
  }

  .error-message {
    font-size: var(--text-xs);
  }

  .loading-container {
    padding: var(--space-4);
  }
}

/* Loading states */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-6);
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4);
  margin-bottom: var(--space-6);
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  color: #991b1b;
  animation: slideDown 0.3s ease-out;
}

.error-content {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
}

.error-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.error-message {
  font-size: var(--text-sm);
  line-height: 1.5;
}

.error-dismiss {
  background: none;
  border: none;
  color: #991b1b;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: background-color 0.2s;
}

.error-dismiss:hover {
  background-color: #fee2e2;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Smooth fade transitions for content updates */
.section {
  animation: fadeIn 0.3s ease-in;
}

.stat-card {
  animation: fadeIn 0.4s ease-in;
}

.quick-overview-grid,
.stats-grid,
.highlights-list,
.partners-enhanced-list {
  animation: fadeIn 0.35s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
