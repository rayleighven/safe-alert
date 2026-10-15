<template>
  <main class="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
    <!-- Left Hero Column with Bohol Church Background -->
    <section
      class="relative hidden overflow-hidden bg-cover bg-center px-12 py-14 text-white lg:flex lg:flex-col lg:justify-between"
      :style="{ backgroundImage: `url(${churchBackground})` }"
    >
      <div class="absolute inset-0 bg-gradient-to-br from-[#071b33]/95 via-[#0d2f57]/90 to-[#1e40af]/80" />

      <div class="relative flex items-center gap-3.5">
        <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-12 w-12 object-contain drop-shadow" />
        <div>
          <p class="text-lg font-extrabold tracking-wide text-white">SAFE-ALERT</p>
          <p class="text-xs font-medium text-blue-200/90">Barangay Disaster Readiness System</p>
        </div>
      </div>

      <div class="relative max-w-xl">
        <p class="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-blue-300">Authentication Portal</p>
        <h1 class="text-4xl font-extrabold leading-tight tracking-tight xl:text-5xl text-white">
          Choose your service area.
        </h1>
        <p class="mt-5 max-w-lg text-sm sm:text-base leading-relaxed text-blue-100/90">
          Select the barangay or municipal department where your authorized SAFE-ALERT account is registered.
        </p>
      </div>

      <p class="relative text-xs text-blue-200/80 border-t border-white/10 pt-4">
        Baclayon, Bohol &middot; Disaster Risk Reduction and Management
      </p>
    </section>

    <!-- Right Column: Area Selection List -->
    <section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10 lg:px-14">
      <div class="w-full max-w-md">
        <div class="text-center">
          <router-link to="/" class="inline-flex items-center gap-2">
            <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-10 w-10 object-contain drop-shadow" />
            <span class="text-lg font-extrabold tracking-tight text-slate-800">
              SAFE-<span class="text-blue-600">ALERT</span>
            </span>
          </router-link>
          <h2 class="mt-5 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Choose your area</h2>
          <p class="mt-2 text-xs sm:text-sm text-slate-500">
            Select the designated community jurisdiction for your login.
          </p>
        </div>

        <div class="mt-8 space-y-3">
          <button
            v-for="area in areas"
            :key="area.value"
            type="button"
            class="group w-full rounded-2xl border border-slate-200/80 bg-white p-4 text-left shadow-card transition-all duration-200 hover:border-blue-400 hover:bg-blue-50/50 hover:shadow-card-hover"
            @click="chooseArea(area.value)"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-bold text-slate-900 group-hover:text-blue-900 transition-colors">{{ area.label }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ area.description }}</p>
              </div>
              <svg class="h-5 w-5 text-slate-400 transition-transform group-hover:translate-x-1 group-hover:text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </div>
          </button>
        </div>

        <router-link
          :to="{ name: 'landing' }"
          class="mt-6 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-blue-600 transition-colors"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          <span>Back to welcome</span>
        </router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'
import churchBackground from '@/assets/images/baclayonchurch.jpg'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'

const router = useRouter()
const areas = [
  { value: 'Cambanac', label: 'Barangay Cambanac', description: 'For registered residents and Barangay Cambanac staff.' },
  { value: 'Poblacion', label: 'Barangay Poblacion', description: 'For registered residents and Barangay Poblacion staff.' },
  { value: 'MDRRMO', label: 'MDRRMO Baclayon', description: 'For municipal disaster risk reduction and management officers.' },
]

function chooseArea(access) {
  router.push({ name: 'login', query: { access } })
}
</script>
