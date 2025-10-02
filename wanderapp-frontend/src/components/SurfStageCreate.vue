<template>
  <div>
    <BaseButton tag="router-link" :to="`/trip/${tripId}`" variant="ghost" size="small">
      &larr; Abbrechen und zurück zum Trip
    </BaseButton>
    <h1>🏄‍♂️ Neue Surf Session hinzufügen</h1>
    <form @submit.prevent="handleSubmit" class="stage-form">
      <!-- Basic Fields -->
      <BaseInput
        id="name"
        type="text"
        v-model="name"
        label="Session Name"
        required
        placeholder="z.B. Morning surf at Malibu"
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
        placeholder="Wie waren die Bedingungen? Wie hat sich die Session angefühlt?"
      />

      <!-- Surf-Specific Fields -->
      <div class="surf-fields">
        <h3>🏄‍♂️ Surf Details</h3>

        <div class="input-wrapper">
          <label for="surfspot-selector" class="input-label">Surf Spot</label>
          <SurfSpotSelector
            id="surfspot-selector"
            v-model="surf_spot"
            placeholder="z.B. Pipeline, Malibu, Supertubes"
          />
        </div>

        <BaseInput
          id="time_in_water"
          type="text"
          v-model="time_in_water"
          label="Zeit im Wasser (HH:MM)"
          placeholder="z.B. 02:30"
          pattern="[0-9]+:[0-5][0-9]"
        />

        <div class="form-row">
          <BaseInput
            id="wave_height"
            type="number"
            step="0.1"
            v-model="wave_height"
            label="Wellenhöhe (m)"
            placeholder="z.B. 1.5"
          />

          <BaseInput
            id="wave_quality"
            type="select"
            v-model="wave_quality"
            label="Wellenqualität (1-5)"
          >
            <option value="">Auswählen...</option>
            <option value="1">⭐ - Schlecht</option>
            <option value="2">⭐⭐ - Okay</option>
            <option value="3">⭐⭐⭐ - Gut</option>
            <option value="4">⭐⭐⭐⭐ - Sehr gut</option>
            <option value="5">⭐⭐⭐⭐⭐ - Perfekt</option>
          </BaseInput>
        </div>

        <div class="input-wrapper">
          <label for="surfboard-selector" class="input-label">Verwendetes Surfbrett</label>
          <SurfboardSelector
            id="surfboard-selector"
            v-model="surfboard_used"
            placeholder="z.B. 6'2 Shortboard, 9'0 Longboard"
          />
        </div>

        <div class="form-row">
          <BaseInput
            id="water_temperature"
            type="number"
            step="0.1"
            v-model="water_temperature"
            label="Wassertemperatur (°C)"
            placeholder="z.B. 18.5"
          />

          <BaseInput
            id="waves_caught"
            type="number"
            v-model="waves_caught"
            label="Anzahl gefangener Wellen"
            placeholder="z.B. 15"
          />
        </div>

        <!-- Tide Information -->
        <div class="tide-section">
          <h4>🌊 Tide Information</h4>
          <div class="form-row">
            <BaseInput
              id="tide_stage"
              type="select"
              v-model="tide_stage"
              label="Tide Stage"
            >
              <option value="">Select...</option>
              <option value="LOW">Low tide</option>
              <option value="MID">Mid tide</option>
              <option value="HIGH">High tide</option>
            </BaseInput>
            <BaseInput
              id="tide_movement"
              type="select"
              v-model="tide_movement"
              label="Tide Movement"
            >
              <option value="">Select...</option>
              <option value="RISING">Rising</option>
              <option value="FALLING">Falling</option>
            </BaseInput>
          </div>
        </div>

        <!-- Wave and Wind Conditions -->
        <div class="conditions-section">
          <h4>🌊 Wave & Wind Conditions</h4>
          <div class="form-row">
            <BaseInput
              id="swell_direction"
              type="select"
              v-model="swell_direction"
              label="Swell Direction"
            >
              <option value="">Select...</option>
              <option value="N">North (N)</option>
              <option value="NE">Northeast (NE)</option>
              <option value="E">East (E)</option>
              <option value="SE">Southeast (SE)</option>
              <option value="S">South (S)</option>
              <option value="SW">Southwest (SW)</option>
              <option value="W">West (W)</option>
              <option value="NW">Northwest (NW)</option>
            </BaseInput>
            <BaseInput
              id="wind_direction"
              type="select"
              v-model="wind_direction"
              label="Wind Direction"
            >
              <option value="">Select...</option>
              <option value="N">North (N)</option>
              <option value="NE">Northeast (NE)</option>
              <option value="E">East (E)</option>
              <option value="SE">Southeast (SE)</option>
              <option value="S">South (S)</option>
              <option value="SW">Southwest (SW)</option>
              <option value="W">West (W)</option>
              <option value="NW">Northwest (NW)</option>
            </BaseInput>
          </div>
          <BaseInput
            id="wave_energy"
            type="number"
            step="0.1"
            v-model="wave_energy"
            label="Wave Energy"
            placeholder="e.g. 2.5 (wave power/energy rating)"
          />
        </div>

        <BaseInput
          id="external_link"
          type="url"
          v-model="external_link"
          label="Links (optional)"
          placeholder="https://surf-forecast.com/... oder andere relevante Links"
        />
      </div>

      <BaseButton
        type="submit"
        variant="primary"
        size="large"
        :disabled="isSubmitting"
        full-width
      >
        {{ isSubmitting ? 'Speichere...' : 'Surf Session speichern' }}
      </BaseButton>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';
import SurfboardSelector from './SurfboardSelector.vue';
import SurfSpotSelector from './SurfSpotSelector.vue';

const route = useRoute();
const router = useRouter();
const tripId = ref(route.params.tripId);

// Basic fields
const name = ref('');
const date = ref('');
const description = ref('');
const external_link = ref('');

// Surf-specific fields
const surf_spot = ref('');
const time_in_water = ref('');
const surfboard_used = ref('');
const wave_height = ref(null);
const wave_quality = ref('');
const water_temperature = ref(null);
const waves_caught = ref(null);
const tide_stage = ref('');
const tide_movement = ref('');

// Additional surf conditions
const swell_direction = ref('');
const wind_direction = ref('');
const wave_energy = ref(null);

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

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    // Format time_in_water if provided
    let timeInWaterToSend = time_in_water.value || null;
    if (timeInWaterToSend && timeInWaterToSend.match(/^[0-9]+:[0-5][0-9]$/)) {
      timeInWaterToSend += ':00';
    }

    // Handle surf spot - find existing or create new
    let surfSpotId = null;
    if (surf_spot.value) {
      try {
        // Try to find existing surf spot by name
        const surfSpotsResponse = await api.get('/surfspots/');
        const existingSpot = surfSpotsResponse.data.find(
          spot => spot.name.toLowerCase() === surf_spot.value.toLowerCase()
        );

        if (existingSpot) {
          surfSpotId = existingSpot.id;
        } else {
          // Create new surf spot
          const newSpotResponse = await api.post('/surfspots/', {
            name: surf_spot.value,
          });
          surfSpotId = newSpotResponse.data.id;
        }
      } catch (spotErr) {
        console.error('Error handling surf spot:', spotErr);
        // Continue without surf spot link if there's an error
      }
    }

    // Handle surfboard - find existing or create new
    let surfboardId = null;
    if (surfboard_used.value) {
      try {
        // Try to find existing surfboard by name
        const surfboardsResponse = await api.get('/surfboards/');
        const existingBoard = surfboardsResponse.data.find(
          board => board.name.toLowerCase() === surfboard_used.value.toLowerCase()
        );

        if (existingBoard) {
          surfboardId = existingBoard.id;
        } else {
          // Create new surfboard
          const newBoardResponse = await api.post('/surfboards/', {
            name: surfboard_used.value,
            board_type: 'OTHER', // Default type, user can edit later in admin
          });
          surfboardId = newBoardResponse.data.id;
        }
      } catch (boardErr) {
        console.error('Error handling surfboard:', boardErr);
        // Continue without surfboard link if there's an error
      }
    }

    const payload = {
      name: name.value,
      date: date.value,
      description: description.value,
      trip: parseInt(tripId.value),
      activity_type: 'SURFING',
      external_link: external_link.value,

      // Surf-specific fields
      surf_spot: surf_spot.value, // Keep for backward compatibility
      surf_spot_id: surfSpotId, // New FK field
      time_in_water: timeInWaterToSend,
      surfboard_used: surfboard_used.value, // Keep for backward compatibility
      surfboard_id: surfboardId, // New FK field
      wave_height: wave_height.value ? parseFloat(wave_height.value) : null,
      wave_quality: wave_quality.value ? parseInt(wave_quality.value) : null,
      water_temperature: water_temperature.value ? parseFloat(water_temperature.value) : null,
      waves_caught: waves_caught.value ? parseInt(waves_caught.value) : null,
      tide_stage: tide_stage.value,
      tide_movement: tide_movement.value,

      // Additional surf conditions
      swell_direction: swell_direction.value,
      wind_direction: wind_direction.value,
      wave_energy: wave_energy.value ? parseFloat(wave_energy.value) : null,

      // No track points for surfing
      track_points: []
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
}

.input-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  display: block;
}

.surf-fields {
  border: 2px solid var(--color-surf);
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  margin-top: var(--space-4);
  background-color: #f0fdff;
}

.surf-fields h3 {
  margin-top: 0;
  margin-bottom: var(--space-4);
  color: var(--color-surf);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
}

.tide-section {
  background-color: rgba(32, 178, 170, 0.05);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-top: var(--space-4);
}

.tide-section h4 {
  margin-top: 0;
  margin-bottom: var(--space-4);
  color: var(--color-surf-dark);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

.conditions-section {
  background-color: rgba(32, 178, 170, 0.05);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-top: var(--space-4);
}

.conditions-section h4 {
  margin-top: 0;
  margin-bottom: var(--space-4);
  color: var(--color-surf-dark);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

.error {
  color: var(--color-error);
  margin-top: var(--space-2);
  padding: var(--space-3);
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .stage-form {
    margin: var(--space-4);
    max-width: none;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }

  .surf-fields {
    padding: var(--space-4);
  }

  /* Emphasize section headers on mobile */
  .surf-fields h3 {
    font-size: var(--text-xl);
    margin-top: var(--space-4);
    margin-bottom: var(--space-5);
    padding-bottom: var(--space-2);
    border-bottom: 2px solid var(--color-surf);
  }

  .tide-section h4,
  .conditions-section h4 {
    font-size: var(--text-lg);
    margin-top: var(--space-5);
    margin-bottom: var(--space-4);
    font-weight: var(--font-bold);
  }
}
</style>