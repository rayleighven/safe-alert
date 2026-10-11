<template>
  <main class="flex min-h-screen items-center justify-center bg-slate-50 px-5 py-12">
    <section class="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm sm:p-10">
      <router-link to="/" class="mx-auto inline-flex items-center gap-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="SAFE-ALERT home">
        <img :src="logo" alt="" class="h-10 w-10 object-contain" /><span class="font-bold text-slate-800">SAFE-ALERT</span>
      </router-link>
      <p class="mt-8 text-sm font-bold uppercase tracking-widest text-blue-600">Error 404</p>
      <h1 class="mt-2 text-3xl font-bold text-slate-900">Page not found</h1>
      <p class="mt-3 text-slate-600">That page may have moved or the address may be incorrect.</p>
      <router-link to="/" class="mt-7 inline-flex min-h-11 items-center justify-center rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white hover:bg-blue-700">Return to home</router-link>
    </section>
  </main>
</template>
<script setup>
import logo from '@/assets/images/safe-alert-logo.png'
</script>
