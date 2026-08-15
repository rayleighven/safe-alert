<template>
  <nav v-if="standalone" class="relative z-20 bg-white shadow-sm">
    <div class="flex items-center justify-between px-6 py-4">
      <div>
        <router-link to="/" class="text-lg font-bold text-slate-800 hover:text-blue-600" @click="closeMenu">
          SAFE-ALERT
        </router-link>
        <p class="text-xs text-slate-500">{{ authStore.user?.role }}</p>
      </div>

      <button
        type="button"
        class="rounded-lg p-2 text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        :aria-expanded="isMenuOpen"
        aria-controls="main-navigation"
        aria-label="Toggle navigation menu"
        @click="isMenuOpen = !isMenuOpen"
      >
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>

    <div
      v-if="isMenuOpen"
      id="main-navigation"
      class="absolute right-6 top-full mt-2 w-64 overflow-hidden rounded-xl border border-slate-200 bg-white py-2 shadow-lg"
    >
      <div class="flex flex-col text-sm">
        <router-link to="/" class="menu-link" @click="closeMenu">Dashboard</router-link>
        <router-link v-if="canViewHouseholds" to="/households" class="menu-link" @click="closeMenu">Households</router-link>
        <router-link v-if="canViewVulnerabilityDashboard" to="/households/dashboard" class="menu-link" @click="closeMenu">
          Vulnerability Dashboard
        </router-link>
        <router-link to="/evacuation-centers" class="menu-link" @click="closeMenu">Evacuation Centers</router-link>
        <router-link to="/announcements" class="menu-link" @click="closeMenu">Announcements</router-link>
        <router-link v-if="canViewSmsBroadcasts" to="/sms-notifications" class="menu-link" @click="closeMenu">SMS Broadcasts</router-link>
        <router-link to="/hazard-maps" class="menu-link" @click="closeMenu">Hazard Maps</router-link>
        <router-link v-if="canViewReports" to="/reports" class="menu-link" @click="closeMenu">Reports</router-link>
        <router-link v-if="isSecretary" to="/accounts" class="menu-link" @click="closeMenu">Accounts</router-link>
        <router-link to="/profile" class="menu-link" @click="closeMenu">Profile</router-link>
        <button type="button" class="menu-link text-left text-red-600 hover:text-red-700" @click="handleLogout">Logout</button>
      </div>
    </div>
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
import ConfirmActionDialog from '@/components/ConfirmActionDialog.vue'

defineProps({
  standalone: { type: Boolean, default: false },
})

const authStore = useAuthStore()
const router = useRouter()
const isMenuOpen = ref(false)
const showLogoutConfirm = ref(false)

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

const canViewVulnerabilityDashboard = computed(() => {
  const role = authStore.user?.role
  return [
    'Barangay Secretary',
    'Barangay Kagawad/Tanod',
    'Barangay Healthworker',
    'MDRRMO Officer',
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
.menu-link {
  @apply border-b border-slate-100 px-3 py-3 font-medium text-slate-700 transition-colors hover:bg-slate-50 hover:text-blue-600;
}

.menu-link:last-child {
  @apply border-b-0;
}
</style>
