<template>
  <span class="processed-text" v-html="processedHtml" @click="handleLinkClick"></span>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { processTextLinks } from '../utils/textProcessing';

const router = useRouter();

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  users: {
    type: Array,
    default: () => []
  }
});

const processedHtml = computed(() => {
  return processTextLinks(props.text, props.users);
});

const handleLinkClick = (event) => {
  // Handle clicks on @mention links
  if (event.target.classList.contains('mention-link')) {
    event.preventDefault();
    const href = event.target.getAttribute('href');
    if (href && href.startsWith('#/')) {
      const route = href.substring(1); // Remove the '#' prefix
      router.push(route);
    }
  }
};
</script>

<style scoped>
.processed-text :deep(.mention-link) {
  color: #0d6efd;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
}

.processed-text :deep(.mention-link:hover) {
  text-decoration: underline;
}

.processed-text :deep(.external-link) {
  color: #0d6efd;
  text-decoration: none;
}

.processed-text :deep(.external-link:hover) {
  text-decoration: underline;
}
</style>