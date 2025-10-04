<template>
  <div>
    <div v-if="isLoading">Lade Trip...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="trip">
      <div class="header">
        <h1>Trip bearbeiten</h1>
        <BaseButton tag="router-link" :to="`/trip/${trip.id}`" variant="ghost" size="small">&larr; Abbrechen und zurück zum Trip</BaseButton>
      </div>
      <form @submit.prevent="handleSubmit" class="trip-form">
        <BaseInput
          id="name"
          type="text"
          v-model="trip.name"
          label="Trip-Name"
          required
        />

        <BaseInput
          id="description"
          type="textarea"
          v-model="trip.description"
          label="Beschreibung"
        />

        <div class="form-group-row">
          <BaseInput
            id="start_date"
            type="date"
            v-model="trip.start_date"
            label="Startdatum"
            required
          />

          <BaseInput
            id="end_date"
            type="date"
            v-model="trip.end_date"
            label="Enddatum"
            required
          />
        </div>

        <hr>

        <ParticipantSelector
          v-model="selectedParticipants"
          :autofocus="false"
        />

        <hr>

        <!-- Show huts section only for hiking trips -->
        <div v-if="trip.activity_type === 'HIKING'" class="form-group">
          <label>🏔️ Übernachtung in Hütten</label>
          <ul v-if="trip.huts && trip.huts.length" class="hut-list">
            <li v-for="(hut, index) in trip.huts" :key="index">
              <span class="hut-info">
                {{ hut.name }} <span v-if="hut.link" class="hut-link">({{ hut.link }})</span>
              </span>
              <BaseButton @click="removeHut(index)" variant="danger" size="small">&times;</BaseButton>
            </li>
          </ul>
          <div class="hut-form">
            <BaseInput
              type="text"
              v-model="newHutName"
              placeholder="Name der Hütte"
            />
            <BaseInput
              type="url"
              v-model="newHutLink"
              placeholder="Link (optional)"
            />
            <BaseButton @click="addHut" variant="secondary">Hütte hinzufügen</BaseButton>
          </div>
        </div>

        <!-- Show country dropdown only for surf trips -->
        <div v-if="trip.activity_type === 'SURFING'">
          <div v-if="countriesLoading">Lade Länder...</div>
          <BaseInput
            v-else
            id="country"
            type="select"
            v-model="selectedCountry"
            label="🌍 Land"
            required
          >
            <option value="">Land auswählen...</option>

            <!-- Popular surf destinations -->
            <optgroup label="🏄‍♂️ Beliebte Surf-Ziele" v-if="popularSurfDestinations.length">
              <option
                v-for="dest in popularSurfDestinations"
                :key="dest.code"
                :value="dest.code"
              >
                {{ dest.display }}
              </option>
            </optgroup>

            <!-- All other countries -->
            <optgroup label="🌍 Alle Länder" v-if="allCountries.length">
              <option
                v-for="country_option in allCountries"
                :key="country_option.code"
                :value="country_option.code"
              >
                {{ country_option.display }}
              </option>
            </optgroup>
          </BaseInput>
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
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import ParticipantSelector from './ParticipantSelector.vue';
import { clearDashboardCache } from '../store';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';

const route = useRoute();
const router = useRouter();
const tripId = route.params.id;

const trip = ref(null);
const isLoading = ref(true);
const error = ref(null);
const isSubmitting = ref(false);

const selectedParticipants = ref([]);

const newHutName = ref('');
const newHutLink = ref('');

// Country (for surf trips)
const selectedCountry = ref('');
const popularSurfDestinations = ref([]);
const allCountries = ref([]);
const countriesLoading = ref(false);

onMounted(async () => {
  try {
    // Fetch the trip data
    const tripResponse = await api.get(`/trips/${tripId}/`);
    trip.value = tripResponse.data;

    // Pre-populate the selected participants with full user objects
    if (trip.value.participants) {
      selectedParticipants.value = [...trip.value.participants];
    }

    // Set the selected country for surf trips
    if (trip.value.activity_type === 'SURFING' && trip.value.country) {
      selectedCountry.value = trip.value.country;
    }

    // Load countries for surf trips
    if (trip.value.activity_type === 'SURFING') {
      countriesLoading.value = true;
      try {
        const countriesResponse = await api.get('/countries/');
        popularSurfDestinations.value = countriesResponse.data.popular_surf_destinations;
        allCountries.value = countriesResponse.data.all_countries;
      } catch (countriesErr) {
        console.error('Error loading countries:', countriesErr);
        error.value = 'Fehler beim Laden der Länderliste.';
      } finally {
        countriesLoading.value = false;
      }
    }
  } catch (err) {
    error.value = "Fehler beim Laden der Trip-Daten.";
  } finally {
    isLoading.value = false;
  }
});

// Update document title when trip data loads
watch(trip, (newTrip) => {
  if (newTrip && newTrip.name) {
    document.title = `Edit: ${newTrip.name} - WanderApp`;
  }
});

const addHut = () => {
  if (newHutName.value.trim()) {
    if (!trip.value.huts) {
      trip.value.huts = [];
    }
    trip.value.huts.push({
      name: newHutName.value.trim(),
      link: newHutLink.value.trim()
    });
    newHutName.value = '';
    newHutLink.value = '';
  }
};

const removeHut = (index) => {
  trip.value.huts.splice(index, 1);
};

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    const payload = {
      name: trip.value.name,
      description: trip.value.description,
      start_date: trip.value.start_date,
      end_date: trip.value.end_date,
      participants_ids: selectedParticipants.value.map(p => p.id),
    };

    // Add activity-specific data
    if (trip.value.activity_type === 'HIKING') {
      payload.huts_data = trip.value.huts;
    } else if (trip.value.activity_type === 'SURFING') {
      payload.country_code = selectedCountry.value;
    }

    await api.patch(`/trips/${tripId}/`, payload);
    clearDashboardCache(); // Clear cache so dashboard reflects changes
    router.push(`/trip/${tripId}`);
  } catch (err) {
    error.value = 'Fehler beim Speichern der Änderungen: ' + (JSON.stringify(err.response?.data) || err.message);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

h1 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: var(--text-2xl);
}

.trip-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  max-width: 600px;
  margin: var(--space-8) auto;
}

.form-group-row {
  display: flex;
  gap: var(--space-4);
}

.form-group-row > * {
  flex: 1;
}

.form-group label {
  margin-bottom: var(--space-2);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

hr {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: var(--space-4) 0;
}

.hut-list {
  list-style: none;
  padding: 0;
  margin-bottom: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.hut-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-bg-secondary);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.hut-info {
  flex: 1;
}

.hut-link {
  color: var(--color-text-secondary);
  font-style: italic;
  font-size: var(--text-sm);
  margin-left: var(--space-2);
}

.hut-form {
  display: flex;
  gap: var(--space-2);
  align-items: flex-end;
}

.hut-form > :first-child {
  flex: 2;
}

.hut-form > :nth-child(2) {
  flex: 2;
}

.error {
  color: var(--color-error);
  text-align: center;
  margin-top: var(--space-4);
  font-size: var(--text-sm);
}

/* Mobile: Stack hut inputs vertically for clarity */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }

  .form-group-row {
    flex-direction: column;
    gap: var(--space-4);
  }

  .form-group-row > * {
    width: 100%;
    max-width: 100%;
  }

  .hut-form {
    flex-direction: column;
    align-items: stretch;
    gap: 0; /* Remove gap, BaseInput has its own margin-bottom */
  }

  .hut-form > * {
    flex: 1 !important;
  }
}
</style>