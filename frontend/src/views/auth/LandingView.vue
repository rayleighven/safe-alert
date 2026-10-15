<template>
  <main class="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
    <!-- Left Hero Column with Bohol Baclayon Church Backdrop -->
    <section
      class="relative hidden overflow-hidden bg-cover bg-center px-12 py-14 text-white lg:flex lg:flex-col lg:justify-between"
      :style="{ backgroundImage: `url(${churchBackground})` }"
    >
      <div class="absolute inset-0 bg-gradient-to-br from-[#071b33]/95 via-[#0d2f57]/90 to-[#1e40af]/80" />

      <!-- Brand Top -->
      <div class="relative flex items-center gap-3.5">
        <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-12 w-12 object-contain drop-shadow" />
        <div>
          <p class="text-lg font-extrabold tracking-wide text-white">SAFE-ALERT</p>
          <p class="text-xs font-medium text-blue-200/90">Barangay Disaster Readiness & Coordination</p>
        </div>
      </div>

      <!-- Hero Message -->
      <div class="relative max-w-xl">
        <p class="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-blue-300">Community Emergency Preparedness</p>
        <h1 class="text-4xl font-extrabold leading-tight tracking-tight xl:text-5xl text-white">
          Be informed. Be prepared. Stay safe.
        </h1>
        <p class="mt-5 max-w-lg text-sm sm:text-base leading-relaxed text-blue-100/90">
          SAFE-ALERT provides Barangay Cambanac and Barangay Poblacion with an integrated platform for household vulnerability scoring, evacuation tracking, and emergency advisories.
        </p>
      </div>

      <!-- Municipal Attribution -->
      <div class="relative flex items-center justify-between text-xs text-blue-200/80 border-t border-white/10 pt-4">
        <span>Municipality of Baclayon, Bohol</span>
        <span>Disaster Risk Reduction and Management</span>
      </div>
    </section>

    <!-- Right Column: Welcome and Sign In CTA -->
    <section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10 lg:px-14">
      <div class="w-full max-w-md">
        <!-- Brand Header on Mobile/Desktop -->
        <div class="text-center">
          <router-link
            to="/"
            class="inline-flex items-center justify-center gap-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="SAFE-ALERT home"
          >
            <img :src="safeAlertLogo" alt="" class="h-11 w-11 object-contain drop-shadow" />
            <span class="text-xl font-extrabold tracking-tight text-slate-900">
              SAFE-<span class="text-blue-600">ALERT</span>
            </span>
          </router-link>
          <h2 class="mt-6 text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">Community readiness starts here.</h2>
          <p class="mt-2.5 text-xs sm:text-sm leading-relaxed text-slate-500">
            Access your barangay's disaster readiness tools, emergency updates, and household information.
          </p>
        </div>

        <!-- Action Card -->
        <div class="mt-8 rounded-2xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-card">
          <router-link
            :to="{ name: 'access-select' }"
            class="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-center text-sm font-bold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <span>Sign In to Safe-Alert</span>
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
            </svg>
          </router-link>

          <div class="my-6 flex items-center gap-3">
            <span class="h-px flex-1 bg-slate-200" />
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Authorized personnel & residents</span>
            <span class="h-px flex-1 bg-slate-200" />
          </div>

          <p class="text-center text-xs text-slate-500">
            For account issuance or password recovery, please contact your Barangay Secretary.
          </p>
        </div>

        <p class="mt-8 text-center text-[11px] leading-relaxed text-slate-400">
          Household vulnerability records are safeguarded under Republic Act 10173 (Data Privacy Act of 2012).
        </p>
        <footer class="mt-6 border-t border-slate-200 pt-4 text-center text-[11px] text-slate-400">
          &copy; {{ new Date().getFullYear() }} SAFE-ALERT · Baclayon, Bohol
        </footer>
      </div>
    </section>
  </main>
</template>

<script setup>
import churchBackground from '@/assets/images/baclayonchurch.jpg'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'
</script>
