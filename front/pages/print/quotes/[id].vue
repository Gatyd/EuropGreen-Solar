<script setup lang="ts">
import type { Quote } from '~/types/billing'
import Preview from '~/components/quote/Preview.vue'

definePageMeta({
  layout: false,
  middleware: []
})

const route = useRoute()
const id = route.params.id as string

const quote = ref<Quote | null>(null)
const offer = ref<any | null>(null)

const pending = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const q = await $fetch(`/api/quotes/${id}/`, { credentials: 'include' })
    quote.value = q as Quote
    // Récupérer l'offre liée pour afficher l'adresse client dans Preview
    if ((q as any).offer) {
      offer.value = await $fetch(`/api/offers/${(q as any).offer}/`, { credentials: 'include' })
    }
  } catch (e: any) {
    error.value = e?.message || 'Erreur lors du chargement du devis'
  } finally {
    pending.value = false
  }
})

const draft = computed(() => {
  const q = quote.value
  if (!q) return { title: '', valid_until: null, tax_rate: 20, lines: [] as any[] }
  return {
    title: q.title || '',
    valid_until: q.valid_until || null,
    tax_rate: typeof q.tax_rate === 'string' ? parseFloat(q.tax_rate) : (q.tax_rate || 20),
    lines: (q.lines || []).map(l => ({
      productId: '',
      name: l.name,
      description: l.description,
      unit_price: parseFloat(l.unit_price as unknown as string),
      quantity: parseFloat(l.quantity as unknown as string),
      discount_rate: l.discount_rate ? parseFloat(l.discount_rate as unknown as string) : 0,
    }))
  }
})
</script>

<template>
  <div class="min-h-screen py-6">
    <div v-if="pending" class="text-center text-gray-500">Chargement…</div>
    <div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
    <Preview v-else-if="quote && offer" :draft="draft" :offer="offer" :quote="quote" class="mx-auto" />
  </div>

</template>

<style>
/* Assure un fond blanc pour l'impression */
@media print {
  body {
    background: white;
  }
}
</style>
