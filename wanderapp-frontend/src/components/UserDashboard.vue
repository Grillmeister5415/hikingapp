<template>
  <div>
    <div class="header">
      <h1>Dashboard von {{ username }}</h1>
      <router-link to="/" class="btn-back">Zurück zur Trip-Liste</router-link>
    </div>

    <div class="section">
      <h2 class="section-title">Total</h2>
      <div v-if="isLoadingTotals">Lade Statistiken...</div>
      <div v-else class="stats-grid">
        <div class="stat-card">
          <span class="value">{{ formatNumber(totals.trip_count) }}</span>
          <span class="label">Trips</span>
        </div>
        <div class="stat-card">
          <span class="value">{{ formatNumber(totals.stage_count) }}</span>
          <span class="label">Etappen</span>
        </div>
        <div class="stat-card">
          <span class="value">{{ formatNumber(totals.total_km) }} <small>km</small></span>
          <span class="label">Gesamtdistanz</span>
        </div>
        <div class="stat-card">
          <span class="value">{{ formatNumber(totals.total_elevation) }} <small>m</small></span>
          <span class="label">Gesamter Aufstieg</span>
        </div>
        <div class="stat-card">
          <span class="value">{{ formatNumber(totals.total_loss) }} <small>m</small></span>
          <span class="label">Gesamter Abstieg</span>
        </div>
      </div>
    </div>

    <div class="section">
      <h2 class="section-title">Persönliche Rekorde</h2>
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
    
    <div class="section">
      <h2 class="section-title">Top Wanderpartner</h2>
      <div v-if="isLoadingDetails">Lade Partner...</div>
      <ol v-else-if="details.top_partners && details.top_partners.length" class="partners-list">
        <li v-for="(partner, index) in details.top_partners" :key="partner.id">
          <router-link :to="`/dashboard/${partner.id}`" class="partner-link">
            <span class="partner-rank">{{ index + 1 }}.</span>
            <span class="partner-name">{{ partner.username }}</span>
            <span class="partner-count">{{ partner.hike_count }} gemeinsame Trips</span>
          </router-link>
        </li>
      </ol>
      <p v-else><em>Sie waren bisher alleine unterwegs.</em></p>
    </div>

    <div class="export-section">
      <button @click="downloadCSV" :disabled="isDownloading">
        {{ isDownloading ? 'Exportiere...' : 'Alle Trips als CSV exportieren' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';

const route = useRoute();
const totals = ref({});
const details = ref({});
const isLoadingTotals = ref(true);
const isLoadingDetails = ref(true);
const error = ref(null);
const username = ref('Dir');
const isDownloading = ref(false);

const fetchData = async () => {
  try {
    isLoadingTotals.value = true;
    isLoadingDetails.value = true;
    error.value = null;
    const userId = route.params.id;
    const [totalsResponse, detailsResponse] = await Promise.all([
      api.get(userId ? `/stats/${userId}/` : '/stats/'),
      api.get(userId ? `/dashboard-data/${userId}/` : '/dashboard-data/')
    ]);
    totals.value = totalsResponse.data;
    details.value = detailsResponse.data;
    username.value = totalsResponse.data.username;
  } catch (err) {
    error.value = "Fehler beim Laden der Dashboard-Daten: " + err.message;
  } finally {
    isLoadingTotals.value = false;
    isLoadingDetails.value = false;
  }
};
onMounted(fetchData);
watch(() => route.params.id, fetchData);

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString('de-CH');
};

const formatDuration = (durationString) => {
  if (!durationString) return '0h 0m';
  
  let totalSeconds = 0;
  if (typeof durationString === 'string') {
    if (durationString.includes('day')) {
      const dayMatch = durationString.match(/(\d+)\s*day/);
      const days = dayMatch ? parseInt(dayMatch[1], 10) : 0;
      totalSeconds += days * 86400;
      const timeMatch = durationString.match(/(\d{1,2}):(\d{2}):(\d{2})/);
      if (timeMatch) {
        totalSeconds += parseInt(timeMatch[1], 10) * 3600;
        totalSeconds += parseInt(timeMatch[2], 10) * 60;
        totalSeconds += parseInt(timeMatch[3], 10);
      }
    } else {
      const timeParts = durationString.split(':');
      if (timeParts.length >= 2) {
        totalSeconds += parseInt(timeParts[0], 10) * 3600;
        totalSeconds += parseInt(timeParts[1], 10) * 60;
        if (timeParts.length === 3) {
          totalSeconds += parseInt(timeParts[2], 10);
        }
      }
    }
  }
  if (isNaN(totalSeconds)) return '0h 0m';
  const totalHours = Math.floor(totalSeconds / 3600);
  const remainingMinutes = Math.round((totalSeconds % 3600) / 60);
  return `${totalHours}h ${remainingMinutes}m`;
};

const downloadCSV = async () => {
  isDownloading.value = true;
  try {
    const response = await api.get('/trips/');
    const trips = response.data;
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Trip Name,Etappen-Name,Datum,Distanz (km),Aufstieg (m),Abstieg (m),Dauer,Teilnehmer\r\n";
    trips.forEach(trip => {
      if (trip.stages.length) {
        trip.stages.forEach(stage => {
          const distance = stage.calculated_length_km || stage.manual_length_km || 0;
          const gain = stage.calculated_elevation_gain || stage.manual_elevation_gain || 0;
          const loss = stage.calculated_elevation_loss || 0;
          const duration = stage.calculated_duration || stage.manual_duration || '00:00:00';
          const participants = trip.participants.map(p => p.username).join('; ');
          let row = [`"${trip.name}"`, `"${stage.name}"`, stage.date, distance, gain, loss, duration, `"${participants}"`].join(',');
          csvContent += row + "\r\n";
        });
      }
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "wanderungen_detail_export.csv");
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
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.btn-back { display: inline-block; padding: 0.8rem 1.5rem; background-color: #6c757d; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }
.section { margin-bottom: 2.5rem; }
.section-title { margin-bottom: 1.5rem; font-size: 1.5rem; color: #343a40; border-bottom: 1px solid #dee2e6; padding-bottom: 0.5rem; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
}
.record-link {
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.record-link:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}
.value { font-size: 2.2rem; font-weight: 500; color: #212529; }
.value small { font-size: 1.2rem; font-weight: 400; color: #6c757d; }
.label { font-size: 0.9rem; color: #6c757d; margin-top: 0.25rem; }
.context { font-size: 1rem; color: #495057; margin-top: 1rem; font-style: italic; border-top: 1px solid #e9ecef; padding-top: 1rem; }
.partners-list { list-style: none; padding: 0; }
.partner-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  background-color: #f8f9fa;
  margin-bottom: 0.5rem;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.2s ease;
}
.partner-link:hover { background-color: #e9ecef; }
.partner-rank { font-weight: bold; color: #6c757d; margin-right: 1rem; }
.partner-name { font-weight: 500; flex-grow: 1; }
.partner-count { color: #6c757d; }
.export-section { text-align: center; margin-top: 2.5rem; }
.export-section button { font-size: 1rem; padding: 1rem 1.5rem; cursor: pointer; background-color: #0d6efd; color: white; border: none; border-radius: 8px; }
.export-section button:disabled { background-color: #ccc; }
.error { color: red; }
</style>