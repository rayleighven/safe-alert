<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-slate-800 mb-6">
        {{ isEditMode ? 'Edit Announcement' : 'New Announcement' }}
      </h1>

      <form @submit.prevent="handleSubmit" class="space-y-4 bg-white rounded-xl shadow-sm p-6">
        <div v-if="isMdrrmo">
          <label class="block text-sm font-medium text-slate-700 mb-1">Barangay</label>
          <select
            v-model="form.barangay"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="" disabled>Select Barangay</option>
            <option v-for="b in barangayOptions" :key="b.barangay_id" :value="b.barangay_id">{{ b.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Title</label>
          <input
            v-model="form.title"
            type="text"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Body</label>
          <textarea
            v-model="form.body"
            required
            rows="5"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Published At (optional)</label>
            <input
              v-model="form.published_at"
              type="datetime-local"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Expires At (optional)</label>
            <input
              v-model="form.expires_at"
              type="datetime-local"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="form.is_public" /> Visible to Residents (public)
        </label>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Categories</label>
          <div class="flex gap-4 flex-wrap">
            <label v-for="cat in categoryOptions" :key="cat" class="flex items-center gap-2 text-sm">
              <input type="checkbox" :value="cat" v-model="selectedCategories" /> {{ cat }}
            </label>
          </div>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="isSaving"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg px-4 py-2"
          >
            {{ isSaving ? 'Saving...' : isEditMode ? 'Save Changes' : 'Post Announcement' }}
          </button>
          <router-link to="/announcements" class="bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium rounded-lg px-4 py-2">
            Cancel
          </router-link>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as announcementsApi from '@/services/announcementsApi'
import * as coreApi from '@/services/coreApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isEditMode = computed(() => !!route.params.id)
const isSaving = ref(false)
const errorMessage = ref('')
const isMdrrmo = computed(() => authStore.user?.role === 'MDRRMO Officer')
const barangayOptions = ref([])

const categoryOptions = ['Advisory', 'Alert', 'Informational', 'Emergency']
const selectedCategories = ref([])

const form = reactive({
  title: '',
  body: '',
  is_public: true,
  published_at: '',
  expires_at: '',
  barangay: '',
})

onMounted(async () => {
  if (isMdrrmo.value) {
    const response = await coreApi.listBarangays()
    barangayOptions.value = response.data
  }
  if (isEditMode.value) {
    const response = await announcementsApi.getAnnouncement(route.params.id)
    Object.assign(form, {
      title: response.data.title,
      body: response.data.body,
      is_public: response.data.is_public,
      published_at: response.data.published_at ? response.data.published_at.slice(0, 16) : '',
      expires_at: response.data.expires_at ? response.data.expires_at.slice(0, 16) : '',
      barangay: response.data.barangay || '',
    })
    selectedCategories.value = response.data.categories.map((c) => c.category)
  }
})

async function handleSubmit() {
  isSaving.value = true
  errorMessage.value = ''
  try {
    const payload = {
      ...form,
      published_at: form.published_at || null,
      expires_at: form.expires_at || null,
      categories: selectedCategories.value.map((category) => ({ category })),
    }
    if (!isMdrrmo.value) delete payload.barangay // every other role keeps barangay fully server-assigned, unchanged
    if (isEditMode.value) {
      await announcementsApi.updateAnnouncement(route.params.id, payload)
    } else {
      await announcementsApi.createAnnouncement(payload)
    }
    router.push({ name: 'announcements' })
  } catch (error) {
    const data = error.response?.data
    errorMessage.value = data
      ? Object.entries(data)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' | ')
      : 'Failed to save announcement.'
  } finally {
    isSaving.value = false
  }
}
</script>