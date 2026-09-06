<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-slate-800">Evacuation Centers</h1>
        <router-link
          v-if="isSecretary"
          to="/evacuation-centers/new"
          class="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2"
        >
          + New Center
        </router-link>
      </div>

      <div v-if="isLoading" class="text-slate-500">Loading evacuation centers...</div>
      <div v-else-if="centers.length === 0" class="text-slate-500">No evacuation centers found.</div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="center in centers"
          :key="center.center_id"
          class="bg-white rounded-xl shadow-sm p-5 cursor-pointer hover:shadow-md transition-shadow"
          @click="router.push({ name: 'evacuation-center-detail', params: { id: center.center_id } })"
        >
          <div v-if="center.photo || center.photo_url" class="-mx-5 -mt-5 mb-3 overflow-hidden rounded-t-xl">
            <img :src="center.photo || center.photo_url" :alt="`${center.name} photo`" class="h-32 w-full object-cover" />
          </div>
          <div class="flex items-center justify-between mb-2">
            <h2 class="font-semibold text-slate-800">{{ center.name }}</h2>
            <span :class="statusBadgeClass(center.status)" class="px-2 py-1 rounded-full text-xs font-medium">
              {{ center.status }}
            </span>
          </div>
          <p class="text-sm text-slate-500 mb-3">{{ center.address }}</p>
          <div class="flex justify-between text-sm text-slate-600 mb-1">
            <span>Occupancy</span>
            <span>{{ center.current_occupancy }} / {{ center.capacity }}</span>
          </div>
          <div class="w-full bg-slate-100 rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all"
              :class="occupancyBarClass(center)"
              :style="{ width: occupancyPercent(center) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as evacuationCentersApi from '@/services/evacuationCentersApi'

const router = useRouter()
const authStore = useAuthStore()

const centers = ref([])
const isLoading = ref(true)

const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

function statusBadgeClass(status) {
  if (status === 'Active') return 'bg-green-100 text-green-700'
  if (status === 'Under Maintenance') return 'bg-yellow-100 text-yellow-700'
  return 'bg-slate-100 text-slate-600'
}

function occupancyPercent(center) {
  if (!center.capacity) return 0
  return Math.min(100, Math.round((center.current_occupancy / center.capacity) * 100))
}

function occupancyBarClass(center) {
  const percent = occupancyPercent(center)
  if (percent >= 90) return 'bg-red-500'
  if (percent >= 60) return 'bg-yellow-500'
  return 'bg-green-500'
}

onMounted(async () => {
  try {
    const response = await evacuationCentersApi.listCenters()
    centers.value = response.data
  } finally {
    isLoading.value = false
  }
})
</script>