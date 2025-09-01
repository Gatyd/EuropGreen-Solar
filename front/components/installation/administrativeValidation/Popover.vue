<script setup lang="ts">

const props = defineProps<{
    formId: string
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const checked = ref(false)
const loading = ref(false)

const submitAdministrativeValidation = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest(() => $fetch(`/api/installations/forms/${props.formId}/administrative-validation/`, {
        method: 'POST',
        credentials: 'include'
    }), toast)
    if (res) {
        loading.value = false
        toast.add({
            title: 'Démarches administratives validées avec succès',
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
        <UButton icon="i-heroicons-document-check" color="primary" size="xs"
            label="Valider les démarches administratives" />
        <template #content>
            <div class="p-4 max-w-xs flex flex-col gap-4">
                <UCheckbox v-model="checked" label="J'atteste que les démarches administratives ont été effectuées." />
                <div>
                    <UButton color="primary" size="xs" label="Valider" :loading="loading" :disabled="!checked"
                        @click="submitAdministrativeValidation" />
                </div>
            </div>
        </template>
    </UPopover>
</template>