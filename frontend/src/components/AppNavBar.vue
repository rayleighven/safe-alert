<template>
  <nav class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
    <div>
      <router-link to="/" class="text-lg font-bold text-slate-800 hover:text-blue-600">SAFE-ALERT</router-link>
      <p class="text-xs text-slate-500">{{ authStore.user?.role }}</p>
    </div>
    <div class="flex items-center gap-4 text-sm">
      <router-link to="/" class="text-slate-600 hover:text-blue-600">Dashboard</router-link>
      <router-link v-if="canViewHouseholds" to="/households" class="text-slate-600 hover:text-blue-600">
        Households
      </router-link>
      <router-link v-if="canViewVulnerabilityDashboard" to="/households/dashboard" class="text-slate-600 hover:text-blue-600">
        Vulnerability Dashboard
      </router-link>
      <router-link to="/evacuation-centers" class="text-slate-600 hover:text-blue-600">
        Evacuation Centers
      </router-link>
      <router-link to="/profile" class="text-slate-600 hover:text-blue-600">Profile</router-link>
      <button @click="handleLogout" class="text-red-600 hover:text-red-700">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

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

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>