<template>
  <div class="participant-selector">
    <label class="selector-label">Teilnehmer</label>

    <!-- Selected participants as chips -->
    <div v-if="selectedParticipants.length > 0" class="selected-chips">
      <div
        v-for="participant in selectedParticipants"
        :key="participant.id"
        class="participant-chip"
      >
        <span class="chip-text">{{ participant.username }}</span>
        <span v-if="participant.is_quick_user" class="quick-user-indicator" title="Schnell hinzugefügter Benutzer">⚡</span>
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
        placeholder="Teilnehmer suchen oder hinzufügen..."
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

        <!-- Existing users -->
        <div
          v-for="(user, index) in searchResults"
          :key="`user-${user.id}`"
          :class="['dropdown-item', { highlighted: highlightedIndex === index }]"
          @mousedown.prevent="selectUser(user)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="user-name">{{ user.username }}</span>
          <span v-if="user.is_quick_user" class="quick-user-badge">⚡</span>
        </div>

        <!-- Add new user option -->
        <div
          v-if="searchQuery.trim().length > 0 && !isSearching && !searchResults.some(u => u.username.toLowerCase() === searchQuery.trim().toLowerCase())"
          :class="['dropdown-item', 'add-new', { highlighted: highlightedIndex === searchResults.length }]"
          @mousedown.prevent="createAndSelectUser"
          @mouseenter="highlightedIndex = searchResults.length"
        >
          <span class="add-icon">+</span>
          <span class="add-text">"{{ searchQuery.trim() }}" hinzufügen</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import api from '../api';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  autofocus: {
    type: Boolean,
    default: false
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

// Initialize selected participants from props - avoid recursive updates
watch(() => props.modelValue, (newValue) => {
  selectedParticipants.value = [...newValue];
}, { immediate: true });

// Emit updates when selection changes - no deep watch to prevent recursion
const updateParents = (newSelection) => {
  emit('update:modelValue', [...newSelection]);
};

// Focus input on mount if autofocus is true
onMounted(() => {
  if (props.autofocus) {
    nextTick(() => {
      searchInput.value?.focus();
    });
  }
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

const createAndSelectUser = async () => {
  const username = searchQuery.value.trim();

  if (!username) return;

  try {
    const response = await api.post('/users/quick_create/', { username });
    const newUser = response.data;

    if (!selectedParticipants.value.some(p => p.id === newUser.id)) {
      selectedParticipants.value.push(newUser);
      updateParents(selectedParticipants.value);
    }
    clearInput();

  } catch (error) {
    console.error('Error creating user:', error);

    // Show error message (you might want to use a toast notification here)
    if (error.response?.data?.error) {
      alert(error.response.data.error);
    } else {
      alert('Fehler beim Erstellen des Benutzers');
    }
  }
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

  const totalItems = searchResults.value.length + (searchQuery.value.trim() && !searchResults.value.some(u => u.username.toLowerCase() === searchQuery.value.trim().toLowerCase()) ? 1 : 0);

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
      if (highlightedIndex.value >= 0) {
        if (highlightedIndex.value < searchResults.value.length) {
          selectUser(searchResults.value[highlightedIndex.value]);
        } else {
          createAndSelectUser();
        }
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
.participant-selector {
  width: 100%;
}

.selector-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

.selected-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  min-height: 1.5rem;
}

.participant-chip {
  display: inline-flex;
  align-items: center;
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
  color: #1565c0;
  gap: 0.5rem;
}

.chip-text {
  font-weight: 500;
}

.quick-user-indicator {
  font-size: 0.8rem;
  opacity: 0.8;
}

.remove-chip {
  background: none;
  border: none;
  color: #1565c0;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.remove-chip:hover {
  background-color: rgba(21, 101, 192, 0.1);
}

.input-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.dropdown-item:hover,
.dropdown-item.highlighted {
  background-color: #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item.loading {
  cursor: default;
  color: #666;
  font-style: italic;
}

.user-name {
  font-weight: 500;
}

.quick-user-badge {
  font-size: 0.8rem;
  opacity: 0.7;
}

.dropdown-item.add-new {
  color: #42b983;
  font-weight: 500;
  border-top: 1px solid #e0e0e0;
}

.dropdown-item.add-new:hover,
.dropdown-item.add-new.highlighted {
  background-color: #f0f9f4;
}

.add-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.add-text {
  flex: 1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .selected-chips {
    gap: 0.25rem;
  }

  .participant-chip {
    font-size: 0.8rem;
    padding: 0.2rem 0.6rem;
  }

  .search-input {
    padding: 0.7rem;
  }

  .dropdown-item {
    padding: 0.6rem 0.8rem;
  }
}
</style>