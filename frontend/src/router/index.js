import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/auth/LoginView.vue'
import LandingView from '@/views/auth/LandingView.vue'
import AccessSelectionView from '@/views/auth/AccessSelectionView.vue'
import ProfileView from '@/views/auth/ProfileView.vue'
import AccountsView from '@/views/auth/AccountsView.vue'
import DashboardView from '@/views/DashboardView.vue'

import HouseholdListView from '@/views/households/HouseholdListView.vue'
import HouseholdFormView from '@/views/households/HouseholdFormView.vue'
import HouseholdDetailView from '@/views/households/HouseholdDetailView.vue'

import EvacuationCenterListView from '@/views/evacuation-centers/EvacuationCenterListView.vue'
import EvacuationCenterFormView from '@/views/evacuation-centers/EvacuationCenterFormView.vue'
import EvacuationCenterDetailView from '@/views/evacuation-centers/EvacuationCenterDetailView.vue'

import AnnouncementListView from '@/views/announcements/AnnouncementListView.vue'
import AnnouncementFormView from '@/views/announcements/AnnouncementFormView.vue'
import SmsNotificationListView from '@/views/announcements/SmsNotificationListView.vue'

import HazardMapListView from '@/views/maps/HazardMapListView.vue'
import HazardMapFormView from '@/views/maps/HazardMapFormView.vue'

import ReportsView from '@/views/reports/ReportsView.vue'
import ArchiveDashboardView from '@/views/ArchiveDashboardView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const routes = [
  { path: '/', name: 'landing', component: LandingView, meta: { requiresAuth: false } },
  { path: '/sign-in', name: 'access-select', component: AccessSelectionView, meta: { requiresAuth: false } },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/dashboard',
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
    path: '/accounts',
    name: 'accounts',
    component: AccountsView,
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
    path: '/hazard-maps/:id/interactive',
    name: 'hazard-map-interactive',
    // Lazy-loaded: pulls in MapLibre GL, which is large and only needed here.
    component: () => import('@/views/maps/HazardMapInteractiveView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'reports',
    component: ReportsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/archives',
    name: 'archives',
    component: ArchiveDashboardView,
    meta: { requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView, meta: { requiresAuth: false, title: 'Page not found', description: 'The requested SAFE-ALERT page could not be found.' } },
]

const pageMeta = {
  landing: ['SAFE-ALERT | Community Readiness', 'SAFE-ALERT supports disaster readiness and emergency coordination in Baclayon, Bohol.'],
  'access-select': ['Choose Access | SAFE-ALERT', 'Choose the area associated with your SAFE-ALERT account.'],
  login: ['Sign In | SAFE-ALERT', 'Sign in to access SAFE-ALERT disaster readiness tools.'],
  dashboard: ['Dashboard | SAFE-ALERT', 'View community readiness and emergency coordination information.'],
  profile: ['Profile | SAFE-ALERT', 'Manage your SAFE-ALERT profile and account security.'],
  accounts: ['Accounts | SAFE-ALERT', 'Manage SAFE-ALERT user accounts.'],
  households: ['Households | SAFE-ALERT', 'View and manage household readiness records.'],
  'household-new': ['Add Household | SAFE-ALERT', 'Create household readiness records.'],
  'household-edit': ['Edit Household | SAFE-ALERT', 'Update household readiness records.'],
  'household-detail': ['Household Details | SAFE-ALERT', 'View household details and family members.'],
  'evacuation-centers': ['Evacuation Centers | SAFE-ALERT', 'View evacuation centers and their readiness information.'],
  'evacuation-center-new': ['Add Evacuation Center | SAFE-ALERT', 'Add an evacuation center to SAFE-ALERT.'],
  'evacuation-center-edit': ['Edit Evacuation Center | SAFE-ALERT', 'Update evacuation center information.'],
  'evacuation-center-detail': ['Evacuation Center Details | SAFE-ALERT', 'View evacuation center details and check-ins.'],
  announcements: ['Announcements | SAFE-ALERT', 'Read community safety announcements and advisories.'],
  'announcement-new': ['New Announcement | SAFE-ALERT', 'Create a community safety announcement.'],
  'announcement-edit': ['Edit Announcement | SAFE-ALERT', 'Update a community safety announcement.'],
  'sms-notifications': ['SMS Broadcasts | SAFE-ALERT', 'Review and authorize emergency SMS broadcasts.'],
  'hazard-maps': ['Hazard Maps | SAFE-ALERT', 'View hazard map references for Baclayon, Bohol.'],
  'hazard-map-new': ['Add Hazard Map | SAFE-ALERT', 'Add a hazard map reference.'],
  'hazard-map-edit': ['Edit Hazard Map | SAFE-ALERT', 'Update a hazard map reference.'],
  'hazard-map-interactive': ['Interactive Hazard Map | SAFE-ALERT', 'Explore interactive hazard information.'],
  reports: ['Reports | SAFE-ALERT', 'View and download SAFE-ALERT reports.'],
  archives: ['Archives | SAFE-ALERT', 'View and restore archived records.'],
}

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  const [title, description] = pageMeta[to.name] || [to.meta.title || 'SAFE-ALERT', to.meta.description || 'SAFE-ALERT community disaster readiness system for Baclayon, Bohol.']
  document.title = title
  document.querySelector('meta[name="description"]')?.setAttribute('content', description)
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (['landing', 'access-select', 'login'].includes(to.name) && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else if (to.name === 'login' && !to.query.access) {
    next({ name: 'access-select' })
  } else {
    next()
  }
})

export default router
