<script setup lang="ts">
import type { Offer } from '~/types/offers';

const model = defineModel({
    type: Boolean
})

const props = defineProps<{
    offer: Offer
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const loading = ref(false)
const state = reactive({
    client_last_name: '',
    client_first_name: '',
    client_address: '',
    installation_power: null as number | null,
    installation_type: [] as string[]
})

watch(() => props.offer, (o) => {
    if (o) {
        state.client_first_name = o.first_name || ''
        state.client_last_name = o.last_name || ''
        state.client_address = o.address || ''
    }
}, { immediate: true })

const validate = (s: typeof state) => {
    const errors: { name: string; message: string }[] = []
    if (!s.client_last_name?.trim()) errors.push({ name: 'client_last_name', message: 'Nom obligatoire.' })
    if (!s.client_first_name?.trim()) errors.push({ name: 'client_first_name', message: 'Prénom obligatoire.' })
    if (!s.client_address?.trim()) errors.push({ name: 'client_address', message: 'Adresse obligatoire.' })
    if (s.installation_power == null || Number(s.installation_power) <= 0) {
        errors.push({ name: 'installation_power', message: 'Puissance invalide.' })
    }
    if (!s.installation_type || s.installation_type.length === 0) errors.push({ name: 'installation_type', message: 'Type d\'installation obligatoire.' })
    return errors
}

const submit = async () => {
    const toast = useToast()
    loading.value = true
    const payload = {
        offer_id: props.offer.id,
        client_first_name: state.client_first_name,
        client_last_name: state.client_last_name,
        client_address: state.client_address,
        installation_power: state.installation_power, // number -> DRF Decimal
        installation_type: state.installation_type.join(',')
    }
    const res = await apiRequest(() => $fetch('/api/installations/forms/', { method: 'POST', body: payload, credentials: 'include' }), toast)
    if (res) {
        toast.add({ title: 'Fiche d\'installation créée', color: 'success', icon: 'i-heroicons-check-circle' })
        model.value = false
        emit('submit')
    }
    loading.value = false
}

</script>

<template>
    <UModal v-model:open="model" title="Fiche d'installation">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="submit" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <UFormField label="Puissance d'installation (kWc)" name="installation_power" required>
                    <UInputNumber v-model="state.installation_power" :step="0.01" :min="0" class="w-full" />
                </UFormField>
                <UFormField label="Type d'installation" name="installation_type" required>
                    <USelect v-model="state.installation_type" multiple :items="[
                        { label: 'Sol', value: 'Sol' },
                        { label: 'Toiture', value: 'Toiture' },
                        { label: 'Hangar', value: 'Hangar' },
                        { label: 'Carport', value: 'Carport' }
                    ]" placeholder="Sélectionner..." class="w-full" />
                </UFormField>
                <UFormField label="Nom" name="client_last_name" required>
                    <UInput v-model="state.client_last_name" class="w-full" />
                </UFormField>
                <UFormField label="Prénom" name="client_first_name" required>
                    <UInput v-model="state.client_first_name" class="w-full" />
                </UFormField>
                <UFormField label="Adresse" name="client_address" class="md:col-span-2" required>
                    <UTextarea v-model="state.client_address" :rows="3" class="w-full" />
                </UFormField>
                <div class="md:col-span-2 flex justify-end mt-2">
                    <UButton type="submit" :loading="loading" color="primary" icon="i-heroicons-check-circle"
                        label="Enregistrer" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>