<script setup lang="ts">
import InvoicePreview from '~/components/invoice/Preview.vue'
import type { Invoice } from '~/types/billing'
import type { Offer } from '~/types/offers'

definePageMeta({ layout: false, middleware: [] })

const route = useRoute()
const id = route.params.id as string
const auto = computed(() => route.query.auto === '1' || route.query.auto === 'true')

const form = ref<any | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)

useSeoMeta({ title: 'Facture' })

async function load() {
    try {
        const f = await $fetch(`/api/installations/forms/${id}/`)
        form.value = f
    } catch (e: any) {
        error.value = e?.message || 'Erreur chargement de la facture'
    } finally {
        pending.value = false
        if (auto.value && form.value?.invoice && form.value?.offer) {
            // Impression seulement si auto demandé et données prêtes
            nextTick(() => {
                setTimeout(() => {
                    window.print()
                }, 80)
            })
        }
    }
}

onMounted(() => {
    load()
    if (auto.value) {
        window.addEventListener('afterprint', () => {
            // Revenir à l'appli : focus onglet parent si existe puis fermer
            try { window.opener?.focus?.() } catch { }
            window.close()
        })
    }
})

const invoice = computed<Invoice | null>(() => form.value?.invoice || null)
const offer = computed<Offer | null>(() => form.value?.offer || null)
</script>

<template>
    <div class="min-h-screen">
        <div v-if="pending" class="text-center text-gray-500 p-8">Chargement…</div>
        <div v-else-if="error" class="text-center text-red-600 p-8">{{ error }}</div>
        <InvoicePreview v-else-if="invoice && offer" :invoice="invoice" :offer="offer" class="mx-auto" />
    </div>
</template>

<style>
@media print {
    body {
        background: #fff;
    }
}
</style>
