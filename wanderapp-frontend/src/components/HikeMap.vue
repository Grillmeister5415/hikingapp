<template>
  <div class="map-container">
    <div v-if="isLoading">Lade Kartendaten...</div>
    <div id="map" ref="mapContainer" style="height: 400px; width: 100%;"></div>
    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    <div v-if="!trackData && !isLoading && !error" style="margin-top: 10px;">Keine GPX-Daten für diese Etappe verfügbar.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';               // <-- uses baseURL '/api' + Authorization interceptor
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const props = defineProps({ stageId: { type: Number, required: true } });

const mapContainer = ref(null);
const error = ref(null);
const isLoading = ref(true);
const trackData = ref(null);

onMounted(async () => {
  // Mapbox Token (leave as-is if this is your dev token)
  mapboxgl.accessToken = 'pk.eyJ1IjoiZmFiZW1laWVyIiwiYSI6ImNtZjJ0azQ2OTJrYXAyanNkMTUzZmg2aDUifQ.2ozmDlUR0cn8v4g5wJicQw';
  if (!mapboxgl.accessToken.includes('pk.')) {
    error.value = "Bitte füge deinen Mapbox Access Token ein!";
    isLoading.value = false;
    return;
  }

  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error("Nicht authentifiziert. Bitte Token setzen.");
    }

    // API-Anfrage über den Proxy (/api) – kein hartkodiertes Backend mehr
    const response = await api.get(`/stages/${props.stageId}/`);
    trackData.value = response.data.track;

    // Karte initialisieren
    const map = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/fabemeier/cmfuxo187000901s840s6d4ev',
      center: [8.2275, 46.8182], // Standardzentrum
      zoom: 7
    });

    // Add navigation controls for better touch interaction
    map.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'top-right');

    map.on('load', () => {
      if (trackData.value && trackData.value.coordinates.length > 0) {
        // Die Route zur Karte hinzufügen
        map.addSource('route', {
          'type': 'geojson',
          'data': { 'type': 'Feature', 'properties': {}, 'geometry': trackData.value }
        });
        map.addLayer({
          'id': 'route',
          'type': 'line',
          'source': 'route',
          'layout': { 'line-join': 'round', 'line-cap': 'round' },
          'paint': { 'line-color': '#e3342f', 'line-width': 4 }
        });

        // Automatisch an den Track heranzoomen
        const bounds = trackData.value.coordinates.reduce(
          (b, coord) => b.extend(coord),
          new mapboxgl.LngLatBounds(trackData.value.coordinates[0], trackData.value.coordinates[0])
        );
        map.fitBounds(bounds, { padding: 40 });
      }
    });
  } catch (err) {
    error.value = "Fehler beim Laden der Etappen-Daten: " + (err.response?.data?.detail || err.message);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
  .map-container { border: 1px solid #ccc; padding: 1rem; margin-top: 1rem; }

  /* Increase map control sizes for better touch interaction on mobile */
  @media (max-width: 768px) {
    :deep(.mapboxgl-ctrl-group) button {
      width: 44px !important;
      height: 44px !important;
      font-size: 18px;
    }

    :deep(.mapboxgl-ctrl-icon) {
      transform: scale(1.3);
    }
  }
</style>