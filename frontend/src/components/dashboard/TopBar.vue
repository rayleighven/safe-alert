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
          {{ locationLabel }}
        </div>

        <div ref="profileMenuRef" class="relative">
          <button
            type="button"
            class="flex items-center gap-2 rounded-lg text-right"
            :aria-expanded="isProfileMenuOpen"
            aria-haspopup="true"
            @click="toggleProfileMenu"
          >
            <div class="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full bg-blue-100 text-xs font-bold text-blue-700">
              <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="" class="h-full w-full object-cover" />
              <span v-else>{{ userInitials }}</span>
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-800">{{ displayName }}</p>
              <p class="text-xs text-slate-500">{{ authStore.user?.role }}</p>
            </div>
          </button>

          <div
            v-if="isProfileMenuOpen"
            class="absolute right-0 top-full z-30 mt-2 w-48 overflow-hidden rounded-xl border border-slate-200 bg-white py-2 shadow-lg"
          >
            <div class="flex flex-col text-sm">
              <router-link to="/profile" class="menu-link" @click="closeProfileMenu">Profile Settings</router-link>
              <button type="button" class="menu-link text-left text-red-600 hover:text-red-700" @click="handleLogout">Logout</button>
            </div>
          </div>
        </div>
      </div>
    </header>

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

const authStore = useAuthStore()
const router = useRouter()

const displayName = computed(() => authStore.user?.first_name || authStore.user?.username)
const userInitials = computed(() => displayName.value?.slice(0, 2).toUpperCase() || 'U')
const locationLabel = computed(() => {
  const barangayName = authStore.user?.barangay_name
  return barangayName ? `${barangayName}, Baclayon, Bohol` : 'Baclayon, Bohol'
})

const isProfileMenuOpen = ref(false)
const profileMenuRef = ref(null)
const showLogoutConfirm = ref(false)

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
  @apply border-b border-slate-100 px-3 py-2.5 font-medium text-slate-700 transition-colors hover:bg-slate-50 hover:text-blue-600;
}

.menu-link:last-child {
  @apply border-b-0;
}
</style>
