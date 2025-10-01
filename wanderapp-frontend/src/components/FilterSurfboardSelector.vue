<template>
  <div class="filter-surfboard-selector">
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
        v-if="showDropdown && (searchResults.length > 0 || isSearching)"
        class="dropdown"
      >
        <!-- Loading state -->
        <div v-if="isSearching" class="dropdown-item loading">
          Suche...
        </div>

        <!-- Existing surfboards -->
        <div
          v-for="(board, index) in searchResults"
          :key="`board-${index}`"
          :class="['dropdown-item', { highlighted: highlightedIndex === index }]"
          @mousedown.prevent="selectSurfboard(board.value)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="board-icon">{{ board.label.charAt(0) }}</span>
          <span class="board-name">{{ board.value }}</span>
        </div>

        <!-- No results message -->
        <div v-if="!isSearching && searchResults.length === 0 && searchQuery.trim().length >= 2" class="dropdown-item no-results">
          Keine Surfboards gefunden
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
    default: 'z.B. Shortboard, Longboard'
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
    showDropdown.value = false;
    return;
  }

  // Debounce search
  showDropdown.value = true;
  searchTimer = setTimeout(() => {
    searchSurfboards(query);
  }, 300);
};

const searchSurfboards = async (query) => {
  isSearching.value = true;
  showDropdown.value = true;

  try {
    const response = await api.get(`/search-suggestions/?q=${encodeURIComponent(query)}`);

    // Filter to only show surfboard suggestions
    const suggestions = response.data.suggestions || [];
    const surfboards = suggestions.filter(s => s.type === 'surfboard');
    searchResults.value = surfboards;

  } catch (error) {
    console.error('[FilterSurfboardSelector] Error searching surfboards:', error);
    searchResults.value = [];
  } finally {
    isSearching.value = false;
  }
};

const selectSurfboard = (boardName) => {
  searchQuery.value = boardName;
  updateParent(boardName);
  clearDropdown();
};

const clearDropdown = () => {
  searchResults.value = [];
  showDropdown.value = false;
  highlightedIndex.value = -1;
};

const handleFocus = () => {
  const query = searchQuery.value.trim();
  if (query.length >= 2) {
    searchSurfboards(query);
  }
};

const handleKeydown = (event) => {
  if (!showDropdown.value || searchResults.value.length === 0) return;

  const totalItems = searchResults.value.length;

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
        selectSurfboard(searchResults.value[highlightedIndex.value].value);
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
.filter-surfboard-selector {
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

.board-icon {
  font-size: var(--text-lg);
}

.board-name {
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
