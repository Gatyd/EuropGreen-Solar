<script setup lang="ts">

const model = defineModel({
    type: Boolean
})

const props = defineProps<{
    task: any
}>()

const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'deleted'): void
}>()

const toast = useToast()
const loading = ref(false)

// Supprimer la tâche
const deleteTask = async () => {
    loading.value = true
    const res = await apiRequest<any>(
        () => $fetch(`/api/tasks/${props.task.id}/`, {
            method: 'DELETE',
            credentials: 'include'
        }),
        toast
    )

    if (res !== null) {
        toast.add({
            title: 'Tâche supprimée',
            color: 'success',
            icon: 'i-heroicons-trash'
        })
        emit('deleted')
        emit('update:modelValue', false)
    }
    loading.value = false
}

// Fermer le modal
const closeModal = () => {
    emit('update:modelValue', false)
}
</script>

<template>
    <UModal v-model:open="model" @update:open="v => emit('update:modelValue', v)" title="Confirmer la suppression"
        :ui="{ content: 'max-w-md', footer: 'justify-end gap-4' }">
        <template #body>
            <p class="text-sm text-gray-600 dark:text-gray-400">
                Êtes-vous sûr de vouloir supprimer la tâche "<strong>{{ task.title }}</strong>" ?
                Cette action est irréversible.
            </p>
        </template>
        <template #footer>
            <UButton label="Annuler" color="neutral" variant="ghost" @click="closeModal" />
            <UButton label="Supprimer" variant="soft" color="error" icon="i-heroicons-trash" :loading="loading"
                @click="deleteTask" />
        </template>
    </UModal>
</template>
