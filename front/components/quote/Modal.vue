<script setup lang="ts">
import type { Offer } from '~/types/offers'

const model = defineModel({
    type: Boolean
})

const props = defineProps<{
    offer: Offer
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
</script>
<template>
    <UModal v-model:open="model" title="Nouveau Devis" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row">
                <QuoteForm class="xl:basis-1/2" :offer="props.offer" :draft="draft" @created="q => { emit('created', q); model = false }" />
                <QuotePreview class="xl:basis-1/2" :offer="props.offer" :draft="draft" />
            </div>
        </template>
    </UModal>
</template>