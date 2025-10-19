<script setup lang="ts">
import type { Invoice } from '~/types/billing'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    invoice?: Invoice
}>()

const emit = defineEmits<{ (e: 'created', invoice: Invoice): void; (e: 'updated'): void }>()

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

// Pré-remplir si on édite une facture existante
watch(() => props.invoice, (inv) => {
    if (!inv) return
    draft.custom_recipient_name = inv.custom_recipient_name || ''
    draft.custom_recipient_company = inv.custom_recipient_company || ''
    draft.custom_recipient_address = inv.custom_recipient_address || ''
    draft.custom_recipient_siret = inv.custom_recipient_siret || ''
    draft.title = inv.title || 'Facture'
    draft.notes = inv.notes || ''
    draft.tax_rate = typeof inv.tax_rate === 'string' ? parseFloat(inv.tax_rate) : (inv.tax_rate || 20)
    draft.lines = (inv.lines || []).map((l: any) => ({
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

function onCreated(invoice: Invoice) {
    emit('created', invoice)
    model.value = false
}

function onUpdated() {
    emit('updated')
    model.value = false
}
</script>

<template>
    <UModal v-model:open="model" :title="`${invoice ? 'Modification' : 'Création'} de Facture`" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4">
                <InvoiceStandaloneForm class="xl:basis-1/2" :draft="draft" :invoice="invoice" @created="onCreated"
                    @updated="onUpdated" />
                <InvoiceStandalonePreview class="xl:basis-1/2 shadow-md rounded-lg border border-default bg-white"
                    :draft="draft" :invoice="invoice" />
            </div>
        </template>
    </UModal>
</template>
