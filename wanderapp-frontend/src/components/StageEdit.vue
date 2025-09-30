<template>
  <div>
    <div v-if="isLoading">Lade Etappen-Daten...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="stage">
      <BaseButton tag="router-link" :to="`/trip/${stage.trip}`" variant="ghost" size="small">
        &larr; Abbrechen und zurück zum Trip
      </BaseButton>
      <h1>Etappe bearbeiten</h1>
      <form @submit.prevent="handleSubmit" class="stage-form">
        <BaseInput
          id="name"
          type="text"
          v-model="stage.name"
          label="Etappen-Name"
          required
        />

        <BaseInput
          id="date"
          type="date"
          v-model="stage.date"
          label="Datum"
          required
          :min="tripStartDate"
          :max="tripEndDate"
        />

        <BaseInput
          id="description"
          type="textarea"
          v-model="stage.description"
          label="Beschreibung (optional)"
        />

        <BaseInput
          id="external_link"
          type="url"
          v-model="stage.external_link"
          label="Link (optional)"
          placeholder="https://tourenportal.com/..."
        />

        <hr>

        <!-- Hiking/Running specific fields -->
        <div v-if="stage.activity_type !== 'SURFING'">
          <div class="form-group">
            <label for="gpxFile">Neue GPX-Datei hochladen (überschreibt existierenden Track)</label>
            <input type="file" id="gpxFile" @change="handleFileUpload" accept=".gpx" />
            <div v-if="parsingStatus" class="parsing-status">{{ parsingStatus }}</div>
          </div>

          <!-- GPX Preview Section -->
          <div v-if="calculatedMetrics" class="gpx-preview">
            <h4>📊 Aus neuer GPX berechnet:</h4>
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
              <small>💡 Diese Werte werden beim Speichern übernommen. Manuelle Eingaben überschreiben diese Berechnungen.</small>
            </p>
          </div>

          <!-- Show existing calculated values if available -->
          <div v-if="stage.calculated_length_km || stage.calculated_elevation_gain || stage.calculated_elevation_loss" class="existing-gpx-data">
            <h4>📊 Aktuelle GPX-Berechnungen:</h4>
            <div class="preview-stats">
              <div class="preview-stat" v-if="stage.calculated_length_km">
                <span class="value">{{ stage.calculated_length_km }} <small>km</small></span>
                <label>Distanz</label>
              </div>
              <div class="preview-stat" v-if="stage.calculated_elevation_gain">
                <span class="value">{{ stage.calculated_elevation_gain }} <small>m</small></span>
                <label>Aufstieg</label>
              </div>
              <div class="preview-stat" v-if="stage.calculated_elevation_loss">
                <span class="value">{{ stage.calculated_elevation_loss }} <small>m</small></span>
                <label>Abstieg</label>
              </div>
              <div class="preview-stat" v-if="stage.calculated_duration">
                <span class="value">{{ formatDurationForDisplay(stage.calculated_duration) }}</span>
                <label>Dauer</label>
              </div>
            </div>
            <p class="preview-note">
              <small>💡 Diese Werte stammen aus der aktuellen GPX-Datei. Neue GPX-Datei hochladen, um sie zu ersetzen.</small>
            </p>
          </div>

          <div class="manual-fields">
            <p>Manuelle Eingabe:</p>
            <BaseInput
              id="duration"
              type="text"
              v-model="stage.manual_duration"
              :label="getDurationLabel()"
              placeholder="z.B. 04:30"
              pattern="[0-9]+:[0-5][0-9]"
              helper-text="Dieses Feld überschreibt die Dauer aus der GPX-Datei, falls vorhanden."
            />
            <BaseInput
              id="length"
              type="number"
              step="0.1"
              v-model="stage.manual_length_km"
              label="Distanz (km)"
            />
            <BaseInput
              id="elevation_gain"
              type="number"
              v-model="stage.manual_elevation_gain"
              label="Höhenmeter (Aufstieg)"
            />
            <BaseInput
              id="elevation_loss"
              type="number"
              v-model="stage.manual_elevation_loss"
              label="Höhenmeter (Abstieg)"
            />
          </div>
        </div>

        <!-- Surfing specific fields -->
        <div v-if="stage.activity_type === 'SURFING'" class="surf-fields">
          <BaseInput
            id="time_in_water"
            type="text"
            v-model="stage.time_in_water"
            label="Zeit im Wasser (HH:MM)"
            placeholder="z.B. 02:30"
            pattern="[0-9]+:[0-5][0-9]"
          />

          <BaseInput
            id="surf_spot"
            type="text"
            v-model="stage.surf_spot"
            label="Surf Spot"
            placeholder="z.B. Pipeline, Ericeira"
          />

          <div class="form-group-row">
            <BaseInput
              id="wave_height"
              type="number"
              step="0.1"
              v-model="stage.wave_height"
              label="Wellenhöhe (m)"
              placeholder="z.B. 1.5"
            />
            <BaseInput
              id="wave_quality"
              type="select"
              v-model="stage.wave_quality"
              label="Wellenqualität (1-5 Sterne)"
            >
              <option value="">Nicht bewertet</option>
              <option value="1">⭐ (1 Stern)</option>
              <option value="2">⭐⭐ (2 Sterne)</option>
              <option value="3">⭐⭐⭐ (3 Sterne)</option>
              <option value="4">⭐⭐⭐⭐ (4 Sterne)</option>
              <option value="5">⭐⭐⭐⭐⭐ (5 Sterne)</option>
            </BaseInput>
          </div>

          <BaseInput
            id="surfboard_used"
            type="text"
            v-model="stage.surfboard_used"
            label="Verwendetes Surfbrett"
            placeholder="z.B. 6'2 Shortboard"
          />

          <div class="form-group-row">
            <BaseInput
              id="waves_caught"
              type="number"
              v-model="stage.waves_caught"
              label="Gefangene Wellen"
              placeholder="z.B. 15"
            />
            <BaseInput
              id="water_temperature"
              type="number"
              v-model="stage.water_temperature"
              label="Wassertemperatur (°C)"
              placeholder="z.B. 18"
            />
          </div>

          <div class="form-group-row">
            <BaseInput
              id="tide_stage"
              type="select"
              v-model="stage.tide_stage"
              label="Gezeitenstadium"
            >
              <option value="">Nicht angegeben</option>
              <option value="LOW">Niedrigwasser</option>
              <option value="MID">Mittleres Wasser</option>
              <option value="HIGH">Hochwasser</option>
            </BaseInput>
            <BaseInput
              id="tide_movement"
              type="select"
              v-model="stage.tide_movement"
              label="Gezeitenbewegung"
            >
              <option value="">Nicht angegeben</option>
              <option value="RISING">Steigend</option>
              <option value="FALLING">Fallend</option>
            </BaseInput>
          </div>
        </div>
        <BaseButton
          type="submit"
          variant="primary"
          size="large"
          :disabled="isSubmitting"
          full-width
        >
          {{ isSubmitting ? 'Speichere...' : 'Änderungen speichern' }}
        </BaseButton>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import gpxParser from 'gpxparser';
import api from '../api';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';

const route = useRoute();
const router = useRouter();
const stageId = ref(route.params.id);

const stage = ref(null);
const isLoading = ref(true);
const error = ref(null);
const isSubmitting = ref(false);

const parsedTrack = ref(null);
const parsingStatus = ref('');

// Calculated values from GPX
const calculatedMetrics = ref(null);

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

// Update document title when stage data loads
watch(stage, (newStage) => {
  if (newStage && newStage.name) {
    document.title = `Edit: ${newStage.name} - WanderApp`;
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

const formatDurationForDisplay = (durationString) => {
  if (!durationString) return '';
  // Duration comes as HH:MM:SS from backend, we want to display as HH:MM
  return durationString.substring(0, 5);
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
      payload.manual_elevation_loss = stage.value.manual_elevation_loss || null;
      
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
h1 {
  margin-top: var(--space-4);
  margin-bottom: var(--space-6);
  color: var(--color-text-primary);
  font-size: var(--text-2xl);
}

.stage-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  max-width: 600px;
  margin: var(--space-8) auto;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: var(--space-2);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.form-group input[type="file"] {
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  background-color: var(--color-bg-primary);
}

hr {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: var(--space-4) 0;
}

.manual-fields {
  border: 1px solid var(--color-border);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-top: var(--space-4);
  background-color: var(--color-bg-secondary);
}

.manual-fields p {
  margin: 0 0 var(--space-4) 0;
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.surf-fields {
  border: 1px solid var(--color-surf);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-top: var(--space-4);
  background-color: rgba(32, 178, 170, 0.05);
}

.form-group-row {
  display: flex;
  gap: var(--space-4);
}

.form-group-row > * {
  flex: 1;
}

.error {
  color: var(--color-error);
  text-align: center;
  margin-top: var(--space-4);
  font-size: var(--text-sm);
}

.parsing-status {
  margin-top: var(--space-2);
  font-style: italic;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

/* GPX Preview Styles */
.gpx-preview {
  border: 2px solid var(--color-primary);
  background-color: var(--color-green-light);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin: var(--space-4) 0;
}

.gpx-preview h4 {
  margin: 0 0 var(--space-2) 0;
  color: var(--color-primary);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

.preview-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-2);
}

.preview-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.preview-stat .value {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

.preview-stat .value small {
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
}

.preview-stat label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0;
  text-align: center;
  font-weight: var(--font-normal);
}

.preview-note {
  margin: 0;
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border-light);
}

.preview-note small {
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

/* Existing GPX Data Styles */
.existing-gpx-data {
  border: 2px solid var(--color-blue);
  background-color: rgba(0, 123, 255, 0.05);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin: var(--space-4) 0;
}

.existing-gpx-data h4 {
  margin: 0 0 var(--space-2) 0;
  color: var(--color-blue);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

/* Mobile: Increase GPX file upload text size for better readability */
@media (max-width: 768px) {
  .form-group input[type="file"] {
    font-size: 16px; /* Prevent iOS auto-zoom and improve readability */
  }
}
</style>