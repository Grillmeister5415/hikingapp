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
          <label for="elevation">Höhenmeter (Aufstieg)</label>
          <input type="number" id="elevation" v-model="manual_elevation_gain" />
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
const parsedTrack = ref(null);
const parsingStatus = ref('');
const error = ref(null);
const isSubmitting = ref(false);

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

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (!file) { parsedTrack.value = null; parsingStatus.value = ''; return; }
  parsingStatus.value = 'Lese Datei...';
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const gpx = new gpxParser();
      gpx.parse(e.target.result);
      if (gpx.tracks.length === 0 || gpx.tracks[0].points.length === 0) { throw new Error("GPX-Datei enthält keine Track-Punkte."); }
      parsedTrack.value = gpx.tracks[0].points.map(p => ({
        lat: p.lat, lon: p.lon, ele: p.ele, time: p.time ? p.time.toISOString() : null
      }));
      parsingStatus.value = `✅ ${parsedTrack.value.length} Punkte erfolgreich geparst.`;
    } catch (err) {
      parsingStatus.value = `❌ Fehler: ${err.message}`;
      parsedTrack.value = null;
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
</style>