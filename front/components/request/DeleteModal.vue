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
                            Supprimer le prospect {{ `${prospect.first_name.split(" ")[0]} ${prospect.last_name.split(" ")[0]}` }}
                        </h3>
                    </div>
                </div>

                <!-- Texte d'avertissement -->
                <div class="mb-3">
                    <div class="space-y-3">
                        <p class="text-sm text-gray-700 dark:text-gray-300">
                            Vous êtes sur le point de <strong>supprimer définitivement</strong> cette demande prospect.
                        </p>

                        <!-- Risques de la suppression -->
                        <div class="mt-4">
                            <div
                                class="p-4 border border-red-200 dark:border-red-800 rounded-lg bg-red-50 dark:bg-red-950/20">
                                <h4 class="font-medium text-red-800 dark:text-red-200 mb-2 flex items-center gap-2">
                                    <UIcon name="i-heroicons-x-circle" class="w-4 h-4" />
                                    Conséquences de la suppression
                                </h4>
                                <ul class="text-sm text-red-700 dark:text-red-300 space-y-1">
                                    <li>• La demande prospect sera supprimée définitivement</li>
                                    <li>• Si une offre est liée à ce prospect, elle sera également supprimée</li>
                                    <!-- <li>• Les installations, devis et factures liés à cette offre seront également supprimés</li> -->
                                    <li>• Les fichiers associés (factures d'électricité, documents) seront supprimés</li>
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
                        class="sm:order-2 w-full sm:w-auto" @click="deleteProspect" :disabled="loading">
                        Supprimer le prospect
                    </UButton>
                </div>
            </div>
        </template>
    </UModal>
</template>

<script setup lang="ts">
import type { ProspectRequest } from '~/types/requests';

const model = defineModel({
    type: Boolean,
    default: false
})

const props = defineProps<{
    prospect: ProspectRequest
}>()

const emit = defineEmits(['delete'])
const loading = ref(false)
const toast = useToast()

const deleteProspect = async () => {
    if (!props.prospect) return

    loading.value = true

    const result = await apiRequest(
        () => $fetch(`/api/requests/${props.prospect!.id}/`, {
            method: 'DELETE',
            credentials: 'include'
        }),
        toast
    )

    if (result !== null) {
        toast.add({
            title: 'Prospect supprimé',
            description: `La demande de ${props.prospect.first_name.split(" ")[0]} ${props.prospect.last_name.split(" ")[0]} a été supprimée avec succès.`,
            icon: 'i-heroicons-trash',
            color: 'success'
        })
        model.value = false
        emit('delete', props.prospect)
    }

    loading.value = false
}

</script>
