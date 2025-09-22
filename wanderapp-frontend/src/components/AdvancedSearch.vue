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

.filter-input, .filter-select {
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