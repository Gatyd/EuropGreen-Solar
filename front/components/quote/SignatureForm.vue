<script setup lang="ts">
import { reactive } from 'vue'

// Placeholder pour future implémentation de signature (SES)
// On garde l'API du composant pour plus tard
const emit = defineEmits<{
  (e: 'submitted'): void
}>()

const state = reactive({})

const onSubmit = async () => {
  emit('submitted')
}
</script>

<template>
  <UForm :state="state" @submit.prevent="onSubmit">
    <UFormField name="signature" label="Signature">
      <div class="text-gray-500 text-sm">Module de signature à venir…</div>
    </UFormField>
    <div class="mt-4">
      <UButton type="submit" color="primary" label="Signer" disabled />
    </div>
  </UForm>
</template>

<style scoped>
.mt-4 { margin-top: 1rem; }
</style>
