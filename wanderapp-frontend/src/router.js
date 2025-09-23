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
  },
  {
    path: '/',
    name: 'TripList',
    component: TripList,
  },
  {
    path: '/hiking',
    name: 'HikingTrips',
    component: TripList,
    props: { defaultCategory: 'HIKING' }
  },
  {
    path: '/surfing',
    name: 'SurfingTrips',
    component: TripList,
    props: { defaultCategory: 'SURFING' }
  },
  {
    path: '/dashboard/:id?', // id is optional
    name: 'Dashboard',
    component: UserDashboard,
  },
  {
    path: '/trip/new',
    name: 'TripCreate',
    component: TripCreate,
  },
  {
    path: '/trip/:id',
    name: 'TripDetail',
    component: TripDetail,
  },
  {
    path: '/trip/:id/edit',
    name: 'TripEdit',
    component: TripEdit,
  },
  {
    path: '/trip/:tripId/add-stage',
    name: 'StageCreate',
    component: StageCreate,
  },
  {
    path: '/trip/:tripId/add-surf-stage',
    name: 'SurfStageCreate',
    component: SurfStageCreate,
  },
  {
    path: '/stage/:id/edit',
    name: 'StageEdit',
    component: StageEdit,
  },
  {
    path: '/surf-stage/:id/edit',
    name: 'SurfStageEdit',
    component: SurfStageEdit,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
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

export default router;