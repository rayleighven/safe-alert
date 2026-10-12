<template>
  <div class="flex items-center gap-2.5 rounded-xl border border-blue-100 bg-blue-50 px-3 py-2 text-blue-950" aria-label="Current date and time in Baclayon, Philippines">
    <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-blue-700" aria-hidden="true">
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <circle cx="12" cy="12" r="9" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 7v5l3 2" />
      </svg>
    </span>
    <span class="min-w-0 leading-tight" aria-live="off">
      <span class="block truncate text-xs font-medium text-blue-800">{{ date }}</span>
      <time class="mt-0.5 block text-sm font-bold tabular-nums tracking-wide text-slate-900">{{ time }}</time>
    </span>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const date = ref('')
const time = ref('')
let timerId

function updateClock() {
  const now = new Date()
  date.value = new Intl.DateTimeFormat('en-PH', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'Asia/Manila',
  }).format(now)
  time.value = new Intl.DateTimeFormat('en-PH', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: 'Asia/Manila',
  }).format(now)
}

onMounted(() => {
  updateClock()
  timerId = window.setInterval(updateClock, 1000)
})

onBeforeUnmount(() => window.clearInterval(timerId))
</script>
