<template>
  <div>
    <div v-if="isLoading">Lade Trip-Details...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="trip">
      <router-link to="/">&larr; Zurück zur Übersicht</router-link>
      <div class="header">
        <h1>{{ trip.name }}</h1>
        <div class="controls">
          <router-link v-if="currentUser && currentUser.id === trip.creator.id" :to="`/trip/${trip.id}/edit`" class="btn btn-edit-trip">Edit Trip</router-link>
          <router-link :to="`/trip/${trip.id}/add-stage`" class="btn btn-add-stage">Neue Etappe</router-link>
        </div>
      </div>
      <p v-if="trip.creator" class="creator"><em>Erstellt von: {{ trip.creator.username }}</em></p>
      <p class="description"><em>{{ trip.description }}</em></p>

      <div class="trip-summary-card">
        <div class="trip-stats-detail">
          <div class="stat-item">
            <span class="stat-value">{{ formatDuration(trip.total_duration) }}</span>
            <label>Gesamtdauer</label>
          </div>
          <span class="stat-separator">|</span>
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(trip.total_distance) }} <small>km</small></span>
          </div>
          <span class="stat-separator">|</span>
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(trip.total_gain) }} <small>m</small></span>
            <label>Aufstieg</label>
          </div>
          <span class="stat-separator">|</span>
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(trip.total_loss) }} <small>m</small></span>
            <label>Abstieg</label>
          </div>
        </div>
        <div class="social-details">
          <div class="participants" v-if="trip.participants.length">
            <strong>Teilnehmer:</strong>
            <span v-for="p in trip.participants" :key="p.id" class="participant-tag">{{ p.username }}</span>
          </div>
          <div class="huts" v-if="trip.huts && trip.huts.length">
            <strong>Hütten:</strong>
            <span v-for="hut in trip.huts" :key="hut.id" class="hut-tag">{{ hut.name }}</span>
          </div>
        </div>
      </div>
      
      <hr>
      
      <h2>Etappen</h2>
      <div v-if="!trip.stages.length" class="no-stages">
        <p>Für diesen Trip wurden noch keine Etappen hinzugefügt.</p>
      </div>
      
      <div v-for="stage in trip.stages" :key="stage.id" class="stage-card">
        <div class="stage-header">
          <h3>{{ stage.name }} ({{ formatDate(stage.date) }})</h3>
          <div class="stage-controls" v-if="currentUser && stage && stage.creator && currentUser.id === stage.creator.id">
            <router-link :to="`/stage/${stage.id}/edit`" class="btn-edit">Bearbeiten ✏️</router-link>
            <button @click="handleDeleteStage(stage.id)" class="btn-delete" title="Etappe löschen">🗑️</button>
          </div>
        </div>
        
        <p class="description">{{ stage.description }}</p>

        <div class="stage-stats">
            <div class="stat-item">
              <span>{{ formatDuration(stage.calculated_duration || stage.manual_duration) }}</span>
              <label>Dauer</label>
            </div>
            <span class="stat-separator">|</span>
            <div class="stat-item">
              <span>{{ (stage.calculated_length_km || stage.manual_length_km || '0') }} <small>km</small></span>
            </div>
            <span class="stat-separator">|</span>
            <div class="stat-item">
              <span>{{ formatNumber(stage.calculated_elevation_gain || stage.manual_elevation_gain) }} <small>m</small></span>
               <label>Aufstieg</label>
            </div>
            <span class="stat-separator">|</span>
             <div class="stat-item">
              <span>{{ formatNumber(stage.calculated_elevation_loss) }} <small>m</small></span>
               <label>Abstieg</label>
            </div>
            <span class="stat-separator" v-if="stage.external_link">|</span>
            <div class="stat-item" v-if="stage.external_link">
              <a :href="stage.external_link" target="_blank" rel="noopener noreferrer">
                {{ formatLink(stage.external_link) }} 🔗
              </a>
            </div>
        </div>

        <div v-if="stage.track">
          <HikeMap :stageId="stage.id" />
        </div>
        <div v-else class="no-track">
          <p>Für diese Etappe sind keine GPX-Daten vorhanden.</p>
        </div>

        <div class="photo-section">
          <h4>Fotos ({{ stage.photos ? stage.photos.length : 0 }})</h4>
          
          <div v-if="stage.photos && stage.photos.length > 0" class="photo-gallery">
            <div v-for="(photo, index) in stage.photos" :key="photo.id" class="photo-wrapper">
              <div class="thumbnail-container" @click="openLightbox(stage.photos, index)">
                <img :src="photo.thumbnail" :alt="photo.caption || 'Etappen-Foto'" loading="lazy" />
              </div>
              <button 
                v-if="currentUser && currentUser.id === photo.creator.id" 
                @click.stop="handleDeletePhoto(photo.id)" 
                class="btn-delete-photo" 
                title="Foto löschen"
              >
                &times;
              </button>
            </div>
          </div>
          <p v-else><em>Für diese Etappe wurden noch keine Fotos hochgeladen.</em></p>

          <ImageUploader 
            v-if="currentUser && stage && stage.creator && currentUser.id === stage.creator.id"
            :stageId="stage.id" 
            @upload-success="handleUploadSuccess" 
          />
        </div>

        <CommentSection 
          :stageId="stage.id" 
          :initialComments="stage.comments"
          :stageCreatorId="stage.creator.id"
          @comment-added="fetchTripData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';
import HikeMap from './HikeMap.vue';
import CommentSection from './CommentSection.vue';
import { currentUser } from '../store';
import ImageUploader from './ImageUploader.vue';
import PhotoSwipeLightbox from 'photoswipe/lightbox';
import 'photoswipe/style.css';

const route = useRoute();
const trip = ref(null);
const isLoading = ref(true);
const error = ref(null);
let lightbox = null;

const openLightbox = (photos, startIndex) => {
  if (!photos || photos.length === 0) return;

  const dataSource = photos.map(photo => ({
    src: photo.original,
    width: photo.original_width,
    height: photo.original_height,
    alt: photo.caption || 'Etappen-Foto'
  }));

  if (lightbox) {
    lightbox.destroy();
  }

  lightbox = new PhotoSwipeLightbox({
    dataSource: dataSource,
    pswpModule: () => import('photoswipe'),
    initialIndex: startIndex,
  });

  lightbox.init();
  lightbox.loadAndOpen(startIndex);
};

onUnmounted(() => {
  if (lightbox) {
    lightbox.destroy();
    lightbox = null;
  }
});

const fetchTripData = async () => {
  const tripId = route.params.id;
  try {
    isLoading.value = true;
    error.value = null;
    const response = await api.get(`/trips/${tripId}/`);
    trip.value = response.data;
  } catch (err) {
    error.value = "Fehler beim Laden des Trips.";
  } finally {
    isLoading.value = false;
  }
};

const handleUploadSuccess = async () => {
  await fetchTripData();
};

const handleDeletePhoto = async (photoId) => {
  if (window.confirm("Sind Sie sicher, dass Sie dieses Foto löschen möchten?")) {
    try {
      await api.delete(`/photos/${photoId}/`);
      await fetchTripData();
    } catch (err) {
      alert("Fehler beim Löschen des Fotos.");
    }
  }
};

onMounted(fetchTripData);

const formatLink = (url) => {
  try {
    const domain = new URL(url).hostname;
    return domain.replace('www.', '');
  } catch (e) {
    return "Tour ansehen";
  }
};

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString('de-CH');
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('de-DE', options);
};

const formatDuration = (duration) => {
  if (!duration) return '0h 0m';
  let totalSeconds = 0;
  if (typeof duration === 'string') {
    if (duration.includes('day')) {
      const dayMatch = duration.match(/(\d+)\s*day/);
      const days = dayMatch ? parseInt(dayMatch[1], 10) : 0;
      totalSeconds += days * 86400;
      const timeMatch = duration.match(/(\d{1,2}):(\d{2}):(\d{2})/);
      if (timeMatch) {
        totalSeconds += parseInt(timeMatch[1], 10) * 3600;
        totalSeconds += parseInt(timeMatch[2], 10) * 60;
        totalSeconds += parseInt(timeMatch[3], 10);
      }
    } else {
      const timeParts = duration.split(':');
      if (timeParts.length >= 2) {
        totalSeconds += parseInt(timeParts[0], 10) * 3600;
        totalSeconds += parseInt(timeParts[1], 10) * 60;
        if (timeParts.length === 3) {
          totalSeconds += parseInt(timeParts[2], 10);
        }
      }
    }
  } else if (typeof duration === 'number') {
    totalSeconds = duration;
  }
  if (isNaN(totalSeconds)) return '0h 0m';
  const totalHours = Math.floor(totalSeconds / 3600);
  const remainingMinutes = Math.round((totalSeconds % 3600) / 60);
  return `${totalHours}h ${remainingMinutes}m`;
};

const handleDeleteStage = async (stageId) => {
  if (window.confirm("Sind Sie sicher, dass Sie diese Etappe löschen möchten?")) {
    try {
      await api.delete(`/stages/${stageId}/`);
      fetchTripData();
    } catch (err) {
      alert("Fehler beim Löschen der Etappe. Sie sind möglicherweise nicht der Ersteller.");
    }
  }
};
</script>

<style scoped>
.description { white-space: pre-wrap; word-break: break-word; margin-top: 0; }
.creator { font-size: 0.9rem; color: #6c757d; }
.header { display: flex; justify-content: space-between; align-items: center; margin: 1rem 0; }
.header .controls { display: flex; gap: 1rem; }
.btn { display: inline-block; padding: 0.8rem 1.5rem; text-decoration: none; border-radius: 8px; font-weight: bold; }
.btn-add-stage { background-color: #0d6efd; color: white; }
.btn-edit-trip { background-color: #ffc107; color: #212529; }
a { text-decoration: none; color: #0d6efd; }
a:hover { text-decoration: underline; }
a[href="/"] { display: inline-block; margin-bottom: 1rem; }
.trip-summary-card { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; }
.trip-stats-detail { display: flex; justify-content: space-around; padding-bottom: 1rem; margin-bottom: 1rem; }
.social-details { border-top: 1px solid #e0e0e0; padding-top: 1rem; font-size: 0.9rem; }
.stat-item { text-align: center; }
.stat-item .stat-value { font-size: 1.5rem; font-weight: 500; }
.stat-item .stat-value small { font-size: 1rem; font-weight: 400; color: #6c757d; margin-left: 0.25rem; }
.stat-item label { font-size: 0.8rem; color: #6c757d; display: block; margin-top: -5px; }
.stat-separator { color: #e0e0e0; font-size: 1.5rem; }
.participants, .huts { margin-bottom: 0.5rem; }
.participant-tag { background-color: #e9ecef; color: #495057; }
.hut-tag { background-color: #d1ecf1; color: #0c5460; }
.participant-tag, .hut-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; margin-right: 0.5rem; margin-top: 0.25rem; }
.stage-card { border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; }
.stage-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.stage-controls { display: flex; align-items: center; gap: 0.5rem; }
.btn-edit { padding: 0.4rem 0.8rem; border: 1px solid #6c757d; color: #6c757d; border-radius: 5px; font-size: 0.9rem; }
.btn-delete { background-color: transparent; border: none; cursor: pointer; font-size: 1.2rem; }
.stage-stats { display: flex; align-items: baseline; gap: 0.75rem; margin: 1rem 0; padding-top: 1rem; border-top: 1px solid #f0f0f0; }
.stage-stats .stat-item { text-align: left; }
.stage-stats .stat-item span { font-size: 1.2rem; font-weight: 500; }
.stage-stats .stat-item span small { font-size: 0.8rem; }
.no-stages, .no-track { margin-top: 2rem; padding: 2rem; background-color: #f8f9fa; border-radius: 8px; text-align: center; color: #6c757d; }
.photo-section { margin-top: 1.5rem; border-top: 1px solid #f0f0f0; padding-top: 1.5rem; }
.photo-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.5rem; margin-bottom: 1.5rem; }
.photo-wrapper { position: relative; }
.thumbnail-container { cursor: pointer; width: 100%; aspect-ratio: 1 / 1; }
.photo-gallery img { width: 100%; height: 100%; object-fit: cover; border-radius: 8px; }
.btn-delete-photo { position: absolute; top: 5px; right: 5px; background-color: rgba(0, 0, 0, 0.5); color: white; border: none; border-radius: 50%; width: 24px; height: 24px; font-size: 16px; line-height: 24px; text-align: center; cursor: pointer; opacity: 0; transition: opacity 0.2s ease; }
.photo-wrapper:hover .btn-delete-photo { opacity: 1; }
.error-message { color: red; }

/* iPhone/Touch: Buttons ohne Hover sichtbar machen */
@media (hover: none) and (pointer: coarse) {
  .btn-add-photo,
  .btn-delete-photo {
    opacity: 1 !important;
  }
}

/* Responsive layout fixes */
@media (max-width: 600px) {
  /* Trip + Stage header: stack title and buttons */
  .trip-header,
  .stage-header,
  .header {
    flex-direction: column;   /* title above, buttons below */
    align-items: flex-start;
    gap: .5rem;
  }

  .trip-controls,
  .stage-controls,
  .controls {
    display: flex;
    flex-wrap: wrap;          /* allow wrapping if two buttons don't fit */
    gap: .5rem;
    width: 100%;
  }

  /* Stats section: wrap nicely */
  .trip-stats {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem 1rem;
  }

  .trip-stats > div {
    min-width: 45%;           /* 2 columns on small screens */
  }
  
  /* Stage stats: keep on one line but adjust spacing */
  .stage-stats {
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  
  .stage-stats .stat-item span {
    font-size: 1rem;
  }
}

</style>