<template>
  <nav v-if="standalone" class="relative z-30 bg-white border-b border-slate-200/80 shadow-xs">
    <div class="flex items-center justify-between gap-3 px-4 py-3 sm:px-6">
      <!-- Mobile Logo and Role -->
      <router-link :to="{ name: 'dashboard' }" class="flex items-center gap-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" @click="closeMenu">
        <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-8 w-8 object-contain" />
        <div>
          <span class="block text-base font-bold tracking-tight text-slate-900 leading-none">SAFE-ALERT</span>
          <span class="block text-[11px] font-medium text-slate-500 leading-tight mt-0.5">{{ authStore.user?.role || 'Community Readiness' }}</span>
        </div>
      </router-link>

      <!-- Current Time + Hamburger -->
      <div class="flex items-center gap-2">
        <CurrentDateTime class="hidden sm:flex text-xs px-2.5 py-1" />

        <button
          type="button"
          class="flex h-11 w-11 items-center justify-center rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :aria-expanded="isMenuOpen"
          aria-controls="mobile-navigation"
          aria-label="Toggle navigation menu"
          @click="isMenuOpen = !isMenuOpen"
        >
          <svg v-if="!isMenuOpen" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
          <svg v-else class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Navigation Drawer Overlay -->
    <div
      v-if="isMenuOpen"
      class="fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-xs transition-opacity"
      @click="closeMenu"
      aria-hidden="true"
    />

    <!-- Mobile Drawer Panel -->
    <div
      v-if="isMenuOpen"
      id="mobile-navigation"
      class="fixed inset-y-0 right-0 z-50 flex w-full max-w-xs flex-col bg-[#0b2545] text-slate-200 shadow-2xl transition-transform"
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation"
    >
      <!-- Drawer Header -->
      <div class="flex h-16 items-center justify-between border-b border-white/10 px-5">
        <div class="flex items-center gap-2.5">
          <img :src="safeAlertLogo" alt="" class="h-8 w-8 object-contain" />
          <span class="text-base font-bold text-white tracking-wide">SAFE-ALERT</span>
        </div>
        <button
          type="button"
          class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-300 hover:bg-white/10 hover:text-white"
          aria-label="Close menu"
          @click="closeMenu"
        >
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- User Card in Drawer -->
      <div class="border-b border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-blue-600 font-bold text-white shadow-inner">
            <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="" class="h-full w-full object-cover" />
            <span v-else>{{ userInitials }}</span>
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-white">{{ displayName }}</p>
            <p class="truncate text-xs text-blue-200/70">{{ authStore.user?.role }}</p>
          </div>
        </div>
      </div>

      <!-- Drawer Nav Links -->
      <div class="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <router-link :to="{ name: 'dashboard' }" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="3" width="7" height="7" rx="1.5" />
            <rect x="14" y="3" width="7" height="7" rx="1.5" />
            <rect x="14" y="14" width="7" height="7" rx="1.5" />
            <rect x="3" y="14" width="7" height="7" rx="1.5" />
          </svg>
          <span>Dashboard</span>
        </router-link>

        <router-link v-if="canViewHouseholds" to="/households" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1m7-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11 9v-1a4 4 0 0 0-3-3.87m-1-12a4 4 0 0 1 0 7.75" />
          </svg>
          <span>Household Records</span>
        </router-link>

        <router-link to="/evacuation-centers" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="m3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6" />
          </svg>
          <span>Evacuation Centers</span>
        </router-link>

        <router-link to="/hazard-maps" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Zm0-15v15m6-12v15" />
          </svg>
          <span>Hazard Maps</span>
        </router-link>

        <router-link to="/announcements" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 11v2a2 2 0 0 0 2 2h2l5 4V5l-5 4H6a2 2 0 0 0-2 2Zm11.5-3.5a5 5 0 0 1 0 9" />
          </svg>
          <span>Announcements</span>
        </router-link>

        <router-link v-if="canViewSmsBroadcasts" to="/sms-notifications" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.7 9.7 0 0 1-4.2-1L3 20l1.1-4A8.4 8.4 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5Z" />
          </svg>
          <span>SMS Broadcasts</span>
        </router-link>

        <router-link v-if="canViewReports" to="/reports" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 3h9l3 3v15H6V3Zm3 8h6m-6 4h6m-6-8h2" />
          </svg>
          <span>Reports</span>
        </router-link>

        <router-link v-if="isSecretary" to="/archives" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
          </svg>
          <span>Archives</span>
        </router-link>

        <router-link v-if="isSecretary" to="/accounts" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m12-11a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm2 3.5a4 4 0 0 1 0 7" />
          </svg>
          <span>User Accounts</span>
        </router-link>

        <router-link to="/profile" class="mobile-nav-link" active-class="mobile-nav-active" @click="closeMenu">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
          </svg>
          <span>Profile Settings</span>
        </router-link>
      </div>

      <!-- Logout Action in Drawer -->
      <div class="border-t border-white/10 p-4">
        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-xl bg-red-600/90 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400"
          @click="handleLogout"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
          </svg>
          <span>Sign Out</span>
        </button>
      </div>
    </div>

    <!-- Confirm Logout Dialog -->
    <ConfirmActionDialog
      v-if="showLogoutConfirm"
      title="Log out of SAFE-ALERT?"
      message="You will need to sign in again to access your account."
      confirm-label="Log out"
      confirm-class="bg-red-600 hover:bg-red-700"
      title-id="mobile-logout-confirmation"
      @cancel="showLogoutConfirm = false"
      @confirm="confirmLogout"
    />
  </nav>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'
import ConfirmActionDialog from '@/components/ConfirmActionDialog.vue'
import CurrentDateTime from '@/components/CurrentDateTime.vue'

defineProps({
  standalone: { type: Boolean, default: false },
})

const authStore = useAuthStore()
const router = useRouter()
const isMenuOpen = ref(false)
const showLogoutConfirm = ref(false)

const displayName = computed(() => authStore.user?.first_name || authStore.user?.username || 'User')
const userInitials = computed(() => displayName.value?.slice(0, 2).toUpperCase() || 'U')

const canViewHouseholds = computed(() => {
  const role = authStore.user?.role
  return [
    'Barangay Secretary',
    'Barangay Kagawad/Tanod',
    'Barangay Healthworker',
    'MDRRMO Officer',
    'Resident',
  ].includes(role)
})

const canViewSmsBroadcasts = computed(() => {
  const role = authStore.user?.role
  return [
    'Barangay Secretary',
    'BDRRMC Chairperson',
    'Barangay Kagawad/Tanod',
    'Barangay Healthworker',
    'MDRRMO Officer',
  ].includes(role)
})

const canViewReports = computed(() => {
  const role = authStore.user?.role
  return [
    'Barangay Secretary',
    'Barangay Kagawad/Tanod',
    'Barangay Healthworker',
    'BDRRMC Chairperson',
    'MDRRMO Officer',
    'Resident',
  ].includes(role)
})
const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

function handleLogout() {
  closeMenu()
  showLogoutConfirm.value = true
}

async function confirmLogout() {
  showLogoutConfirm.value = false
  await authStore.logout()
  router.push({ name: 'login' })
}

function closeMenu() {
  isMenuOpen.value = false
}
</script>

<style scoped>
.mobile-nav-link {
  @apply flex min-h-11 items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-300 transition-colors hover:bg-white/10 hover:text-white;
}

.mobile-nav-active {
  @apply bg-blue-600 font-semibold text-white shadow-sm;
}
</style>
