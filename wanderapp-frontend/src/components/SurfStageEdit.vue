<template>
  <div>
    <div v-if="isLoading">Lade Surf Session Daten...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="stage">
      <BaseButton tag="router-link" :to="`/trip/${stage.trip}`" variant="ghost" size="small">
        &larr; Abbrechen und zurück zum Trip
      </BaseButton>
      <h1>🏄‍♂️ Surf Session bearbeiten</h1>
      <form @submit.prevent="handleSubmit" class="stage-form">
        <!-- Basic Fields -->
        <BaseInput
          id="name"
          type="text"
          v-model="stage.name"
          label="Session Name"
          required
          placeholder="z.B. Morning surf at Malibu"
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
          placeholder="Wie waren die Bedingungen? Wie hat sich die Session angefühlt?"
        />

        <!-- Surf-Specific Fields -->
        <div class="surf-fields">
          <h3>🏄‍♂️ Surf Details</h3>

          <div class="input-wrapper">
            <label for="surfspot-selector" class="input-label">Surf Spot</label>
            <SurfSpotSelector
              id="surfspot-selector"
              v-model="stage.surf_spot"
              placeholder="z.B. Pipeline, Malibu, Supertubes"
            />
          </div>

          <BaseInput
            id="time_in_water"
            type="text"
            v-model="stage.time_in_water"
            label="Zeit im Wasser (HH:MM)"
            placeholder="z.B. 02:30"
            pattern="[0-9]+:[0-5][0-9]"
          />

          <div class="form-row">
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
              v-model="stage.surfboard_used"
              placeholder="z.B. 6'2 Shortboard, 9'0 Longboard"
            />
          </div>

          <div class="form-row">
            <BaseInput
              id="water_temperature"
              type="number"
              step="0.1"
              v-model="stage.water_temperature"
              label="Wassertemperatur (°C)"
              placeholder="z.B. 18.5"
            />

            <BaseInput
              id="waves_caught"
              type="number"
              v-model="stage.waves_caught"
              label="Anzahl gefangener Wellen"
              placeholder="z.B. 15"
            />
          </div>

          <div class="form-row">
            <BaseInput
              id="crowd_factor"
              type="select"
              v-model="stage.crowd_factor"
              label="Crowd Factor"
            >
              <option value="">Select...</option>
              <option value="EMPTY">Empty</option>
              <option value="CHILL">Chill</option>
              <option value="CROWDED">Crowded</option>
              <option value="PACKED">Packed</option>
            </BaseInput>
          </div>

          <!-- Tide Information -->
          <div class="tide-section">
            <h4>🌊 Tide Information</h4>
            <div class="form-row">
              <BaseInput
                id="tide_stage"
                type="select"
                v-model="stage.tide_stage"
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
                v-model="stage.tide_movement"
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
                v-model="stage.swell_direction"
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
                v-model="stage.wind_direction"
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
            <div class="form-row">
              <BaseInput
                id="wave_energy"
                type="number"
                step="0.1"
                v-model="stage.wave_energy"
                label="Wave Energy (kJ)"
                placeholder="z.B. 255"
              />
              <BaseInput
                id="wind_speed"
                type="number"
                step="0.1"
                v-model="stage.wind_speed"
                label="Windgeschwindigkeit (km/h)"
                placeholder="z.B. 15.5"
              />
            </div>
          </div>

          <BaseInput
            id="external_link"
            type="url"
            v-model="stage.external_link"
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
          {{ isSubmitting ? 'Speichere...' : 'Änderungen speichern' }}
        </BaseButton>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import { clearDashboardCache } from '../store';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';
import SurfboardSelector from './SurfboardSelector.vue';
import SurfSpotSelector from './SurfSpotSelector.vue';

const route = useRoute();
const router = useRouter();
const stageId = ref(route.params.id);

const stage = ref(null);
const isLoading = ref(true);
const error = ref(null);
const isSubmitting = ref(false);
const tripStartDate = ref('');
const tripEndDate = ref('');

onMounted(async () => {
  try {
    // Load stage data
    const stageResponse = await api.get(`/stages/${stageId.value}/`);
    stage.value = stageResponse.data;
    
    // Format time_in_water for display (remove seconds if present)
    if (stage.value.time_in_water) {
      stage.value.time_in_water = stage.value.time_in_water.substring(0, 5); // "02:30:00" -> "02:30"
    }
    
    // Load trip data for date constraints
    const tripResponse = await api.get(`/trips/${stage.value.trip}/`);
    tripStartDate.value = tripResponse.data.start_date;
    tripEndDate.value = tripResponse.data.end_date;
    
    isLoading.value = false;
  } catch (err) {
    console.error("Error loading stage data:", err);
    error.value = "Konnte Surf Session Daten nicht laden.";
    isLoading.value = false;
  }
});

// Update document title when stage data loads
watch(stage, (newStage) => {
  if (newStage && newStage.name) {
    document.title = `Edit: ${newStage.name} - WanderApp`;
  }
});

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    // Format time_in_water if provided
    let timeInWaterToSend = stage.value.time_in_water || null;
    if (timeInWaterToSend && timeInWaterToSend.match(/^[0-9]+:[0-5][0-9]$/)) {
      timeInWaterToSend += ':00';
    }

    // Handle surf spot - find existing or create new
    let surfSpotId = null;
    if (stage.value.surf_spot) {
      try {
        // Try to find existing surf spot by name
        const surfSpotsResponse = await api.get('/surfspots/');
        const existingSpot = surfSpotsResponse.data.find(
          spot => spot.name.toLowerCase() === stage.value.surf_spot.toLowerCase()
        );

        if (existingSpot) {
          surfSpotId = existingSpot.id;
        } else {
          // Create new surf spot
          const newSpotResponse = await api.post('/surfspots/', {
            name: stage.value.surf_spot,
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
    if (stage.value.surfboard_used) {
      try {
        // Try to find existing surfboard by name
        const surfboardsResponse = await api.get('/surfboards/');
        const existingBoard = surfboardsResponse.data.find(
          board => board.name.toLowerCase() === stage.value.surfboard_used.toLowerCase()
        );

        if (existingBoard) {
          surfboardId = existingBoard.id;
        } else {
          // Create new surfboard
          const newBoardResponse = await api.post('/surfboards/', {
            name: stage.value.surfboard_used,
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
      name: stage.value.name,
      date: stage.value.date,
      description: stage.value.description,
      external_link: stage.value.external_link,

      // Surf-specific fields
      surf_spot: stage.value.surf_spot, // Keep for backward compatibility
      surf_spot_id: surfSpotId, // New FK field
      time_in_water: timeInWaterToSend,
      surfboard_used: stage.value.surfboard_used, // Keep for backward compatibility
      surfboard_id: surfboardId, // New FK field
      wave_height: stage.value.wave_height ? parseFloat(stage.value.wave_height) : null,
      wave_quality: stage.value.wave_quality ? parseInt(stage.value.wave_quality) : null,
      water_temperature: stage.value.water_temperature ? parseFloat(stage.value.water_temperature) : null,
      waves_caught: stage.value.waves_caught ? parseInt(stage.value.waves_caught) : null,
      tide_stage: stage.value.tide_stage,
      tide_movement: stage.value.tide_movement,

      // Additional surf conditions
      swell_direction: stage.value.swell_direction,
      wind_direction: stage.value.wind_direction,
      wave_energy: stage.value.wave_energy ? parseFloat(stage.value.wave_energy) : null,
      crowd_factor: stage.value.crowd_factor,
      wind_speed: stage.value.wind_speed ? parseFloat(stage.value.wind_speed) : null
    };

    await api.patch(`/stages/${stageId.value}/`, payload);
    clearDashboardCache(); // Clear cache so dashboard reflects changes
    router.push(`/trip/${stage.value.trip}`);
  } catch (err) {
    console.error("Error updating stage:", err);
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