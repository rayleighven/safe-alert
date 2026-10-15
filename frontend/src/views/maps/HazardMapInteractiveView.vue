<template>
  <div class="space-y-6 pb-6 max-w-5xl">
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <router-link to="/hazard-maps" class="transition-colors hover:text-blue-600">Hazard Maps</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Interactive GIS</span>
      </nav>

      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">{{ hazardMap ? hazardMap.map_title : 'Interactive Hazard Map' }}</h1>
          <p v-if="locationLabel" class="mt-1 text-xs sm:text-sm font-medium text-slate-500">{{ locationLabel }}</p>
        </div>
        <router-link to="/hazard-maps" class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-xs transition-colors hover:bg-slate-50">
          ← Back to Maps
        </router-link>
      </div>
    </header>

      <div v-if="isLoading" class="text-slate-500">Loading interactive map...</div>
      <div v-if="errorMessage" class="bg-white rounded-xl shadow-sm p-5 text-sm text-red-600">{{ errorMessage }}</div>

      <!--
        v-show (not v-if) so this stays mounted in the DOM the whole time —
        `mapContainer` below must already be a real element the moment
        onMounted() runs, since that's where the MapLibre map is constructed.
      -->
      <div v-show="!isLoading && !errorMessage" class="bg-white rounded-xl shadow-sm p-5">
        <div class="flex items-center gap-3 flex-wrap mb-3">
          <span class="text-sm font-semibold text-slate-700">Hazard: {{ selectedHazardType }}</span>

          <button
            v-for="layer in layerOptions"
            v-show="layerOptions.length > 1"
            :key="layer.id"
            type="button"
            @click="activeLayerId = layer.id"
            :class="activeLayerId === layer.id ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-300 hover:bg-slate-50'"
            class="px-3 py-1.5 rounded-lg text-sm font-medium"
          >
            {{ layer.label }}
          </button>
        </div>

        <p v-if="!layerOptions.length" class="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
          No built-in Project NOAH interactive layer is configured for this hazard type.
        </p>

        <div ref="mapContainer" class="h-[520px] w-full rounded-lg overflow-hidden border border-slate-200"></div>

        <div class="flex items-center gap-2 mt-3 text-sm">
          <span class="font-medium text-slate-700">Severity at this location:</span>
          <span v-if="severityLoading" class="text-slate-400">Checking&hellip;</span>
          <span v-else-if="severityError" class="text-red-600">{{ severityError }}</span>
          <span v-else-if="!severityLevel" class="text-slate-500">No mapped hazard at this location.</span>
          <span v-else class="inline-flex items-center gap-1.5 font-semibold" :style="{ color: HAZARD_SEVERITY_COLORS[severityLevel] }">
            <span class="w-3 h-3 rounded-sm inline-block" :style="{ background: HAZARD_SEVERITY_COLORS[severityLevel] }"></span>
            {{ HAZARD_SEVERITY_LABELS[severityLevel] }}
          </span>
        </div>

        <div class="flex items-center gap-4 mt-2 text-xs text-slate-600">
          <span class="font-medium">Hazard Level:</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm inline-block" style="background:#facc15"></span> Low</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm inline-block" style="background:#fb923c"></span> Medium</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm inline-block" style="background:#ef4444"></span> High</span>
        </div>

        <p class="text-xs text-slate-400 mt-4 leading-relaxed">
          Hazard data &copy; <a href="https://noah.up.edu.ph" target="_blank" rel="noopener noreferrer" class="underline">Project NOAH</a>,
          UP Resilience Institute, republished by
          <a href="https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps" target="_blank" rel="noopener noreferrer" class="underline">BetterGov.ph</a>
          under the
          <a href="https://opendatacommons.org/licenses/odbl/1.0/" target="_blank" rel="noopener noreferrer" class="underline">Open Data Commons Open Database License (ODbL) 1.0</a>.
          Base map &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer" class="underline">OpenStreetMap</a> contributors.
        </p>
      </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Map as MapLibreMap,
  Marker,
  NavigationControl,
  AttributionControl,
  addProtocol,
  removeProtocol,
} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Protocol } from 'pmtiles'
import AppNavBar from '@/components/AppNavBar.vue'
import * as mapsApi from '@/services/mapsApi'
import * as coreApi from '@/services/coreApi'
import {
  NOAH_PMTILES_BASE_URL,
  NOAH_HAZARD_LAYERS,
  HAZARD_SEVERITY_COLORS,
  HAZARD_SEVERITY_LABELS,
} from '@/services/noahHazardLayers'

const route = useRoute()

const ALL_LAYERS = Object.values(NOAH_HAZARD_LAYERS).flat()

const isLoading = ref(true)
const errorMessage = ref('')
const hazardMap = ref(null)
const locationLabel = ref('')
const activeLayerId = ref('')
const mapContainer = ref(null)
const severityLevel = ref(0)
const severityLoading = ref(false)
const severityError = ref('')

const selectedHazardType = computed(() => hazardMap.value?.hazard_type || '')
const layerOptions = computed(() => NOAH_HAZARD_LAYERS[selectedHazardType.value] || [])

let map = null
let protocol = null
let markerLngLat = null
const failedSourceIds = new Set()

function fillColorExpression(field) {
  return [
    'match', ['get', field],
    1, HAZARD_SEVERITY_COLORS[1],
    2, HAZARD_SEVERITY_COLORS[2],
    3, HAZARD_SEVERITY_COLORS[3],
    'rgba(0,0,0,0)',
  ]
}

async function geocodeLocation(query) {
  // A barangay's coordinates don't change, so cache the lookup for the
  // session instead of re-querying the public geocoder on every visit.
  const cacheKey = `noah-geocode:${query}`
  const cached = sessionStorage.getItem(cacheKey)
  if (cached) return JSON.parse(cached)

  const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(query)}`
  const response = await fetch(url)
  if (!response.ok) throw new Error('Location lookup failed. Please try again later.')
  const results = await response.json()
  if (!results.length) throw new Error('Could not determine coordinates for this location.')
  const coords = { lat: parseFloat(results[0].lat), lon: parseFloat(results[0].lon) }
  sessionStorage.setItem(cacheKey, JSON.stringify(coords))
  return coords
}

function setActiveLayer(layerId) {
  if (!map) return
  ALL_LAYERS.forEach((layer) => {
    const glLayerId = `noah-${layer.id}`
    if (map.getLayer(glLayerId)) {
      map.setLayoutProperty(glLayerId, 'visibility', layer.id === layerId ? 'visible' : 'none')
    }
  })
}

// Reads the currently active hazard layer's polygons at the project's exact
// coordinates via MapLibre's rendered-feature query — an exact point-in-polygon
// test against the vector-tile geometry, never a nearest-polygon guess. When
// more than one polygon covers the point (overlapping tile geometry), the
// highest severity present wins.
function computeSeverityAtMarker() {
  severityError.value = ''
  severityLevel.value = 0
  if (!map || !markerLngLat) return

  const layer = layerOptions.value.find((l) => l.id === activeLayerId.value)
  if (!layer) return

  const glLayerId = `noah-${layer.id}`
  if (!map.getLayer(glLayerId)) return

  if (failedSourceIds.has(glLayerId)) {
    severityError.value = 'Could not load hazard data for this layer. Please try again later.'
    return
  }

  const point = map.project(markerLngLat)
  const features = map.queryRenderedFeatures(point, { layers: [glLayerId] })

  let highest = 0
  for (const feature of features) {
    const value = Number(feature.properties?.[layer.field])
    if (value > highest) highest = value
  }
  severityLevel.value = highest
}

function scheduleSeverityCheck() {
  if (!map) return
  severityLoading.value = true
  map.once('idle', () => {
    computeSeverityAtMarker()
    severityLoading.value = false
  })
}

watch(activeLayerId, (id) => {
  if (!id) return
  setActiveLayer(id)
  scheduleSeverityCheck()
})

onMounted(async () => {
  try {
    const hazardMapResponse = await mapsApi.getHazardMap(route.params.id)
    hazardMap.value = hazardMapResponse.data

    const barangayResponse = await coreApi.getBarangay(hazardMap.value.barangay)
    const barangay = barangayResponse.data
    locationLabel.value = `${barangay.name}, ${barangay.municipality}, ${barangay.province}`

    const { lat, lon } = await geocodeLocation(`${locationLabel.value}, Philippines`)
    markerLngLat = [lon, lat]

    activeLayerId.value = layerOptions.value[0]?.id || ''

    // Reveal the map panel (and let Vue render it) before constructing
    // MapLibre — its container must have real layout dimensions, which it
    // doesn't while hidden behind the loading state.
    isLoading.value = false
    await nextTick()

    protocol = new Protocol()
    addProtocol('pmtiles', protocol.tile)

    map = new MapLibreMap({
      container: mapContainer.value,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors',
          },
        },
        layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
      },
      center: [lon, lat],
      zoom: 13,
      attributionControl: false,
    })
    map.addControl(new AttributionControl({ compact: true }))
    map.addControl(new NavigationControl(), 'top-right')
    map.on('error', (e) => {
      console.error('Hazard map layer failed to load:', e.error)
      if (e.sourceId) failedSourceIds.add(e.sourceId)
    })

    map.on('load', () => {
      ALL_LAYERS.forEach((layer) => {
        const sourceId = `noah-${layer.id}`
        map.addSource(sourceId, {
          type: 'vector',
          url: `pmtiles://${NOAH_PMTILES_BASE_URL}/${layer.id}.pmtiles`,
        })
        map.addLayer({
          id: sourceId,
          type: 'fill',
          source: sourceId,
          'source-layer': layer.id,
          layout: { visibility: layer.id === activeLayerId.value ? 'visible' : 'none' },
          paint: {
            'fill-color': fillColorExpression(layer.field),
            'fill-opacity': 0.55,
          },
        })
      })
      scheduleSeverityCheck()
    })

    new Marker({ color: '#1d4ed8' }).setLngLat(markerLngLat).addTo(map)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load the interactive hazard map.'
    isLoading.value = false
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
  if (protocol) {
    removeProtocol('pmtiles')
    protocol = null
  }
})
</script>
