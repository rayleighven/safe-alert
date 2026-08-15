<template>
  <aside class="hidden h-full w-72 shrink-0 flex-col bg-[#0d2f57] text-slate-200 shadow-xl lg:flex">
    <div class="flex h-[72px] items-center gap-3 border-b border-white/10 px-6">
      <img :src="safeAlertLogo" alt="SAFE-ALERT" class="h-9 w-9 object-contain" />
      <div>
        <p class="text-base font-bold tracking-wide text-white">SAFE-ALERT</p>
        <p class="text-xs text-blue-200">Baclayon, Bohol</p>
      </div>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-5">
      <p class="nav-section">Overview</p>
      <router-link :to="{ name: 'dashboard' }" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 11.5 12 4l9 7.5v8a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1v-8Z" /></svg>
        <span>Dashboard</span>
      </router-link>
      <p v-if="canViewHouseholds || canViewVulnerabilityDashboard" class="nav-section">Household Records</p>
      <router-link v-if="canViewHouseholds" to="/households" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1m7-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11 9v-1a4 4 0 0 0-3-3.87m-1-12a4 4 0 0 1 0 7.75" /></svg>
        <span>Households</span>
      </router-link>
      <router-link v-if="canViewVulnerabilityDashboard" to="/households/dashboard" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M4 19V5m0 14h16M8 16v-4m4 4V8m4 8v-6" /></svg>
        <span>Vulnerability Dashboard</span>
      </router-link>
      <p class="nav-section">Response Operations</p>
      <router-link to="/evacuation-centers" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="m3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6" /></svg>
        <span>Evacuation Centers</span>
      </router-link>
      <router-link to="/hazard-maps" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Zm0-15v15m6-12v15" /></svg>
        <span>Hazard Maps</span>
      </router-link>
      <p class="nav-section">Communication</p>
      <router-link to="/announcements" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M4 11v2a2 2 0 0 0 2 2h2l5 4V5l-5 4H6a2 2 0 0 0-2 2Zm11.5-3.5a5 5 0 0 1 0 9" /></svg>
        <span>Announcements</span>
      </router-link>
      <router-link v-if="canViewSmsBroadcasts" to="/sms-notifications" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.7 9.7 0 0 1-4.2-1L3 20l1.1-4A8.4 8.4 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5Z" /></svg>
        <span>SMS Broadcasts</span>
      </router-link>
      <p v-if="canViewReports" class="nav-section">Administration</p>
      <router-link v-if="canViewReports" to="/reports" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M6 3h9l3 3v15H6V3Zm3 8h6m-6 4h6m-6-8h2" /></svg>
        <span>Reports</span>
      </router-link>
      <router-link v-if="isSecretary" to="/accounts" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m12-11a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm2 3.5a4 4 0 0 1 0 7" /></svg>
        <span>Accounts</span>
      </router-link>
    </nav>

    <div class="border-t border-white/10 p-4">
      <div class="mb-3 flex items-center gap-3 px-2">
        <div class="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full bg-blue-500 text-xs font-bold text-white">
          <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="" class="h-full w-full object-cover" />
          <span v-else>{{ userInitials }}</span>
        </div>
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold text-white">{{ displayName }}</p>
          <p class="truncate text-xs text-blue-200">{{ authStore.user?.role }}</p>
        </div>
      </div>
      <router-link to="/profile" class="nav-link mb-1" active-class="nav-link-active">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M20 21a8 8 0 0 0-16 0m12-14a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z" /></svg>
        <span>Profile</span>
      </router-link>
      <button type="button" class="nav-link w-full text-left hover:bg-red-500/10 hover:text-red-200" @click="handleLogout">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M10 17l5-5-5-5m5 5H3m10-8h5a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-5" /></svg>
        <span>Logout</span>
      </button>
    </div>
    <ConfirmActionDialog
      v-if="showLogoutConfirm"
      title="Log out of SAFE-ALERT?"
      message="You will need to sign in again to access your account."
      confirm-label="Log out"
      confirm-class="bg-red-600 hover:bg-red-700"
      title-id="sidebar-logout-confirmation"
      @cancel="showLogoutConfirm = false"
      @confirm="confirmLogout"
    />
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ConfirmActionDialog from '@/components/ConfirmActionDialog.vue'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'

const authStore = useAuthStore()
const router = useRouter()
const showLogoutConfirm = ref(false)
const role = computed(() => authStore.user?.role)
const displayName = computed(() => authStore.user?.first_name || authStore.user?.username || 'User')
const userInitials = computed(() => displayName.value.slice(0, 2).toUpperCase())
const canViewHouseholds = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer', 'Resident'].includes(role.value))
const canViewVulnerabilityDashboard = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer'].includes(role.value))
const canViewSmsBroadcasts = computed(() => ['Barangay Secretary', 'BDRRMC Chairperson', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer'].includes(role.value))
const canViewReports = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'BDRRMC Chairperson', 'MDRRMO Officer', 'Resident'].includes(role.value))
const isSecretary = computed(() => role.value === 'Barangay Secretary')

function handleLogout() {
  showLogoutConfirm.value = true
}

async function confirmLogout() {
  showLogoutConfirm.value = false
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.nav-link {
  @apply mb-1 flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium text-blue-100 transition-colors hover:bg-white/10 hover:text-white;
}

.nav-link-active {
  @apply bg-gradient-to-r from-blue-500 to-blue-600 font-semibold text-white shadow-lg shadow-blue-950/20;
}

.nav-section {
  @apply mb-2 mt-5 px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-blue-300/70;
}
</style>
