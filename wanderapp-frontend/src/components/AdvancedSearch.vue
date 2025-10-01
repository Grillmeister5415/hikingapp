<template>
  <div class="advanced-search">
    <div v-if="props.showAdvancedFilters" class="advanced-filters">
      <div class="filter-grid">
        <!-- Location Filters -->
        <div class="filter-group">
          <label>Surf Spot:</label>
          <BaseInput
            id="surf-spot"
            v-model="filters.surf_spot"
            type="text"
            placeholder="e.g. Pipeline, Mavericks"
          />
        </div>

        <div class="filter-group">
          <label>Country:</label>
          <BaseInput
            id="country-code"
            v-model="filters.country_code"
            type="select"
          >
            <option value="">All Countries</option>
            <option v-for="country in countries" :key="country.code" :value="country.code">
              {{ country.name }}
            </option>
          </BaseInput>
        </div>

        <!-- Wave Conditions -->
        <div class="filter-group">
          <label>Wave Height (m):</label>
          <div class="range-inputs">
            <BaseInput
              id="wave-height-min"
              v-model="filters.wave_height_min"
              type="number"
              placeholder="0 m"
              :step="0.5"
            />
            <span>to</span>
            <BaseInput
              id="wave-height-max"
              v-model="filters.wave_height_max"
              type="number"
              placeholder="∞"
              :step="0.5"
            />
          </div>
        </div>

        <div class="filter-group">
          <label>Wave Quality (1-5):</label>
          <div class="range-inputs">
            <BaseInput
              id="wave-quality-min"
              v-model="filters.wave_quality_min"
              type="number"
              :min="1"
              :max="5"
              placeholder="1 ★"
            />
            <span>to</span>
            <BaseInput
              id="wave-quality-max"
              v-model="filters.wave_quality_max"
              type="number"
              :min="1"
              :max="5"
              placeholder="5 ★"
            />
          </div>
        </div>

        <!-- Equipment -->
        <div class="filter-group">
          <label>Surfboard:</label>
          <FilterSurfboardSelector
            id="surfboard-type"
            v-model="filters.surfboard_type"
            placeholder="e.g. Shortboard, Longboard"
          />
        </div>

        <!-- Water Conditions -->
        <div class="filter-group">
          <label>Water Temp (°C):</label>
          <div class="range-inputs">
            <BaseInput
              id="water-temp-min"
              v-model="filters.water_temp_min"
              type="number"
              placeholder="0°C"
            />
            <span>to</span>
            <BaseInput
              id="water-temp-max"
              v-model="filters.water_temp_max"
              type="number"
              placeholder="∞"
            />
          </div>
        </div>

        <div class="filter-group">
          <label>Tide Stage:</label>
          <BaseInput
            id="tide-stage"
            v-model="filters.tide_stage"
            type="select"
          >
            <option value="">All Tides</option>
            <option value="LOW">Low Tide</option>
            <option value="MID_INCOMING">Mid Incoming</option>
            <option value="HIGH">High Tide</option>
            <option value="MID_OUTGOING">Mid Outgoing</option>
          </BaseInput>
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
import { ref, onMounted } from 'vue';
import api from '../api';
import BaseButton from './base/BaseButton.vue';
import BaseInput from './base/BaseInput.vue';
import FilterSurfboardSelector from './FilterSurfboardSelector.vue';

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
  wave_quality_max: '',
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

onMounted(() => {
  fetchCountries();
});
</script>

<style scoped>
.advanced-search {
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
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    max-width: 1200px;
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
  white-space: nowrap;
}

/* Regular filter input wrappers (not in ranges) */
.filter-group > .input-wrapper {
  margin-bottom: 0; /* Override BaseInput default margin */
}

/* Range input wrappers */
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
  .advanced-search {
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

  /* Mobile input wrappers */
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
  .advanced-search {
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