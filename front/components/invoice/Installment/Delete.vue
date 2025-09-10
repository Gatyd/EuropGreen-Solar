<script setup lang="ts">
import type { Installment } from '~/types/billing'

const props = defineProps({
    installment: {
        type: Object as PropType<Installment>,
        required: true
    }
})

const model = defineModel({
    type: Boolean
})

const loading = ref(false)
const toast = useToast()
const emit = defineEmits(['submit'])

const handleDelete = async () => {
    loading.value = true
    try {
        await apiRequest(
            () => $fetch(`/api/installments/${props.installment.id}/`, {
                method: 'DELETE',
                credentials: "include"
            }),
            toast
        )
        toast.add({
            title: 'Succès',
            description: 'Echéance supprimée avec succès',
            color: 'success'
        })
        emit('submit')
        model.value = false
    } catch (error) {
        console.error('Erreur lors de la suppression :', error);
    }
    loading.value = false
}
</script>

<template>
    <UModal v-model:open="model" title="Supprimer une échéance"
        :ui="{ header: 'border-none text-xl justify-center', body: 'sm:pt-0' }">
        <template #body>
            <div class="flex flex-col justify-center items-center gap-4">
                <div class="text-center">
                    <p class="text-gray-600 mb-4">
                        Êtes-vous sûr de vouloir supprimer l'échéance <span class="font-bold">{{ installment.label }}</span> ?
                    </p>
                    <p class="text-red-500 mb-4">
                        Cette action est irréversible mais les paiements liés à cette échéance ne seront pas supprimés.
                    </p>
                </div>

                <div class="flex justify-center gap-10">
                    <UButton color="neutral" variant="soft" @click="model = false" :disabled="loading">
                        Annuler
                    </UButton>
                    <UButton color="error" variant="solid" @click="handleDelete" :loading="loading" :disabled="loading">
                        Supprimer
                    </UButton>
                </div>
            </div>
        </template>
    </UModal>
</template>