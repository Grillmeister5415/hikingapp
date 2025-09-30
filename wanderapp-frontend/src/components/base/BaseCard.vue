<template>
  <div :class="cardClasses">
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>

    <div class="card-body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'bordered', 'elevated', 'flat'].includes(value)
  },
  padding: {
    type: String,
    default: 'normal',
    validator: (value) => ['none', 'small', 'normal', 'large'].includes(value)
  },
  hoverable: {
    type: Boolean,
    default: false
  }
});

const cardClasses = computed(() => [
  'card',
  `card-${props.variant}`,
  `card-padding-${props.padding}`,
  {
    'card-hoverable': props.hoverable
  }
]);
</script>

<style scoped>
.card {
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  overflow: hidden;
}

/* Variants */
.card-default {
  border: 1px solid var(--color-border-light);
}

.card-bordered {
  border: 2px solid var(--color-border-medium);
}

.card-elevated {
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-md);
}

.card-flat {
  background-color: var(--color-bg-secondary);
  border: none;
}

/* Padding Variants */
.card-padding-none .card-body {
  padding: 0;
}

.card-padding-small .card-body {
  padding: var(--space-4);
}

.card-padding-normal .card-body {
  padding: var(--space-6);
}

.card-padding-large .card-body {
  padding: var(--space-8);
}

/* Hoverable State */
.card-hoverable {
  cursor: pointer;
}

.card-hoverable:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

/* Card Sections */
.card-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-light);
}

.card-body {
  min-width: 0;
}

.card-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg-secondary);
}
</style>