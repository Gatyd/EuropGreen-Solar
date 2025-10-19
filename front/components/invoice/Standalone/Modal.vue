<script setup lang="ts">
import type { Invoice } from '~/types/billing'

const model = defineModel({ type: Boolean })

const emit = defineEmits<{ (e: 'created', invoice: Invoice): void }>()

// État partagé du brouillon de facture
const draft = reactive({
    custom_recipient_name: '',
    custom_recipient_company: '',
    custom_recipient_address: '',
    custom_recipient_siret: '',
    title: '',
    notes: '',
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

function onCreated(invoice: Invoice) {
    emit('created', invoice)
    model.value = false
}
</script>

<template>
    <UModal v-model:open="model" fullscreen :ui="{ content: 'max-w-screen' }">
        <template #header>
            <div class="flex items-center justify-between w-full pr-2">
                <span class="font-semibold">Création de facture</span>
                <UButton icon="i-lucide-x" @click="model = false" color="neutral" variant="ghost" />
            </div>
        </template>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4">
                <InvoiceStandaloneForm class="xl:basis-1/2" :draft="draft" @created="onCreated" />
                <InvoiceStandalonePreview class="xl:basis-1/2 shadow-md rounded-lg border border-default bg-white"
                    :draft="draft" />
            </div>
        </template>
    </UModal>
</template>
