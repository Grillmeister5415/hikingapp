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

        <!-- Surf Stats - Redesigned -->
        <div v-if="stage.activity_type === 'SURFING'" class="surf-session">
          <!-- Environment Badge -->
          <div v-if="stage.environment" class="environment-badge" :class="`env-${stage.environment?.toLowerCase()}`">
            {{ getEnvironmentLabel(stage.environment) }}
          </div>

          <!-- Session Overview -->
          <div class="session-overview">
            <div class="overview-item">
              <span class="overview-icon">⏱</span>
              <div>
                <div class="overview-value">{{ formatDuration(stage.time_in_water) }}</div>
                <div class="overview-label">Time in water</div>
              </div>
            </div>
            <div class="overview-item" v-if="stage.waves_caught">
              <span class="overview-icon">🌊</span>
              <div>
                <div class="overview-value">{{ stage.waves_caught }}</div>
                <div class="overview-label">Waves caught</div>
              </div>
            </div>
            <div class="overview-item" v-if="stage.surfboard?.name || stage.surfboard_used">
              <span class="overview-icon">🏄</span>
              <div>
                <div class="overview-value">{{ stage.surfboard?.name || stage.surfboard_used }}</div>
                <div class="overview-label">Surfboard</div>
              </div>
            </div>
          </div>

          <!-- Quality Stars (Hero Element) -->
          <div v-if="stage.wave_quality" class="quality-hero">
            <div class="quality-stars">{{ '★'.repeat(stage.wave_quality) }}</div>
            <div class="quality-label">Wave Quality</div>
          </div>

          <!-- Ocean Conditions -->
          <div v-if="!stage.environment || stage.environment === 'OCEAN'" class="conditions-grid">
            <!-- Wave Conditions Card -->
            <BaseCard variant="flat" padding="small" v-if="stage.wave_height || stage.wave_energy || stage.surf_spot">
              <div class="condition-card">
                <h5 class="condition-title">
                  <span>Wave Conditions</span>
                  <span v-if="stage.wave_height" class="wave-size-badge" :class="getWaveSizeClass(stage.wave_height)">
                    {{ getWaveSizeLabel(stage.wave_height) }}
                  </span>
                </h5>
                <div class="condition-items">
                  <div v-if="stage.surf_spot" class="condition-row">
                    <span class="condition-label">Surf Spot</span>
                    <span class="condition-value">{{ stage.surf_spot }}</span>
                  </div>
                  <div v-if="stage.wave_height" class="condition-row">
                    <span class="condition-label">Wave Height</span>
                    <span class="condition-value">{{ stage.wave_height }}m</span>
                  </div>
                  <div v-if="stage.wave_energy" class="condition-row">
                    <span class="condition-label">Wave Energy</span>
                    <span class="condition-value">{{ stage.wave_energy }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <!-- Swell & Wind Card -->
            <BaseCard variant="flat" padding="small" v-if="stage.swell_direction || stage.wind_direction">
              <div class="condition-card">
                <h5 class="condition-title">
                  <span>Swell & Wind</span>
                  <span
                    v-if="getWindCondition(stage.swell_direction, stage.wind_direction)"
                    class="wind-quality-badge"
                    :style="{ backgroundColor: getWindCondition(stage.swell_direction, stage.wind_direction).color }"
                  >
                    {{ getWindConditionLabel(getWindCondition(stage.swell_direction, stage.wind_direction).type) }}
                  </span>
                </h5>
                <div class="condition-items">
                  <div v-if="stage.swell_direction" class="condition-row">
                    <span class="condition-label">Swell</span>
                    <span class="condition-value">
                      <span class="direction-arrow" :style="{ transform: `rotate(${getDirectionDegrees(stage.swell_direction)}deg)` }">↑</span>
                      {{ getDirectionLabel(stage.swell_direction) }}
                    </span>
                  </div>
                  <div v-if="stage.wind_direction" class="condition-row">
                    <span class="condition-label">Wind</span>
                    <span class="condition-value">
                      <span v-if="stage.wind_speed" class="wind-speed">{{ stage.wind_speed }} km/h</span>
                      <span class="direction-arrow" :style="{ transform: `rotate(${getDirectionDegrees(stage.wind_direction)}deg)` }">↑</span>
                      {{ getDirectionLabel(stage.wind_direction) }}
                    </span>
                  </div>
                </div>
              </div>
            </BaseCard>

            <!-- Environment Card -->
            <BaseCard variant="flat" padding="small" v-if="stage.water_temperature || stage.tide_stage || stage.tide_movement || stage.crowd_factor">
              <div class="condition-card">
                <h5 class="condition-title">
                  <span>Environment</span>
                  <span v-if="stage.crowd_factor" class="crowd-badge" :class="`crowd-${stage.crowd_factor.toLowerCase()}`">
                    {{ getCrowdLabel(stage.crowd_factor) }}
                  </span>
                </h5>
                <div class="condition-items">
                  <div v-if="stage.water_temperature" class="condition-row">
                    <span class="condition-label">Water Temp</span>
                    <span class="condition-value">{{ stage.water_temperature }}°C</span>
                  </div>
                  <div v-if="getFormattedTide(stage.tide_stage, stage.tide_movement)" class="condition-row">
                    <span class="condition-label">Tide</span>
                    <span class="condition-value">{{ getFormattedTide(stage.tide_stage, stage.tide_movement) }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>

          <!-- Riverwave Conditions -->
          <div v-if="stage.environment === 'RIVERWAVE'" class="conditions-grid">
            <BaseCard variant="flat" padding="small">
              <div class="condition-card">
                <h5 class="condition-title">
                  <span>🏞️ Riverwave Infos</span>
                  <span v-if="stage.wave_power" class="wave-power-badge" :class="`power-${stage.wave_power?.toLowerCase()}`">
                    {{ getWavePowerLabel(stage.wave_power) }}
                  </span>
                </h5>
                <div class="condition-items">
                  <div v-if="stage.surf_spot" class="condition-row">
                    <span class="condition-label">Riverwave</span>
                    <span class="condition-value">{{ stage.surf_spot }}</span>
                  </div>
                  <div v-if="stage.average_wait_time" class="condition-row">
                    <span class="condition-label">Avg Wait Time</span>
                    <span class="condition-value">{{ stage.average_wait_time }} min</span>
                  </div>
                  <div v-if="stage.flow_rate" class="condition-row">
                    <span class="condition-label">Flow Rate</span>
                    <span class="condition-value">{{ stage.flow_rate }} m³/s</span>
                  </div>
                  <div v-if="stage.water_level" class="condition-row">
                    <span class="condition-label">Water Level</span>
                    <span class="condition-value">{{ stage.water_level }} m</span>
                  </div>
                  <div v-if="stage.water_temperature" class="condition-row">
                    <span class="condition-label">Temperature</span>
                    <span class="condition-value">{{ stage.water_temperature }}°C</span>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>

          <!-- Poolwave Conditions -->
          <div v-if="stage.environment === 'POOLWAVE'" class="conditions-grid">
            <BaseCard variant="flat" padding="small">
              <div class="condition-card">
                <h5 class="condition-title">🏊 Poolwave Session</h5>
                <div class="condition-items">
                  <div v-if="stage.surf_spot" class="condition-row">
                    <span class="condition-label">Pool</span>
                    <span class="condition-value">{{ stage.surf_spot }}</span>
                  </div>
                </div>
              </div>
            </BaseCard>
          </div>

          <!-- External Link -->
          <div v-if="stage.external_link" class="surf-external-link">
            <a :href="stage.external_link" target="_blank" rel="noopener noreferrer">
              {{ formatLink(stage.external_link) }} 🔗
            </a>
          </div>
        </div>

        <div v-if="stage.activity_type !== 'SURFING' && stage.track">
          <HikeMap :stageId="stage.id" :highlightedPosition="highlightedPosition" />
          <ElevationProfile
            v-if="hasElevationData(stage.track)"
            :trackData="stage.track"
            @position-hover="handlePositionHover"
            @position-leave="handlePositionLeave"
          />
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
import ElevationProfile from './ElevationProfile.vue';
import CommentSection from './CommentSection.vue';
import { currentUser } from '../store';
import ImageUploader from './ImageUploader.vue';
import ProcessedText from './ProcessedText.vue';
import { getTripUsers, getStageUsers } from '../utils/textProcessing.js';
import PhotoSwipeLightbox from 'photoswipe/lightbox';
import 'photoswipe/style.css';
import BaseButton from './base/BaseButton.vue';
import BaseBadge from './base/BaseBadge.vue';
import BaseCard from './base/BaseCard.vue';
import { formatDurationHoursMinutes } from '../utils/duration.js';

const route = useRoute();
const trip = ref(null);
const isLoading = ref(true);

// Computed property for trip list navigation
const tripListRoute = computed(() => getTripListRoute());
const error = ref(null);
let lightbox = null;

// State for elevation profile interaction
const highlightedPosition = ref(null);

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

// Helper function to get direction in degrees for arrow rotation
const getDirectionDegrees = (direction) => {
  const directionMap = {
    'N': 0,
    'NE': 45,
    'E': 90,
    'SE': 135,
    'S': 180,
    'SW': 225,
    'W': 270,
    'NW': 315
  };
  return directionMap[direction] || 0;
};

// Calculate wind conditions relative to swell (offshore/onshore/cross)
const getWindCondition = (swellDir, windDir) => {
  if (!swellDir || !windDir) return null;

  const directionMap = {
    'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
    'S': 180, 'SW': 225, 'W': 270, 'NW': 315
  };

  const swell = directionMap[swellDir];
  const wind = directionMap[windDir];

  if (swell === undefined || wind === undefined) return null;

  // Calculate difference (normalized to 0-180)
  let diff = Math.abs(swell - wind);
  if (diff > 180) diff = 360 - diff;

  // Offshore: wind blowing from land to sea (opposite to swell)
  // Onshore: wind blowing from sea to land (same direction as swell)
  // Cross: wind perpendicular to swell
  if (diff >= 135 && diff <= 225) {
    return { type: 'offshore', emoji: '✓', color: 'var(--color-success)' };
  } else if (diff <= 45) {
    return { type: 'onshore', emoji: '⚠', color: 'var(--color-warning)' };
  } else {
    return { type: 'cross', emoji: '→', color: 'var(--color-neutral-500)' };
  }
};

// Format combined tide display
const getFormattedTide = (tideStage, tideMovement) => {
  if (!tideStage && !tideMovement) return null;

  const stageMap = {
    'LOW': 'Low',
    'MID': 'Mid',
    'HIGH': 'High'
  };

  const movementMap = {
    'RISING': 'Rising',
    'FALLING': 'Falling'
  };

  const stage = stageMap[tideStage] || tideStage;
  const movement = movementMap[tideMovement] || tideMovement;

  if (stage && movement) {
    return `${stage} → ${movement}`;
  }
  return stage || movement;
};

// Get wind condition label text
const getWindConditionLabel = (type) => {
  const labels = {
    'offshore': 'Offshore',
    'onshore': 'Onshore',
    'cross': 'Cross-shore'
  };
  return labels[type] || type;
};

// Get crowd factor label
const getCrowdLabel = (crowdFactor) => {
  const labels = {
    'EMPTY': 'Empty',
    'CHILL': 'Chill',
    'CROWDED': 'Crowded',
    'PACKED': 'Packed'
  };
  return labels[crowdFactor] || crowdFactor;
};

// Get wave size category and label
const getWaveSizeLabel = (height) => {
  if (height >= 4) return 'Suicidal';
  if (height >= 2.5) return 'Huge';
  if (height >= 1.8) return 'Big';
  if (height >= 1.0) return 'Medium';
  if (height >= 0.5) return 'Small';
  return 'Tiny';
};

const getWaveSizeClass = (height) => {
  if (height >= 4) return 'wave-suicidal';
  if (height >= 2.5) return 'wave-huge';
  if (height >= 1.8) return 'wave-big';
  if (height >= 1.0) return 'wave-medium';
  if (height >= 0.5) return 'wave-small';
  return 'wave-tiny';
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

const formatDuration = formatDurationHoursMinutes;

// Environment helper functions
const getEnvironmentLabel = (env) => {
  const labels = { 'OCEAN': '🌊 Ocean', 'RIVERWAVE': '🏞️ Riverwave', 'POOLWAVE': '🏊 Poolwave' };
  return labels[env] || '🌊 Ocean';
};

const getWavePowerLabel = (power) => {
  const labels = {
    'DEAD': 'Dead',
    'SOFT': 'Soft',
    'FUN': 'Fun',
    'JUICY': 'Juicy',
    'BEAST_MODE': 'Beast Mode'
  };
  return labels[power] || power;
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

// Check if track has elevation data
const hasElevationData = (trackData) => {
  if (!trackData || !trackData.elevations) return false;
  // Check if there's at least one non-null elevation value
  return trackData.elevations.some(ele => ele !== null);
};

// Handle elevation profile hover
const handlePositionHover = (positionData) => {
  highlightedPosition.value = positionData;
};

// Handle elevation profile leave
const handlePositionLeave = () => {
  highlightedPosition.value = null;
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

/* Surf Session - Redesigned Layout */
.surf-session {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border-light);
}

.session-overview {
  display: flex;
  gap: var(--space-6);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: linear-gradient(135deg, rgba(32, 178, 170, 0.05) 0%, rgba(72, 187, 120, 0.05) 100%);
  border-radius: var(--radius-md);
}

.overview-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
  min-width: 140px;
}

.overview-icon {
  font-size: var(--text-3xl);
}

.overview-value {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.overview-label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* Quality Hero Section */
.quality-hero {
  text-align: center;
  padding: var(--space-6) 0;
  margin-bottom: var(--space-4);
}

.quality-stars {
  font-size: 3rem;
  color: var(--color-primary);
  letter-spacing: 0.25rem;
  line-height: 1;
}

.quality-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--font-medium);
}

/* Conditions Grid */
.conditions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.condition-card {
  min-width: 0;
}

.condition-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 var(--space-3) 0;
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.condition-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.condition-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.condition-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
}

.condition-value {
  font-size: var(--text-base);
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.direction-arrow {
  display: inline-block;
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-primary);
  transition: transform var(--transition-fast);
}

.wind-speed {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
  margin-right: var(--space-2);
}

.wind-quality-badge {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  color: white;
  white-space: nowrap;
}

/* Crowd Factor Badges */
.crowd-badge {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.crowd-empty {
  background-color: var(--color-success);
  color: white;
}

.crowd-chill {
  background-color: #4299E1;
  color: white;
}

.crowd-crowded {
  background-color: var(--color-warning);
  color: white;
}

.crowd-packed {
  background-color: var(--color-error);
  color: white;
}

/* Wave Size Badges */
.wave-size-badge {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  color: white;
}

.wave-tiny {
  background-color: #90CDF4; /* Light Blue */
}

.wave-small {
  background-color: #48BB78; /* Green */
}

.wave-medium {
  background-color: #ECC94B; /* Yellow */
}

.wave-big {
  background-color: #ED8936; /* Orange */
}

.wave-huge {
  background-color: #F56565; /* Red */
}

/* Environment Badge */
.environment-badge {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-4);
  color: white;
}

.env-ocean {
  background-color: var(--color-surfing);
}

.env-riverwave {
  background-color: #2F855A;
}

.env-poolwave {
  background-color: #2C5282;
}

/* Wave Power Badge */
.wave-power-badge {
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  color: white;
}

.power-dead {
  background-color: #718096; /* Gray */
}

.power-soft {
  background-color: #90CDF4; /* Light Blue */
}

.power-fun {
  background-color: #48BB78; /* Green */
}

.power-juicy {
  background-color: #ED8936; /* Orange */
}

.power-beast_mode {
  background-color: #F56565; /* Red */
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 8px rgba(245, 101, 101, 0.8);
  }
  50% {
    box-shadow: 0 0 16px rgba(245, 101, 101, 1);
  }
}

.wave-suicidal {
  background-color: #C53030; /* Dark Red */
  animation: defcon-blink 0.8s ease-in-out infinite;
}

@keyframes defcon-blink {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 10px rgba(197, 48, 48, 0.8);
  }
  50% {
    opacity: 0.6;
    box-shadow: 0 0 20px rgba(197, 48, 48, 1);
  }
}

.surf-external-link {
  text-align: center;
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border-light);
}

.surf-external-link a {
  color: var(--color-primary);
  font-weight: var(--font-medium);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.surf-external-link a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
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

  /* Surf session mobile optimizations */
  .session-overview {
    flex-direction: column;
    gap: var(--space-4);
  }

  .overview-item {
    min-width: 100%;
  }

  .quality-stars {
    font-size: 2.5rem;
  }

  .conditions-grid {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }

  .condition-row {
    font-size: var(--text-sm);
  }

  .condition-value {
    font-size: var(--text-sm);
  }
}

</style>
