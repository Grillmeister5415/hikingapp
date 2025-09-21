<template>
  <div>
    <router-link to="/">&larr; Abbrechen</router-link>
    <h1>{{ getTripTypeLabel() }} erstellen</h1>
    <form @submit.prevent="handleSubmit" class="trip-form">
      <div class="form-group">
        <label for="name">Trip-Name</label>
        <input type="text" id="name" v-model="name" required />
      </div>
      <div class="form-group">
        <label for="description">Beschreibung</label>
        <textarea id="description" v-model="description"></textarea>
      </div>
      <div class="form-group-row">
        <div class="form-group">
          <label for="start_date">Startdatum</label>
          <input type="date" id="start_date" v-model="start_date" required :max="end_date" />
        </div>
        <div class="form-group">
          <label for="end_date">Enddatum</label>
          <input type="date" id="end_date" v-model="end_date" required :min="start_date" />
        </div>
      </div>

      <hr>

      <div class="form-group">
        <label>Teilnehmer</label>
        <div v-if="usersLoading">Lade Benutzer...</div>
        <div v-else class="checkbox-group">
          <div v-for="user in allUsers" :key="user.id" class="checkbox-item">
            <input type="checkbox" :id="`user-${user.id}`" :value="user.id" v-model="selectedParticipants" />
            <label :for="`user-${user.id}`">{{ user.username }}</label>
          </div>
        </div>
      </div>

      <hr>

      <!-- Show huts section only for hiking trips -->
      <div v-if="activityType === 'HIKING'" class="form-group">
        <label>🏔️ Übernachtung in Hütten</label>
        <ul v-if="huts.length" class="hut-list">
          <li v-for="(hut, index) in huts" :key="index">
            {{ hut.name }} <span v-if="hut.link" class="hut-link">({{ hut.link }})</span>
            <button type="button" @click="removeHut(index)" class="btn-remove">&times;</button>
          </li>
        </ul>
        <div class="hut-form">
          <input type="text" v-model="newHutName" placeholder="Name der Hütte" />
          <input type="url" v-model="newHutLink" placeholder="Link (optional)" />
          <button type="button" @click="addHut" class="btn-add-item">Hütte hinzufügen</button>
        </div>
      </div>

      <!-- Show country dropdown only for surf trips -->
      <div v-if="activityType === 'SURFING'" class="form-group">
        <label for="country">🌍 Land *</label>
        <div v-if="countriesLoading">Lade Länder...</div>
        <select v-else id="country" v-model="country" required class="country-select">
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
        </select>
      </div>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Speichere...' : 'Trip speichern' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';

const router = useRouter();
const route = useRoute();

// Get activity type from URL query parameter, default to HIKING
const activityType = route.query.activity_type || 'HIKING';

const name = ref('');
const description = ref('');
const start_date = ref('');
const end_date = ref('');
const error = ref(null);
const isSubmitting = ref(false);

const allUsers = ref([]);
const usersLoading = ref(true);
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
    // Load users
    const usersResponse = await api.get('/users/');
    allUsers.value = usersResponse.data;

    const meResponse = await api.get('/users/me/');
    const currentUserId = meResponse.data.id;
    if (currentUserId && !selectedParticipants.value.includes(currentUserId)) {
      selectedParticipants.value.push(currentUserId);
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
  } finally {
    usersLoading.value = false;
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
      participants_ids: selectedParticipants.value,
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
    router.push('/');
  } catch (err) {
    error.value = 'Fehler beim Speichern des Trips: ' + (JSON.stringify(err.response?.data) || err.message);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.trip-form { display: flex; flex-direction: column; gap: 1.5rem; max-width: 600px; margin: 2rem auto; }
.form-group { display: flex; flex-direction: column; }
.form-group-row { display: flex; gap: 1rem; }
.form-group-row .form-group { flex: 1; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, textarea { padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.checkbox-group { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.5rem; }
.checkbox-item { display: flex; align-items: center; }
.checkbox-item input { margin-right: 0.5rem; width: auto; }
.hut-list { list-style: none; padding: 0; margin-bottom: 1rem; }
.hut-list li { display: flex; justify-content: space-between; align-items: center; background: #f1f1f1; padding: 0.5rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; }
.hut-link { color: #555; font-style: italic; font-size: 0.9rem; }
.btn-remove { background: #e74c3c; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; line-height: 1; cursor: pointer; font-weight: bold; }
.hut-form { display: flex; gap: 0.5rem; }
.hut-form input { flex-grow: 1; }
.btn-add-item { padding: 0.8rem; background-color: #555; color: white; border: none; border-radius: 4px; cursor: pointer; }
button[type="submit"] { padding: 1rem; background-color: #42b983; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
button:disabled { background-color: #ccc; cursor: not-allowed; }
.error { color: red; }

/* Country dropdown styles */
.country-select {
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  background: white;
  min-width: 100%;
}

.country-select:focus {
  outline: none;
  border-color: #20b2aa;
  box-shadow: 0 0 0 3px rgba(32, 178, 170, 0.1);
}

.country-select optgroup {
  font-weight: bold;
  color: #333;
}

.country-select option {
  font-weight: normal;
  padding: 0.5rem;
}
</style>