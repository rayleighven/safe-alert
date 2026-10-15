<template>
  <div class="space-y-6 pb-6 max-w-4xl">
    <!-- Breadcrumb & Header -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Announcements</span>
      </nav>

      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Community Announcements</h1>
          <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            Official emergency advisories, disaster preparedness alerts, and barangay updates.
          </p>
        </div>
        <router-link
          v-if="canManageAnnouncements"
          to="/announcements/new"
          class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>New Announcement</span>
        </router-link>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="inline-flex h-10 w-10 animate-spin items-center justify-center rounded-full border-2 border-blue-600 border-t-transparent text-blue-600" />
      <p class="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Loading announcements...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="announcements.length === 0" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 11v2a2 2 0 0 0 2 2h2l5 4V5l-5 4H6a2 2 0 0 0-2 2Zm11.5-3.5a5 5 0 0 1 0 9" />
        </svg>
      </div>
      <h3 class="mt-4 text-sm font-bold text-slate-800">No announcements posted</h3>
      <p class="mt-1 text-xs text-slate-500">Published community advisories and updates will appear here.</p>
    </div>

    <!-- Announcements Feed -->
    <div v-else class="space-y-4">
      <article
        v-for="a in announcements"
        :key="a.announcement_id"
        class="overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card transition-all duration-200 hover:border-slate-300 hover:shadow-card-hover"
      >
        <!-- Optional Image Cover -->
        <div v-if="a.image || a.image_url" class="-mx-5 -mt-5 sm:-mx-6 sm:-mt-6 mb-4 overflow-hidden border-b border-slate-100 bg-slate-100">
          <img :src="a.image || a.image_url" :alt="`${a.title} image`" class="h-56 w-full object-cover" />
        </div>

        <!-- Title & Category Badges -->
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <h2 class="text-base sm:text-lg font-bold text-slate-900">{{ a.title }}</h2>
          <div class="flex items-center gap-1.5 flex-wrap">
            <span v-if="!a.is_public" class="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold text-slate-600">
              Internal Only
            </span>
            <span
              v-for="cat in a.categories"
              :key="cat.announcement_category_id"
              :class="categoryBadgeClass(cat.category)"
              class="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold"
            >
              {{ cat.category }}
            </span>
          </div>
        </div>

        <!-- Message Body -->
        <p class="mt-3 text-xs sm:text-sm text-slate-600 whitespace-pre-line leading-relaxed">{{ a.body }}</p>

        <!-- Footer / Metadata & Actions -->
        <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-400">
          <span class="flex items-center gap-1.5 font-medium">
            <svg class="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            <span>Posted {{ formatDate(a.created_at) }}</span>
          </span>

          <div v-if="canManageAnnouncements" class="flex items-center gap-3">
            <router-link
              :to="{ name: 'announcement-edit', params: { id: a.announcement_id } }"
              class="font-semibold text-blue-600 hover:text-blue-800 transition-colors"
            >
              Edit
            </router-link>
            <button
              type="button"
              class="font-semibold text-red-600 hover:text-red-800 transition-colors"
              @click="handleArchive(a.announcement_id)"
            >
              Archive
            </button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import * as announcementsApi from '@/services/announcementsApi'

const authStore = useAuthStore()
const announcements = ref([])
const isLoading = ref(true)

const canManageAnnouncements = computed(() => ['Barangay Secretary', 'MDRRMO Officer'].includes(authStore.user?.role))

function categoryBadgeClass(category) {
  if (category === 'Emergency') return 'bg-red-100 text-red-800'
  if (category === 'Alert') return 'bg-amber-100 text-amber-900'
  if (category === 'Advisory') return 'bg-amber-50 text-amber-800 border border-amber-200'
  return 'bg-blue-50 text-blue-700'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Intl.DateTimeFormat('en-PH', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Manila' }).format(new Date(dateStr))
}

async function loadAnnouncements() {
  isLoading.value = true
  try {
    const response = await announcementsApi.listAnnouncements()
    announcements.value = response.data
  } finally {
    isLoading.value = false
  }
}

onMounted(loadAnnouncements)

async function handleArchive(id) {
  if (!window.confirm('Archive this announcement?')) return
  await announcementsApi.archiveAnnouncement(id)
  await loadAnnouncements()
}
</script>