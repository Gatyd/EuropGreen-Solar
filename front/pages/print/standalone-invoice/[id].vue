<script setup lang="ts">
import type { Invoice } from '~/types/billing'

definePageMeta({
    layout: false,
})

const route = useRoute()
const invoice = ref<Invoice | null>(null)
const loading = ref(true)
const auto = computed(() => route.query.auto === '1' || route.query.auto === 'true')

onMounted(async () => {
    try {
        const res = await $fetch<Invoice>(`/api/invoices/${route.params.id}/`, { 
            credentials: 'include',
            headers: useRequestHeaders(['cookie'])
        })
        invoice.value = res
    } catch (e) {
        console.error('Erreur chargement facture:', e)
    } finally {
        loading.value = false
        if (auto.value && invoice.value) {
            // Impression seulement si auto demandé et données prêtes
            nextTick(() => {
                setTimeout(() => {
                    window.print()
                }, 80)
            })
        }
    }
    if (auto.value) {
        window.addEventListener('afterprint', () => {
            // Revenir à l'appli : focus onglet parent si existe puis fermer
            try { window.opener?.focus?.() } catch { }
            window.close()
        })
    }
})

const draft = computed(() => {
    if (!invoice.value) return null
    return {
        custom_recipient_name: invoice.value.custom_recipient_name || '',
        custom_recipient_company: invoice.value.custom_recipient_company || '',
        custom_recipient_address: invoice.value.custom_recipient_address || '',
        custom_recipient_siret: invoice.value.custom_recipient_siret || '',
        title: invoice.value.title || '',
        notes: invoice.value.notes || '',
        tax_rate: typeof invoice.value.tax_rate === 'string' ? parseFloat(invoice.value.tax_rate) : (invoice.value.tax_rate || 20),
        lines: (invoice.value.lines || []).map((l: any) => ({
            productId: '',
            name: l.name,
            description: l.description,
            unit_price: parseFloat(l.unit_price),
            cost_price: l.cost_price ? parseFloat(l.cost_price) : 0,
            product_type: l.product_type,
            quantity: parseFloat(l.quantity),
            discount_rate: l.discount_rate ? parseFloat(l.discount_rate) : 0,
        }))
    }
})
</script>

<template>
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin size-12" />
    </div>

    <InvoiceStandalonePreview v-else-if="draft && invoice" :draft="draft" :invoice="invoice" />

    <div v-else class="flex items-center justify-center min-h-screen">
        <p class="text-gray-600">Facture introuvable</p>
    </div>
</template>

<style>
@media print {
    body {
        margin: 0;
        padding: 0;
    }
}
</style>
