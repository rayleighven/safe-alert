<template>
  <div>
    <!-- Mobile Navigation Shell -->
    <div class="lg:hidden">
      <AppNavBar standalone />
    </div>

    <!-- Desktop Operational TopBar -->
    <header class="hidden h-16 items-center justify-between border-b border-slate-200/80 bg-white px-8 lg:flex">
      <!-- Quick Search / Filter Bar -->
      <div class="relative w-80">
        <label for="topbar-search" class="sr-only">Search households, centers, reports</label>
        <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400" aria-hidden="true">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
        </span>
        <input
          id="topbar-search"
          v-model="searchQuery"
          type="search"
          placeholder="Search households, centers, reports..."
          class="w-full rounded-xl border border-slate-200 bg-slate-50/70 py-1.5 pl-9 pr-3 text-xs font-medium text-slate-800 placeholder:text-slate-400 transition-colors focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
          @keydown.enter="handleSearch"
        />
      </div>

      <!-- Operational Status & User Controls -->
      <div class="ml-6 flex min-w-0 items-center gap-3.5">
        <!-- Live Clock -->
        <CurrentDateTime />

        <!-- Barangay Location Badge -->
        <div class="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/60 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-xs">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
          </span>
          <span>{{ locationLabel }}</span>
        </div>

        <!-- Advisory Quick Link -->
        <router-link
          to="/announcements"
          class="flex items-center gap-1.5 rounded-xl border border-amber-200/80 bg-amber-50/70 px-3 py-1.5 text-xs font-semibold text-amber-900 transition-colors hover:bg-amber-100"
          title="View community announcements and advisories"
        >
          <svg class="h-3.5 w-3.5 text-amber-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
          </svg>
          <span>Advisories</span>
        </router-link>

        <!-- Profile Menu Dropdown -->
        <div ref="profileMenuRef" class="relative">
          <button
            type="button"
            class="flex items-center gap-2.5 rounded-xl border border-transparent p-1 transition-colors hover:border-slate-200 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :aria-expanded="isProfileMenuOpen"
            aria-haspopup="true"
            @click="toggleProfileMenu"
          >
            <div class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg bg-blue-100 text-xs font-bold text-blue-700 ring-1 ring-blue-200">
              <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="" class="h-full w-full object-cover" />
              <span v-else>{{ userInitials }}</span>
            </div>
            <div class="hidden text-left sm:block">
              <p class="text-xs font-semibold text-slate-800 leading-tight">{{ displayName }}</p>
              <p class="text-[10px] text-slate-500 leading-tight">{{ authStore.user?.role }}</p>
            </div>
            <svg class="h-3.5 w-3.5 text-slate-400 transition-transform" :class="{ 'rotate-180': isProfileMenuOpen }" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
            </svg>
          </button>

          <div
            v-if="isProfileMenuOpen"
            class="absolute right-0 top-full z-40 mt-2 w-52 overflow-hidden rounded-2xl border border-slate-200 bg-white py-1.5 shadow-xl transition-all"
          >
            <div class="border-b border-slate-100 px-3.5 py-2">
              <p class="text-xs font-bold text-slate-800">{{ displayName }}</p>
              <p class="text-[11px] text-slate-500">{{ authStore.user?.email || authStore.user?.role }}</p>
            </div>
            <div class="flex flex-col py-1 text-xs">
              <router-link to="/profile" class="menu-link flex items-center gap-2" @click="closeProfileMenu">
                <svg class="h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
                </svg>
                <span>Profile Settings</span>
              </router-link>
              <button type="button" class="menu-link flex items-center gap-2 text-red-600 hover:bg-red-50 hover:text-red-700" @click="handleLogout">
                <svg class="h-4 w-4 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Logout Confirmation Modal -->
    <ConfirmActionDialog
      v-if="showLogoutConfirm"
      title="Log out of SAFE-ALERT?"
      message="You will need to sign in again to access your account."
      confirm-label="Log out"
      confirm-class="bg-red-600 hover:bg-red-700"
      title-id="topbar-logout-confirmation"
      @cancel="showLogoutConfirm = false"
      @confirm="confirmLogout"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import ConfirmActionDialog from '@/components/ConfirmActionDialog.vue'
import CurrentDateTime from '@/components/CurrentDateTime.vue'

const authStore = useAuthStore()
const router = useRouter()

const displayName = computed(() => authStore.user?.first_name || authStore.user?.username || 'User')
const userInitials = computed(() => displayName.value?.slice(0, 2).toUpperCase() || 'U')
const locationLabel = computed(() => {
  const barangayName = authStore.user?.barangay_name
  return barangayName ? `Brgy. ${barangayName}` : 'Baclayon, Bohol'
})

const searchQuery = ref('')
const isProfileMenuOpen = ref(false)
const profileMenuRef = ref(null)
const showLogoutConfirm = ref(false)

function handleSearch() {
  const query = searchQuery.value.trim()
  if (!query) return
  router.push({ name: 'households', query: { q: query } })
}

function toggleProfileMenu() {
  isProfileMenuOpen.value = !isProfileMenuOpen.value
}

function closeProfileMenu() {
  isProfileMenuOpen.value = false
}

function handleDocumentClick(event) {
  if (profileMenuRef.value && !profileMenuRef.value.contains(event.target)) {
    isProfileMenuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocumentClick))

function handleLogout() {
  closeProfileMenu()
  showLogoutConfirm.value = true
}

async function confirmLogout() {
  showLogoutConfirm.value = false
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.menu-link {
  @apply px-3.5 py-2 text-slate-700 transition-colors hover:bg-slate-50 hover:text-blue-600 font-medium;
}
</style>
