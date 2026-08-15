<template>
  <main class="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
    <section class="relative hidden overflow-hidden bg-cover bg-center px-12 py-14 text-white lg:flex lg:flex-col lg:justify-between" :style="{ backgroundImage: `url(${churchBackground})` }"><div class="absolute inset-0 bg-gradient-to-br from-blue-950/95 via-blue-800/90 to-cyan-800/80" /><div class="relative flex items-center gap-3"><img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-14 w-14 object-contain" /><div><p class="text-lg font-bold tracking-wide">SAFE-ALERT</p><p class="text-xs text-blue-100">Barangay disaster readiness system</p></div></div><div class="relative max-w-xl"><p class="mb-4 text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200">Secure access</p><h1 class="text-4xl font-bold leading-tight xl:text-5xl">Choose your service area.</h1><p class="mt-6 max-w-lg text-base leading-relaxed text-blue-100">Select the barangay or municipal office where your SAFE-ALERT account is registered.</p></div><p class="relative text-sm text-blue-100">Baclayon, Bohol &middot; Disaster Risk Reduction and Management</p></section>
    <section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10 lg:px-14"><div class="w-full max-w-md"><div class="text-center"><img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="mx-auto h-10 w-10 object-contain" /><h2 class="mt-5 text-3xl font-bold text-slate-900">Choose your area</h2><p class="mt-3 text-sm text-slate-500">Continue using the option that matches your account.</p></div><div class="mt-8 space-y-3"><button v-for="area in areas" :key="area.value" type="button" class="w-full rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-blue-300 hover:bg-blue-50" @click="chooseArea(area.value)"><p class="font-semibold text-slate-800">{{ area.label }}</p><p class="mt-1 text-sm text-slate-500">{{ area.description }}</p></button></div><router-link :to="{ name: 'landing' }" class="mt-6 block text-center text-sm font-medium text-slate-500 hover:text-blue-600">← Back to welcome</router-link></div></section>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'
import churchBackground from '@/assets/images/baclayonchurch.jpg'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'

const router = useRouter()
const areas = [
  { value: 'Cambanac', label: 'Barangay Cambanac', description: 'For Cambanac barangay accounts.' },
  { value: 'Poblacion', label: 'Barangay Poblacion', description: 'For Poblacion barangay accounts.' },
  { value: 'MDRRMO', label: 'MDRRMO', description: 'For municipal disaster risk reduction officers.' },
]
function chooseArea(access) { router.push({ name: 'login', query: { access } }) }
</script>
