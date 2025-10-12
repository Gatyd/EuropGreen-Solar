<script setup lang="ts">
import type { ProspectRequest } from '~/types/requests'
import { useAuthStore } from '~/store/auth'

const props = defineProps<{ item: ProspectRequest }>()
const emit = defineEmits(['convert'])
const auth = useAuthStore()
const loading = ref(false)

const toast = useToast()

const setDecision = async (value: boolean) => {
    if (loading.value) return
    loading.value = true
    const res = await apiRequest<ProspectRequest>(
        () => $fetch(`/api/requests/${props.item.id}/`, { method: 'PATCH', credentials: 'include', body: { converted_decision: value } }),
        toast
    )
    if (res) {
        props.item.converted_decision = value
        toast.add({ title: 'Décision enregistrée', description: value ? 'Prospect converti' : 'Prospect abandonné', color: value ? 'success' : 'warning', icon: value ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle' })
    }
    loading.value = false
}

const convertToOffer = async () => {
    loading.value = true
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
    <UCard :ui="{ body: 'p-3 sm:p-4' }" class="cursor-grab">
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
        <div v-if="item.status === 'closed' && item.converted_decision !== undefined && item.converted_decision !== null"
            class="mt-1">
            <UBadge :color="item.converted_decision ? 'success' : 'warning'" variant="subtle" size="sm">
                {{ item.converted_decision ? 'Converti' : 'Abandonné' }}
            </UBadge>
        </div>
        <!-- <div v-if="item.created_by" class="text-xs text-gray-500 mt-1">
            <span class="font-medium">Créée par :</span>
            {{ item.created_by.first_name }} {{ item.created_by.last_name }}
        </div> -->
        <div v-if="auth.user?.is_superuser && item.assigned_to" class="mt-2 pt-2 border-t text-xs text-gray-500">
            Chargé d'affaire: {{ item.assigned_to.first_name }} {{ item.assigned_to.last_name }}
            <span v-if="item.sales_commission_value && item.assigned_to">(Commission: {{ item.sales_commission_type ===
                'percentage' ? `${item.sales_commission_value}%` : `${item.sales_commission_value}€` }})</span>
        </div>
        <div v-if="item.commission_value && (item.source_type === 'collaborator' || item.source_type === 'client')"
            class="mt-2 pt-2 border-t text-xs space-y-1 text-gray-600">
            <span class="font-medium">
                Commission {{ !auth.user?.is_superuser ? '' : item.source_type === 'collaborator' ? 'collaborateur' : 'client'}}:
                {{ item.commission_type === 'percentage' ? `${item.commission_value}%` : `${item.commission_value}€` }}
            </span>
        </div>
        <div class="mt-2 flex flex-wrap gap-2 justify-end">
            <!-- Si fermé et pas encore de décision -->
            <template
                v-if="item.status === 'closed' && (item.converted_decision === undefined || item.converted_decision === null)">
                <UButton size="xs" :loading="loading" color="success" variant="subtle" icon="i-heroicons-check-circle"
                    label="Converti" @click.stop="setDecision(true)" />
                <UButton size="xs" :loading="loading" color="warning" variant="subtle" icon="i-heroicons-x-mark"
                    label="Abandonné" @click.stop="setDecision(false)" />
            </template>
            <!-- Bouton transformer en offre seulement si décision = converti -->
            <UButton v-if="item.status !== 'closed' || (item.converted_decision === true && !item.offer)" size="xs"
                :loading="loading" icon="i-heroicons-arrow-right-circle" label="Transformer en offre"
                @click.stop="convertToOffer" />
        </div>
    </UCard>
</template>
