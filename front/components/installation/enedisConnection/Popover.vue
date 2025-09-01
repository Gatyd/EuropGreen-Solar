<script setup lang="ts">

const props = defineProps<{
    formId: string
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const checked = ref(false)
const loading = ref(false)

const submitEnedisConnection = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest(() => $fetch(`/api/installations/forms/${props.formId}/enedis-connection/`, {
        method: 'POST',
        credentials: 'include'
    }), toast)
    if (res) {
        loading.value = false
        toast.add({
            title: 'Raccordement ENEDIS validé avec succès',
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
            label="Valider le raccordement ENEDIS" />
        <template #content>
            <div class="p-4 max-w-xs flex flex-col gap-4">
                <UCheckbox v-model="checked" label="J'atteste que le raccordement ENEDIS a été effectué." />
                <div>
                    <UButton color="primary" size="xs" label="Valider" :loading="loading" :disabled="!checked"
                        @click="submitEnedisConnection" />
                </div>
            </div>
        </template>
    </UPopover>
</template>