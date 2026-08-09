import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/auth/LoginView.vue'
import ProfileView from '@/views/auth/ProfileView.vue'
import DashboardView from '@/views/DashboardView.vue'

import HouseholdListView from '@/views/households/HouseholdListView.vue'
import HouseholdFormView from '@/views/households/HouseholdFormView.vue'
import HouseholdDetailView from '@/views/households/HouseholdDetailView.vue'
import HouseholdDashboardView from '@/views/households/HouseholdDashboardView.vue'

import EvacuationCenterListView from '@/views/evacuation-centers/EvacuationCenterListView.vue'
import EvacuationCenterFormView from '@/views/evacuation-centers/EvacuationCenterFormView.vue'
import EvacuationCenterDetailView from '@/views/evacuation-centers/EvacuationCenterDetailView.vue'

import AnnouncementListView from '@/views/announcements/AnnouncementListView.vue'
import AnnouncementFormView from '@/views/announcements/AnnouncementFormView.vue'
import SmsNotificationListView from '@/views/announcements/SmsNotificationListView.vue'

import HazardMapListView from '@/views/maps/HazardMapListView.vue'
import HazardMapFormView from '@/views/maps/HazardMapFormView.vue'

import ReportsView from '@/views/reports/ReportsView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: '/households',
    name: 'households',
    component: HouseholdListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/households/new',
    name: 'household-new',
    component: HouseholdFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/households/dashboard',
    name: 'household-dashboard',
    component: HouseholdDashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/households/:id/edit',
    name: 'household-edit',
    component: HouseholdFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/households/:id',
    name: 'household-detail',
    component: HouseholdDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/evacuation-centers',
    name: 'evacuation-centers',
    component: EvacuationCenterListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/evacuation-centers/new',
    name: 'evacuation-center-new',
    component: EvacuationCenterFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/evacuation-centers/:id/edit',
    name: 'evacuation-center-edit',
    component: EvacuationCenterFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/evacuation-centers/:id',
    name: 'evacuation-center-detail',
    component: EvacuationCenterDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/announcements',
    name: 'announcements',
    component: AnnouncementListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/announcements/new',
    name: 'announcement-new',
    component: AnnouncementFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/announcements/:id/edit',
    name: 'announcement-edit',
    component: AnnouncementFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/sms-notifications',
    name: 'sms-notifications',
    component: SmsNotificationListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/hazard-maps',
    name: 'hazard-maps',
    component: HazardMapListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/hazard-maps/new',
    name: 'hazard-map-new',
    component: HazardMapFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/hazard-maps/:id/edit',
    name: 'hazard-map-edit',
    component: HazardMapFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'reports',
    component: ReportsView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router