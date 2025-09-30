<template>
  <div id="app-container">
    <router-view></router-view>
    <AuthNotification />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { fetchCurrentUser } from './store';
import AuthNotification from './components/AuthNotification.vue';

// This line was missing. It tells the app to fetch the user's
// data as soon as the application is loaded.
onMounted(fetchCurrentUser);
</script>

<style>
/* Import global design system styles */
@import './styles/base.css';

#app-container {
  font-family: var(--font-base);
  color: var(--color-text-primary);
  max-width: 960px;
  margin: var(--space-10) auto;
  padding: var(--space-5);
}
</style>