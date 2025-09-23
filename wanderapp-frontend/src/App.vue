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
#app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
  max-width: 960px;
  margin: 40px auto;
  padding: 20px;
}
</style>