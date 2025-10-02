import { createRouter, createWebHistory } from 'vue-router';
import TripList from './components/TripList.vue';
import TripDetail from './components/TripDetail.vue';
import TripCreate from './components/TripCreate.vue';
import TripEdit from './components/TripEdit.vue';
import UserDashboard from './components/UserDashboard.vue';
import StageCreate from './components/StageCreate.vue';
import SurfStageCreate from './components/SurfStageCreate.vue';
import StageEdit from './components/StageEdit.vue';
import SurfStageEdit from './components/SurfStageEdit.vue';
import LoginView from './components/LoginView.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { title: 'Login - WanderApp' }
  },
  {
    path: '/',
    name: 'TripList',
    component: TripList,
    meta: { title: 'All Trips - WanderApp' }
  },
  {
    path: '/hiking',
    name: 'HikingTrips',
    component: TripList,
    props: { defaultCategory: 'HIKING' },
    meta: { title: 'Hiking Trips - WanderApp' }
  },
  {
    path: '/surfing',
    name: 'SurfingTrips',
    component: TripList,
    props: { defaultCategory: 'SURFING' },
    meta: { title: 'Surfing Trips - WanderApp' }
  },
  {
    path: '/dashboard/:id?', // id is optional
    name: 'Dashboard',
    component: UserDashboard,
    meta: { title: 'Dashboard - WanderApp' }
  },
  {
    path: '/trip/new',
    name: 'TripCreate',
    component: TripCreate,
    meta: { title: 'New Trip - WanderApp' }
  },
  {
    path: '/trip/:id',
    name: 'TripDetail',
    component: TripDetail,
    meta: { title: 'Trip Details - WanderApp' }
  },
  {
    path: '/trip/:id/edit',
    name: 'TripEdit',
    component: TripEdit,
    meta: { title: 'Edit Trip - WanderApp' }
  },
  {
    path: '/trip/:tripId/add-stage',
    name: 'StageCreate',
    component: StageCreate,
    meta: { title: 'Add Stage - WanderApp' }
  },
  {
    path: '/trip/:tripId/add-surf-stage',
    name: 'SurfStageCreate',
    component: SurfStageCreate,
    meta: { title: 'Add Surf Stage - WanderApp' }
  },
  {
    path: '/stage/:id/edit',
    name: 'StageEdit',
    component: StageEdit,
    meta: { title: 'Edit Stage - WanderApp' }
  },
  {
    path: '/surf-stage/:id/edit',
    name: 'SurfStageEdit',
    component: SurfStageEdit,
    meta: { title: 'Edit Surf Stage - WanderApp' }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // If there's a saved position (browser back/forward), use it
    if (savedPosition) {
      return savedPosition;
    }
    // Otherwise, always scroll to top
    return { top: 0, behavior: 'instant' };
  }
});

// Navigation guard to protect routes
router.beforeEach(async (to, from, next) => {
  const publicPages = ['/login'];
  const authRequired = !publicPages.includes(to.path);
  const hasToken = localStorage.getItem('accessToken');

  // If going to login page and already authenticated, redirect to home
  if (to.path === '/login' && hasToken) {
    return next('/');
  }

  // If auth required but no token, redirect to login
  if (authRequired && !hasToken) {
    return next('/login');
  }

  // Prevent navigation during token refresh to avoid race conditions
  const { isAuthLoading } = await import('./store');
  if (isAuthLoading.value && authRequired) {
    // Wait briefly for auth operation to complete
    await new Promise(resolve => setTimeout(resolve, 100));
    if (!localStorage.getItem('accessToken')) {
      return next('/login');
    }
  }

  next();
});

// Update document title based on route meta
router.afterEach((to) => {
  document.title = to.meta.title || 'WanderApp';
});

export default router;