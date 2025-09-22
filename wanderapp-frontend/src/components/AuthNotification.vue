<template>
  <transition name="fade">
    <div v-if="authMessage" :class="['auth-notification', `auth-notification--${authMessage.type}`]">
      {{ authMessage.text }}
      <button @click="clearMessage" class="auth-notification__close">&times;</button>
    </div>
  </transition>
</template>

<script setup>
import { authMessage } from '../store';

const clearMessage = () => {
  authMessage.value = null;
};
</script>

<style scoped>
.auth-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-width: 400px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.auth-notification--info {
  background-color: #0d6efd;
}

.auth-notification--warning {
  background-color: #fd7e14;
}

.auth-notification--error {
  background-color: #dc3545;
}

.auth-notification__close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  opacity: 0.8;
}

.auth-notification__close:hover {
  opacity: 1;
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>