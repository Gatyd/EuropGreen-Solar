<script setup lang="ts">
import type { Product } from '~/types/billing'

const props = defineProps({
    product: {
        type: Object as PropType<Product>,
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
            () => $fetch(`/api/products/${props.product.id}/`, {
                method: 'DELETE',
                credentials: "include"
            }),
            toast
        )
        toast.add({
            title: 'Succès',
            description: 'Produit / Service supprimé avec succès',
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
    <UModal v-model:open="model" title="Supprimer un produit"
        :ui="{ content: 'max-w-2xl', header: 'border-none text-xl justify-center', body: 'sm:pt-0' }">
        <template #body>
            <div class="flex flex-col justify-center items-center gap-4">
                <div class="text-center">
                    <p class="text-gray-600 mb-4">
                        Êtes-vous sûr de vouloir supprimer le produit/service <span class="font-bold">{{ product.name }}</span> ?
                    </p>
                    <p class="text-red-500 mb-4">
                        Cette action est irréversible mais ne supprimera pas les informations du produit/service dans
                        les transactions passées.
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