<template>
  <div>
    <div v-if="isLoading">Lade Trip-Details...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="trip">
      <div class="header-with-controls">
        <h1>{{ trip.name }}</h1>
        <div class="top-controls">
          <BaseButton tag="router-link" :to="tripListRoute" variant="secondary" size="small">
            <span class="btn-text-desktop">&larr; Zurück zur Übersicht</span>
            <span class="btn-text-mobile">Zurück</span>
          </BaseButton>
          <BaseButton v-if="currentUser && currentUser.id === trip.creator.id" tag="router-link" :to="`/trip/${trip.id}/edit`" variant="secondary" size="small">
            <span class="btn-text-desktop">Edit Trip</span>
            <span class="btn-text-mobile">Edit</span>
          </BaseButton>
          <BaseButton tag="router-link" :to="getAddStageRoute()" variant="primary" size="small">
            <span class="btn-text-desktop">{{ getAddStageLabel() }}</span>
            <span class="btn-text-mobile">{{ getAddStageLabelMobile() }}</span>
          </BaseButton>
        </div>
      </div>
      <p v-if="trip.creator" class="creator"><em>Erstellt von: {{ trip.creator.username }}</em></p>
      <p class="description"><em><ProcessedText :text="trip.description" :users="getTripUsers(trip)" /></em></p>

      <div class="trip-summary-card">
        <!-- Surf Trip Overview -->
        <div v-if="trip.activity_type === 'SURFING'" class="trip-stats-detail surf-overview">
          <div class="stat-item">
            <span class="stat-value">{{ formatDuration(trip.total_surf_time) }}</span>
            <label>Total Surftime</label>
          </div>
          <span class="stat-separator">|</span>
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(trip.total_wave_count) }}</span>
            <label>Total Wavecount</label>
          </div>
          <span class="stat-separator">|</span>
          <div class="stat-item">
            <span class="stat-value">{{ trip.country_display }}</span>
            <label>Country</label>
          </div>
          <span class="stat-separator">|</span>
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(trip.unique_surf_spots_count) }}</span>
            <label>Spots Surfed</label>
          </div>
        </div>
        
        <!-- Hiking/Running Trip Overview -->
        <div v-else class="trip-stats-detail">
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
            <router-link v-for="p in trip.participants" :key="p.id" :to="`/dashboard/${p.id}`" class="user-link">
              <BaseBadge variant="default">{{ p.username }}</BaseBadge>
            </router-link>
          </div>
          <!-- Show huts for hiking trips -->
          <div class="huts" v-if="trip.activity_type === 'HIKING' && trip.huts && trip.huts.length">
            <strong>Hütten:</strong>
            <template v-for="hut in trip.huts" :key="hut.id">
              <a v-if="hut.link" :href="hut.link" target="_blank" @click.stop>
                <BaseBadge variant="info">{{ hut.name }}</BaseBadge>
              </a>
              <BaseBadge v-else variant="info">{{ hut.name }}</BaseBadge>
            </template>
          </div>

          <!-- Show surf spots for surf trips -->
          <div class="surf-spots" v-if="trip.activity_type === 'SURFING' && getSurfSpotsList().length">
            <strong>🏄‍♂️ Surf Spots:</strong>
            <BaseBadge v-for="spot in getSurfSpotsList()" :key="spot.name" variant="surfing">{{ spot.display }}</BaseBadge>
          </div>
        </div>
      </div>
      
      <hr>
      
      <h2 v-if="trip.activity_type === 'SURFING'">Surfs</h2>
      <h2 v-else>Etappen</h2>
      <div v-if="!trip.stages.length" class="no-stages">
        <p v-if="trip.activity_type === 'SURFING'">Für diesen Trip wurden noch keine Surfs hinzugefügt.</p>
        <p v-else>Für diesen Trip wurden noch keine Etappen hinzugefügt.</p>
      </div>
      
      <div v-for="stage in trip.stages" :key="stage.id" class="stage-card" :class="`activity-${stage.activity_type?.toLowerCase()}`">
        <div class="stage-header">
          <div class="stage-title">
            <span class="activity-icon">{{ getActivityIcon(stage.activity_type) }}</span>
            <div class="title-content">
              <h3>{{ stage.name }}</h3>
              <div class="stage-date">{{ formatDate(stage.date) }}</div>
            </div>
          </div>
          <div class="stage-controls" v-if="currentUser && stage && stage.creator && currentUser.id === stage.creator.id">
            <BaseButton tag="router-link" :to="getStageEditRoute(stage)" variant="ghost" size="small">Bearbeiten ✏️</BaseButton>
            <BaseButton @click="handleDeleteStage(stage.id)" variant="ghost" size="small" title="Etappe löschen">🗑️</BaseButton>
          </div>
        </div>
        
        <p class="description"><ProcessedText :text="stage.description" :users="getStageUsers(stage, trip)" /></p>

        <!-- Hiking/Running Stats -->
        <div v-if="stage.activity_type !== 'SURFING'" class="stage-stats">
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

        <!-- Surf Stats -->
        <div v-if="stage.activity_type === 'SURFING'" class="stage-stats surf-stats">
            <div class="stat-item">
              <span>{{ formatDuration(stage.time_in_water) }}</span>
              <label>Time in water</label>
            </div>
            <span class="stat-separator" v-if="stage.surf_spot">|</span>
            <div class="stat-item" v-if="stage.surf_spot">
              <span>{{ stage.surf_spot }}</span>
              <label>Surf Spot</label>
            </div>
            <span class="stat-separator" v-if="stage.wave_height">|</span>
            <div class="stat-item" v-if="stage.wave_height">
              <span>{{ stage.wave_height }} <small>m</small></span>
              <label>Wave height</label>
            </div>
            <span class="stat-separator" v-if="stage.wave_quality">|</span>
            <div class="stat-item" v-if="stage.wave_quality">
              <span>{{ '★'.repeat(stage.wave_quality) }}</span>
              <label>Quality</label>
            </div>
            <span class="stat-separator" v-if="stage.swell_direction">|</span>
            <div class="stat-item" v-if="stage.swell_direction">
              <span>{{ getDirectionLabel(stage.swell_direction) }}</span>
              <label>Swell</label>
            </div>
            <span class="stat-separator" v-if="stage.wind_direction">|</span>
            <div class="stat-item" v-if="stage.wind_direction">
              <span>{{ getDirectionLabel(stage.wind_direction) }}</span>
              <label>Wind</label>
            </div>
            <span class="stat-separator" v-if="stage.wave_energy">|</span>
            <div class="stat-item" v-if="stage.wave_energy">
              <span>{{ stage.wave_energy }}</span>
              <label>Wave energy</label>
            </div>
            <span class="stat-separator" v-if="stage.external_link">|</span>
            <div class="stat-item" v-if="stage.external_link">
              <a :href="stage.external_link" target="_blank" rel="noopener noreferrer">
                {{ formatLink(stage.external_link) }} 🔗
              </a>
            </div>
        </div>

        <!-- Additional Surf Details -->
        <div v-if="stage.activity_type === 'SURFING'" class="surf-details">
          <div v-if="stage.surfboard_used" class="detail-item">
            <strong>Surfboard:</strong> {{ stage.surfboard_used }}
          </div>
          <div v-if="stage.waves_caught" class="detail-item">
            <strong>Waves caught:</strong> {{ stage.waves_caught }}
          </div>
          <div v-if="stage.water_temperature" class="detail-item">
            <strong>Water temperature:</strong> {{ stage.water_temperature }}°C
          </div>
          <div v-if="stage.tide_stage || stage.tide_movement" class="detail-item">
            <strong>Tides:</strong> 
            <span v-if="stage.tide_stage">{{ getTideLabel(stage.tide_stage) }}</span>
            <span v-if="stage.tide_stage && stage.tide_movement"> - </span>
            <span v-if="stage.tide_movement">{{ getTideMovementLabel(stage.tide_movement) }}</span>
          </div>
          <div v-if="stage.swell_direction" class="detail-item">
            <strong>Swell direction:</strong> {{ getDirectionLabel(stage.swell_direction) }}
          </div>
          <div v-if="stage.wind_direction" class="detail-item">
            <strong>Wind direction:</strong> {{ getDirectionLabel(stage.wind_direction) }}
          </div>
          <div v-if="stage.wave_energy" class="detail-item">
            <strong>Wave energy:</strong> {{ stage.wave_energy }}
          </div>
        </div>

        <div v-if="stage.activity_type !== 'SURFING' && stage.track">
          <HikeMap :stageId="stage.id" />
        </div>
        <div v-else-if="stage.activity_type !== 'SURFING'" class="no-track">
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
          :trip="trip"
          @comment-added="fetchTripData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';
import { getTripListRoute } from '../utils/navigation.js';
import HikeMap from './HikeMap.vue';
import CommentSection from './CommentSection.vue';
import { currentUser } from '../store';
import ImageUploader from './ImageUploader.vue';
import ProcessedText from './ProcessedText.vue';
import { getTripUsers, getStageUsers } from '../utils/textProcessing.js';
import PhotoSwipeLightbox from 'photoswipe/lightbox';
import 'photoswipe/style.css';
import BaseButton from './base/BaseButton.vue';
import BaseBadge from './base/BaseBadge.vue';

const route = useRoute();
const trip = ref(null);
const isLoading = ref(true);

// Computed property for trip list navigation
const tripListRoute = computed(() => getTripListRoute());
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

// Update document title when trip data loads
watch(trip, (newTrip) => {
  if (newTrip && newTrip.name) {
    document.title = `${newTrip.name} - WanderApp`;
  }
});

const formatLink = (url) => {
  try {
    const domain = new URL(url).hostname;
    return domain.replace('www.', '');
  } catch (e) {
    return "Tour ansehen";
  }
};

const getActivityIcon = (activityType) => {
  switch (activityType) {
    case 'HIKING': return '🥾';
    case 'RUNNING': return '🏃‍♂️';
    case 'SURFING': return '🏄‍♂️';
    default: return '🥾';
  }
};

// Get the correct route for adding a stage based on trip's activity type
const getAddStageRoute = () => {
  if (!trip.value) return `/trip/${route.params.id}/add-stage`;
  
  switch (trip.value.activity_type) {
    case 'HIKING':
      return `/trip/${trip.value.id}/add-stage`;
    case 'SURFING':
      return `/trip/${trip.value.id}/add-surf-stage`;
    default:
      return `/trip/${trip.value.id}/add-stage`;
  }
};

// Get the correct label for the add stage button
const getAddStageLabel = () => {
  if (!trip.value) return 'Add Stage';

  switch (trip.value.activity_type) {
    case 'HIKING':
      return 'Add Hiking Stage';
    case 'SURFING':
      return 'Add Surf';
    default:
      return 'Add Stage';
  }
};

// Get the correct label for mobile
const getAddStageLabelMobile = () => {
  if (!trip.value) return 'Add Stage';

  switch (trip.value.activity_type) {
    case 'HIKING':
      return 'Add Hike';
    case 'SURFING':
      return 'Add Surf';
    default:
      return 'Add Stage';
  }
};

// Get the correct edit route based on stage activity type
const getStageEditRoute = (stage) => {
  if (!stage) return `/stage/${stage.id}/edit`;
  
  switch (stage.activity_type) {
    case 'SURFING':
      return `/surf-stage/${stage.id}/edit`;
    case 'HIKING':
    default:
      return `/stage/${stage.id}/edit`;
  }
};

const getTideLabel = (tideStage) => {
  switch (tideStage) {
    case 'LOW': return 'Low tide';
    case 'MID': return 'Mid tide';
    case 'HIGH': return 'High tide';
    default: return tideStage;
  }
};

const getTideMovementLabel = (tideMovement) => {
  switch (tideMovement) {
    case 'RISING': return 'Rising';
    case 'FALLING': return 'Falling';
    default: return tideMovement;
  }
};

// Helper function to get direction label
const getDirectionLabel = (direction) => {
  const directions = {
    'N': 'North',
    'NE': 'Northeast', 
    'E': 'East',
    'SE': 'Southeast',
    'S': 'South',
    'SW': 'Southwest',
    'W': 'West',
    'NW': 'Northwest',
  };
  return directions[direction] || direction;
};

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString('de-CH');
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
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

// Helper function to get list of unique surf spots with counts from stages
const getSurfSpotsList = () => {
  if (!trip.value || !trip.value.stages) return [];
  
  const surfStages = trip.value.stages
    .filter(stage => stage.activity_type === 'SURFING' && stage.surf_spot && stage.surf_spot.trim())
    .map(stage => stage.surf_spot.trim());
  
  // Count occurrences of each surf spot
  const spotCounts = {};
  surfStages.forEach(spot => {
    spotCounts[spot] = (spotCounts[spot] || 0) + 1;
  });
  
  // Return array of objects with spot name and count
  return Object.entries(spotCounts).map(([spot, count]) => ({
    name: spot,
    count: count,
    display: count > 1 ? `${spot} (${count})` : spot
  }));
};
</script>

<style scoped>
/* TripDetail - Migrated to Design System */
.description {
  white-space: pre-wrap;
  word-break: break-word;
  margin-top: 0;
}

.creator {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: var(--space-4) 0;
  min-width: 0;
}

.header h1 {
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  min-width: 0;
  margin: 0;
}

.header .controls {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  flex-wrap: wrap;
}

a {
  text-decoration: none;
  color: var(--color-blue);
}

a:hover {
  text-decoration: underline;
}

.header-with-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: var(--space-4) 0;
  gap: var(--space-4);
}

.header-with-controls h1 {
  margin: 0;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  min-width: 0;
  flex: 1;
}

.top-controls {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.btn-text-mobile {
  display: none;
}

.btn-text-desktop {
  display: inline;
}

/* Trip summary card */
.trip-summary-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin: var(--space-6) 0;
}

.trip-stats-detail {
  display: flex;
  justify-content: space-around;
  padding-bottom: var(--space-4);
  margin-bottom: var(--space-4);
  min-width: 0;
  overflow: hidden;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.social-details {
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--space-4);
  font-size: var(--text-sm);
  min-width: 0;
  overflow: hidden;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-medium);
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}

.stat-item .stat-value small {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  color: var(--color-text-secondary);
  margin-left: var(--space-1);
}

.stat-item label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  display: block;
  margin-top: -5px;
}

.stat-separator {
  color: var(--color-border-light);
  font-size: var(--text-2xl);
}

.participants,
.huts,
.surf-spots {
  margin-bottom: var(--space-2);
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3); /* Badge spacing for better tap targets */
  align-items: center;
}
/* Stage cards */
.stage-card {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-top: var(--space-6);
  min-width: 0;
  overflow: hidden;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  min-width: 0;
}

.stage-controls {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.stage-stats {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  margin: var(--space-4) 0;
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border-light);
  min-width: 0;
  overflow: hidden;
}

.stage-stats .stat-item {
  text-align: left;
  min-width: 0;
  flex-shrink: 1;
}

.stage-stats .stat-item span {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}

.stage-stats .stat-item span small {
  font-size: var(--text-xs);
}

.no-stages,
.no-track {
  margin-top: var(--space-8);
  padding: var(--space-8);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  text-align: center;
  color: var(--color-text-secondary);
}
/* Photo section */
.photo-section {
  margin-top: var(--space-6);
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--space-6);
}

.photo-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.photo-wrapper {
  position: relative;
}

.thumbnail-container {
  cursor: pointer;
  width: 100%;
  aspect-ratio: 1 / 1;
}

.photo-gallery img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.btn-delete-photo {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  line-height: 24px;
  text-align: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.photo-wrapper:hover .btn-delete-photo {
  opacity: 1;
}

.error-message {
  color: var(--color-error);
}

/* Activity-specific styling */
.stage-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  flex: 1;
}

.title-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.title-content h3 {
  margin-bottom: var(--space-1);
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  margin-top: 0;
}

.stage-date {
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  color: var(--color-text-secondary);
  margin-top: 0;
}

.activity-icon {
  font-size: var(--text-2xl);
  margin-right: var(--space-2);
}

.activity-hiking {
  border-left: 4px solid var(--color-hiking);
}

.activity-running {
  border-left: 4px solid var(--color-running);
}

.activity-surfing {
  border-left: 4px solid var(--color-surfing);
}

.surf-details {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background-color: rgba(32, 178, 170, 0.05);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-surfing);
}

.detail-item {
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
}

.detail-item:last-child {
  margin-bottom: 0;
}

.surf-stats {
  border-top-color: var(--color-surfing);
}

.surf-overview {
  background: linear-gradient(135deg, rgba(32, 178, 170, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin: calc(-1 * var(--space-4));
  margin-bottom: var(--space-4);
}

/* iPhone/Touch: Buttons ohne Hover sichtbar machen */
@media (hover: none) and (pointer: coarse) {
  .btn-add-photo,
  .btn-delete-photo {
    opacity: 1 !important;
  }
}

/* Responsive layout fixes */
@media (max-width: 600px) {
  /* Show mobile text, hide desktop text */
  .btn-text-mobile {
    display: inline;
  }

  .btn-text-desktop {
    display: none;
  }

  /* Header with controls: stack buttons above title on mobile */
  .header-with-controls {
    flex-direction: column-reverse;
    align-items: stretch;
    gap: var(--space-4);
  }

  .header-with-controls h1 {
    font-size: 1.5rem;
    line-height: 1.3;
  }

  /* Top controls: horizontal buttons above title */
  .top-controls {
    justify-content: flex-start;
    width: 100%;
  }

  /* Trip + Stage header: stack title and buttons */
  .trip-header,
  .stage-header {
    flex-direction: column;   /* title above, buttons below */
    align-items: flex-start;
    gap: .5rem;
  }

  .trip-controls,
  .stage-controls,
  .controls {
    display: flex;
    flex-direction: column;   /* Stack buttons vertically to prevent wrapping issues */
    gap: var(--space-2);
    width: 100%;
  }

  .trip-controls > *,
  .stage-controls > *,
  .controls > * {
    width: 100%;              /* Full-width buttons on mobile */
    text-align: center;
  }

  .title-content h3 {
    font-size: 1.2rem;
    line-height: 1.3;
  }

  /* Improve participant badge wrapping on mobile */
  .participants,
  .huts,
  .surf-spots {
    gap: var(--space-3); /* Maintain 12px gap on mobile for easy tapping */
  }

  .participants strong,
  .huts strong,
  .surf-spots strong {
    width: 100%;
    margin-bottom: var(--space-1);
  }

  .stage-card {
    padding: 1rem;
  }

  /* Badge sizing and overflow handling on mobile */
  .participants :deep(.badge),
  .huts :deep(.badge),
  .surf-spots :deep(.badge) {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
    font-size: 0.75rem;
  }

  /* Legacy classes - kept for backwards compatibility */
  .participant-tag, .hut-tag, .surf-spot-tag {
    max-width: 120px;
    font-size: 0.75rem;
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

  /* Trip summary stats: convert to grid for better readability */
  .trip-stats-detail {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
    justify-content: center;
  }

  .trip-stats-detail .stat-separator {
    display: none;
  }

  /* Stage stats: convert to grid for better mobile readability */
  .stage-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
    font-size: 0.9rem;
  }

  .stage-stats .stat-separator {
    display: none;
  }

  .stage-stats .stat-item span {
    font-size: 1rem;
  }

  /* Better description handling */
  .description {
    font-size: 0.9rem;
    line-height: 1.4;
  }

  /* Photo gallery optimization for mobile */
  .photo-gallery {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); /* Slightly smaller thumbnails */
    gap: var(--space-3); /* Increased from 8px to 12px for better spacing */
    max-width: 100%;
  }

  /* Ensure 2-3 columns max on narrow screens */
  @media (max-width: 400px) {
    .photo-gallery {
      grid-template-columns: repeat(2, 1fr); /* Force 2 columns on very narrow screens */
    }
  }
}

</style>