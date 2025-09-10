<script setup lang="ts">
import type { Payment } from '~/types/billing'

const props = defineProps({
    payment: {
        type: Object as PropType<Payment>,
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
            () => $fetch(`/api/payments/${props.payment.id}/`, {
                method: 'DELETE',
                credentials: "include"
            }),
            toast
        )
        toast.add({
            title: 'Succès',
            description: 'Paiement supprimé avec succès',
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
    <UModal v-model:open="model" title="Supprimer un paiement"
        :ui="{ header: 'border-none text-xl justify-center', body: 'sm:pt-0' }">
        <template #body>
            <div class="flex flex-col justify-center items-center gap-4">
                <div class="text-center">
                    <p class="text-gray-600 mb-4">
                        Êtes-vous sûr de vouloir supprimer le paiement de <span class="font-bold">
                            {{ payment.amount }} €</span> effectué le {{ payment.date }} ?
                    </p>
                    <p class="text-red-500 mb-4">
                        Cette action est irréversible.
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