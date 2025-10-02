<template>
  <div class="map-container">
    <div v-if="isLoading">Lade Kartendaten...</div>
    <div id="map" ref="mapContainer" style="height: 400px; width: 100%;"></div>
    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    <div v-if="!trackData && !isLoading && !error" style="margin-top: 10px;">Keine GPX-Daten für diese Etappe verfügbar.</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/api';               // <-- uses baseURL '/api' + Authorization interceptor
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const props = defineProps({
  stageId: { type: Number, required: true },
  highlightedPosition: { type: Object, default: null } // { index, coordinates }
});

const mapContainer = ref(null);
const error = ref(null);
const isLoading = ref(true);
const trackData = ref(null);
const map = ref(null);
const positionMarker = ref(null);

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
    map.value = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/fabemeier/cmfuxo187000901s840s6d4ev',
      center: [8.2275, 46.8182], // Standardzentrum
      zoom: 7
    });

    // Add navigation controls for better touch interaction
    map.value.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'top-right');

    map.value.on('load', () => {
      if (trackData.value && trackData.value.coordinates.length > 0) {
        // Die Route zur Karte hinzufügen
        map.value.addSource('route', {
          'type': 'geojson',
          'data': { 'type': 'Feature', 'properties': {}, 'geometry': trackData.value }
        });
        map.value.addLayer({
          'id': 'route',
          'type': 'line',
          'source': 'route',
          'layout': { 'line-join': 'round', 'line-cap': 'butt' },
          'paint': {
            'line-color': '#D32F2F',
            'line-width': 4
          }
        });

        // Automatisch an den Track heranzoomen
        const bounds = trackData.value.coordinates.reduce(
          (b, coord) => b.extend(coord),
          new mapboxgl.LngLatBounds(trackData.value.coordinates[0], trackData.value.coordinates[0])
        );
        map.value.fitBounds(bounds, { padding: 40 });

        // Add Start marker
        const startCoord = trackData.value.coordinates[0];
        const startEl = document.createElement('div');
        startEl.className = 'start-marker';
        const startInner = document.createElement('div');
        startInner.className = 'start-marker-inner';
        startEl.appendChild(startInner);
        new mapboxgl.Marker({ element: startEl, anchor: 'center' })
          .setLngLat(startCoord)
          .addTo(map.value);

        // Add End marker
        const coords = trackData.value.coordinates;
        const endCoord = coords[coords.length - 1];
        const endEl = document.createElement('div');
        endEl.className = 'end-marker';
        const endInner = document.createElement('div');
        endInner.className = 'end-marker-inner';
        endEl.appendChild(endInner);
        new mapboxgl.Marker({ element: endEl, anchor: 'center' })
          .setLngLat(endCoord)
          .addTo(map.value);

        // Create position marker (initially hidden)
        const el = document.createElement('div');
        el.className = 'position-marker';
        positionMarker.value = new mapboxgl.Marker({ element: el, anchor: 'center' })
          .setLngLat([0, 0]);
      }
    });
  } catch (err) {
    error.value = "Fehler beim Laden der Etappen-Daten: " + (err.response?.data?.detail || err.message);
  } finally {
    isLoading.value = false;
  }
});

// Watch for changes in highlighted position
watch(() => props.highlightedPosition, (newPos) => {
  if (!map.value || !positionMarker.value) return;

  if (newPos && newPos.coordinates) {
    // Update marker position and show it
    const [lon, lat] = newPos.coordinates;
    positionMarker.value.setLngLat([lon, lat]).addTo(map.value);
  } else {
    // Hide marker
    positionMarker.value.remove();
  }
});
</script>

<style scoped>
  .map-container { border: 1px solid #ccc; padding: 1rem; margin-top: 1rem; }

  /* Position marker styling - Elevation profile interaction */
  :deep(.position-marker) {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: #D32F2F;
    border: 3px solid white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    cursor: pointer;
  }

  /* Start marker styling - Swisstopo style */
  :deep(.start-marker) {
    width: 20px;
    height: 20px;
    background-color: #D32F2F;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    cursor: pointer;
  }

  :deep(.start-marker-inner) {
    width: 8px;
    height: 8px;
    background-color: white;
    border-radius: 50%;
  }

  /* End marker styling - Swisstopo style (identical to start) */
  :deep(.end-marker) {
    width: 20px;
    height: 20px;
    background-color: #D32F2F;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    cursor: pointer;
  }

  :deep(.end-marker-inner) {
    width: 8px;
    height: 8px;
    background-color: white;
    border-radius: 50%;
  }

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