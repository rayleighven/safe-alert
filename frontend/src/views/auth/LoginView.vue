<template>
  <main class="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
    <section
      class="relative hidden overflow-hidden bg-cover bg-center px-12 py-14 text-white lg:flex lg:flex-col lg:justify-between"
      :style="{ backgroundImage: `url(${churchBackground})` }"
    >
      <div class="absolute inset-0 bg-gradient-to-br from-blue-950/95 via-blue-800/90 to-cyan-800/80" />
      <div class="absolute -left-24 -top-24 h-72 w-72 rounded-full bg-cyan-300/20 blur-3xl" />
      <div class="absolute -bottom-20 -right-20 h-80 w-80 rounded-full bg-blue-300/20 blur-3xl" />

      <div class="relative flex items-center gap-3">
        <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-14 w-14 object-contain" />
        <div>
          <p class="text-lg font-bold tracking-wide">SAFE-ALERT</p>
          <p class="text-xs text-blue-100">Barangay disaster readiness system</p>
        </div>
      </div>

      <div class="relative max-w-xl">
        <p class="mb-4 text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200">Prepared communities save lives</p>
        <h1 class="text-4xl font-bold leading-tight xl:text-5xl">Be informed. Be prepared. Stay safe.</h1>
        <p class="mt-6 max-w-lg text-base leading-relaxed text-blue-100">
          SAFE-ALERT helps Barangay Cambanac and Poblacion coordinate household records, evacuation readiness, and timely emergency updates.
        </p>
        <img :src="safeAlertLogo" alt="" class="mt-8 h-44 object-contain object-left drop-shadow-xl xl:h-52" />
      </div>

      <p class="relative text-sm text-blue-100">Baclayon, Bohol &middot; Disaster Risk Reduction and Management</p>
    </section>

    <section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10 lg:px-14">
      <div class="w-full max-w-md">
        <div class="mb-8 text-center">
          <div class="flex items-center justify-center gap-2">
            <img :src="safeAlertLogo" alt="SAFE-ALERT logo" class="h-10 w-10 object-contain" />
            <span class="text-lg font-bold tracking-wide text-slate-800">
              SAFE-<span class="text-blue-600">ALERT</span>
            </span>
          </div>
          <h2 class="mt-5 text-3xl font-bold text-slate-900">Sign In</h2>
          <p class="mt-3 text-sm leading-relaxed text-slate-500">Use your authorized Barangay-issued account to continue.</p>
        </div>

        <form @submit.prevent="handleLogin" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div class="space-y-5">
            <div>
              <label for="username" class="mb-1.5 block text-sm font-semibold text-slate-700">Username</label>
              <input
                id="username"
                v-model="username"
                type="text"
                required
                autocomplete="username"
                placeholder="Enter your username"
                class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div>
              <label for="password" class="mb-1.5 block text-sm font-semibold text-slate-700">Password</label>
              <input
                id="password"
                v-model="password"
                type="password"
                required
                autocomplete="current-password"
                placeholder="Enter your password"
                class="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <p v-if="isLockedOut" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
              Maximum attempts tried. Try again in {{ formattedRemainingTime }}.
            </p>
            <p v-else-if="errorMessage" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{{ errorMessage }}</p>

            <button
              type="submit"
              :disabled="isLoading || isLockedOut"
              class="w-full rounded-lg bg-blue-600 py-2.5 font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-blue-300"
            >
              {{ isLoading ? 'Signing in...' : isLockedOut ? `Try again in ${formattedRemainingTime}` : 'Sign In' }}
            </button>
          </div>
        </form>

        <div class="my-7 flex items-center gap-3">
          <span class="h-px flex-1 bg-slate-200" />
          <span class="text-xs font-semibold uppercase tracking-wide text-slate-400">Authorized access only</span>
          <span class="h-px flex-1 bg-slate-200" />
        </div>

        <p class="text-center text-sm text-slate-500">Need an account? Please contact your Barangay Secretary.</p>
        <p class="mt-8 text-center text-xs leading-relaxed text-slate-400">
          Household information is protected under the Data Privacy Act of 2012 (RA 10173).
        </p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import churchBackground from '@/assets/images/baclayonchurch.jpg'
import safeAlertLogo from '@/assets/images/safe-alert-logo.png'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const lockoutUntil = ref(null)
const lockedUsername = ref(null)
const remainingSeconds = ref(0)

const LOCKOUT_STORAGE_KEY = 'safe_alert_login_lockout'
let countdownTimer = null

const authStore = useAuthStore()
const router = useRouter()

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
    await authStore.login(username.value, password.value)
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
