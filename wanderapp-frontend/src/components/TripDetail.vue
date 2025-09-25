<template>
  <div>
    <div v-if="isLoading">Lade Trip-Details...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="trip">
      <router-link :to="tripListRoute">&larr; Zurück zur Übersicht</router-link>
      <div class="header">
        <h1>{{ trip.name }}</h1>
        <div class="controls">
          <router-link v-if="currentUser && currentUser.id === trip.creator.id" :to="`/trip/${trip.id}/edit`" class="btn btn-edit-trip">Edit Trip</router-link>
          <router-link :to="getAddStageRoute()" class="btn btn-add-stage">{{ getAddStageLabel() }}</router-link>
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
            <router-link v-for="p in trip.participants" :key="p.id" :to="`/dashboard/${p.id}`" class="participant-tag user-link">{{ p.username }}</router-link>
          </div>
          <!-- Show huts for hiking trips -->
          <div class="huts" v-if="trip.activity_type === 'HIKING' && trip.huts && trip.huts.length">
            <strong>🏔️ Hütten:</strong>
            <template v-for="hut in trip.huts" :key="hut.id">
              <a v-if="hut.link" :href="hut.link" target="_blank" @click.stop class="hut-tag">{{ hut.name }}</a>
              <span v-else class="hut-tag">{{ hut.name }}</span>
            </template>
          </div>
          
          <!-- Show surf spots for surf trips -->
          <div class="surf-spots" v-if="trip.activity_type === 'SURFING' && getSurfSpotsList().length">
            <strong>🏄‍♂️ Surf Spots:</strong>
            <span v-for="spot in getSurfSpotsList()" :key="spot.name" class="surf-spot-tag">{{ spot.display }}</span>
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
            <router-link :to="getStageEditRoute(stage)" class="btn-edit">Bearbeiten ✏️</router-link>
            <button @click="handleDeleteStage(stage.id)" class="btn-delete" title="Etappe löschen">🗑️</button>
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
import { ref, onMounted, onUnmounted, computed } from 'vue';
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
  if (!trip.value) return '🥾 Add Stage';
  
  switch (trip.value.activity_type) {
    case 'HIKING':
      return '🥾 Add Hiking Stage';
    case 'SURFING':
      return '🏄‍♂️ Add Surf';
    default:
      return '🥾 Add Stage';
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
.description { white-space: pre-wrap; word-break: break-word; margin-top: 0; }
.creator { font-size: 0.9rem; color: #6c757d; }
.header { display: flex; justify-content: space-between; align-items: center; margin: 1rem 0; min-width: 0; }
.header h1 { word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; hyphens: auto; min-width: 0; margin: 0; }
.header .controls { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.btn { display: inline-block; padding: 0.8rem 1.5rem; text-decoration: none; border-radius: 8px; font-weight: bold; }
.btn-edit-trip { background-color: #ffc107; color: #212529; }

.btn-add-stage { 
  background-color: #42b983; 
  color: white; 
  padding: 0.6rem 1rem; 
  font-size: 0.9rem;
}
a { text-decoration: none; color: #0d6efd; }
a:hover { text-decoration: underline; }
a[href="/"] { display: inline-block; margin-bottom: 1rem; }
.trip-summary-card { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; }
.trip-stats-detail { display: flex; justify-content: space-around; padding-bottom: 1rem; margin-bottom: 1rem; min-width: 0; overflow: hidden; flex-wrap: wrap; gap: 0.5rem; }
.social-details { border-top: 1px solid #e0e0e0; padding-top: 1rem; font-size: 0.9rem; min-width: 0; overflow: hidden; }
.stat-item { text-align: center; }
.stat-item .stat-value { font-size: 1.5rem; font-weight: 500; word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; }
.stat-item .stat-value small { font-size: 1rem; font-weight: 400; color: #6c757d; margin-left: 0.25rem; }
.stat-item label { font-size: 0.8rem; color: #6c757d; display: block; margin-top: -5px; }
.stat-separator { color: #e0e0e0; font-size: 1.5rem; }
.participants, .huts, .surf-spots { margin-bottom: 0.5rem; min-width: 0; }
.participant-tag { background-color: #e9ecef; color: #495057; }
.hut-tag { background-color: #d1ecf1; color: #0c5460; }
.hut-tag:hover { background-color: #bee5eb; color: #062c33; }
a.hut-tag { text-decoration: none; }
.surf-spot-tag { background-color: #20b2aa; color: white; }
.participant-tag, .hut-tag, .surf-spot-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; margin-right: 0.5rem; margin-top: 0.25rem; word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; max-width: 200px; }
.stage-card { border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; min-width: 0; overflow: hidden; }
.stage-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; min-width: 0; }
.stage-controls { display: flex; align-items: center; gap: 0.5rem; }
.btn-edit { padding: 0.4rem 0.8rem; border: 1px solid #6c757d; color: #6c757d; border-radius: 5px; font-size: 0.9rem; }
.btn-delete { background-color: transparent; border: none; cursor: pointer; font-size: 1.2rem; }
.stage-stats { display: flex; align-items: baseline; gap: 0.75rem; margin: 1rem 0; padding-top: 1rem; border-top: 1px solid #f0f0f0; min-width: 0; overflow: hidden; }
.stage-stats .stat-item { text-align: left; min-width: 0; flex-shrink: 1; }
.stage-stats .stat-item span { font-size: 1.2rem; font-weight: 500; word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; }
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

/* Activity-specific styling */
.stage-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  margin-bottom: 0.25rem;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  margin-top: 0;
}

.stage-date {
  font-size: 0.9rem;
  font-weight: normal;
  color: #6c757d;
  margin-top: 0;
}

.activity-icon {
  font-size: 1.5rem;
  margin-right: 0.5rem;
}

.activity-hiking {
  border-left: 4px solid #28a745;
}

.activity-running {
  border-left: 4px solid #007bff;
}

.activity-surfing {
  border-left: 4px solid #20b2aa;
}

.surf-details {
  margin-top: 1rem;
  padding: 1rem;
  background-color: rgba(32, 178, 170, 0.05);
  border-radius: 8px;
  border-left: 3px solid #20b2aa;
}

.detail-item {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.surf-stats {
  border-top-color: #20b2aa;
}

.surf-overview {
  background: linear-gradient(135deg, rgba(32, 178, 170, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
  border-radius: 8px;
  padding: 1rem;
  margin: -1rem;
  margin-bottom: 1rem;
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

  /* Enhanced word-breaking for mobile */
  .header h1 {
    font-size: 1.5rem;
    line-height: 1.3;
  }

  .title-content h3 {
    font-size: 1.2rem;
    line-height: 1.3;
  }

  .stage-card {
    padding: 1rem;
  }

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

  /* Stage stats: keep on one line but adjust spacing */
  .stage-stats {
    gap: 0.5rem;
    font-size: 0.9rem;
    flex-wrap: wrap;
  }

  .stage-stats .stat-item span {
    font-size: 1rem;
  }

  /* Better description handling */
  .description {
    font-size: 0.9rem;
    line-height: 1.4;
  }
}

</style>