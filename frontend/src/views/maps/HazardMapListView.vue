<template>
  <div class="space-y-6 pb-6 max-w-5xl">
    <!-- Breadcrumb & Header -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Hazard Maps</span>
      </nav>

      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Hazard Exposure Maps</h1>
          <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            Official hazard maps for Baclayon barangays, sourced from Project NOAH and national hazard monitoring agencies.
          </p>
        </div>
        <router-link
          v-if="isSecretary"
          to="/hazard-maps/new"
          class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>New Map Reference</span>
        </router-link>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="inline-flex h-10 w-10 animate-spin items-center justify-center rounded-full border-2 border-blue-600 border-t-transparent text-blue-600" />
      <p class="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Loading hazard maps...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="maps.length === 0" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Zm0-15v15m6-12v15" />
        </svg>
      </div>
      <h3 class="mt-4 text-sm font-bold text-slate-800">No hazard maps cataloged</h3>
      <p class="mt-1 text-xs text-slate-500">Official hazard map resources will appear here once registered.</p>
    </div>

    <!-- Grouped Maps by Hazard Type -->
    <div v-else class="space-y-8">
      <section v-for="group in groupedMaps" :key="group.hazardType" class="space-y-4">
        <div class="flex items-center gap-2.5 border-b border-slate-200/70 pb-2.5">
          <span :class="hazardDotClass(group.hazardType)" class="h-2.5 w-2.5 rounded-full ring-2 ring-white shadow-xs" />
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-700">{{ group.hazardType }} Hazard Maps</h2>
          <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-500">{{ group.maps.length }}</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <article
            v-for="map in group.maps"
            :key="map.map_id"
            class="group flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card transition-all duration-200 hover:border-slate-300 hover:shadow-card-hover"
          >
            <div>
              <!-- Clickable Image Thumbnail with Preview Hover Cue -->
              <div
                v-if="map.map_image"
                class="group/thumb relative -mx-5 -mt-5 mb-4 overflow-hidden border-b border-slate-100 bg-slate-100 cursor-pointer"
                title="Click to preview full map"
                tabindex="0"
                @click="openPreview(map)"
                @keydown.enter="openPreview(map)"
              >
                <img
                  :src="map.map_image"
                  :alt="`${map.map_title} image`"
                  class="h-48 w-full object-cover transition-transform duration-300 group-hover/thumb:scale-105"
                />
                <div class="absolute inset-0 bg-slate-900/40 opacity-0 group-hover/thumb:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white font-bold text-xs backdrop-blur-2xs">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  </svg>
                  <span>Click to Preview Full Map</span>
                </div>
              </div>

              <!-- Title & Hazard Badge -->
              <div class="flex items-start justify-between gap-3 mb-2">
                <h3 class="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors">{{ map.map_title }}</h3>
                <span :class="hazardBadgeClass(map.hazard_type)" class="inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold">
                  {{ map.hazard_type }}
                </span>
              </div>

              <p v-if="map.description" class="text-xs sm:text-sm text-slate-600 mb-3 leading-relaxed line-clamp-3">{{ map.description }}</p>
              <p class="text-[11px] font-medium text-slate-400 mb-4">Source: {{ map.source }}</p>
            </div>

            <!-- Card Actions Row -->
            <div class="flex items-center justify-between border-t border-slate-100 pt-3 text-xs gap-2 flex-wrap">
              <div class="flex items-center gap-2 flex-wrap">
                <!-- Preview Button -->
                <button
                  type="button"
                  class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 font-semibold text-slate-700 shadow-xs hover:border-slate-300 hover:bg-slate-50 hover:text-blue-600 transition-all"
                  @click="openPreview(map)"
                >
                  <svg class="h-3.5 w-3.5 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  </svg>
                  <span>Preview</span>
                </button>

                <!-- Interactive Map Link -->
                <router-link
                  v-if="map.source === 'Project NOAH' && NOAH_HAZARD_LAYERS[map.hazard_type]"
                  :to="{ name: 'hazard-map-interactive', params: { id: map.map_id } }"
                  class="inline-flex items-center gap-1.5 rounded-xl bg-emerald-50 px-3 py-1.5 font-bold text-emerald-700 hover:bg-emerald-100 transition-colors"
                >
                  <span>Interactive Map →</span>
                </router-link>

                <!-- External URL Link -->
                <a
                  v-else-if="map.map_url"
                  :href="map.map_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-1.5 font-semibold text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
                >
                  <span>Open Resource</span>
                  <svg class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </a>
              </div>

              <!-- Admin Controls -->
              <div v-if="isSecretary" class="flex items-center gap-2.5">
                <router-link :to="{ name: 'hazard-map-edit', params: { id: map.map_id } }" class="font-medium text-slate-500 hover:text-blue-600">
                  Edit
                </router-link>
                <button type="button" @click="handleArchive(map.map_id)" class="font-medium text-slate-400 hover:text-red-600">
                  Archive
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>

    <!-- Quick Map Preview Modal Lightbox -->
    <Teleport to="body">
      <div
        v-if="previewMap"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-xs p-3 sm:p-6"
        role="dialog"
        aria-modal="true"
        aria-labelledby="hazard-preview-title"
        @keydown.esc="closePreview"
        @click.self="closePreview"
      >
        <section class="flex h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
          <!-- Modal Header -->
          <header class="flex items-center justify-between border-b border-slate-200 px-5 py-3.5">
            <div class="flex items-center gap-3 min-w-0">
              <span :class="hazardBadgeClass(previewMap.hazard_type)" class="inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-xs font-bold">
                {{ previewMap.hazard_type }}
              </span>
              <div class="min-w-0">
                <h2 id="hazard-preview-title" class="truncate text-base font-bold text-slate-900">{{ previewMap.map_title }}</h2>
                <p class="text-[11px] text-slate-500 font-medium">Source: {{ previewMap.source }} · Official Hazard Reference</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-100 hover:text-slate-800 transition-colors"
                aria-label="Close preview"
                @click="closePreview"
              >
                <span aria-hidden="true" class="text-2xl leading-none">&times;</span>
              </button>
            </div>
          </header>

          <!-- Modal Body / Map Image Display -->
          <div class="relative flex-1 overflow-auto bg-slate-900/95 flex flex-col items-center justify-center p-4">
            <div v-if="previewMap.map_image" class="relative max-h-full max-w-full flex items-center justify-center">
              <img
                :src="previewMap.map_image"
                :alt="`${previewMap.map_title} high resolution map preview`"
                class="max-h-[62vh] w-auto max-w-full rounded-lg object-contain shadow-2xl ring-1 ring-white/10"
              />
            </div>
            <div v-else class="text-center p-8 max-w-md bg-white rounded-2xl shadow-xl">
              <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 mb-3">
                <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Zm0-15v15m6-12v15" />
                </svg>
              </div>
              <h3 class="text-base font-bold text-slate-900">Map Graphic File Not Attached</h3>
              <p class="mt-1 text-xs text-slate-500 leading-relaxed">
                This entry is cataloged as a digital reference. You can launch the interactive GIS layer or visit the source repository.
              </p>
            </div>

            <!-- Severity Legend Pill in Preview -->
            <div class="mt-3 flex items-center gap-4 rounded-full bg-slate-900/80 px-4 py-1.5 text-xs text-white border border-white/10 shadow-lg">
              <span class="font-bold text-[11px] uppercase tracking-wider text-slate-300">Severity:</span>
              <span class="flex items-center gap-1.5 font-medium"><span class="h-2.5 w-2.5 rounded-sm bg-[#facc15]" /> Low</span>
              <span class="flex items-center gap-1.5 font-medium"><span class="h-2.5 w-2.5 rounded-sm bg-[#fb923c]" /> Medium</span>
              <span class="flex items-center gap-1.5 font-medium"><span class="h-2.5 w-2.5 rounded-sm bg-[#ef4444]" /> High</span>
            </div>
          </div>

          <!-- Modal Footer Details & Navigation Options -->
          <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-white px-5 py-3.5">
            <div class="min-w-0 max-w-md">
              <p v-if="previewMap.description" class="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                {{ previewMap.description }}
              </p>
              <p v-else class="text-xs text-slate-400">
                Official hazard boundary data verified for Baclayon, Bohol.
              </p>
            </div>

            <div class="flex items-center gap-2.5">
              <button
                type="button"
                class="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                @click="closePreview"
              >
                Close Preview
              </button>

              <a
                v-if="previewMap.map_url"
                :href="previewMap.map_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
              >
                <span>Open External Link</span>
                <svg class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                  <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                </svg>
              </a>

              <router-link
                v-if="previewMap.source === 'Project NOAH' && NOAH_HAZARD_LAYERS[previewMap.hazard_type]"
                :to="{ name: 'hazard-map-interactive', params: { id: previewMap.map_id } }"
                class="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-emerald-700 transition-colors"
                @click="closePreview"
              >
                <span>Launch Interactive GIS Map</span>
                <span aria-hidden="true">→</span>
              </router-link>
            </div>
          </footer>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import * as mapsApi from '@/services/mapsApi'
import { NOAH_HAZARD_LAYERS } from '@/services/noahHazardLayers'

const authStore = useAuthStore()
const maps = ref([])
const isLoading = ref(true)
const previewMap = ref(null)

const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

const HAZARD_ORDER = ['Flood', 'Storm Surge', 'Landslide', 'Earthquake']

const groupedMaps = computed(() => {
  return HAZARD_ORDER.map((hazardType) => ({
    hazardType,
    maps: maps.value.filter((m) => m.hazard_type === hazardType),
  })).filter((group) => group.maps.length > 0)
})

function openPreview(map) {
  previewMap.value = map
}

function closePreview() {
  previewMap.value = null
}

function handleKeydown(event) {
  if (event.key === 'Escape' && previewMap.value) {
    closePreview()
  }
}

function hazardBadgeClass(hazardType) {
  const map = {
    Flood: 'bg-blue-100 text-blue-800',
    'Storm Surge': 'bg-cyan-100 text-cyan-800',
    Landslide: 'bg-amber-100 text-amber-800',
    Earthquake: 'bg-red-100 text-red-800',
  }
  return map[hazardType] || 'bg-slate-100 text-slate-700'
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
  try {
    const response = await mapsApi.listHazardMaps()
    maps.value = response.data
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadMaps()
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

async function handleArchive(mapId) {
  if (!window.confirm('Archive this hazard map reference?')) return
  await mapsApi.archiveHazardMap(mapId)
  await loadMaps()
}
</script>
