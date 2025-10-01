<template>
  <div class="filter-participant-selector">
    <!-- Input field with autocomplete -->
    <div class="input-container" ref="inputContainer">
      <input
        ref="searchInput"
        v-model="searchQuery"
        @input="handleInput"
        @keydown="handleKeydown"
        @focus="showDropdown = true"
        @blur="handleBlur"
        type="text"
        :placeholder="selectedParticipants.length > 0 ? 'Weitere hinzufügen...' : 'Teilnehmer suchen...'"
        class="search-input"
        autocomplete="off"
      />

      <!-- Dropdown with suggestions -->
      <div
        v-if="showDropdown && searchResults.length > 0"
        class="dropdown"
      >
        <!-- Loading state -->
        <div v-if="isSearching" class="dropdown-item loading">
          Suche...
        </div>

        <!-- Existing users -->
        <div
          v-for="(user, index) in searchResults"
          :key="`user-${user.id}`"
          :class="['dropdown-item', { highlighted: highlightedIndex === index }]"
          @mousedown.prevent="selectUser(user)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="user-name">{{ user.username }}</span>
        </div>

        <!-- No results message -->
        <div v-if="!isSearching && searchResults.length === 0 && searchQuery.trim().length >= 2" class="dropdown-item no-results">
          Keine Benutzer gefunden
        </div>
      </div>
    </div>

    <!-- Selected participants as chips -->
    <div v-if="selectedParticipants.length > 0" class="selected-chips">
      <div
        v-for="participant in selectedParticipants"
        :key="participant.id"
        class="participant-chip"
      >
        <span class="chip-text">{{ participant.username }}</span>
        <button
          type="button"
          @click="removeParticipant(participant.id)"
          class="remove-chip"
          :aria-label="`${participant.username} entfernen`"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import api from '../api';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:modelValue']);

// Reactive data
const searchQuery = ref('');
const searchResults = ref([]);
const selectedParticipants = ref([]);
const showDropdown = ref(false);
const isSearching = ref(false);
const highlightedIndex = ref(-1);

// Template refs
const searchInput = ref(null);
const inputContainer = ref(null);

// Debounce timer
let searchTimer = null;

// Initialize selected participants from props
watch(() => props.modelValue, (newValue) => {
  selectedParticipants.value = [...newValue];
}, { immediate: true });

// Emit updates when selection changes
const updateParents = (newSelection) => {
  emit('update:modelValue', [...newSelection]);
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
    showDropdown.value = true;
    return;
  }

  // Debounce search
  searchTimer = setTimeout(() => {
    searchUsers(query);
  }, 300);
};

const searchUsers = async (query) => {
  isSearching.value = true;
  showDropdown.value = true;

  try {
    const response = await api.get(`/users/search/?q=${encodeURIComponent(query)}`);

    // Filter out already selected users
    const selectedIds = selectedParticipants.value.map(p => p.id);
    searchResults.value = response.data.users.filter(user => !selectedIds.includes(user.id));

  } catch (error) {
    console.error('Error searching users:', error);
    searchResults.value = [];
  } finally {
    isSearching.value = false;
  }
};

const selectUser = (user) => {
  if (!selectedParticipants.value.some(p => p.id === user.id)) {
    selectedParticipants.value.push(user);
    updateParents(selectedParticipants.value);
  }
  clearInput();
};

const removeParticipant = (participantId) => {
  selectedParticipants.value = selectedParticipants.value.filter(p => p.id !== participantId);
  updateParents(selectedParticipants.value);
};

const clearInput = () => {
  searchQuery.value = '';
  searchResults.value = [];
  showDropdown.value = false;
  highlightedIndex.value = -1;
};

const handleKeydown = (event) => {
  if (!showDropdown.value) return;

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
        selectUser(searchResults.value[highlightedIndex.value]);
      }
      break;

    case 'Escape':
      clearInput();
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
.filter-participant-selector {
  width: 100%;
}

.selected-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.participant-chip {
  display: inline-flex;
  align-items: center;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  color: white;
  gap: var(--space-2);
  line-height: 1.2;
}

.chip-text {
  font-weight: var(--font-medium);
}

.remove-chip {
  background: none;
  border: none;
  color: white;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color var(--transition-fast);
}

.remove-chip:hover {
  background-color: rgba(255, 255, 255, 0.2);
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

.user-name {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .selected-chips {
    gap: var(--space-1);
    margin-top: var(--space-2);
  }

  .participant-chip {
    font-size: var(--text-xs);
    padding: 0.15rem var(--space-2);
  }

  .search-input {
    font-size: 16px; /* Prevent iOS zoom */
  }

  .dropdown-item {
    padding: var(--space-2) var(--space-3);
  }
}
</style>
