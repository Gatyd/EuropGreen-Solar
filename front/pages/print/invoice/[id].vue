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
</script>

<template>
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin size-12" />
    </div>

    <InvoicePreview v-else-if="invoice" :invoice="invoice" />

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
