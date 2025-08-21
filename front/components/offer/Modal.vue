<script setup lang="ts">
import type { Offer } from '~/types/offers'

const props = defineProps<{
    modelValue: boolean,
    offer: Offer
}>()
const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'submit'): void
}>()

const loading = ref(false)
const quoteLoading = ref(false)
const quoteModal = ref(false)
const quoteToEdit = ref<any | null>(null)
const previewOpen = ref(false)

const previewDraft = computed(() => {
    const q = props.offer?.last_quote as any
    if (!q) {
        return {
            title: '',
            valid_until: null,
            tax_rate: 20,
            lines: [] as Array<{ productId: string; name: string; description: string; unit_price: number; quantity: number; discount_rate: number }>
        }
    }
    return {
        title: q.title || '',
        valid_until: q.valid_until || null,
        tax_rate: Number(q.tax_rate ?? 20),
        lines: (q.lines || []).map((l: any) => ({
            productId: l.product || l.product_id || '',
            name: l.name,
            description: l.description,
            unit_price: Number(l.unit_price ?? 0),
            quantity: Number(l.quantity ?? 0),
            discount_rate: Number(l.discount_rate ?? 0)
        }))
    }
})

const state = reactive({
    last_name: '',
    first_name: '',
    email: '',
    phone: '',
    address: '',
    project_details: ''
})

watch(() => props.offer, (v) => {
    if (v) {
        Object.assign(state, v)
    }
}, { immediate: true })

const validate = (st: any) => {
    const errors: any[] = []
    if (!st.last_name) errors.push({ name: 'last_name', message: 'Nom obligatoire.' })
    if (!st.first_name) errors.push({ name: 'first_name', message: 'Prénom obligatoire.' })
    if (!st.email) errors.push({ name: 'email', message: 'Email obligatoire.' })
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(st.email)) errors.push({ name: 'email', message: 'Email invalide.' })
    if (!st.phone) errors.push({ name: 'phone', message: 'Téléphone obligatoire.' })
    if (!st.address) errors.push({ name: 'address', message: 'Adresse obligatoire.' })
    if (!st.project_details) errors.push({ name: 'project_details', message: 'Détails du projet obligatoire.' })
    return errors
}

const sendQuote = async () => {
    const toast = useToast()
    quoteLoading.value = true
    if (!props.offer.last_quote) return
    const res = await apiRequest<any>(
        () => $fetch(`/api/quotes/${props.offer.last_quote!.id}/send/`, { method: 'POST', credentials: 'include' }),
        toast
    )
    if (res) {
        toast.add({ title: 'Devis envoyé', color: 'success', icon: 'i-heroicons-paper-airplane' })
        emit('submit')
    }
    quoteLoading.value = false
}

const submit = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest<any>(
        () => $fetch(`/api/offers/${props.offer.id}/`, { method: 'PATCH', body: state, credentials: 'include' }),
        toast
    )
    if (res) {
        toast.add({ title: 'Offre modifiée avec succès', color: 'success', icon: 'i-heroicons-check-circle' })
        emit('submit')
    }
    loading.value = false
}

const createQuote = () => {
    quoteToEdit.value = null
    quoteModal.value = true
}

const editQuote = () => {
    quoteToEdit.value = props.offer.last_quote
    quoteModal.value = true
}

function onQuoteCreated(_q: any) {
    // Fermer le modal de devis et rafraîchir l'offre côté parent
    quoteModal.value = false
    emit('submit')
}

const toast = useToast()
const onMoveToInstallation = () => {
    toast.add({ title: 'Logique de déplacement vers installation à venir', color: 'info', icon: 'i-heroicons-information-circle' })
}
const onDisapproveSignature = () => {
    toast.add({ title: 'Logique de désapprobation à venir', color: 'warning', icon: 'i-heroicons-exclamation-triangle' })
}

</script>

<template>
    <Teleport to="body">
        <QuoteModal v-if="quoteModal" v-model="quoteModal" :offer="offer" :quote="quoteToEdit || undefined"
            @created="onQuoteCreated" />
    </Teleport>
    <UModal :open="modelValue" @update:open="v => emit('update:modelValue', v)" title="Détails de l'offre"
        :ui="{ title: 'text-xl', content: 'max-w-2xl' }">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="submit" class="grid grid-cols-2 gap-4">
                <UFormField label="Nom" name="last_name" required>
                    <UInput v-model="state.last_name" class="w-full" />
                </UFormField>
                <UFormField label="Prénom" name="first_name" required>
                    <UInput v-model="state.first_name" class="w-full" />
                </UFormField>
                <UFormField label="Email" name="email" required>
                    <UInput v-model="state.email" type="email" class="w-full" />
                </UFormField>
                <UFormField label="Téléphone" name="phone" required>
                    <UInput v-model="state.phone" class="w-full" />
                </UFormField>
                <UFormField label="Adresse" class="col-span-2" name="address" required>
                    <UInput v-model="state.address" class="w-full" />
                </UFormField>
                <UFormField class="col-span-2 md:col-span-1" label="Détails du projet" name="project_details" required>
                    <UTextarea v-model="state.project_details" :rows="5" class="w-full"
                        placeholder="Puissance, matériel, remarques..." />
                </UFormField>

                <!-- Panneau d'information du devis -->
                <div class="col-span-2 md:col-span-1 border rounded-md p-4 bg-gray-50 dark:bg-gray-800/50">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Dernier devis</span>
                        <span v-if="props.offer.last_quote" class="text-xs px-2 py-1 rounded-full" :class="{
                            'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200': props.offer.last_quote.status === 'draft',
                            'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200': props.offer.last_quote.status === 'sent',
                            'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-200': props.offer.last_quote.status === 'pending',
                            'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200': props.offer.last_quote.status === 'accepted',
                            'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200': props.offer.last_quote.status === 'declined'
                        }">
                            {{
                                props.offer.last_quote.status === 'draft' ? 'Brouillon' :
                                    props.offer.last_quote.status === 'sent' ? 'Envoyé' :
                                        props.offer.last_quote.status === 'pending' ? 'En attente' :
                                            props.offer.last_quote.status === 'accepted' ? 'Accepté' :
                                                props.offer.last_quote.status === 'declined' ? 'Refusé' : props.offer.last_quote.status
                            }}
                        </span>
                    </div>

                    <div v-if="props.offer.last_quote" class="flex justify-between items-center">
                        <div class="space-y-1 text-sm">
                            <div class="text-gray-700 dark:text-gray-200">
                                <span class="font-medium">N°:</span> {{ props.offer.last_quote.number }}
                            </div>
                            <div class="text-gray-700 dark:text-gray-200">
                                <span class="font-medium">Version:</span> v{{ props.offer.last_quote.version }}
                            </div>
                            <div class="text-gray-700 dark:text-gray-200">
                                <span class="font-medium">Total:</span> {{ props.offer.last_quote.total }} €
                            </div>
                        </div>
                        <!-- Si le devis est signé (signature présente), afficher l'aperçu au lieu du PDF -->
                        <UButton v-if="props.offer.last_quote.signature" variant="ghost" color="neutral" size="xl"
                            icon="i-heroicons-eye" @click="previewOpen = true" :title="'Voir l\'aperçu du devis'" />
                        <!-- Sinon, lien vers le PDF si disponible -->
                        <UButton v-else-if="props.offer.last_quote.pdf" variant="ghost" color="neutral" size="xl"
                            icon="i-heroicons-document" target="_blank" :to="props.offer.last_quote.pdf" />
                    </div>

                    <div v-else class="text-sm text-gray-500 dark:text-gray-400">
                        Aucun devis
                    </div>

                    <div class="mt-3 flex gap-2 justify-end">
                        <UButton v-if="!props.offer.last_quote" color="primary" size="sm" label="Créer le devis"
                            @click="createQuote" />
                        <template v-else>
                            <UButton v-if="props.offer.last_quote.status === 'draft'" color="secondary" size="sm"
                                label="Modifier le brouillon" @click="editQuote" />
                            <UButton v-if="props.offer.last_quote.status === 'draft'" :loading="quoteLoading"
                                color="primary" size="sm" label="Envoyer le devis" @click="sendQuote" />
                            <UButton v-else-if="props.offer.last_quote.status === 'pending'" color="secondary" size="sm"
                                label="Modifier le devis (négociation)" @click="editQuote" />
                            <!-- Actions d'administration -->
                            <UButton v-if="props.offer.last_quote.signature" color="error" size="sm" variant="soft"
                                icon="i-heroicons-x-circle" label="Désapprouver signature"
                                @click="onDisapproveSignature" />
                        </template>
                    </div>
                </div>

                <div class="col-span-2 flex justify-between mt-2">
                    <UButton type="submit" :loading="loading" color="secondary" icon="i-heroicons-pencil-square"
                        label="Modifier" />
                    <UButton v-if="props.offer.status === 'quote_signed'" color="primary" size="sm" variant="solid"
                        icon="i-heroicons-arrow-right-circle" label="Déplacer vers installation"
                        @click="onMoveToInstallation" />
                </div>
            </UForm>
        </template>
    </UModal>

    <!-- Aperçu du devis signé -->
    <Teleport to="body">
        <UModal :open="previewOpen" @update:open="v => (previewOpen = v)" title="Aperçu du devis"
            :ui="{ content: 'max-w-5xl' }">
            <template #body>
                <div v-if="offer?.last_quote" class="space-y-4">
                    <QuotePreview :offer="offer" :quote="offer.last_quote" :draft="previewDraft" />
                </div>
            </template>
        </UModal>
    </Teleport>
</template>