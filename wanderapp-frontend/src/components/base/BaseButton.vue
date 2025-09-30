<template>
  <component
    :is="tag"
    :type="tag === 'button' ? type : undefined"
    :to="tag === 'router-link' ? to : undefined"
    :href="tag === 'a' ? href : undefined"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-spinner"></span>
    <slot v-else />
  </component>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'ghost', 'danger', 'link'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  type: {
    type: String,
    default: 'button'
  },
  tag: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'a', 'router-link'].includes(value)
  },
  to: {
    type: [String, Object],
    default: null
  },
  href: {
    type: String,
    default: null
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click']);

const buttonClasses = computed(() => [
  'btn',
  `btn-${props.variant}`,
  `btn-${props.size}`,
  {
    'btn-full-width': props.fullWidth,
    'btn-loading': props.loading
  }
]);

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>

<style scoped>
/* Base Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-base);
  font-weight: var(--font-medium);
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Sizes */
.btn-small {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
}

.btn-medium {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
}

.btn-large {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
}

.btn-full-width {
  width: 100%;
}

/* Variants */
.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-secondary {
  background-color: var(--color-gray-500);
  color: white;
  border-color: var(--color-gray-500);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-gray-600);
}

.btn-ghost {
  background-color: transparent;
  color: var(--color-text-primary);
  border-color: var(--color-border-medium);
}

.btn-ghost:hover:not(:disabled) {
  background-color: var(--color-bg-secondary);
}

.btn-danger {
  background-color: var(--color-error);
  color: white;
  border-color: var(--color-error);
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-link {
  background-color: transparent;
  color: var(--color-blue);
  border-color: transparent;
  padding: 0;
}

.btn-link:hover:not(:disabled) {
  color: var(--color-blue-hover);
  text-decoration: underline;
}

/* Loading State */
.btn-loading {
  position: relative;
  color: transparent;
}

.btn-spinner {
  position: absolute;
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  color: white;
}

.btn-ghost .btn-spinner,
.btn-link .btn-spinner {
  color: var(--color-text-primary);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Focus States */
.btn:focus-visible {
  outline: 2px solid var(--color-blue);
  outline-offset: 2px;
}
</style>