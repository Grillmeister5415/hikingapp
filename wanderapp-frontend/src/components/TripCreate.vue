<template>
  <div>
    <router-link to="/">&larr; Abbrechen</router-link>
    <h1>Neuen Trip erstellen</h1>
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

      <div class="form-group">
        <label>Übernachtung in Hütten</label>
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

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Speichere...' : 'Trip speichern' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const name = ref('');
const description = ref('');
const start_date = ref('');
const end_date = ref('');
const error = ref(null);
const isSubmitting = ref(false);

const allUsers = ref([]);
const usersLoading = ref(true);
const selectedParticipants = ref([]);

const huts = ref([]);
const newHutName = ref('');
const newHutLink = ref('');

watch(start_date, (newStartDate) => {
  if (newStartDate && end_date.value && newStartDate > end_date.value) {
    end_date.value = newStartDate;
  }
});

onMounted(async () => {
  try {
    const usersResponse = await api.get('/users/');
    allUsers.value = usersResponse.data;

    const meResponse = await api.get('/users/me/');
    const currentUserId = meResponse.data.id;
    if (currentUserId && !selectedParticipants.value.includes(currentUserId)) {
      selectedParticipants.value.push(currentUserId);
    }
  } catch (err) {
    error.value = 'Fehler beim Laden der Benutzerliste.';
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

const handleSubmit = async () => {
  isSubmitting.value = true;
  error.value = null;
  try {
    const payload = {
      name: name.value,
      description: description.value,
      start_date: start_date.value,
      end_date: end_date.value,
      participants_ids: selectedParticipants.value,
      huts_data: huts.value
    };
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
</style>