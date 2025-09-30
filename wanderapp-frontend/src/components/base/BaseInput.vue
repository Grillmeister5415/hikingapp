<template>
  <div class="input-wrapper">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="input-required">*</span>
    </label>

    <input
      v-if="type !== 'textarea' && type !== 'select'"
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :min="min"
      :max="max"
      :autocomplete="autocomplete"
      :class="inputClasses"
      @input="handleInput"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    />

    <textarea
      v-else-if="type === 'textarea'"
      :id="id"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      :class="inputClasses"
      @input="handleInput"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    ></textarea>

    <select
      v-else-if="type === 'select'"
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :class="inputClasses"
      @change="handleChange"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    >
      <slot />
    </select>

    <p v-if="helperText && !error" class="input-helper">{{ helperText }}</p>
    <p v-if="error" class="input-error">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'text'
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  rows: {
    type: Number,
    default: 4
  },
  min: {
    type: [String, Number],
    default: undefined
  },
  max: {
    type: [String, Number],
    default: undefined
  },
  autocomplete: {
    type: String,
    default: undefined
  }
});

const emit = defineEmits(['update:modelValue', 'blur', 'focus']);

const inputClasses = computed(() => [
  'input-field',
  {
    'input-error-state': props.error,
    'input-disabled': props.disabled
  }
]);

const handleInput = (event) => {
  emit('update:modelValue', event.target.value);
};

const handleChange = (event) => {
  emit('update:modelValue', event.target.value);
};
</script>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  margin-bottom: var(--space-4);
}

.input-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  display: block;
}

.input-required {
  color: var(--color-error);
  margin-left: var(--space-1);
}

.input-field {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  font-family: var(--font-base);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border-medium);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  width: 100%;
}

.input-field:focus {
  outline: none;
  border-color: var(--color-blue);
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}

.input-field:disabled,
.input-disabled {
  background-color: var(--color-bg-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}

.input-field::placeholder {
  color: var(--color-text-tertiary);
}

.input-error-state {
  border-color: var(--color-error);
}

.input-error-state:focus {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.input-helper {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin-top: var(--space-2);
  margin-bottom: 0;
}

.input-error {
  font-size: var(--text-xs);
  color: var(--color-error);
  margin-top: var(--space-2);
  margin-bottom: 0;
}

textarea.input-field {
  resize: vertical;
  min-height: 100px;
  line-height: var(--leading-relaxed);
}

select.input-field {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236c757d' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--space-3) center;
  padding-right: var(--space-8);
}

/* Mobile-specific: ensure date inputs prevent iOS zoom and increase spacing */
@media (max-width: 768px) {
  .input-wrapper {
    margin-bottom: var(--space-5); /* Increase from space-4 (16px) to space-5 (20px) */
  }

  input[type="date"].input-field {
    font-size: 16px; /* Prevent iOS auto-zoom */
  }
}
</style>