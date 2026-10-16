<template>
  <aside class="hidden h-full w-72 shrink-0 flex-col bg-[#0b2545] text-slate-200 shadow-xl lg:flex">
    <!-- Brand Header -->
    <div class="flex h-[72px] items-center gap-3 border-b border-white/10 px-6">
      <router-link
        :to="{ name: 'dashboard' }"
        class="flex min-w-0 items-center gap-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        aria-label="SAFE-ALERT dashboard"
      >
        <img :src="safeAlertLogo" alt="" class="h-10 w-10 shrink-0 object-contain drop-shadow" />
        <div class="min-w-0">
          <p class="text-base font-bold tracking-wide text-white">SAFE-ALERT</p>
          <p class="text-xs font-medium text-blue-200/80">Baclayon, Bohol</p>
        </div>
      </router-link>
    </div>

    <!-- Navigation List -->
    <nav class="flex-1 overflow-y-auto px-3 py-5" aria-label="Main sidebar navigation">
      <p class="nav-section">Overview</p>
      <router-link :to="{ name: 'dashboard' }" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" rx="1.5" />
          <rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="14" y="14" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" />
        </svg>
        <span>Dashboard</span>
      </router-link>

      <template v-if="canViewHouseholds">
        <p class="nav-section">Household Records</p>
        <router-link to="/households" class="nav-link" active-class="nav-link-active">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1m7-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11 9v-1a4 4 0 0 0-3-3.87m-1-12a4 4 0 0 1 0 7.75" />
          </svg>
          <span>Household Records</span>
        </router-link>
      </template>

      <p class="nav-section">Response Operations</p>
      <router-link to="/evacuation-centers" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="m3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6" />
        </svg>
        <span>Evacuation Centers</span>
      </router-link>
      <router-link to="/hazard-maps" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Zm0-15v15m6-12v15" />
        </svg>
        <span>Hazard Maps</span>
      </router-link>

      <p class="nav-section">Communication</p>
      <router-link to="/announcements" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 11v2a2 2 0 0 0 2 2h2l5 4V5l-5 4H6a2 2 0 0 0-2 2Zm11.5-3.5a5 5 0 0 1 0 9" />
        </svg>
        <span>Announcements</span>
      </router-link>
      <router-link v-if="canViewSmsBroadcasts" to="/sms-notifications" class="nav-link" active-class="nav-link-active">
        <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.7 9.7 0 0 1-4.2-1L3 20l1.1-4A8.4 8.4 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5Z" />
        </svg>
        <span class="flex-1">SMS Broadcasts</span>
      </router-link>

      <template v-if="canViewReports || isSecretary">
        <p class="nav-section">Administration</p>
        <router-link v-if="canViewReports" to="/reports" class="nav-link" active-class="nav-link-active">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 3h9l3 3v15H6V3Zm3 8h6m-6 4h6m-6-8h2" />
          </svg>
          <span>Reports</span>
        </router-link>
        <router-link v-if="isSecretary" to="/archives" class="nav-link" active-class="nav-link-active">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
          </svg>
          <span>Archives</span>
        </router-link>
        <router-link v-if="isSecretary" to="/accounts" class="nav-link" active-class="nav-link-active">
          <svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m12-11a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm2 3.5a4 4 0 0 1 0 7" />
          </svg>
          <span>User Accounts</span>
        </router-link>
      </template>
    </nav>

    <!-- Bottom User Profile Footer -->
    <div class="border-t border-white/10 p-3">
      <div class="flex items-center justify-between rounded-xl bg-white/5 p-2.5 transition-colors hover:bg-white/10">
        <router-link
          to="/profile"
          class="flex min-w-0 flex-1 items-center gap-3 focus:outline-none focus:ring-1 focus:ring-blue-400 rounded-lg p-1"
          aria-label="View user profile"
        >
          <div class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-blue-600 text-xs font-bold text-white shadow-inner">
            <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="" class="h-full w-full object-cover" />
            <span v-else>{{ userInitials }}</span>
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-xs font-semibold text-white">{{ displayName }}</p>
            <p class="truncate text-[11px] text-blue-200/70">{{ authStore.user?.role }}</p>
          </div>
        </router-link>
        <button
          type="button"
          class="rounded-lg p-2 text-blue-300 transition-colors hover:bg-white/10 hover:text-white focus:outline-none focus:ring-1 focus:ring-blue-400"
          title="Log out"
          aria-label="Log out of SAFE-ALERT"
          @click="showLogoutConfirm = true"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
          </svg>
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
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'
import ConfirmActionDialog from '@/components/ConfirmActionDialog.vue'

const authStore = useAuthStore()
const router = useRouter()
const showLogoutConfirm = ref(false)

const role = computed(() => authStore.user?.role)
const displayName = computed(() => authStore.user?.first_name || authStore.user?.username || 'User')
const userInitials = computed(() => displayName.value?.slice(0, 2).toUpperCase() || 'U')

const canViewHouseholds = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer', 'Resident'].includes(role.value))
const canViewSmsBroadcasts = computed(() => ['Barangay Secretary', 'BDRRMC Chairperson', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer'].includes(role.value))
const canViewReports = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'BDRRMC Chairperson', 'MDRRMO Officer', 'Resident'].includes(role.value))
const isSecretary = computed(() => role.value === 'Barangay Secretary')

async function confirmLogout() {
  showLogoutConfirm.value = false
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.nav-link {
  @apply mb-1 flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-300 transition-all duration-150 hover:bg-white/10 hover:text-white;
}

.nav-link-active {
  @apply bg-blue-600 font-semibold text-white shadow-md shadow-blue-950/30;
}

.nav-section {
  @apply mb-2 mt-5 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-blue-300/60;
}
</style>
