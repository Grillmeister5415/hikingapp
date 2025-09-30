<template>
  <div class="login-container">
    <BaseCard variant="elevated" padding="large" class="login-form">
      <h2>Anmelden</h2>

      <BaseInput
        id="email"
        type="email"
        v-model="email"
        label="E-Mail"
        required
        autocomplete="username"
      />

      <BaseInput
        id="password"
        type="password"
        v-model="password"
        label="Passwort"
        required
        autocomplete="current-password"
      />

      <BaseButton
        type="submit"
        variant="primary"
        size="large"
        :loading="isLoading"
        full-width
        @click.prevent="handleLogin"
      >
        {{ isLoading ? 'Melde an...' : 'Anmelden' }}
      </BaseButton>

      <p v-if="error" class="error">{{ error }}</p>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api'; // <-- shared axios instance with baseURL: '/api'
import { useTabAwareNavigation } from '../utils/navigation.js';
import BaseCard from './base/BaseCard.vue';
import BaseInput from './base/BaseInput.vue';
import BaseButton from './base/BaseButton.vue';

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
  min-height: 80vh;
}

.login-form {
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: var(--space-6);
  color: var(--color-text-primary);
}

.error {
  color: var(--color-error);
  text-align: center;
  margin-top: var(--space-4);
  font-size: var(--text-sm);
}
</style>
