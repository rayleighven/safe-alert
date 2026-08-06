<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />

    <main class="p-6">
      <h2 class="text-xl font-semibold text-slate-800 mb-2">
        Welcome, {{ authStore.user?.first_name || authStore.user?.username }}
      </h2>
      <p class="text-slate-500 mb-6">{{ roleDescription }}</p>

      <div class="bg-white rounded-xl shadow-sm p-6 text-slate-500">
        This dashboard will fill in as each module is built (Evacuation Centers,
        Announcements, Maps, Reports).
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'

const authStore = useAuthStore()

const roleDescriptions = {
  'Barangay Secretary': 'Full system administration and household record management.',
  'BDRRMC Chairperson': 'Executive oversight and SMS broadcast authorization.',
  'MDRRMO Officer': 'Read-only municipal-level monitoring across both barangays.',
  'Barangay Kagawad/Tanod': 'Field validation and evacuation center management.',
  'Barangay Healthworker': 'Health-related vulnerability indicator management.',
  Resident: 'View your household information and public announcements.',
}

const roleDescription = computed(() => roleDescriptions[authStore.user?.role] || '')
</script>