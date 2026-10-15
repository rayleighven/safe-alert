<template>
  <main class="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
    <!-- Left Hero Column with Bohol Church Background -->
    <section
      class="relative hidden overflow-hidden bg-cover bg-center px-12 py-14 text-white lg:flex lg:flex-col lg:justify-between"
      :style="{ backgroundImage: `url(${churchBackground})` }"
    >
      <div class="absolute inset-0 bg-gradient-to-br from-[#071b33]/95 via-[#0d2f57]/90 to-[#1e40af]/80" />

      <div class="relative flex items-center gap-3.5">
        <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-12 w-12 object-contain drop-shadow" />
        <div>
          <p class="text-lg font-extrabold tracking-wide text-white">SAFE-ALERT</p>
          <p class="text-xs font-medium text-blue-200/90">Barangay Disaster Readiness System</p>
        </div>
      </div>

      <div class="relative max-w-xl">
        <p class="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-blue-300">Authorized Personnel & Residents</p>
        <h1 class="text-4xl font-extrabold leading-tight tracking-tight xl:text-5xl text-white">
          Be informed. Be prepared. Stay safe.
        </h1>
        <p class="mt-5 max-w-lg text-sm sm:text-base leading-relaxed text-blue-100/90">
          Coordinate household preparedness records, real-time evacuation tracking, and emergency advisories in Baclayon, Bohol.
        </p>
      </div>

      <div class="relative flex items-center justify-between text-xs text-blue-200/80 border-t border-white/10 pt-4">
        <span>Baclayon, Bohol &middot; DRRM Office</span>
        <span>Secure Access System</span>
      </div>
    </section>

    <!-- Right Column: Login Form -->
    <section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10 lg:px-14">
      <div class="w-full max-w-md">
        <!-- Top Brand Title -->
        <div class="mb-6 text-center">
          <router-link to="/" class="inline-flex items-center gap-2">
            <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-10 w-10 object-contain drop-shadow" />
            <span class="text-lg font-extrabold tracking-tight text-slate-800">
              SAFE-<span class="text-blue-600">ALERT</span>
            </span>
          </router-link>
          <h2 class="mt-5 text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">Sign In</h2>
          <div class="mt-2 flex items-center justify-center gap-2 text-xs sm:text-sm text-slate-500">
            <span>{{ accessLabel ? `Signing in for ${accessLabel}` : 'Authorized community login' }}</span>
            <router-link :to="{ name: 'access-select' }" class="font-semibold text-blue-600 hover:text-blue-800 transition-colors">
              (Change)
            </router-link>
          </div>
        </div>

        <!-- Form Card -->
        <form @submit.prevent="handleLogin" class="rounded-2xl border border-slate-200/80 bg-white p-6 sm:p-8 shadow-card">
          <div class="space-y-4">
            <div>
              <label for="username" class="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-700">Username</label>
              <input
                id="username"
                v-model="username"
                type="text"
                required
                autocomplete="username"
                placeholder="Enter your system username"
                class="w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2.5 text-xs sm:text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-colors"
              />
            </div>

            <div>
              <label for="password" class="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-700">Password</label>
              <div class="relative">
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  autocomplete="current-password"
                  placeholder="Enter your password"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50/60 py-2.5 pl-3.5 pr-11 text-xs sm:text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 transition-colors"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center px-3.5 text-slate-400 hover:text-slate-700 transition-colors"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="showPassword" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 4.2A10.8 10.8 0 0 1 12 4c5 0 8.3 4.1 9.5 6-0.5.8-1.3 2-2.4 3.1M6.2 6.2C4.7 7.4 3.6 9 2.5 10c1.2 1.9 4.5 6 9.5 6 1.1 0 2.1-.2 3-.5" />
                  </svg>
                  <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.5 12S5.8 6 12 6s9.5 6 9.5 6-3.3 6-9.5 6S2.5 12 2.5 12Z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Error and Lockout Banners -->
            <div v-if="isLockedOut" class="rounded-xl border border-red-200 bg-red-50 p-3 text-xs font-semibold text-red-700" role="alert">
              Too many invalid login attempts. Try again in {{ formattedRemainingTime }}.
            </div>
            <div v-else-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 p-3 text-xs font-semibold text-red-700" role="alert">
              {{ errorMessage }}
            </div>

            <button
              type="submit"
              :disabled="isLoading || isLockedOut"
              class="w-full rounded-xl bg-blue-600 py-3 text-xs sm:text-sm font-bold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-blue-300"
            >
              {{ isLoading ? 'Signing in...' : isLockedOut ? `Locked (${formattedRemainingTime})` : 'Sign In' }}
            </button>
          </div>
        </form>

        <div class="my-6 flex items-center gap-3">
          <span class="h-px flex-1 bg-slate-200" />
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Authorized personnel & residents</span>
          <span class="h-px flex-1 bg-slate-200" />
        </div>

        <p class="text-center text-xs text-slate-500">Need an account? Please contact your Barangay Secretary.</p>
        <p class="mt-6 text-center text-[11px] leading-relaxed text-slate-400">
          Household records are protected under Republic Act 10173 (Data Privacy Act of 2012).
        </p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import churchBackground from '@/assets/images/baclayonchurch.jpg'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)
const lockoutUntil = ref(null)
const lockedUsername = ref(null)
const remainingSeconds = ref(0)

const LOCKOUT_STORAGE_KEY = 'safe_alert_login_lockout'
let countdownTimer = null

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const selectedAccess = computed(() => route.query.access || '')
const accessLabel = computed(() => selectedAccess.value === 'MDRRMO' ? 'MDRRMO' : selectedAccess.value ? `Barangay ${selectedAccess.value}` : '')

const isLockedOut = computed(() => (
  remainingSeconds.value > 0
  && username.value.trim() === lockedUsername.value
))

const formattedRemainingTime = computed(() => {
  const minutes = Math.floor(remainingSeconds.value / 60)
  const seconds = String(remainingSeconds.value % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
})

function clearLockout() {
  lockoutUntil.value = null
  lockedUsername.value = null
  remainingSeconds.value = 0
  localStorage.removeItem(LOCKOUT_STORAGE_KEY)
  if (countdownTimer) {
    window.clearInterval(countdownTimer)
    countdownTimer = null
  }
}

function updateCountdown() {
  const seconds = Math.ceil((lockoutUntil.value - Date.now()) / 1000)
  if (seconds <= 0) {
    clearLockout()
    return
  }
  remainingSeconds.value = seconds
}

function startLockout(usernameToLock, durationSeconds = 60) {
  lockoutUntil.value = Date.now() + durationSeconds * 1000
  lockedUsername.value = usernameToLock.trim()
  localStorage.setItem(LOCKOUT_STORAGE_KEY, JSON.stringify({
    username: lockedUsername.value,
    until: lockoutUntil.value,
  }))
  updateCountdown()
  if (!countdownTimer) {
    countdownTimer = window.setInterval(updateCountdown, 1000)
  }
}

onMounted(() => {
  try {
    const savedLockout = JSON.parse(localStorage.getItem(LOCKOUT_STORAGE_KEY))
    if (savedLockout?.username && Number.isFinite(savedLockout.until)) {
      lockoutUntil.value = savedLockout.until
      lockedUsername.value = savedLockout.username
      updateCountdown()
      if (remainingSeconds.value > 0) {
        countdownTimer = window.setInterval(updateCountdown, 1000)
      }
    }
  } catch {
    localStorage.removeItem(LOCKOUT_STORAGE_KEY)
  }
})

onBeforeUnmount(() => {
  if (countdownTimer) {
    window.clearInterval(countdownTimer)
  }
})

async function handleLogin() {
  errorMessage.value = ''
  isLoading.value = true
  try {
    await authStore.login(username.value, password.value, selectedAccess.value)
    router.push({ name: 'dashboard' })
  } catch (error) {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data || {}

      if (status === 403) {
        startLockout(username.value)
      } else if (status === 401) {
        errorMessage.value = 'Incorrect password! Please try again.'
      } else {
        errorMessage.value =
          data.detail ||
          (data.non_field_errors && data.non_field_errors[0]) ||
          'Invalid username or password.'
      }
    } else {
      errorMessage.value = 'Unable to reach the server. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>
