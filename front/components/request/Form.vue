<script setup lang="ts">
import type { ProspectRequestPayload, ProspectStatus, ProspectSource, ProspectRequest } from '~/types/requests'

const props = defineProps<{ modelValue?: ProspectRequest | null }>()
const emit = defineEmits(['submit'])

const loading = ref(false)

const state = reactive<ProspectRequestPayload>({
    last_name: '',
    first_name: '',
    email: '',
    phone: '',
    address: '',
    housing_type: '',
    electricity_bill: null,
    status: 'new' as ProspectStatus,
    source: 'web_form' as ProspectSource,
    assigned_to_id: undefined,
    // notes: ''
})

watch(() => props.modelValue, (v) => {
    if (v) Object.assign(state, v)
    state.assigned_to_id = v?.assigned_to?.id
}, { immediate: true })

const validate = (st: any) => {
    const errors: any[] = []
    if (!st.last_name) errors.push({ name: 'last_name', message: 'Nom obligatoire.' })
    if (!st.first_name) errors.push({ name: 'first_name', message: 'Prénom obligatoire.' })
    if (!st.email) errors.push({ name: 'email', message: 'Email obligatoire.' })
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(st.email)) errors.push({ name: 'email', message: 'Email invalide.' })
    if (!st.phone) errors.push({ name: 'phone', message: 'Téléphone obligatoire.' })
    if (!st.address) errors.push({ name: 'address', message: 'Adresse obligatoire.' })
    return errors
}

const submit = async () => {
    loading.value = true
    const form = new FormData()
    form.append('last_name', state.last_name)
    form.append('first_name', state.first_name)
    form.append('email', state.email)
    form.append('phone', state.phone)
    form.append('address', state.address)
    if (state.housing_type) form.append('housing_type', state.housing_type)
    if (state.electricity_bill) form.append('electricity_bill', state.electricity_bill)
    if (state.status) form.append('status', state.status)
    form.append('source', state.source)
    if (state.assigned_to_id) form.append('assigned_to_id', state.assigned_to_id)
    // if (state.notes) form.append('notes', state.notes)
    emit('submit', form)
    loading.value = false
}
</script>

<template>
    <UForm :state="state" :validate="validate" @submit="submit" class="w-full">
        <div class="grid grid-cols-2 gap-5 mb-6">
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
            <UFormField label="Adresse" name="address" required class="col-span-2">
                <UInput v-model="state.address" class="w-full" />
            </UFormField>
            <div class="space-y-5">
                <UFormField label="Employé chargé d'affaire" name="assigned_to_id">
                    <UserSelectMenu v-model="state.assigned_to_id" class="w-full" />
                </UFormField>
                <UFormField label="Type de logement" name="housing_type">
                    <UInput v-model="state.housing_type" class="w-full" />
                </UFormField>
            </div>
            <UFormField label="Facture d’électricité (optionnelle)" description="JPG, PNG ou PDF" name="electricity_bill">
                <UFileUpload class="w-full" />
            </UFormField>
            <!-- <UFormField label="Notes" name="notes" class="col-span-2">
				<UTextarea v-model="state.notes" :rows="3" />
			</UFormField> -->
        </div>
        <div class="flex justify-center">
            <UButton type="submit" :loading="loading" icon="i-heroicons-check-circle" label="Valider" />
        </div>
    </UForm>

</template>
