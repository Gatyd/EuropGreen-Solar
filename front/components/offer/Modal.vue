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

</script>

<template>
    <UModal :open="modelValue" @update:open="v => emit('update:modelValue', v)" title="Détails de l'offre"
        :ui="{ title: 'text-xl', content: 'max-w-2xl' }">
        <template #body>
            <div class="grid grid-cols-2 gap-4">
                <UFormField label="Nom">
                    <UInput v-model="state.last_name" class="w-full" />
                </UFormField>
                <UFormField label="Prénom">
                    <UInput v-model="state.first_name" class="w-full" />
                </UFormField>
                <UFormField label="Email">
                    <UInput v-model="state.email" type="email" class="w-full" />
                </UFormField>
                <UFormField label="Téléphone">
                    <UInput v-model="state.phone" class="w-full" />
                </UFormField>
                <UFormField label="Adresse" class="col-span-2">
                    <UInput v-model="state.address" class="w-full" />
                </UFormField>
                <UFormField label="Détails du projet" class="col-span-2">
                    <UTextarea v-model="state.project_details" :rows="5" class="w-full"
                        placeholder="Puissance, matériel, remarques..." />
                </UFormField>
            </div>
            <div class="flex justify-end mt-2">
                <UButton type="submit" :loading="loading" color="primary" icon="i-heroicons-check-circle" label="Enregistrer" />
            </div>
        </template>
    </UModal>
</template>