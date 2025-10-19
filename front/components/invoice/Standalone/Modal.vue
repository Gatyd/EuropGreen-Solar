<script setup lang="ts">
import type { Invoice } from '~/types/billing'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    invoice?: Invoice
    action?: 'preview' | 'manage'
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

function openPrint() {
    if (!props.invoice) return
    const url = `/print/standalone-invoice/${props.invoice.id}?auto=1`
    const w = window.open(url, '_blank', 'noopener,width=1024,height=800')
}
</script>

<template>
    <UModal v-model:open="model" 
        :fullscreen="action !== 'preview'"
        :ui="{ content: action !== 'preview' ? 'max-w-screen' : 'max-w-5xl' }">
        <template #header>
            <div class="flex items-center justify-between w-full pr-2">
                <span class="font-semibold">
                    {{ action === 'preview' ? 'Aperçu' : (invoice ? 'Modification' : 'Création') }} de la facture
                </span>
                <div class="flex items-center gap-2">
                    <UButton v-if="props.invoice" size="sm" icon="i-heroicons-printer" @click="openPrint" color="primary">Imprimer</UButton>
                    <UButton icon="i-lucide-x" @click="model = false" color="neutral" variant="ghost" />
                </div>
            </div>
        </template>
        <template #body>
            <div class="" :class="action !== 'preview' ? 'flex flex-col xl:flex-row gap-4' : ''">
                <InvoiceStandaloneForm v-if="action !== 'preview'" class="xl:basis-1/2" :draft="draft" :invoice="invoice" 
                    @created="onCreated" @updated="onUpdated" />
                <InvoiceStandalonePreview 
                    :class="action !== 'preview' ? 'xl:basis-1/2 shadow-md rounded-lg border border-default bg-white' : ''"
                    :draft="draft" :invoice="invoice" />
            </div>
        </template>
    </UModal>
</template>
