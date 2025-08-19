<script setup lang="ts">
import type { ProspectRequest } from '~/types/requests'
import { useAuthStore } from '~/store/auth'

const props = defineProps<{ item: ProspectRequest }>()
const emit = defineEmits(['convert'])
const auth = useAuthStore()
const loading = ref(false)

const convertToOffer = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest<any>(
        () => $fetch(`/api/requests/${props.item.id}/convert_to_offer/`, { method: 'POST', credentials: 'include' }),
        toast
    )
    if (res) {
        toast.add({ title: 'Convertie en offre', description: `${props.item.last_name} ${props.item.first_name}`, icon: 'i-heroicons-check-circle', color: 'success' })
        emit('convert', props.item)
    }
    loading.value = false
}

</script>

<template>
    <UCard :ui="{ body: 'p-3' }" class="cursor-grab">
        <div class="font-medium">
            {{ item.last_name }} {{ item.first_name }}
        </div>
        <div class="text-sm text-gray-500">
            {{ item.phone }} • {{ item.email }}
        </div>
        <div class="text-xs text-gray-400 truncate">
            {{ item.address }}
        </div>
        <div v-if="item.appointment_date" class="text-xs text-blue-600 mt-1">
            <span class="font-medium">Rendez-vous :</span>
            {{ new Date(item.appointment_date).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }) }}
        </div>
        <!-- <div v-if="item.created_by" class="text-xs text-gray-500 mt-1">
            <span class="font-medium">Créée par :</span>
            {{ item.created_by.first_name }} {{ item.created_by.last_name }}
        </div> -->
        <div v-if="auth.user?.is_superuser && item.assigned_to" class="mt-2 pt-2 border-t text-xs text-gray-500">
            Chargé d'affaire: {{ item.assigned_to.first_name }} {{ item.assigned_to.last_name }}
        </div>
        <div v-if="item.status === 'closed'" class="mt-2 flex justify-end">
            <UButton size="xs" color="primary" variant="solid" icon="i-heroicons-arrow-right-circle" label="Transformer en offre" @click.stop="convertToOffer" />
        </div>
    </UCard>
</template>
