<template>
  <span :class="badgeClasses">
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'error', 'warning', 'info', 'hiking', 'surfing'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
});

const badgeClasses = computed(() => [
  'badge',
  `badge-${props.variant}`,
  `badge-${props.size}`
]);
</script>

<style scoped>
.badge {
  display: inline-block;
  font-weight: var(--font-medium);
  border-radius: var(--radius-full);
  white-space: nowrap;
  line-height: 1;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* Sizes */
.badge-small {
  padding: var(--space-1) var(--space-2);
  font-size: 0.625rem;
}

.badge-medium {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

.badge-large {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

/* Variants */
.badge-default {
  background-color: var(--color-gray-100);
  color: var(--color-gray-600);
}

.badge-primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary-hover);
}

.badge-success {
  background-color: rgba(40, 167, 69, 0.1);
  color: var(--color-success);
}

.badge-error {
  background-color: rgba(220, 53, 69, 0.1);
  color: var(--color-error);
}

.badge-warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #856404;
}

.badge-info {
  background-color: rgba(23, 162, 184, 0.1);
  color: var(--color-info);
}

.badge-hiking {
  background-color: rgba(40, 167, 69, 0.1);
  color: var(--color-hiking);
}

.badge-surfing {
  background-color: rgba(32, 178, 170, 0.1);
  color: var(--color-surfing);
}
</style>