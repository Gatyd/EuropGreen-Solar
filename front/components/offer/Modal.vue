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
const quoteModal = ref(false)

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
    quoteModal.value = true
}

</script>

<template>
    <Teleport to="body">
        <QuoteModal v-if="quoteModal" v-model="quoteModal" :offer="offer" />
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
                <UFormField label="Détails du projet" name="project_details" required>
                    <UTextarea v-model="state.project_details" :rows="5" class="w-full"
                        placeholder="Puissance, matériel, remarques..." />
                </UFormField>

                <!-- Panneau d'information du devis -->
                <div class="border rounded-md p-4 bg-gray-50 dark:bg-gray-800/50">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Dernier devis</span>
                        <span v-if="props.offer.last_quote" class="text-xs px-2 py-1 rounded-full"
                              :class="{
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

                    <div v-if="props.offer.last_quote" class="space-y-1 text-sm">
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
                    <div v-else class="text-sm text-gray-500 dark:text-gray-400">
                        Aucun devis
                    </div>

                    <div class="mt-3 flex gap-2 justify-end">
                        <UButton v-if="!props.offer.last_quote" color="primary" size="sm" label="Créer le devis" @click="createQuote" />
                        <UButton v-else-if="props.offer.last_quote.status === 'draft'" color="secondary" size="sm" label="Envoyer le devis" />
                        <UButton v-else-if="props.offer.last_quote.status === 'pending'" color="secondary" size="sm" label="Modifier le devis" />
                    </div>
                </div>

                <div class="col-span-2 flex justify-end mt-2">
                    <UButton type="submit" :loading="loading" color="primary" icon="i-heroicons-check-circle"
                        label="Enregistrer" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>