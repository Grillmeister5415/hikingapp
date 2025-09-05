<template>
  <div>
    <div v-if="isLoading">Lade Trip...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="trip">
      <router-link :to="`/trip/${trip.id}`">&larr; Abbrechen</router-link>
      <h1>Trip bearbeiten</h1>
      <form @submit.prevent="handleSubmit" class="trip-form">
        <div class="form-group">
          <label for="name">Trip-Name</label>
          <input type="text" id="name" v-model="trip.name" required />
        </div>
        <div class="form-group">
          <label for="description">Beschreibung</label>
          <textarea id="description" v-model="trip.description"></textarea>
        </div>
        <div class="form-group-row">
          <div class="form-group">
            <label for="start_date">Startdatum</label>
            <input type="date" id="start_date" v-model="trip.start_date" required />
          </div>
          <div class="form-group">
            <label for="end_date">Enddatum</label>
            <input type="date" id="end_date" v-model="trip.end_date" required />
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

        <div class="form-group">
          <label>Übernachtung in Hütten</label>
          <ul v-if="trip.huts && trip.huts.length" class="hut-list">
            <li v-for="(hut, index) in trip.huts" :key="index">
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

        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Speichere...' : 'Änderungen speichern' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';

const route = useRoute();
const router = useRouter();
const tripId = route.params.id;

const trip = ref(null);
const isLoading = ref(true);
const error = ref(null);
const isSubmitting = ref(false);

const allUsers = ref([]);
const usersLoading = ref(true);
const selectedParticipants = ref([]);

const newHutName = ref('');
const newHutLink = ref('');

onMounted(async () => {
  try {
    // Fetch both the trip data and the list of all users at the same time
    const [tripResponse, usersResponse] = await Promise.all([
      api.get(`/trips/${tripId}/`),
      api.get('/users/')
    ]);

    trip.value = tripResponse.data;
    allUsers.value = usersResponse.data;

    // Pre-select the checkboxes for participants who are already on the trip
    if (trip.value.participants) {
      selectedParticipants.value = trip.value.participants.map(p => p.id);
    }
  } catch (err) {
    error.value = "Fehler beim Laden der Trip-Daten.";
  } finally {
    isLoading.value = false;
    usersLoading.value = false;
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
      participants_ids: selectedParticipants.value,
      huts_data: trip.value.huts,
    };
    await api.patch(`/trips/${tripId}/`, payload);
    router.push(`/trip/${tripId}`);
  } catch (err) {
    error.value = 'Fehler beim Speichern der Änderungen: ' + (JSON.stringify(err.response?.data) || err.message);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* You can copy the styles from TripCreate.vue as they are identical */
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
</style>