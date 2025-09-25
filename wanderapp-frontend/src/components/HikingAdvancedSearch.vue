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
  background-color: #f8f9fa;
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

@media (min-width: 1200px) {
  .filter-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.filter-input {
  padding: 0.6rem;
  border-radius: 6px;
  border: 1px solid #ced4da;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 44px;
  background-color: white;
}

.filter-input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.filter-input.small {
  flex: 1;
  min-width: 70px;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.range-inputs span {
  color: #6c757d;
  font-size: 0.85rem;
  white-space: nowrap;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
}

.btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn:focus {
  outline: 2px solid #42b983;
  outline-offset: 2px;
}

.btn:active {
  transform: translateY(1px);
}

.btn-primary {
  background-color: #42b983;
  font-weight: 600;
}

.btn-primary:hover {
  background-color: #369870;
}

.btn-secondary {
  background-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

@media (max-width: 768px) {
  .hiking-advanced-search {
    padding: 0.75rem;
    gap: 0.5rem;
    margin: 0 0.5rem 1rem 0.5rem;
  }

  .filter-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .filter-group {
    gap: 0.25rem;
  }

  .filter-group label {
    font-size: 0.85rem;
    margin: 0;
  }

  .filter-input {
    padding: 0.6rem 0.8rem;
    font-size: 0.9rem;
    border-radius: 8px;
  }

  .range-inputs {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0.5rem;
    align-items: center;
  }

  .range-inputs input {
    padding: 0.5rem;
    font-size: 0.9rem;
  }

  .range-inputs span {
    text-align: center;
    font-size: 0.85rem;
  }

  .filter-actions {
    margin-top: 0.5rem;
  }

  .btn {
    padding: 0.8rem 1rem;
    font-size: 0.95rem;
    border-radius: 10px;
  }
}

@media (max-width: 480px) {
  .hiking-advanced-search {
    padding: 0.75rem;
    margin: 0 0.5rem 1rem 0.5rem;
  }

  .filter-grid {
    gap: 0.5rem;
  }

  .range-inputs {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .range-inputs span {
    text-align: left;
    align-self: start;
    font-size: 0.8rem;
    margin-bottom: -0.25rem;
  }

  .filter-actions {
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }

  .btn {
    width: 100%;
    padding: 0.8rem;
    font-size: 0.95rem;
    font-weight: 600;
  }
}
</style>