<template>
  <div class="hiking-advanced-search">
    <div v-if="props.showAdvancedFilters" class="advanced-filters">
      <div class="filter-grid">
        <!-- Distance Filters -->
        <div class="filter-group">
          <label>Distance (km):</label>
          <div class="range-inputs">
            <BaseInput
              id="distance-min"
              v-model="filters.distance_min"
              type="number"
              placeholder="0 km"
              :step="0.5"
            />
            <span>to</span>
            <BaseInput
              id="distance-max"
              v-model="filters.distance_max"
              type="number"
              placeholder="∞"
              :step="0.5"
            />
          </div>
        </div>

        <!-- Elevation Filters -->
        <div class="filter-group">
          <label>Elevation Gain (m):</label>
          <div class="range-inputs">
            <BaseInput
              id="elevation-min"
              v-model="filters.elevation_min"
              type="number"
              placeholder="0 m"
              :step="50"
            />
            <span>to</span>
            <BaseInput
              id="elevation-max"
              v-model="filters.elevation_max"
              type="number"
              placeholder="∞"
              :step="50"
            />
          </div>
        </div>

        <!-- Duration Filters -->
        <div class="filter-group">
          <label>Duration (hours):</label>
          <div class="range-inputs">
            <BaseInput
              id="duration-min"
              v-model="filters.duration_min"
              type="number"
              placeholder="0h"
              :step="0.5"
            />
            <span>to</span>
            <BaseInput
              id="duration-max"
              v-model="filters.duration_max"
              type="number"
              placeholder="∞"
              :step="0.5"
            />
          </div>
        </div>
      </div>

      <div class="filter-actions">
        <BaseButton @click="applyFilters" variant="primary" size="small">Apply Filters</BaseButton>
        <BaseButton @click="clearFilters" variant="secondary" size="small">Clear All</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';

const props = defineProps({
  showAdvancedFilters: {
    type: Boolean,
    default: false
  }
});

const filters = ref({
  distance_min: '',
  distance_max: '',
  elevation_min: '',
  elevation_max: '',
  duration_min: '',
  duration_max: ''
});

const emit = defineEmits(['search']);

const applyFilters = () => {
  const activeFilters = {};

  Object.keys(filters.value).forEach(key => {
    if (filters.value[key] !== '' && filters.value[key] !== null) {
      // Convert numeric filter values to numbers
      const value = filters.value[key];
      activeFilters[key] = (typeof value === 'string' && !isNaN(value) && value !== '')
        ? Number(value)
        : value;
    }
  });

  emit('search', activeFilters);
};

const clearFilters = () => {
  Object.keys(filters.value).forEach(key => {
    filters.value[key] = '';
  });
  emit('search', {});
};
</script>

<style scoped>
.hiking-advanced-search {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

@media (min-width: 1200px) {
  .filter-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.filter-group label {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  font-size: var(--text-sm);
}

/* Range input wrappers (BaseInput) */
.range-inputs .input-wrapper {
  flex: 1;
  min-width: 120px;
  margin-bottom: 0; /* Override BaseInput default margin */
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.range-inputs span {
  color: var(--color-text-secondary);
  font-size: var(--text-xs);
  white-space: nowrap;
}

.filter-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-start;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .hiking-advanced-search {
    padding: var(--space-4);
    gap: var(--space-2);
    margin: 0 0.5rem var(--space-4) 0.5rem;
  }

  .filter-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .filter-group {
    gap: var(--space-2);
  }

  .filter-group label {
    font-size: var(--text-sm);
    margin: 0;
  }

  /* Range input wrappers on mobile */
  .range-inputs {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: var(--space-2);
    align-items: center;
  }

  .range-inputs .input-wrapper {
    margin-bottom: 0;
  }

  .range-inputs span {
    text-align: center;
    font-size: var(--text-sm);
  }

  .filter-actions {
    margin-top: var(--space-2);
  }
}

@media (max-width: 480px) {
  .hiking-advanced-search {
    padding: var(--space-4);
    margin: 0 0.5rem var(--space-4) 0.5rem;
  }

  .filter-grid {
    gap: var(--space-2);
  }

  .range-inputs {
    grid-template-columns: 1fr auto 1fr;
    gap: var(--space-2);
  }

  .range-inputs span {
    /* Keep "to" text visible for clarity */
    text-align: center;
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
  }

  .range-inputs .input-field::placeholder {
    font-weight: var(--font-medium);
  }

  .filter-actions {
    flex-direction: column;
    gap: var(--space-2);
    margin-top: var(--space-4);
  }

  .filter-actions > * {
    width: 100%;
  }
}
</style>