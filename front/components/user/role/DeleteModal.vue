<template>
    <UModal v-model:open="model" :close="false">
        <template #body>
            <div class="p-3">
                <!-- En-tête du modal -->
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 bg-error-100 dark:bg-error-900/30 rounded-lg flex items-center justify-center">
                        <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-error-600 dark:text-error-400" />
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                            Supprimer le rôle "{{ role?.name }}"
                        </h3>
                    </div>
                </div>

                <!-- Texte d'avertissement -->
                <div class="mb-3">
                    <div class="space-y-3">
                        <p class="text-sm text-gray-700 dark:text-gray-300">
                            Vous êtes sur le point de <strong>supprimer définitivement</strong> ce rôle.
                        </p>

                        <!-- Risques de la suppression -->
                        <div class="mt-4">
                            <div
                                class="p-4 border border-error-200 dark:border-error-800 rounded-lg bg-error-50 dark:bg-error-950/20">
                                <h4 class="font-medium text-error-800 dark:text-error-200 mb-2 flex items-center gap-2">
                                    <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
                                    Conséquences de la suppression
                                </h4>
                                <ul class="text-sm text-error-700 dark:text-error-300 space-y-1">
                                    <li>• Le rôle sera supprimé définitivement et ne pourra pas être récupéré</li>
                                    <li>• Les utilisateurs avec ce rôle garderont le rôle</li>
                                    <li>• Cette action est irréversible</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Boutons d'action -->
                <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4">
                    <UButton type="button" color="neutral" variant="soft" size="lg" @click="model = false"
                        class="sm:order-1 w-full sm:w-auto" :disabled="loading">
                        Annuler
                    </UButton>

                    <UButton type="button" color="error" size="lg" :loading="loading" icon="i-heroicons-trash"
                        class="sm:order-2 w-full sm:w-auto" @click="deleteRole" :disabled="loading">
                        Supprimer définitivement
                    </UButton>
                </div>
            </div>
        </template>
    </UModal>
</template>

<script setup lang="ts">
import type { Role } from '~/types';

const model = defineModel({
    type: Boolean,
    default: false
})

const props = defineProps<{
    role?: Role | null
}>()

const emit = defineEmits(['deleted'])
const loading = ref(false)
const toast = useToast()

const deleteRole = async () => {
    if (!props.role) return

    loading.value = true

    const result = await apiRequest(
        () => $fetch(`/api/roles/${props.role!.id}/`, {
            method: 'DELETE',
            credentials: 'include'
        }),
        toast
    )

    if (result !== null) {
        toast.add({
            title: 'Rôle supprimé',
            description: `Le rôle "${props.role.name}" a été supprimé avec succès.`,
            icon: 'i-heroicons-trash',
            color: 'success'
        })
        model.value = false
        emit('deleted', props.role)
    }

    loading.value = false
}

</script>