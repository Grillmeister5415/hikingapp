<template>
  <div>
    <BaseButton tag="router-link" :to="cancelRoute" variant="ghost" size="small">&larr; Abbrechen</BaseButton>
    <h1>{{ getTripTypeLabel() }} erstellen</h1>
    <form @submit.prevent="handleSubmit" class="trip-form">
      <BaseInput
        id="name"
        type="text"
        v-model="name"
        label="Trip-Name"
        required
      />

      <BaseInput
        id="description"
        type="textarea"
        v-model="description"
        label="Beschreibung"
      />

      <div class="form-group-row">
        <BaseInput
          id="start_date"
          type="date"
          v-model="start_date"
          label="Startdatum"
          required
          :max="end_date"
        />

        <BaseInput
          id="end_date"
          type="date"
          v-model="end_date"
          label="Enddatum"
          required
          :min="start_date"
        />
      </div>

      <hr>

      <ParticipantSelector
        v-model="selectedParticipants"
        :autofocus="false"
      />

      <hr>

      <!-- Show huts section only for hiking trips -->
      <div v-if="activityType === 'HIKING'" class="form-group">
        <label>🏔️ Übernachtung in Hütten</label>
        <ul v-if="huts.length" class="hut-list">
          <li v-for="(hut, index) in huts" :key="index">
            <span class="hut-info">
              {{ hut.name }} <span v-if="hut.link" class="hut-link">({{ hut.link }})</span>
            </span>
            <BaseButton @click="removeHut(index)" variant="danger" size="small">&times;</BaseButton>
          </li>
        </ul>
        <div class="hut-form">
          <BaseInput
            id="hut_name"
            type="text"
            v-model="newHutName"
            placeholder="Name der Hütte"
          />
          <BaseInput
            id="hut_link"
            type="url"
            v-model="newHutLink"
            placeholder="Link (optional)"
          />
          <BaseButton @click="addHut" variant="secondary">Hütte hinzufügen</BaseButton>
        </div>
      </div>

      <!-- Show country dropdown only for surf trips -->
      <div v-if="activityType === 'SURFING'">
        <div v-if="countriesLoading">Lade Länder...</div>
        <BaseInput
          v-else
          id="country"
          type="select"
          v-model="country"
          label="🌍 Land"
          required
        >
          <option value="">Land auswählen...</option>

          <!-- Popular surf destinations -->
          <optgroup label="🏄‍♂️ Beliebte Surf-Ziele">
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
        {{ isSubmitting ? 'Speichere...' : 'Trip speichern' }}
      </BaseButton>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import ParticipantSelector from './ParticipantSelector.vue';
import { useTabAwareNavigation } from '../utils/navigation.js';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';

const router = useRouter();
const route = useRoute();
const { getTripListRoute } = useTabAwareNavigation();

// Computed property for cancel link
const cancelRoute = computed(() => getTripListRoute());

// Get activity type from URL query parameter, default to HIKING
const activityType = route.query.activity_type || 'HIKING';

const name = ref('');
const description = ref('');
const start_date = ref('');
const end_date = ref('');
const error = ref(null);
const isSubmitting = ref(false);

const selectedParticipants = ref([]);

// Huts (for hiking trips)
const huts = ref([]);
const newHutName = ref('');
const newHutLink = ref('');

// Country (for surf trips)
const country = ref('');
const popularSurfDestinations = ref([]);
const allCountries = ref([]);
const countriesLoading = ref(false);

watch(start_date, (newStartDate) => {
  if (newStartDate && end_date.value && newStartDate > end_date.value) {
    end_date.value = newStartDate;
  }
});

onMounted(async () => {
  try {
    // Auto-add current user as participant
    const meResponse = await api.get('/users/me/');
    const currentUser = meResponse.data;
    if (currentUser && !selectedParticipants.value.some(p => p.id === currentUser.id)) {
      selectedParticipants.value.push(currentUser);
    }

    // Load countries for surf trips
    if (activityType === 'SURFING') {
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
    error.value = 'Fehler beim Laden der Daten.';
  }
});

const addHut = () => {
  if (newHutName.value.trim()) {
    huts.value.push({
      name: newHutName.value.trim(),
      link: newHutLink.value.trim()
    });
    newHutName.value = '';
    newHutLink.value = '';
  }
};

const removeHut = (index) => {
  huts.value.splice(index, 1);
};

const getTripTypeLabel = () => {
  const typeLabels = {
    'HIKING': '🥾 Neuen Wander-Trip',
    'RUNNING': '🏃‍♂️ Neuen Lauf-Trip',
    'SURFING': '🏄‍♂️ Neuen Surf-Trip'
  };
  return typeLabels[activityType] || '🥾 Neuen Trip';
};

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    // Validate surf trip country selection
    if (activityType === 'SURFING' && !country.value) {
      error.value = 'Bitte wählen Sie ein Land für den Surf-Trip aus.';
      return;
    }

    const payload = {
      name: name.value,
      description: description.value,
      start_date: start_date.value,
      end_date: end_date.value,
      activity_type: activityType,
      participants_ids: selectedParticipants.value.map(p => p.id),
    };

    // Add activity-specific data
    if (activityType === 'HIKING') {
      payload.huts_data = huts.value;
    } else if (activityType === 'SURFING') {
      payload.country_code = country.value;
      // Debug logging
      console.log('Surf trip payload:', {
        activityType,
        countryValue: country.value,
        countriesLoaded: !countriesLoading.value,
        popularCount: popularSurfDestinations.value.length,
        allCountriesCount: allCountries.value.length
      });
    }

    await api.post('/trips/', payload);
    const tripListRoute = getTripListRoute();
    router.push(tripListRoute);
  } catch (err) {
    error.value = 'Fehler beim Speichern des Trips: ' + (JSON.stringify(err.response?.data) || err.message);
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