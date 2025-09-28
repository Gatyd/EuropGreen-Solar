<script setup lang="ts">
import AdministrativeCerfa16702AttachmentsPreview from '~/components/administrative/Cerfa16702/attachments/Preview.vue'

definePageMeta({
  layout: false,
  middleware: []
})

const route = useRoute()
const id = route.params.id as string

const form = ref<any | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)

useSeoMeta({
  title: 'CERFA 16702 - Pièces jointes',
})

onMounted(async () => {
  try {
    const f = await $fetch(`/api/installations/forms/${id}/`)
    form.value = f
  } catch (e: any) {
    error.value = e?.message || 'Erreur lors du chargement de la fiche installation'
  } finally {
    pending.value = false
  }
})

const draft = computed(() => {
  const cf: any = form.value?.cerfa16702
  if (!cf) return null
  return {
    dpc1: [], dpc1_url: cf.dpc1 || null,
    dpc2: [], dpc2_url: cf.dpc2 || null,
    dpc3: [], dpc3_url: cf.dpc3 || null,
    dpc4: [], dpc4_url: cf.dpc4 || null,
    dpc5: [], dpc5_url: cf.dpc5 || null,
    dpc6: [], dpc6_url: cf.dpc6 || null,
    dpc7: [], dpc7_url: cf.dpc7 || null,
    dpc8: [], dpc8_url: cf.dpc8 || null,
    dpc11: [], dpc11_url: cf.dpc11 || null,
    dpc11_notice_materiaux: cf.dpc11_notice_materiaux || '',
  }
})
</script>

<template>
  <div class="min-h-screen">
    <div v-if="pending" class="text-center text-gray-500">Chargement…</div>
    <div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
    <AdministrativeCerfa16702AttachmentsPreview
      v-else-if="form?.cerfa16702 && draft"
      :draft="draft"
      :cerfa16702="form?.cerfa16702"
      class="mx-auto"
    />
  </div>
  
</template>

<style>
@page { size: A4; margin: 0; }
html, body { margin: 0; padding: 0; }
@media print { body { background: white; } }
</style>
