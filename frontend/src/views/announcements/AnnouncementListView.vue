<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-3xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-slate-800">Announcements</h1>
        <router-link
          v-if="canManageAnnouncements"
          to="/announcements/new"
          class="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2"
        >
          + New Announcement
        </router-link>
      </div>

      <div v-if="isLoading" class="text-slate-500">Loading announcements...</div>
      <div v-else-if="announcements.length === 0" class="text-slate-500">No announcements yet.</div>

      <div v-else class="space-y-4">
        <div v-for="a in announcements" :key="a.announcement_id" class="bg-white rounded-xl shadow-sm p-5">
          <div class="flex items-start justify-between mb-2 gap-3 flex-wrap">
            <h2 class="font-semibold text-slate-800">{{ a.title }}</h2>
            <div class="flex items-center gap-2 flex-wrap">
              <span v-if="!a.is_public" class="bg-slate-100 text-slate-600 px-2 py-1 rounded-full text-xs font-medium">
                Internal
              </span>
              <span
                v-for="cat in a.categories"
                :key="cat.announcement_category_id"
                :class="categoryBadgeClass(cat.category)"
                class="px-2 py-1 rounded-full text-xs font-medium"
              >
                {{ cat.category }}
              </span>
            </div>
          </div>
          <p class="text-slate-600 text-sm mb-3 whitespace-pre-line">{{ a.body }}</p>
          <div class="flex items-center justify-between text-xs text-slate-400">
            <span>Posted {{ formatDate(a.created_at) }}</span>
            <div v-if="canManageAnnouncements" class="flex gap-3">
              <router-link :to="{ name: 'announcement-edit', params: { id: a.announcement_id } }" class="text-blue-600 hover:text-blue-700">
                Edit
              </router-link>
              <button @click="handleArchive(a.announcement_id)" class="text-red-600 hover:text-red-700">Archive</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as announcementsApi from '@/services/announcementsApi'

const authStore = useAuthStore()
const announcements = ref([])
const isLoading = ref(true)

const canManageAnnouncements = computed(() => ['Barangay Secretary', 'MDRRMO Officer'].includes(authStore.user?.role))

function categoryBadgeClass(category) {
  if (category === 'Emergency') return 'bg-red-100 text-red-700'
  if (category === 'Alert') return 'bg-orange-100 text-orange-700'
  if (category === 'Advisory') return 'bg-yellow-100 text-yellow-700'
  return 'bg-blue-100 text-blue-700'
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}

async function loadAnnouncements() {
  isLoading.value = true
  const response = await announcementsApi.listAnnouncements()
  announcements.value = response.data
  isLoading.value = false
}

onMounted(loadAnnouncements)

async function handleArchive(id) {
  if (!confirm('Archive this announcement?')) return
  await announcementsApi.archiveAnnouncement(id)
  await loadAnnouncements()
}
</script>