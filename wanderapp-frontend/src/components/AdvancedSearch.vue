<template>
  <div class="advanced-search">
    <div v-if="props.showAdvancedFilters" class="advanced-filters">
      <div class="filter-grid">
        <!-- Location Filters -->
        <div class="filter-group">
          <label>Surf Spot:</label>
          <input
            v-model="filters.surf_spot"
            type="text"
            placeholder="e.g. Pipeline, Mavericks"
            class="filter-input"
          />
        </div>

        <div class="filter-group">
          <label>Country:</label>
          <select v-model="filters.country_code" class="filter-select">
            <option value="">All Countries</option>
            <option v-for="country in countries" :key="country.code" :value="country.code">
              {{ country.name }}
            </option>
          </select>
        </div>

        <!-- Wave Conditions -->
        <div class="filter-group">
          <label>Wave Height (m):</label>
          <div class="range-inputs">
            <input
              v-model="filters.wave_height_min"
              type="number"
              placeholder="Min"
              step="0.5"
              class="filter-input small"
            />
            <span>to</span>
            <input
              v-model="filters.wave_height_max"
              type="number"
              placeholder="Max"
              step="0.5"
              class="filter-input small"
            />
          </div>
        </div>

        <div class="filter-group">
          <label>Wave Quality (1-5):</label>
          <input
            v-model="filters.wave_quality_min"
            type="number"
            min="1"
            max="5"
            placeholder="Min quality"
            class="filter-input"
          />
        </div>

        <!-- Equipment -->
        <div class="filter-group">
          <label>Surfboard:</label>
          <input
            v-model="filters.surfboard_type"
            type="text"
            placeholder="e.g. Shortboard, Longboard"
            class="filter-input"
          />
        </div>

        <!-- Water Conditions -->
        <div class="filter-group">
          <label>Water Temp (°C):</label>
          <div class="range-inputs">
            <input
              v-model="filters.water_temp_min"
              type="number"
              placeholder="Min"
              class="filter-input small"
            />
            <span>to</span>
            <input
              v-model="filters.water_temp_max"
              type="number"
              placeholder="Max"
              class="filter-input small"
            />
          </div>
        </div>

        <div class="filter-group">
          <label>Tide Stage:</label>
          <select v-model="filters.tide_stage" class="filter-select">
            <option value="">All Tides</option>
            <option value="LOW">Low Tide</option>
            <option value="MID_INCOMING">Mid Incoming</option>
            <option value="HIGH">High Tide</option>
            <option value="MID_OUTGOING">Mid Outgoing</option>
          </select>
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
import { ref, onMounted } from 'vue';
import api from '../api';

const props = defineProps({
  showAdvancedFilters: {
    type: Boolean,
    default: false
  }
});

const filters = ref({
  surf_spot: '',
  country_code: '',
  wave_height_min: '',
  wave_height_max: '',
  wave_quality_min: '',
  water_temp_min: '',
  water_temp_max: '',
  tide_stage: '',
  surfboard_type: ''
});

const countries = ref([]);

const emit = defineEmits(['search']);

const fetchCountries = async () => {
  try {
    const response = await api.get('/countries/');

    // Parse the API response correctly - combine popular destinations and all countries
    const popularDestinations = response.data.popular_surf_destinations || [];
    const allCountries = response.data.all_countries || [];

    // Combine both arrays and extract only code and name for dropdown
    const combinedCountries = [
      ...popularDestinations.map(country => ({ code: country.code, name: country.name })),
      ...allCountries.map(country => ({ code: country.code, name: country.name }))
    ];

    countries.value = combinedCountries;
  } catch (error) {
    console.error('Error fetching countries:', error);
    // Fallback to basic popular surf destinations if API fails
    countries.value = [
      { code: 'PT', name: 'Portugal' },
      { code: 'MX', name: 'Mexico' },
      { code: 'US', name: 'United States' },
      { code: 'ES', name: 'Spain' },
      { code: 'FR', name: 'France' },
      { code: 'AU', name: 'Australia' },
      { code: 'ID', name: 'Indonesia' },
      { code: 'CR', name: 'Costa Rica' },
      { code: 'BR', name: 'Brazil' },
      { code: 'PE', name: 'Peru' }
    ];
  }
};

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

onMounted(() => {
  fetchCountries();
});
</script>

<style scoped>
.advanced-search {
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
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    max-width: 1200px;
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

.filter-input, .filter-select {
  padding: 0.6rem;
  border-radius: 6px;
  border: 1px solid #ced4da;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
  background-color: white;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 44px;
}

.filter-input:focus, .filter-select:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.filter-select {
  cursor: pointer;
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
  .advanced-search {
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

  .filter-input, .filter-select {
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
  .advanced-search {
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