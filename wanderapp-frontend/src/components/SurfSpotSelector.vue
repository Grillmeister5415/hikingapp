<template>
  <div class="surfspot-selector">
    <div class="input-container" ref="inputContainer">
      <input
        ref="searchInput"
        v-model="searchQuery"
        @input="handleInput"
        @keydown="handleKeydown"
        @focus="handleFocus"
        @blur="handleBlur"
        type="text"
        :placeholder="placeholder"
        class="search-input"
        autocomplete="off"
      />

      <!-- Dropdown with suggestions -->
      <div
        v-if="showDropdown && (searchResults.length > 0 || (searchQuery.trim().length > 0 && !isSearching))"
        class="dropdown"
      >
        <!-- Loading state -->
        <div v-if="isSearching" class="dropdown-item loading">
          Suche...
        </div>

        <!-- Existing surf spots -->
        <div
          v-for="(spot, index) in searchResults"
          :key="`spot-${index}`"
          :class="['dropdown-item', { highlighted: highlightedIndex === index }]"
          @mousedown.prevent="selectSurfSpot(spot.value)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="spot-name">{{ spot.value }}</span>
        </div>

        <!-- Add new surf spot option -->
        <div
          v-if="searchQuery.trim().length > 0 && !isSearching && !searchResults.some(s => s.value.toLowerCase() === searchQuery.trim().toLowerCase())"
          :class="['dropdown-item', 'add-new', { highlighted: highlightedIndex === searchResults.length }]"
          @mousedown.prevent="selectSurfSpot(searchQuery.trim())"
          @mouseenter="highlightedIndex = searchResults.length"
        >
          <span class="add-icon">+</span>
          <span class="add-text">"{{ searchQuery.trim() }}" verwenden</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import api from '../api';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'z.B. Pipeline, Malibu, Supertubes'
  }
});

const emit = defineEmits(['update:modelValue']);

// Reactive data
const searchQuery = ref('');
const searchResults = ref([]);
const showDropdown = ref(false);
const isSearching = ref(false);
const highlightedIndex = ref(-1);

// Template refs
const searchInput = ref(null);
const inputContainer = ref(null);

// Debounce timer
let searchTimer = null;

// Initialize from props
watch(() => props.modelValue, (newValue) => {
  searchQuery.value = newValue || '';
}, { immediate: true });

// Emit updates when value changes
const updateParent = (newValue) => {
  emit('update:modelValue', newValue);
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  if (searchTimer) {
    clearTimeout(searchTimer);
  }
});

// Methods
const handleInput = () => {
  highlightedIndex.value = -1;
  updateParent(searchQuery.value);

  if (searchTimer) {
    clearTimeout(searchTimer);
  }

  const query = searchQuery.value.trim();

  if (query.length === 0) {
    searchResults.value = [];
    showDropdown.value = false;
    return;
  }

  if (query.length < 2) {
    searchResults.value = [];
    // Don't hide dropdown - keep it open to show "create new" option
    showDropdown.value = true;
    return;
  }

  // Debounce search
  showDropdown.value = true;
  searchTimer = setTimeout(() => {
    searchSurfSpots(query);
  }, 300);
};

const searchSurfSpots = async (query) => {
  isSearching.value = true;
  showDropdown.value = true;

  try {
    const response = await api.get(`/search-suggestions/?q=${encodeURIComponent(query)}`);

    // Filter to only show surf spot suggestions
    const suggestions = response.data.suggestions || [];
    const spots = suggestions.filter(s => s.type === 'surf_spot');
    searchResults.value = spots;

  } catch (error) {
    console.error('[SurfSpotSelector] Error searching surf spots:', error);
    searchResults.value = [];
  } finally {
    isSearching.value = false;
  }
};

const selectSurfSpot = (spotName) => {
  searchQuery.value = spotName;
  updateParent(spotName);
  clearDropdown();
};

const clearDropdown = () => {
  searchResults.value = [];
  showDropdown.value = false;
  highlightedIndex.value = -1;
};

const handleFocus = () => {
  showDropdown.value = true;  // Always show dropdown on focus
  const query = searchQuery.value.trim();
  if (query.length >= 2) {
    searchSurfSpots(query);
  }
};

const handleKeydown = (event) => {
  if (!showDropdown.value) return;

  // Check if "add new" option is visible
  const query = searchQuery.value.trim();
  const hasAddNewOption = query.length > 0 &&
                          !isSearching.value &&
                          !searchResults.value.some(s => s.value.toLowerCase() === query.toLowerCase());

  const totalItems = searchResults.value.length + (hasAddNewOption ? 1 : 0);

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, totalItems - 1);
      break;

    case 'ArrowUp':
      event.preventDefault();
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1);
      break;

    case 'Enter':
      event.preventDefault();
      if (highlightedIndex.value >= 0 && highlightedIndex.value < searchResults.value.length) {
        // Select existing surf spot
        selectSurfSpot(searchResults.value[highlightedIndex.value].value);
      } else if (highlightedIndex.value === searchResults.value.length && hasAddNewOption) {
        // Select "add new" option
        selectSurfSpot(query);
      } else if (query.length > 0) {
        // No selection, just use the typed value
        selectSurfSpot(query);
      } else {
        clearDropdown();
      }
      break;

    case 'Escape':
      clearDropdown();
      searchInput.value?.blur();
      break;
  }
};

const handleBlur = () => {
  // Delay hiding dropdown to allow clicks on dropdown items
  setTimeout(() => {
    showDropdown.value = false;
    highlightedIndex.value = -1;
  }, 150);
};

const handleClickOutside = (event) => {
  if (inputContainer.value && !inputContainer.value.contains(event.target)) {
    showDropdown.value = false;
    highlightedIndex.value = -1;
  }
};
</script>

<style scoped>
.surfspot-selector {
  width: 100%;
}

.input-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  font-family: var(--font-base);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-blue);
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.dropdown {
  position: absolute;
  top: calc(100% + var(--space-1));
  left: 0;
  right: 0;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  z-index: 1000;
  max-height: 240px;
  overflow-y: auto;
}

.dropdown-item {
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border-bottom: 1px solid var(--color-border-light);
  transition: background-color var(--transition-fast);
}

.dropdown-item:hover,
.dropdown-item.highlighted {
  background-color: var(--color-bg-secondary);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item.loading,
.dropdown-item.no-results {
  cursor: default;
  color: var(--color-text-secondary);
  font-style: italic;
}

.dropdown-item.add-new {
  background-color: rgba(40, 167, 69, 0.05);
  border-top: 1px solid var(--color-border-medium);
}

.dropdown-item.add-new:hover,
.dropdown-item.add-new.highlighted {
  background-color: rgba(40, 167, 69, 0.1);
}

.add-icon {
  color: var(--color-success);
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
}

.add-text {
  color: var(--color-success);
  font-weight: var(--font-medium);
}

.spot-icon {
  font-size: var(--text-lg);
}

.spot-name {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .search-input {
    font-size: 16px; /* Prevent iOS zoom */
  }

  .dropdown-item {
    padding: var(--space-2) var(--space-3);
  }
}
</style>
