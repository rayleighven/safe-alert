<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4" role="presentation" @click.self="$emit('cancel')">
    <section class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl" role="dialog" aria-modal="true" :aria-labelledby="titleId">
      <div class="flex h-11 w-11 items-center justify-center rounded-full bg-blue-50 text-blue-600">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.3 3.7 2.9 16.5A2 2 0 0 0 4.6 19.5h14.8a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z" /></svg>
      </div>
      <h2 :id="titleId" class="mt-4 text-lg font-bold text-slate-900">{{ title }}</h2>
      <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ message }}</p>
      <div class="mt-6 flex justify-end gap-3">
        <button type="button" class="rounded-lg px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100" @click="$emit('cancel')">Cancel</button>
        <button type="button" :class="confirmClass" class="rounded-lg px-4 py-2 text-sm font-semibold text-white shadow-sm" @click="$emit('confirm')">{{ confirmLabel }}</button>
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
