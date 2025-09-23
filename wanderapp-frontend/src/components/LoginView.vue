<template>
  <div class="login-container">
    <form @submit.prevent="handleLogin" class="login-form">
      <h2>Anmelden</h2>
      <div class="form-group">
        <label for="email">E-Mail</label>
        <input type="email" id="email" v-model="email" required autocomplete="username" />
      </div>
      <div class="form-group">
        <label for="password">Passwort</label>
        <input type="password" id="password" v-model="password" required autocomplete="current-password" />
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Melde an...' : 'Anmelden' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api'; // <-- shared axios instance with baseURL: '/api'
import { useTabAwareNavigation } from '../utils/navigation.js';

const { navigateToTripList } = useTabAwareNavigation();
const email = ref('');
const password = ref('');
const error = ref(null);
const isLoading = ref(false);

const handleLogin = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.post('/token/', {
      email: email.value,
      password: password.value,
    });

    // WICHTIG: Beide Tokens speichern!
    localStorage.setItem('accessToken', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);

    // Nach erfolgreichem Login zur Hauptseite weiterleiten
    navigateToTripList();
  } catch (err) {
    if (err.response && err.response.status === 401) {
      error.value = 'Ungültige Anmeldedaten. Bitte versuchen Sie es erneut.';
    } else {
      error.value = 'Ein Netzwerkfehler ist aufgetreten.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
.login-form {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
h2 { 
  text-align: center; 
  margin-bottom: 1.5rem; 
}
.form-group { 
  display: flex; 
  flex-direction: column; 
}
label { 
  margin-bottom: 0.5rem; 
  font-weight: bold; 
}
input { 
  padding: 0.8rem; 
  border: 1px solid #ccc; 
  border-radius: 4px; 
  font-size: 1rem; 
  margin-bottom: 1rem; 
}
button { 
  padding: 1rem; 
  background-color: #42b983; 
  color: white; 
  border: none; 
  border-radius: 4px; 
  font-size: 1rem; 
  cursor: pointer; 
  width: 100%; 
}
.error { 
  color: red; 
  text-align: center; 
  margin-top: 1rem; 
}
</style>
