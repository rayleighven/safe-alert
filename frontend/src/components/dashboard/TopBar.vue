<template>
  <div>
    <div class="lg:hidden">
      <AppNavBar standalone />
    </div>

    <header class="hidden h-16 items-center justify-between border-b border-slate-200 bg-white px-8 lg:flex">
      <label class="relative block w-full max-w-sm">
        <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="6" />
          <path stroke-linecap="round" d="m16 16 4 4" />
        </svg>
        <input
          type="search"
          aria-label="Search SAFE-ALERT"
          placeholder="Search households, centers, reports..."
          class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
      </label>

      <div class="ml-6 flex items-center gap-4">
        <div class="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700">
          <span class="h-2 w-2 rounded-full bg-emerald-500" />
          Baclayon, Bohol
        </div>
        <button type="button" class="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700" aria-label="Notifications">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-8 12h4" />
          </svg>
          <span class="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
        </button>
        <span class="rounded-full bg-amber-100 px-3 py-1.5 text-xs font-semibold text-amber-700">Advisory Active</span>
        <router-link to="/profile" class="text-right">
          <p class="text-sm font-semibold text-slate-800">{{ displayName }}</p>
          <p class="text-xs text-slate-500">{{ authStore.user?.role }}</p>
        </router-link>
      </div>
    </header>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'

const authStore = useAuthStore()
const displayName = computed(() => authStore.user?.first_name || authStore.user?.username)
</script>
