<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-xs p-4 transition-all"
    role="presentation"
    @click.self="$emit('cancel')"
    @keydown.escape="$emit('cancel')"
  >
    <section
      class="w-full max-w-md rounded-2xl border border-slate-200/80 bg-white p-6 shadow-2xl transition-all"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="titleId"
    >
      <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-50 text-amber-600 ring-1 ring-amber-100">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.3 3.7 2.9 16.5A2 2 0 0 0 4.6 19.5h14.8a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z" />
        </svg>
      </div>
      <h2 :id="titleId" class="mt-4 text-lg font-bold tracking-tight text-slate-900">{{ title }}</h2>
      <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ message }}</p>
      <div class="mt-6 flex items-center justify-end gap-3">
        <button
          type="button"
          class="min-h-10 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-300"
          @click="$emit('cancel')"
        >
          Cancel
        </button>
        <button
          type="button"
          :class="confirmClass"
          class="min-h-10 rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2"
          @click="$emit('confirm')"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  message: { type: String, required: true },
  confirmLabel: { type: String, default: 'Continue' },
  confirmClass: { type: String, default: 'bg-blue-600 hover:bg-blue-700' },
  titleId: { type: String, default: 'confirmation-dialog-title' },
})

defineEmits(['confirm', 'cancel'])
</script>
