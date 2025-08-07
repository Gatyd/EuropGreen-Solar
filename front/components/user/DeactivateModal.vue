<template>
    <UModal v-model:open="model" :close="false">
        <template #body>
            <div class="p-3">
                <!-- En-tête du modal -->
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
                        <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-red-600 dark:text-red-400" />
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                            Désactiver l'utilisateur {{ `${user.first_name.split(" ")[0]} ${user.last_name.split(" ")[0]}` }}
                        </h3>
                    </div>
                </div>

                <!-- Texte d'avertissement -->
                <div class="mb-3">
                    <div class="space-y-3">
                        <p class="text-sm text-gray-700 dark:text-gray-300">
                            Vous êtes sur le point de <strong>désactiver temporairement</strong> ou <strong>définitivement</strong> ce compte.
                            Cette action est <strong>irréversible</strong>.
                        </p>

                        <!-- Risques de la suppression -->
                        <div class="mt-4">
                            <div
                                class="p-4 border border-red-200 dark:border-red-800 rounded-lg bg-red-50 dark:bg-red-950/20">
                                <h4 class="font-medium text-red-800 dark:text-red-200 mb-2 flex items-center gap-2">
                                    <UIcon name="i-heroicons-x-circle" class="w-4 h-4" />
                                    Conséquences de la désactivation
                                </h4>
                                <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                                    <li>• L'utilisateur ne pourra plus se connecter sur la plateforme</li>
                                    <li>• Les projets en cours de cet utilisateur ne pourront plus être suivis</li>
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

                    <UButton type="button" color="error" size="lg" :loading="loading" icon="i-heroicons-x-circle"
                        class="sm:order-2 w-full sm:w-auto" @click="deactivateUser" :disabled="loading">
                        Désactiver l'utilisateur
                    </UButton>
                </div>
            </div>
        </template>
    </UModal>
</template>

<script setup lang="ts">
import type { User } from '~/types';

const model = defineModel({
    type: Boolean,
    default: false
})

const props = defineProps<{
    user: User
}>()

const emit = defineEmits(['deactivate'])
const loading = ref(false)
const toast = useToast()

const deactivateUser = async () => {
    if (!props.user) return

    loading.value = true

    const result = await apiRequest(
        () => $fetch(`/api/users/${props.user!.id}/deactivate/`, {
            method: 'PATCH'
        }),
        toast
    )

    if (result !== null) {
        toast.add({
            title: 'Utilisateur désactivé',
            description: `Le compte de ${props.user.first_name.split(" ")[0]} ${props.user.last_name.split(" ")[0]} a été désactivé avec succès.`,
            icon: 'i-heroicons-x-circle',
            color: 'success'
        })
        model.value = false
        emit('deactivate', props.user)
    }

    loading.value = false
}

</script>