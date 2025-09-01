<script setup lang="ts">

const props = defineProps<{
    formId: string
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const loading = ref(false)

const yesNoItems = [
    { label: 'Oui', value: 'yes' },
    { label: 'Non', value: 'no' }
]

const state = reactive({
    handover_receipt_given: false
})

const passedYN = computed<string>({
    get: () => (state.handover_receipt_given ? 'yes' : 'no'),
    set: (v: string) => { state.handover_receipt_given = v === 'yes' }
})

const submitCommissioning = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest(() => $fetch(`/api/installations/forms/${props.formId}/commissioning/`, {
        method: 'POST',
        body: state,
        credentials: 'include'
    }), toast)
    if (res) {
        loading.value = false
        toast.add({
            title: `Projet ${state.handover_receipt_given ? 'finalisé' : 'mis en service'} avec succès`,
            icon: 'i-heroicons-check-circle',
            color: 'success'
        })
        emit('submit')
    }
    loading.value = false
}

</script>
<template>
    <UPopover>
        <UButton icon="i-heroicons-check-badge" color="primary" size="xs" label="Mettre en service" />
        <template #content>
            <div class="p-4 flex flex-col gap-4">
                <UFormField name="passed" label="Le Procès-Verbal de réception a été remis au client">
                    <URadioGroup v-model="passedYN" :items="yesNoItems" orientation="horizontal" />
                </UFormField>
                <div>
                    <UButton color="primary" size="xs" label="Valider" :loading="loading"
                        @click="submitCommissioning" />
                </div>
            </div>
        </template>
    </UPopover>
</template>