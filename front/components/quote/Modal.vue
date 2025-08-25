<script setup lang="ts">
import type { Offer } from '~/types/offers'

const model = defineModel({
    type: Boolean
})

const props = defineProps<{
    offer: Offer
    quote?: any // brouillon existant à éditer
}>()

const emit = defineEmits<{
    (e: 'created', quote: any): void
}>()

// État partagé du devis en cours de création
const draft = reactive({
    offer: props.offer.id,
    title: '',
    valid_until: '' as string | null,
    tax_rate: 20,
    notes: '',
    lines: [] as Array<{
        productId: string
        name: string
        description: string
        unit_price: number
        cost_price?: number
        product_type?: string
        quantity: number
        discount_rate: number
    }>,
})

// Pré-remplir si on édite un brouillon existant
watch(() => props.quote, (q: any) => {
    if (!q) return
    draft.title = q.title || ''
    draft.valid_until = q.valid_until || null
    draft.tax_rate = typeof q.tax_rate === 'string' ? parseFloat(q.tax_rate) : (q.tax_rate || 20)
    draft.lines = (q.lines || []).map((l: any) => ({
        productId: '',
        name: l.name,
        description: l.description,
        unit_price: parseFloat(l.unit_price),
        cost_price: l.cost_price ? parseFloat(l.cost_price) : undefined,
        product_type: l.product_type,
        quantity: parseFloat(l.quantity),
        discount_rate: l.discount_rate ? parseFloat(l.discount_rate) : 0,
    }))
}, { immediate: true })
</script>
<template>
    <UModal v-model:open="model" :title="`${quote ? 'Modification' : 'Création'} de Devis`" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row">
                <QuoteForm class="xl:basis-1/2" :offer="props.offer" :draft="draft" :quote="props.quote"
                    @created="q => { emit('created', q); model = false }" />
                <QuotePreview class="xl:basis-1/2 shadow-md rounded-lg" :offer="props.offer" :quote="props.quote" :draft="draft" />
            </div>
        </template>
    </UModal>
</template>