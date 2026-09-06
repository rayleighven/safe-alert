<template>
  <main class="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
    <section class="relative hidden overflow-hidden bg-cover bg-center px-12 py-14 text-white lg:flex lg:flex-col lg:justify-between" :style="{ backgroundImage: `url(${churchBackground})` }">
      <div class="absolute inset-0 bg-gradient-to-br from-blue-950/95 via-blue-800/90 to-cyan-800/80" />
      <div class="absolute -left-24 -top-24 h-72 w-72 rounded-full bg-cyan-300/20 blur-3xl" />
      <div class="absolute -bottom-20 -right-20 h-80 w-80 rounded-full bg-blue-300/20 blur-3xl" />
      <div class="relative flex items-center gap-3"><img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-14 w-14 object-contain" /><div><p class="text-lg font-bold tracking-wide">SAFE-ALERT</p><p class="text-xs text-blue-100">Barangay disaster readiness system</p></div></div>
      <div class="relative max-w-xl"><p class="mb-4 text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200">Prepared communities save lives</p><h1 class="text-5xl font-bold leading-tight xl:text-6xl">Be informed. Be prepared. Stay safe.</h1><p class="mt-6 max-w-lg text-base leading-relaxed text-blue-100">SAFE-ALERT helps Barangay Cambanac and Poblacion coordinate household records, evacuation readiness, and timely emergency updates.</p></div>
      <p class="relative text-sm text-blue-100">Baclayon, Bohol &middot; Disaster Risk Reduction and Management</p>
    </section>
    <section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10 lg:px-14"><div class="w-full max-w-md text-center"><div class="flex items-center justify-center gap-2"><img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-10 w-10 object-contain" /><span class="text-lg font-bold tracking-wide text-slate-800">SAFE-<span class="text-blue-600">ALERT</span></span></div><h2 class="mt-7 text-3xl font-bold text-slate-900">Community readiness starts here.</h2><p class="mt-3 text-sm leading-relaxed text-slate-500">Access your barangay’s disaster readiness tools, emergency updates, and household information.</p><router-link :to="{ name: 'access-select' }" class="mt-8 block w-full rounded-lg bg-blue-600 py-3 text-center font-semibold text-white shadow-sm transition-colors hover:bg-blue-700">Sign In</router-link><div class="my-7 flex items-center gap-3"><span class="h-px flex-1 bg-slate-200" /><span class="text-xs font-semibold uppercase tracking-wide text-slate-400">Authorized access only</span><span class="h-px flex-1 bg-slate-200" /></div><p class="text-sm text-slate-500">For account assistance, contact your Barangay Secretary.</p><p class="mt-8 text-xs leading-relaxed text-slate-400">Household information is protected under the Data Privacy Act of 2012 (RA 10173).</p></div></section>
  </main>
</template>

<script setup>
import churchBackground from '@/assets/images/baclayonchurch.jpg'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'
</script>
