<template>
  <div>
    <div v-if="isLoading">Lade Etappen-Daten...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="stage">
      <router-link :to="`/trip/${stage.trip}`">&larr; Abbrechen und zurück zum Trip</router-link>
      <h1>Etappe bearbeiten</h1>
      <form @submit.prevent="handleSubmit" class="stage-form">
        <div class="form-group">
          <label for="name">Etappen-Name</label>
          <input type="text" id="name" v-model="stage.name" required />
        </div>
        <div class="form-group">
          <label for="date">Datum</label>
          <input type="date" id="date" v-model="stage.date" required :min="tripStartDate" :max="tripEndDate" />
        </div>
        <div class="form-group">
          <label for="description">Beschreibung (optional)</label>
          <textarea id="description" v-model="stage.description"></textarea>
        </div>
        <div class="form-group">
          <label for="external_link">Link (optional)</label>
          <input type="url" id="external_link" v-model="stage.external_link" placeholder="https://tourenportal.com/..." />
        </div>

        <hr>

        <!-- Hiking/Running specific fields -->
        <div v-if="stage.activity_type !== 'SURFING'">
          <div class="form-group">
            <label for="gpxFile">Neue GPX-Datei hochladen (überschreibt existierenden Track)</label>
            <input type="file" id="gpxFile" @change="handleFileUpload" accept=".gpx" />
            <div v-if="parsingStatus" class="parsing-status">{{ parsingStatus }}</div>
          </div>
          
          <div class="manual-fields">
            <p>Manuelle Eingabe:</p>
            <div class="form-group">
              <label for="duration">{{ getDurationLabel() }}</label>
              <input 
                type="text" 
                id="duration" 
                v-model="stage.manual_duration" 
                placeholder="z.B. 04:30" 
                pattern="[0-9]+:[0-5][0-9]"
                title="Bitte im Format Stunden:Minuten eingeben."
              />
              <small>Dieses Feld überschreibt die Dauer aus der GPX-Datei, falls vorhanden.</small>
            </div>
            <div class="form-group">
              <label for="length">Distanz (km)</label>
              <input type="number" step="0.1" id="length" v-model="stage.manual_length_km" />
            </div>
            <div class="form-group">
              <label for="elevation">Höhenmeter (Aufstieg)</label>
              <input type="number" id="elevation" v-model="stage.manual_elevation_gain" />
            </div>
          </div>
        </div>

        <!-- Surfing specific fields -->
        <div v-if="stage.activity_type === 'SURFING'" class="surf-fields">
          <div class="form-group">
            <label for="time_in_water">Zeit im Wasser (HH:MM)</label>
            <input 
              type="text" 
              id="time_in_water" 
              v-model="stage.time_in_water" 
              placeholder="z.B. 02:30" 
              pattern="[0-9]+:[0-5][0-9]"
              title="Bitte im Format Stunden:Minuten eingeben."
            />
          </div>
          
          <div class="form-group">
            <label for="surf_spot">Surf Spot</label>
            <input type="text" id="surf_spot" v-model="stage.surf_spot" placeholder="z.B. Pipeline, Ericeira" />
          </div>
          
          <div class="form-group-row">
            <div class="form-group">
              <label for="wave_height">Wellenhöhe (m)</label>
              <input type="number" step="0.1" id="wave_height" v-model="stage.wave_height" placeholder="z.B. 1.5" />
            </div>
            <div class="form-group">
              <label for="wave_quality">Wellenqualität (1-5 Sterne)</label>
              <select id="wave_quality" v-model="stage.wave_quality">
                <option value="">Nicht bewertet</option>
                <option value="1">⭐ (1 Stern)</option>
                <option value="2">⭐⭐ (2 Sterne)</option>
                <option value="3">⭐⭐⭐ (3 Sterne)</option>
                <option value="4">⭐⭐⭐⭐ (4 Sterne)</option>
                <option value="5">⭐⭐⭐⭐⭐ (5 Sterne)</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="surfboard_used">Verwendetes Surfbrett</label>
            <input type="text" id="surfboard_used" v-model="stage.surfboard_used" placeholder="z.B. 6'2 Shortboard" />
          </div>

          <div class="form-group-row">
            <div class="form-group">
              <label for="waves_caught">Gefangene Wellen</label>
              <input type="number" id="waves_caught" v-model="stage.waves_caught" placeholder="z.B. 15" />
            </div>
            <div class="form-group">
              <label for="water_temperature">Wassertemperatur (°C)</label>
              <input type="number" id="water_temperature" v-model="stage.water_temperature" placeholder="z.B. 18" />
            </div>
          </div>

          <div class="form-group-row">
            <div class="form-group">
              <label for="tide_stage">Gezeitenstadium</label>
              <select id="tide_stage" v-model="stage.tide_stage">
                <option value="">Nicht angegeben</option>
                <option value="LOW">Niedrigwasser</option>
                <option value="MID">Mittleres Wasser</option>
                <option value="HIGH">Hochwasser</option>
              </select>
            </div>
            <div class="form-group">
              <label for="tide_movement">Gezeitenbewegung</label>
              <select id="tide_movement" v-model="stage.tide_movement">
                <option value="">Nicht angegeben</option>
                <option value="RISING">Steigend</option>
                <option value="FALLING">Fallend</option>
              </select>
            </div>
          </div>
        </div>
        
        <button type="submit" :disabled="isSubmitting">Änderungen speichern</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import gpxParser from 'gpxparser';
import api from '../api';

const route = useRoute();
const router = useRouter();
const stageId = ref(route.params.id);

const stage = ref(null);
const isLoading = ref(true);
const error = ref(null);
const isSubmitting = ref(false);

const parsedTrack = ref(null);
const parsingStatus = ref('');

const tripStartDate = ref('');
const tripEndDate = ref('');

onMounted(async () => {
  try {
    const response = await api.get(`/stages/${stageId.value}/`);
    stage.value = response.data;

    // Convert 'HH:MM:SS' to 'HH:MM' for display
    if (stage.value.manual_duration && stage.value.manual_duration.length > 5) {
      stage.value.manual_duration = stage.value.manual_duration.substring(0, 5);
    }
    
    // Convert surf time_in_water from 'HH:MM:SS' to 'HH:MM' for display
    if (stage.value.time_in_water && stage.value.time_in_water.length > 5) {
      stage.value.time_in_water = stage.value.time_in_water.substring(0, 5);
    }

    // Fetch parent trip data to constrain the date picker
    const tripResponse = await api.get(`/trips/${stage.value.trip}/`);
    tripStartDate.value = tripResponse.data.start_date;
    tripEndDate.value = tripResponse.data.end_date;

  } catch (err) {
    error.value = "Fehler beim Laden der Etappe: " + err.message;
  } finally {
    isLoading.value = false;
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

const getDurationLabel = () => {
  if (!stage.value) return 'Dauer (HH:MM)';
  switch (stage.value.activity_type) {
    case 'HIKING':
      return 'Wanderdauer (HH:MM)';
    case 'RUNNING':
      return 'Laufdauer (HH:MM)';
    case 'SURFING':
      return 'Zeit im Wasser (HH:MM)';
    default:
      return 'Dauer (HH:MM)';
  }
};

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    const payload = {
      name: stage.value.name,
      date: stage.value.date,
      description: stage.value.description,
      external_link: stage.value.external_link,
    };

    // Activity-specific fields
    if (stage.value.activity_type === 'SURFING') {
      // Surf-specific fields
      let timeInWaterToSend = stage.value.time_in_water || null;
      if (timeInWaterToSend && timeInWaterToSend.match(/^[0-9]+:[0-5][0-9]$/)) {
        timeInWaterToSend += ':00';
      }
      
      payload.time_in_water = timeInWaterToSend;
      payload.surf_spot = stage.value.surf_spot || null;
      payload.wave_height = stage.value.wave_height || null;
      payload.wave_quality = stage.value.wave_quality || null;
      payload.surfboard_used = stage.value.surfboard_used || null;
      payload.waves_caught = stage.value.waves_caught || null;
      payload.water_temperature = stage.value.water_temperature || null;
      payload.tide_stage = stage.value.tide_stage || null;
      payload.tide_movement = stage.value.tide_movement || null;
    } else {
      // Hiking/Running fields
      let durationToSend = stage.value.manual_duration || null;
      if (durationToSend && durationToSend.match(/^[0-9]+:[0-5][0-9]$/)) {
        durationToSend += ':00';
      }
      
      payload.manual_duration = durationToSend;
      payload.manual_length_km = stage.value.manual_length_km || null;
      payload.manual_elevation_gain = stage.value.manual_elevation_gain || null;
      
      if (parsedTrack.value) {
        payload.track_points = parsedTrack.value;
      }
    }

    await api.patch(`/stages/${stageId.value}/`, payload);
    router.push(`/trip/${stage.value.trip}`);

  } catch (err) {
    error.value = 'Fehler beim Speichern der Änderungen: ' + (JSON.stringify(err.response?.data) || err.message);
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
.surf-fields { border: 1px solid #20b2aa; padding: 1rem; border-radius: 8px; margin-top: 1rem; background-color: rgba(32, 178, 170, 0.05); }
.form-group-row { display: flex; gap: 1rem; }
.form-group-row .form-group { flex: 1; }
select { padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; background: white; }
.error { color: red; }
.parsing-status { margin-top: 0.5rem; font-style: italic; }
</style>