<template>
  <div class="hiking-advanced-search">
    <div v-if="props.showAdvancedFilters" class="advanced-filters">
      <div class="filter-grid">
        <!-- Distance Filters -->
        <div class="filter-group">
          <label>Distance (km):</label>
          <div class="range-inputs">
            <input
              v-model="filters.distance_min"
              type="number"
              placeholder="Min"
              step="0.5"
              class="filter-input small"
            />
            <span>to</span>
            <input
              v-model="filters.distance_max"
              type="number"
              placeholder="Max"
              step="0.5"
              class="filter-input small"
            />
          </div>
        </div>

        <!-- Elevation Filters -->
        <div class="filter-group">
          <label>Elevation Gain (m):</label>
          <div class="range-inputs">
            <input
              v-model="filters.elevation_min"
              type="number"
              placeholder="Min"
              step="50"
              class="filter-input small"
            />
            <span>to</span>
            <input
              v-model="filters.elevation_max"
              type="number"
              placeholder="Max"
              step="50"
              class="filter-input small"
            />
          </div>
        </div>

        <!-- Duration Filters -->
        <div class="filter-group">
          <label>Duration (hours):</label>
          <div class="range-inputs">
            <input
              v-model="filters.duration_min"
              type="number"
              placeholder="Min"
              step="0.5"
              class="filter-input small"
            />
            <span>to</span>
            <input
              v-model="filters.duration_max"
              type="number"
              placeholder="Max"
              step="0.5"
              class="filter-input small"
            />
          </div>
        </div>
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-primary">Apply Filters</button>
        <button @click="clearFilters" class="btn btn-secondary">Clear All</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

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
      activeFilters[key] = filters.value[key];
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
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2c3e50;
}

.filter-input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.filter-input.small {
  width: 80px;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #28a745;
  color: white;
}

.btn-primary:hover {
  background: #218838;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

@media (max-width: 768px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }

  .range-inputs {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-input.small {
    width: 100%;
  }
}
</style>