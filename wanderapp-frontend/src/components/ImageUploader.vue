<template>
  <div class="uploader-container">
    <button @click="openUppyModal" class="upload-button">
      + Foto hinzufügen
    </button>
    <div ref="uppyContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Uppy from '@uppy/core';
import Dashboard from '@uppy/dashboard';
import XHRUpload from '@uppy/xhr-upload';

// IHRE KORREKTEN CSS-IMPORTS WERDEN NUN VERWENDET
import '@uppy/core/css/style.min.css';
import '@uppy/dashboard/css/style.min.css';

const props = defineProps({
  stageId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(['upload-success']);

const uppyContainer = ref(null);
let uppy = null;

const openUppyModal = () => {
  if (uppy) {
    const dashboard = uppy.getPlugin('Dashboard');
    if (dashboard) {
      dashboard.openModal();
    }
  }
};

onMounted(() => {
  const token = localStorage.getItem('accessToken');

  uppy = new Uppy({
    autoProceed: true,
    restrictions: {
      maxFileSize: 20 * 1024 * 1024, // 20 MB
      allowedFileTypes: ['image/jpeg', 'image/png'],
    },
  })
  .use(Dashboard, {
    target: uppyContainer.value,
    inline: false,
    closeModalOnClickOutside: true,
    proudlyDisplayPoweredByUppy: false,
    note: 'Nur JPEG oder PNG, max. 20 MB pro Bild',
  })
  .use(XHRUpload, {
    endpoint: `/api/stages/${props.stageId}/upload_photos/`,
    fieldName: 'photos',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })
  .on('complete', (result) => {
    if (result.successful.length > 0) {
      emit('upload-success');
    }
    if (result.failed.length > 0) {
      console.error('Upload error! Failed files:', result.failed);
    }
  });
});

onUnmounted(() => {
  if (uppy) {
    uppy.destroy();
  }
});
</script>

<style scoped>
.upload-button {
  cursor: pointer;
  font-weight: 500;
  color: #007bff;
  padding: 0.5rem 1rem;
  border: 1px solid #007bff;
  border-radius: 5px;
  background-color: #ffffff;
  transition: all 0.2s ease-in-out;
}
.upload-button:hover {
  background-color: #007bff;
  color: white;
}
</style>