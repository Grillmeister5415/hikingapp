<template>
  <div>
    <div v-if="isLoading">Lade Surf Session Daten...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="stage">
      <router-link :to="`/trip/${stage.trip}`">&larr; Abbrechen und zurück zum Trip</router-link>
      <h1>🏄‍♂️ Surf Session bearbeiten</h1>
      <form @submit.prevent="handleSubmit" class="stage-form">
        <!-- Basic Fields -->
        <div class="form-group">
          <label for="name">Session Name</label>
          <input type="text" id="name" v-model="stage.name" required placeholder="z.B. Morning surf at Malibu" />
        </div>
        <div class="form-group">
          <label for="date">Datum</label>
          <input type="date" id="date" v-model="stage.date" required :min="tripStartDate" :max="tripEndDate" />
        </div>
        <div class="form-group">
          <label for="description">Beschreibung (optional)</label>
          <textarea id="description" v-model="stage.description" placeholder="Wie waren die Bedingungen? Wie hat sich die Session angefühlt?"></textarea>
        </div>

        <!-- Surf-Specific Fields -->
        <div class="surf-fields">
          <h3>🏄‍♂️ Surf Details</h3>
          
          <div class="form-group">
            <label for="surf_spot">Surf Spot</label>
            <input type="text" id="surf_spot" v-model="stage.surf_spot" required placeholder="Name des Surf Spots" />
          </div>

          <div class="form-group">
            <label for="time_in_water">Zeit im Wasser (HH:MM)</label>
            <input 
              type="text" 
              id="time_in_water" 
              v-model="stage.time_in_water" 
              placeholder="z.B. 02:30" 
              pattern="[0-9]+:[0-5][0-9]"
              title="Bitte im Format Stunden:Minuten eingeben, z.B. 02:30."
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="wave_height">Wellenhöhe (m)</label>
              <input type="number" step="0.1" id="wave_height" v-model="stage.wave_height" placeholder="z.B. 1.5" />
            </div>
            
            <div class="form-group">
              <label for="wave_quality">Wellenqualität (1-5)</label>
              <select id="wave_quality" v-model="stage.wave_quality">
                <option value="">Auswählen...</option>
                <option value="1">⭐ - Schlecht</option>
                <option value="2">⭐⭐ - Okay</option>
                <option value="3">⭐⭐⭐ - Gut</option>
                <option value="4">⭐⭐⭐⭐ - Sehr gut</option>
                <option value="5">⭐⭐⭐⭐⭐ - Perfekt</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="surfboard_used">Verwendetes Surfbrett</label>
            <input type="text" id="surfboard_used" v-model="stage.surfboard_used" placeholder="z.B. 6'2 Shortboard, 9'0 Longboard" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="water_temperature">Wassertemperatur (°C)</label>
              <input type="number" step="0.1" id="water_temperature" v-model="stage.water_temperature" placeholder="z.B. 18.5" />
            </div>
            
            <div class="form-group">
              <label for="waves_caught">Anzahl gefangener Wellen</label>
              <input type="number" id="waves_caught" v-model="stage.waves_caught" placeholder="z.B. 15" />
            </div>
          </div>

          <!-- Tide Information -->
          <div class="tide-section">
            <h4>🌊 Tide Information</h4>
            <div class="form-row">
              <div class="form-group">
                <label for="tide_stage">Tide Stage</label>
                <select id="tide_stage" v-model="stage.tide_stage">
                  <option value="">Select...</option>
                  <option value="LOW">Low tide</option>
                  <option value="MID">Mid tide</option>
                  <option value="HIGH">High tide</option>
                </select>
              </div>
              <div class="form-group">
                <label for="tide_movement">Tide Movement</label>
                <select id="tide_movement" v-model="stage.tide_movement">
                  <option value="">Select...</option>
                  <option value="RISING">Rising</option>
                  <option value="FALLING">Falling</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Wave and Wind Conditions -->
          <div class="conditions-section">
            <h4>🌊 Wave & Wind Conditions</h4>
            <div class="form-row">
              <div class="form-group">
                <label for="swell_direction">Swell Direction</label>
                <select id="swell_direction" v-model="stage.swell_direction">
                  <option value="">Select...</option>
                  <option value="N">North (N)</option>
                  <option value="NE">Northeast (NE)</option>
                  <option value="E">East (E)</option>
                  <option value="SE">Southeast (SE)</option>
                  <option value="S">South (S)</option>
                  <option value="SW">Southwest (SW)</option>
                  <option value="W">West (W)</option>
                  <option value="NW">Northwest (NW)</option>
                </select>
              </div>
              <div class="form-group">
                <label for="wind_direction">Wind Direction</label>
                <select id="wind_direction" v-model="stage.wind_direction">
                  <option value="">Select...</option>
                  <option value="N">North (N)</option>
                  <option value="NE">Northeast (NE)</option>
                  <option value="E">East (E)</option>
                  <option value="SE">Southeast (SE)</option>
                  <option value="S">South (S)</option>
                  <option value="SW">Southwest (SW)</option>
                  <option value="W">West (W)</option>
                  <option value="NW">Northwest (NW)</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label for="wave_energy">Wave Energy</label>
              <input type="number" step="0.1" id="wave_energy" v-model="stage.wave_energy" placeholder="e.g. 2.5 (wave power/energy rating)" />
            </div>
          </div>

          <div class="form-group">
            <label for="external_link">Links (optional)</label>
            <input type="url" id="external_link" v-model="stage.external_link" placeholder="https://surf-forecast.com/... oder andere relevante Links" />
          </div>
        </div>
        
        <button type="submit" :disabled="isSubmitting">Änderungen speichern</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';

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

    const payload = {
      name: stage.value.name,
      date: stage.value.date,
      description: stage.value.description,
      external_link: stage.value.external_link,
      
      // Surf-specific fields
      surf_spot: stage.value.surf_spot,
      time_in_water: timeInWaterToSend,
      surfboard_used: stage.value.surfboard_used,
      wave_height: stage.value.wave_height ? parseFloat(stage.value.wave_height) : null,
      wave_quality: stage.value.wave_quality ? parseInt(stage.value.wave_quality) : null,
      water_temperature: stage.value.water_temperature ? parseFloat(stage.value.water_temperature) : null,
      waves_caught: stage.value.waves_caught ? parseInt(stage.value.waves_caught) : null,
      tide_stage: stage.value.tide_stage,
      tide_movement: stage.value.tide_movement,
      
      // Additional surf conditions
      swell_direction: stage.value.swell_direction,
      wind_direction: stage.value.wind_direction,
      wave_energy: stage.value.wave_energy ? parseFloat(stage.value.wave_energy) : null
    };
    
    await api.patch(`/stages/${stageId.value}/`, payload);
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
.stage-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 600px;
  margin: 2rem auto;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

label {
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

input, textarea, select {
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: #20b2aa;
  box-shadow: 0 0 0 3px rgba(32, 178, 170, 0.1);
}

button {
  padding: 1rem;
  background: linear-gradient(135deg, #20b2aa, #17a2b8);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: linear-gradient(135deg, #17a2b8, #138496);
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.surf-fields {
  border: 2px solid #20b2aa;
  padding: 1.5rem;
  border-radius: 12px;
  margin-top: 1rem;
  background-color: #f0fdff;
}

.surf-fields h3 {
  margin-top: 0;
  color: #20b2aa;
}

.tide-section {
  background-color: rgba(32, 178, 170, 0.05);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.tide-section h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #17a2b8;
}

.conditions-section {
  background-color: rgba(32, 178, 170, 0.05);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.conditions-section h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #17a2b8;
}

.error {
  color: red;
  margin-top: 0.5rem;
  padding: 0.8rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .stage-form {
    margin: 1rem;
    max-width: none;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .surf-fields {
    padding: 1rem;
  }
}
</style>