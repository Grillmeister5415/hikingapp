<template>
  <div>
    <router-link :to="`/trip/${tripId}`">&larr; Abbrechen und zurück zum Trip</router-link>
    <h1>Neue Etappe hinzufügen</h1>
    <form @submit.prevent="handleSubmit" class="stage-form">
      <div class="form-group">
        <label for="name">Etappen-Name</label>
        <input type="text" id="name" v-model="name" required />
      </div>
      <div class="form-group">
        <label for="date">Datum</label>
        <input type="date" id="date" v-model="date" required :min="tripStartDate" :max="tripEndDate" />
      </div>
      <div class="form-group">
        <label for="description">Beschreibung (optional)</label>
        <textarea id="description" v-model="description"></textarea>
      </div>
      <div class="form-group">
        <label for="external_link">Link (optional)</label>
        <input type="url" id="external_link" v-model="external_link" placeholder="https://tourenportal.com/..." />
      </div>

      <hr>

      <div class="form-group">
        <label for="gpxFile">GPX-Datei (füllt Dauer, Distanz & Höhenmeter automatisch)</label>
        <input type="file" id="gpxFile" @change="handleFileUpload" accept=".gpx" />
        <div v-if="parsingStatus" class="parsing-status">{{ parsingStatus }}</div>
      </div>

      <!-- GPX Preview Section -->
      <div v-if="calculatedMetrics" class="gpx-preview">
        <h4>📊 Aus GPX berechnet:</h4>
        <div class="preview-stats">
          <div class="preview-stat">
            <span class="value">{{ calculatedMetrics.length }} <small>km</small></span>
            <label>Distanz</label>
          </div>
          <div class="preview-stat">
            <span class="value">{{ calculatedMetrics.elevationGain }} <small>m</small></span>
            <label>Aufstieg</label>
          </div>
          <div class="preview-stat">
            <span class="value">{{ calculatedMetrics.elevationLoss }} <small>m</small></span>
            <label>Abstieg</label>
          </div>
          <div class="preview-stat" v-if="calculatedMetrics.durationFormatted">
            <span class="value">{{ calculatedMetrics.durationFormatted }}</span>
            <label>Dauer</label>
          </div>
        </div>
        <p class="preview-note">
          <small>💡 Diese Werte werden automatisch gespeichert. Manuelle Eingaben überschreiben diese Berechnungen.</small>
        </p>
      </div>
      
      <div class="manual-fields">
        <p>Manuelle Eingabe:</p>
        <div class="form-group">
          <label for="duration">Wanderdauer (HH:MM)</label>
          <input 
            type="text" 
            id="duration" 
            v-model="manual_duration" 
            placeholder="z.B. 04:30 oder 50:00" 
            pattern="[0-9]+:[0-5][0-9]"
            title="Bitte im Format Stunden:Minuten eingeben, z.B. 04:30."
          />
          <small>Dieses Feld überschreibt die Dauer aus der GPX-Datei, falls vorhanden.</small>
        </div>
        <div class="form-group">
          <label for="length">Distanz (km)</label>
          <input type="number" step="0.1" id="length" v-model="manual_length_km" />
        </div>
        <div class="form-group">
          <label for="elevation_gain">Höhenmeter (Aufstieg)</label>
          <input type="number" id="elevation_gain" v-model="manual_elevation_gain" />
        </div>
        <div class="form-group">
          <label for="elevation_loss">Höhenmeter (Abstieg)</label>
          <input type="number" id="elevation_loss" v-model="manual_elevation_loss" />
        </div>
      </div>
      
      <button type="submit" :disabled="isSubmitting">Etappe speichern</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import gpxParser from 'gpxparser';
import api from '../api';

// Props for activity type (can be passed from router)
const props = defineProps({
  activityType: {
    type: String,
    default: 'HIKING'
  }
});

const route = useRoute();
const router = useRouter();
const tripId = ref(route.params.tripId);

const name = ref('');
const date = ref('');
const description = ref('');
const external_link = ref('');
const manual_duration = ref('');
const manual_length_km = ref(null);
const manual_elevation_gain = ref(null);
const manual_elevation_loss = ref(null);
const parsedTrack = ref(null);
const parsingStatus = ref('');
const error = ref(null);
const isSubmitting = ref(false);

// Calculated values from GPX
const calculatedMetrics = ref(null);

const tripStartDate = ref('');
const tripEndDate = ref('');

onMounted(async () => {
  try {
    const response = await api.get(`/trips/${tripId.value}/`);
    tripStartDate.value = response.data.start_date;
    tripEndDate.value = response.data.end_date;
  } catch (err) {
    error.value = "Konnte Trip-Daten für den Datumsbereich nicht laden.";
  }
});

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) {
    parsedTrack.value = null;
    parsingStatus.value = '';
    calculatedMetrics.value = null;
    return;
  }
  parsingStatus.value = 'Lese Datei...';
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const gpx = new gpxParser();
      gpx.parse(e.target.result);
      if (gpx.tracks.length === 0 || gpx.tracks[0].points.length === 0) {
        throw new Error("GPX-Datei enthält keine Track-Punkte.");
      }

      parsedTrack.value = gpx.tracks[0].points.map(p => ({
        lat: p.lat, lon: p.lon, ele: p.ele, time: p.time ? p.time.toISOString() : null
      }));

      parsingStatus.value = `📊 Berechne Metriken...`;

      // Use backend API for accurate calculations
      try {
        const response = await api.post('/calculate-gpx/', {
          track_points: parsedTrack.value
        });
        calculatedMetrics.value = response.data;
        parsingStatus.value = `✅ ${parsedTrack.value.length} Punkte geparst und berechnet.`;
      } catch (calcError) {
        console.error('Calculation error:', calcError);
        parsingStatus.value = `✅ ${parsedTrack.value.length} Punkte geparst. (Berechnung fehlgeschlagen)`;
        calculatedMetrics.value = null;
      }
    } catch (err) {
      parsingStatus.value = `❌ Fehler: ${err.message}`;
      parsedTrack.value = null;
      calculatedMetrics.value = null;
    }
  };
  reader.readAsText(file);
};

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    let durationToSend = manual_duration.value || null;
    if (durationToSend && durationToSend.match(/^[0-9]+:[0-5][0-9]$/)) {
      durationToSend += ':00';
    }

    const payload = {
      name: name.value,
      date: date.value,
      description: description.value,
      trip: parseInt(tripId.value),
      activity_type: props.activityType, // Use the activity type from props
      track_points: parsedTrack.value || [],
      manual_duration: durationToSend,
      manual_length_km: manual_length_km.value || null,
      manual_elevation_gain: manual_elevation_gain.value || null,
      manual_elevation_loss: manual_elevation_loss.value || null,
      external_link: external_link.value
    };
    await api.post('/stages/', payload);
    router.push(`/trip/${tripId.value}`);
  } catch (err) {
    if (err.response && err.response.data) {
      const errorData = err.response.data;
      const firstErrorKey = Object.keys(errorData)[0];
      error.value = `${firstErrorKey}: ${errorData[firstErrorKey][0]}`;
    } else {
      error.value = 'Ein unerwarteter Fehler ist aufgetreten.';
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.stage-form { display: flex; flex-direction: column; gap: 1rem; max-width: 500px; margin: 2rem auto; }
.form-group { display: flex; flex-direction: column; }
.form-group small { font-size: 0.8rem; color: #6c757d; margin-top: 0.25rem; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, textarea { padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
button { padding: 1rem; background-color: #42b983; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
button:disabled { background-color: #ccc; cursor: not-allowed; }
.manual-fields { border: 1px solid #ddd; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
.error { color: red; }
.parsing-status { margin-top: 0.5rem; font-style: italic; }

/* GPX Preview Styles */
.gpx-preview {
  border: 2px solid #42b983;
  background-color: rgba(66, 185, 131, 0.05);
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}
.gpx-preview h4 {
  margin: 0 0 0.5rem 0;
  color: #42b983;
  font-size: 1rem;
}
.preview-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
}
.preview-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}
.preview-stat .value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2c3e50;
}
.preview-stat label {
  font-size: 0.8rem;
  color: #6c757d;
  margin: 0;
  text-align: center;
}
.preview-note {
  margin: 0;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(66, 185, 131, 0.3);
}
.preview-note small {
  color: #6c757d;
}
</style>