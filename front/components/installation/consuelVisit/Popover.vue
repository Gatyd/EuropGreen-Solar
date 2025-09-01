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
    passed: false,
    refusal_reason: ''
})

const passedYN = computed<string>({
    get: () => (state.passed ? 'yes' : 'no'),
    set: (v: string) => { state.passed = v === 'yes' }
})

const submitConsuelVisit = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest(() => $fetch(`/api/installations/forms/${props.formId}/consuel-visit/`, {
        method: 'POST',
        body: state,
        credentials: 'include'
    }), toast)
    if (res) {
        loading.value = false
        toast.add({
            title: 'Conformité CONSUEL enregistrée avec succès',
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
        <UButton icon="i-heroicons-check-badge" color="primary" size="xs"
            label="Valider la conformité CONSUEL" />
        <template #content>
            <div class="p-4 flex flex-col gap-4">
                <UFormField name="passed" label="La visite du CONSUEL a été validée ">
                    <URadioGroup v-model="passedYN" :items="yesNoItems" orientation="horizontal" />
                </UFormField>
                <UFormField v-if="!state.passed" name="refusal_reason" label="Raison du refus">
                    <UTextarea v-model="state.refusal_reason" placeholder="Raison du refus" :rows="3" class="w-full" />
                </UFormField>
                <div>
                    <UButton color="primary" size="xs" label="Valider" :loading="loading" :disabled="!state.passed && !state.refusal_reason"
                        @click="submitConsuelVisit" />
                </div>
            </div>
        </template>
    </UPopover>
</template>