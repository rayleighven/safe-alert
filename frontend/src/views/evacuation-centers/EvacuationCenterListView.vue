<template>
  <div class="space-y-6 pb-6">
    <!-- Breadcrumb & Header -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Evacuation Centers</span>
      </nav>

      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Evacuation Centers</h1>
          <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            Designated emergency evacuation shelters, real-time capacity monitoring, and check-in records.
          </p>
        </div>
        <router-link
          v-if="isSecretary"
          to="/evacuation-centers/new"
          class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>New Center</span>
        </router-link>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="inline-flex h-10 w-10 animate-spin items-center justify-center rounded-full border-2 border-blue-600 border-t-transparent text-blue-600" />
      <p class="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Loading evacuation centers...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="centers.length === 0" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="m3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6" />
        </svg>
      </div>
      <h3 class="mt-4 text-sm font-bold text-slate-800">No evacuation centers registered</h3>
      <p class="mt-1 text-xs text-slate-500">Designated evacuation facilities will appear here once added.</p>
    </div>

    <!-- Center Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div
        v-for="center in centers"
        :key="center.center_id"
        class="group flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card transition-all duration-200 hover:border-slate-300 hover:shadow-card-hover cursor-pointer"
        tabindex="0"
        @click="router.push({ name: 'evacuation-center-detail', params: { id: center.center_id } })"
        @keydown.enter="router.push({ name: 'evacuation-center-detail', params: { id: center.center_id } })"
      >
        <div>
          <!-- Optional Image Thumbnail -->
          <div v-if="center.photo || center.photo_url" class="-mx-5 -mt-5 mb-4 overflow-hidden border-b border-slate-100 bg-slate-100">
            <img :src="center.photo || center.photo_url" :alt="`${center.name} photo`" class="h-40 w-full object-cover transition-transform duration-300 group-hover:scale-105" />
          </div>

          <!-- Header & Status Badge -->
          <div class="flex items-start justify-between gap-3 mb-2">
            <h2 class="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors">{{ center.name }}</h2>
            <span :class="statusBadgeClass(center.status)" class="inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold">
              {{ center.status }}
            </span>
          </div>

          <!-- Address -->
          <p class="text-xs text-slate-500 flex items-center gap-1.5 mb-4">
            <svg class="h-3.5 w-3.5 text-slate-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
            </svg>
            <span class="truncate">{{ center.address || 'Address not recorded' }}</span>
          </p>
        </div>

        <!-- Occupancy Bar & Numbers -->
        <div class="border-t border-slate-100 pt-3">
          <div class="flex items-center justify-between text-xs mb-1.5">
            <span class="font-semibold text-slate-600">Occupancy</span>
            <span class="font-bold text-slate-900 tabular-nums">
              {{ center.current_occupancy }} <span class="font-normal text-slate-400">/</span> {{ center.capacity }}
              <span class="ml-1 text-[11px] font-medium text-slate-500">({{ occupancyPercent(center) }}%)</span>
            </span>
          </div>
          <div class="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-300"
              :class="occupancyBarClass(center)"
              :style="{ width: occupancyPercent(center) + '%' }"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as evacuationCentersApi from '@/services/evacuationCentersApi'

const router = useRouter()
const authStore = useAuthStore()

const centers = ref([])
const isLoading = ref(true)

const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

function statusBadgeClass(status) {
  if (status === 'Active') return 'bg-emerald-100 text-emerald-800'
  if (status === 'Under Maintenance') return 'bg-amber-100 text-amber-800'
  return 'bg-slate-100 text-slate-700'
}

function occupancyPercent(center) {
  if (!center.capacity) return 0
  return Math.min(100, Math.round((Number(center.current_occupancy || 0) / Number(center.capacity)) * 100))
}

function occupancyBarClass(center) {
  const percent = occupancyPercent(center)
  if (percent >= 90) return 'bg-red-500'
  if (percent >= 70) return 'bg-amber-500'
  return 'bg-emerald-500'
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