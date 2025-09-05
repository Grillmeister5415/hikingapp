// src/store.js
import { ref } from 'vue';
import api from './api';

// Eine reaktive Variable, um den eingeloggten Benutzer zu speichern
export const currentUser = ref(null);

// Eine Funktion, die die Benutzerdaten vom Backend abruft
export async function fetchCurrentUser() {
  const token = localStorage.getItem('accessToken');
  if (token && !currentUser.value) {
    try {
      const response = await api.get('/users/me/');
      currentUser.value = response.data;
    } catch (error) {
      console.error("Could not fetch user.", error);
      currentUser.value = null;
    }
  }
}