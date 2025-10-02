<template>
  <div class="elevation-profile-container">
    <div class="profile-header" :class="{ expanded: !isCollapsed }" @click="toggleCollapsed">
      <div class="header-content">
        <h4>Höhenprofil</h4>
        <p v-if="!isCollapsed" class="hint-text">
          <span class="hint-desktop">Bewege die Maus über das Profil, um die Position auf der Karte zu sehen</span>
          <span class="hint-mobile">Tippe auf das Profil, um die Position auf der Karte zu sehen</span>
        </p>
      </div>
      <button class="collapse-button" :class="{ collapsed: isCollapsed }" aria-label="Toggle elevation profile">
        <span class="chevron">▼</span>
      </button>
    </div>

    <div v-show="!isCollapsed" class="profile-content">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Lade Höhenprofil...</p>
      </div>

      <div v-else class="chart-wrapper" @click="handleChartClick" @touchstart="handleTouchStart">
        <Line
          ref="chartRef"
          :data="chartData"
          :options="chartOptions"
          @mousemove="handleChartHover"
          @mouseleave="handleChartLeave"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps({
  trackData: {
    type: Object,
    required: true,
    validator: (value) => {
      return value.elevations && value.distances && value.coordinates;
    }
  }
});

const emit = defineEmits(['position-hover', 'position-leave']);

const isLoading = ref(true);
const chartRef = ref(null);
const isCollapsed = ref(true);

onMounted(() => {
  // Simulate chart loading
  setTimeout(() => {
    isLoading.value = false;
  }, 300);
});

const toggleCollapsed = () => {
  isCollapsed.value = !isCollapsed.value;
};

// Process elevation data for the chart
const validData = computed(() => {
  const elevations = props.trackData.elevations || [];
  const distances = props.trackData.distances || [];

  // Filter out null elevations
  return elevations
    .map((ele, idx) => ({
      elevation: ele,
      distance: distances[idx] / 1000, // Convert to km
      index: idx
    }))
    .filter(d => d.elevation !== null);
});

const maxDistance = computed(() => {
  const data = validData.value;
  return data.length > 0 ? Math.max(...data.map(d => d.distance)) : 0;
});

const chartData = computed(() => {
  const data = validData.value;
  if (data.length === 0) return null;

  // Create data points with x/y coordinates for linear scale
  const dataPoints = data.map(d => ({
    x: d.distance,
    y: d.elevation
  }));

  return {
    datasets: [{
      label: 'Höhe (m)',
      data: dataPoints,
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-hiking').trim() || '#e3342f',
      backgroundColor: (context) => {
        const ctx = context.chart.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        const hikeColor = getComputedStyle(document.documentElement).getPropertyValue('--color-hiking').trim() || '#e3342f';
        gradient.addColorStop(0, hikeColor + '19'); // 10% opacity (more subtle)
        gradient.addColorStop(1, hikeColor + '00'); // 0% opacity
        return gradient;
      },
      borderWidth: 2,
      fill: true,
      tension: 0.4, // Smooth curves
      pointRadius: 0, // Hide points for cleaner look
      pointHoverRadius: 5,
      pointHoverBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-hiking').trim() || '#e3342f',
      pointHoverBorderColor: '#fff',
      pointHoverBorderWidth: 2,
    }]
  };
});

const chartOptions = computed(() => {
  const textColor = getComputedStyle(document.documentElement).getPropertyValue('--color-text-primary').trim() || '#333';
  const gridColor = getComputedStyle(document.documentElement).getPropertyValue('--color-neutral-300').trim() || '#d0d0d0';

  // Determine font size based on screen width
  const isMobile = window.innerWidth <= 600;
  const axisLabelFontSize = isMobile ? 13 : 12;
  const tickFontSize = isMobile ? 11 : 10;

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false,
        callbacks: {
          title: (context) => {
            return `${context[0].label} km`;
          },
          label: (context) => {
            return `Höhe: ${Math.round(context.parsed.y)} m`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'linear',
        min: 0,
        max: maxDistance.value,
        title: {
          display: true,
          text: 'Distanz (km)',
          color: textColor,
          font: {
            size: axisLabelFontSize
          }
        },
        grid: {
          color: gridColor,
          drawBorder: false
        },
        ticks: {
          color: textColor,
          maxTicksLimit: isMobile ? 6 : 10,
          font: {
            size: tickFontSize
          },
          stepSize: 0.5,
          callback: function(value) {
            // Format to show whole numbers or .5 values cleanly
            const numValue = parseFloat(value);
            return numValue % 1 === 0 ? numValue.toFixed(0) : numValue.toFixed(1);
          }
        }
      },
      y: {
        title: {
          display: true,
          text: 'Höhe (m)',
          color: textColor,
          font: {
            size: axisLabelFontSize
          }
        },
        grid: {
          color: gridColor,
          drawBorder: false
        },
        ticks: {
          color: textColor,
          font: {
            size: tickFontSize
          },
          callback: function(value) {
            // Format large numbers more compactly
            if (value >= 1000) {
              return (value / 1000).toFixed(1) + 'k';
            }
            return Math.round(value);
          }
        }
      }
    },
    onHover: (event, activeElements) => {
      if (activeElements && activeElements.length > 0) {
        const index = activeElements[0].index;
        const realIndex = getRealIndexFromChartIndex(index);
        const coords = props.trackData.coordinates[realIndex];
        emit('position-hover', { index: realIndex, coordinates: coords });
      }
    }
  };
});

// Map chart index (filtered data) back to original track point index
const getRealIndexFromChartIndex = (chartIndex) => {
  const data = validData.value;
  if (chartIndex >= 0 && chartIndex < data.length) {
    return data[chartIndex].index;
  }
  return 0;
};

// Mobile touch handling
const handleTouchStart = (event) => {
  if (!chartRef.value || !chartRef.value.chart) return;

  const chart = chartRef.value.chart;
  const rect = chart.canvas.getBoundingClientRect();
  const touch = event.touches[0];

  const x = touch.clientX - rect.left;
  const y = touch.clientY - rect.top;

  // Get the elements at this position
  const elements = chart.getElementsAtEventForMode(
    { x, y },
    'index',
    { intersect: false },
    false
  );

  if (elements && elements.length > 0) {
    const index = elements[0].index;
    const realIndex = getRealIndexFromChartIndex(index);
    const coords = props.trackData.coordinates[realIndex];
    emit('position-hover', { index: realIndex, coordinates: coords });

    // Clear after 2 seconds
    setTimeout(() => {
      emit('position-leave');
    }, 2000);
  }
};

const handleChartClick = (event) => {
  // Handle click for mobile
  if (window.innerWidth <= 600) {
    handleTouchStart({ touches: [{ clientX: event.clientX, clientY: event.clientY }] });
  }
};

const handleChartHover = () => {
  // Chart.js handles hover via onHover in options
};

const handleChartLeave = () => {
  emit('position-leave');
};
</script>

<style scoped>
.elevation-profile-container {
  margin-top: var(--space-6);
  padding: var(--space-6);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  cursor: pointer;
  user-select: none;
  gap: var(--space-3);
  transition: margin-bottom 0.2s ease;
}

.profile-header.expanded {
  margin-bottom: var(--space-4);
}

.profile-header:hover {
  opacity: 0.8;
}

.header-content {
  flex: 1;
  min-width: 0;
}

.elevation-profile-container h4 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
}

.hint-text {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  font-style: italic;
}

.collapse-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
  color: var(--color-text-secondary);
  transition: transform 0.2s ease;
  flex-shrink: 0;
  margin-top: -4px;
}

.collapse-button:hover {
  color: var(--color-text-primary);
}

.chevron {
  display: inline-block;
  font-size: var(--text-base);
  transition: transform 0.2s ease;
}

.collapse-button.collapsed .chevron {
  transform: rotate(-90deg);
}

.profile-content {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hint-mobile {
  display: none;
}

.hint-desktop {
  display: inline;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 250px;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border-light);
  border-top-color: var(--color-hiking);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.chart-wrapper {
  position: relative;
  height: 250px;
  width: 100%;
}

/* Mobile responsive */
@media (max-width: 600px) {
  .elevation-profile-container {
    padding: var(--space-3);
    margin-left: calc(-1 * var(--space-2));
    margin-right: calc(-1 * var(--space-2));
  }

  .profile-header {
    align-items: flex-start;
  }

  .hint-mobile {
    display: inline;
  }

  .hint-desktop {
    display: none;
  }

  .chart-wrapper {
    height: 200px;
  }

  .loading-state {
    height: 200px;
  }

  .elevation-profile-container h4 {
    font-size: var(--text-base);
  }

  .hint-text {
    font-size: 0.7rem;
  }
}

/* Very small screens */
@media (max-width: 400px) {
  .chart-wrapper {
    height: 180px;
  }

  .loading-state {
    height: 180px;
  }
}
</style>
