<template>
  <div class="multiselect" ref="multiselect">
    <button type="button" @click="isOpen = !isOpen" class="multiselect-button">
      {{ buttonLabel }}
      <span class="arrow" :class="{ rotated: isOpen }">▼</span>
    </button>
    <div v-if="isOpen" class="multiselect-panel">
      <ul>
        <li v-for="option in options" :key="option.id">
          <label>
            <input type="checkbox" :value="option.id" :checked="modelValue.includes(option.id)" @change="toggleOption(option.id)" />
            {{ option.username }}
          </label>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  options: {
    type: Array,
    required: true,
  },
  modelValue: { // This is the v-model value
    type: Array,
    required: true,
  },
  placeholder: {
    type: String,
    default: 'Auswählen...'
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const multiselect = ref(null);

const buttonLabel = computed(() => {
  if (props.modelValue.length === 0) {
    return props.placeholder;
  }
  if (props.modelValue.length === 1) {
    const selected = props.options.find(opt => opt.id === props.modelValue[0]);
    return selected ? selected.username : '';
  }
  return `${props.modelValue.length} ausgewählt`;
});

const toggleOption = (optionId) => {
  const newSelection = [...props.modelValue];
  const index = newSelection.indexOf(optionId);

  if (index > -1) {
    newSelection.splice(index, 1); // Remove if already selected
  } else {
    newSelection.push(optionId); // Add if not selected
  }
  emit('update:modelValue', newSelection);
};

// Logic to close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (multiselect.value && !multiselect.value.contains(event.target)) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.multiselect {
  position: relative;
  width: 200px;
}
.multiselect-button {
  width: 100%;
  padding: 0.7rem;
  border-radius: 8px;
  border: 1px solid #ccc;
  background-color: white;
  text-align: left;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.arrow {
  transition: transform 0.2s ease;
}
.arrow.rotated {
  transform: rotate(180deg);
}
.multiselect-panel {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: white;
  z-index: 10;
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
li label {
  display: block;
  padding: 0.5rem 1rem;
  cursor: pointer;
}
li label:hover {
  background-color: #f0f0f0;
}
input[type="checkbox"] {
  margin-right: 0.5rem;
}
</style>