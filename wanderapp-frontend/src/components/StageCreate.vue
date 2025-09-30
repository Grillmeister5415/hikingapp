<template>
  <div>
    <BaseButton tag="router-link" :to="`/trip/${tripId}`" variant="ghost" size="small">
      &larr; Abbrechen und zurück zum Trip
    </BaseButton>
    <h1>Neue Etappe hinzufügen</h1>
    <form @submit.prevent="handleSubmit" class="stage-form">
      <BaseInput
        id="name"
        type="text"
        v-model="name"
        label="Etappen-Name"
        required
      />

      <BaseInput
        id="date"
        type="date"
        v-model="date"
        label="Datum"
        required
        :min="tripStartDate"
        :max="tripEndDate"
      />

      <BaseInput
        id="description"
        type="textarea"
        v-model="description"
        label="Beschreibung (optional)"
      />

      <BaseInput
        id="external_link"
        type="url"
        v-model="external_link"
        label="Link (optional)"
        placeholder="https://tourenportal.com/..."
      />

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
        <BaseInput
          id="duration"
          type="text"
          v-model="manual_duration"
          label="Wanderdauer (HH:MM)"
          placeholder="z.B. 04:30 oder 50:00"
          pattern="[0-9]+:[0-5][0-9]"
          helper-text="Dieses Feld überschreibt die Dauer aus der GPX-Datei, falls vorhanden."
        />
        <BaseInput
          id="length"
          type="number"
          step="0.1"
          v-model="manual_length_km"
          label="Distanz (km)"
        />
        <BaseInput
          id="elevation_gain"
          type="number"
          v-model="manual_elevation_gain"
          label="Höhenmeter (Aufstieg)"
        />
        <BaseInput
          id="elevation_loss"
          type="number"
          v-model="manual_elevation_loss"
          label="Höhenmeter (Abstieg)"
        />
      </div>

      <BaseButton
        type="submit"
        variant="primary"
        size="large"
        :disabled="isSubmitting"
        full-width
      >
        {{ isSubmitting ? 'Speichere...' : 'Etappe speichern' }}
      </BaseButton>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import gpxParser from 'gpxparser';
import api from '../api';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';

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

/* Mobile: Increase GPX file upload text size for better readability */
@media (max-width: 768px) {
  .form-group input[type="file"] {
    font-size: 16px; /* Prevent iOS auto-zoom and improve readability */
  }
}
</style>