<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-4xl mx-auto">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-slate-800">Hazard Maps</h1>
        <router-link
          v-if="isSecretary"
          to="/hazard-maps/new"
          class="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2"
        >
          + New Map Reference
        </router-link>
      </div>
      <p class="text-slate-500 text-sm mb-6">
        Official hazard maps for your barangay, sourced from Project NOAH and other agencies. Click a card to open the full map.
      </p>

      <div v-if="isLoading" class="text-slate-500">Loading hazard maps...</div>
      <div v-else-if="maps.length === 0" class="text-slate-500">No hazard maps have been added yet.</div>

      <div v-else class="space-y-8">
        <div v-for="group in groupedMaps" :key="group.hazardType">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-3 flex items-center gap-2">
            <span :class="hazardDotClass(group.hazardType)" class="w-2 h-2 rounded-full"></span>
            {{ group.hazardType }}
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="map in group.maps"
              :key="map.map_id"
              class="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between mb-2">
                <h3 class="font-semibold text-slate-800">{{ map.map_title }}</h3>
                <span :class="hazardBadgeClass(map.hazard_type)" class="px-2 py-1 rounded-full text-xs font-medium shrink-0 ml-2">
                  {{ map.hazard_type }}
                </span>
              </div>
              <p v-if="map.description" class="text-sm text-slate-500 mb-3">{{ map.description }}</p>
              <p class="text-xs text-slate-400 mb-4">Source: {{ map.source }}</p>

              <div class="flex items-center justify-between">
                <a
                  :href="map.map_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-sm text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1"
                >
                  Open Map
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </a>
                <div v-if="isSecretary" class="flex gap-3 text-xs">
                  <router-link :to="{ name: 'hazard-map-edit', params: { id: map.map_id } }" class="text-slate-500 hover:text-blue-600">
                    Edit
                  </router-link>
                  <button @click="handleArchive(map.map_id)" class="text-slate-500 hover:text-red-600">Archive</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as mapsApi from '@/services/mapsApi'

const authStore = useAuthStore()
const maps = ref([])
const isLoading = ref(true)

const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

const HAZARD_ORDER = ['Flood', 'Storm Surge', 'Landslide', 'Earthquake']

const groupedMaps = computed(() => {
  return HAZARD_ORDER.map((hazardType) => ({
    hazardType,
    maps: maps.value.filter((m) => m.hazard_type === hazardType),
  })).filter((group) => group.maps.length > 0)
})

function hazardBadgeClass(hazardType) {
  const map = {
    Flood: 'bg-blue-100 text-blue-700',
    'Storm Surge': 'bg-cyan-100 text-cyan-700',
    Landslide: 'bg-amber-100 text-amber-700',
    Earthquake: 'bg-red-100 text-red-700',
  }
  return map[hazardType] || 'bg-slate-100 text-slate-600'
}

function hazardDotClass(hazardType) {
  const map = {
    Flood: 'bg-blue-500',
    'Storm Surge': 'bg-cyan-500',
    Landslide: 'bg-amber-500',
    Earthquake: 'bg-red-500',
  }
  return map[hazardType] || 'bg-slate-400'
}

async function loadMaps() {
  isLoading.value = true
  const response = await mapsApi.listHazardMaps()
  maps.value = response.data
  isLoading.value = false
}

onMounted(loadMaps)

async function handleArchive(mapId) {
  if (!confirm('Archive this hazard map reference?')) return
  await mapsApi.archiveHazardMap(mapId)
  await loadMaps()
}
</script>