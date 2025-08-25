<script setup lang="ts">
import NegotiationForm from '~/components/quote/NegotiationForm.vue'
import SignatureForm from '~/components/quote/SignatureForm.vue'
import QuotePreview from '~/components/quote/Preview.vue'
import type { Offer } from '~/types/offers'

definePageMeta({ layout: false })

const route = useRoute()

const offer = ref<Offer | null>(null)
const lastQuote = ref<any | null>(null)
const state = reactive({ loading: true, error: '', success: false })

const action = computed(() => (route.query.action as string) || 'negotiation')

useSeoMeta({
    title: `Offre #${route.params.id || ''}`,
})

// draft minimal pour Preview à partir du devis existant
const draft = computed(() => {
    const q = lastQuote.value
    return q ? {
        title: q.title || '',
        valid_until: q.valid_until || null,
        tax_rate: q.tax_rate || 20,
        lines: (q.lines || []).map((l: any) => ({
            productId: l.source_product || '',
            name: l.name,
            description: l.description || '',
            unit_price: Number(l.unit_price || 0),
            quantity: Number(l.quantity || 0),
            discount_rate: Number(l.discount_rate || 0),
        })),
    } : {
        title: '', valid_until: null, tax_rate: 20, lines: [] as any[],
    }
})

const loadData = async () => {
    state.loading = true; state.error = ''
    try {
        // Récupérer l'offre (public)
        const offerRes = await $fetch(`/api/offers/${route.params.id}/`)
        offer.value = offerRes as any
        lastQuote.value = offer.value?.last_quote
        // Si des négociations existent déjà -> succès direct
        // succès pour négociation (message enregistré)
        state.success = !!(lastQuote.value && lastQuote.value.negociations && String(lastQuote.value.negociations).trim().length > 0)
        // si action=signature et devis déjà signé → succès direct
        if (action.value === 'signature' && lastQuote.value && lastQuote.value.signature) {
            state.success = true
        }
    } catch (e: any) {
        state.error = 'Devis introuvable'
    } finally {
        state.loading = false
    }
}

onMounted(loadData)

const handleNegotiationSubmit = async (message: string) => { state.success = true }
const handleSignatureSubmitted = async () => {
    state.success = true
    // recharger lastQuote pour inclure la signature
    try {
        const quotes = await $fetch(`/api/quotes/?offer=${route.params.id}`)
        const arr = (quotes as any[]).sort((a, b) => (b.version || 0) - (a.version || 0))
        lastQuote.value = arr.length ? arr[0] : null
    } catch { }
}
</script>

<template>
    <div class="px-4 py-6">
        <div v-if="state.loading" class="flex items-center justify-center min-h-[40vh]">
            <div class="flex items-center gap-3 text-gray-600">
                <span
                    class="inline-block w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
                <span>Chargement…</span>
            </div>
        </div>
        <div v-else>
            <div v-if="state.error" class="text-center text-red-600 font-medium">{{ state.error }}</div>
            <div v-else>
                <div v-if="state.success" class="flex items-center justify-center min-h-[60vh] px-2">
                    <div class="max-w-2xl w-full">
                        <div class="rounded-xl border border-emerald-200 bg-emerald-50/60 p-6">
                            <div class="flex items-start gap-3">
                                <div class="mt-0.5 text-emerald-600">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
                                        class="w-6 h-6">
                                        <path fill-rule="evenodd"
                                            d="M16.704 4.153a.75.75 0 01.143 1.052l-7.5 9.5a.75.75 0 01-1.127.075l-3.5-3.5a.75.75 0 011.06-1.06l2.894 2.893 6.973-8.834a.75.75 0 011.057-.126z"
                                            clip-rule="evenodd" />
                                    </svg>
                                </div>
                                <div>
                                    <h2 class="text-lg font-semibold text-emerald-800">
                                        {{ action === 'signature' ? 'Votre signature a bien été enregistrée' : 'Votre message a bien été enregistré' }}
                                    </h2>
                                    <p class="text-sm text-emerald-700 mt-1">
                                        {{ action === 'signature' ? "Notre équipe va approuver votre signature et commencera l'installation." : 
                                        "Notre équipe va étudier votre demande de négociation et reviendra vers vous rapidement." }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else>
                    <div class="flex flex-col xl:flex-row gap-6">
                        <!-- Colonne gauche: Formulaire -->
                        <div class="xl:basis-1/2">
                            <UCard>
                                <template #header>
                                    <div class="font-semibold">
                                        {{ action === 'signature' ? 'Signature du devis' : 'Négociation du devis' }}
                                    </div>
                                </template>
                                <div v-if="action === 'signature'">
                                    <SignatureForm :quote-id="lastQuote?.id" @submitted="handleSignatureSubmitted" />
                                </div>
                                <div v-else>
                                    <NegotiationForm :last-quote="lastQuote" @submitted="handleNegotiationSubmit" />
                                </div>
                            </UCard>
                        </div>

                        <!-- Colonne droite: Devis -->
                        <div class="xl:basis-1/2 mx-auto">
                            <UCard>
                                <template #header>
                                    <div class="font-semibold">Aperçu du devis</div>
                                </template>
                                <div v-if="offer && lastQuote" class="w-full overflow-x-auto"
                                    style="-webkit-overflow-scrolling: touch;">
                                    <QuotePreview class="inline-block shrink-0 shadow-md rounded-lg" :offer="offer"
                                        :quote="lastQuote" :draft="draft" />
                                </div>
                                <div v-else class="text-gray-500">Aucun devis à afficher</div>
                            </UCard>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
