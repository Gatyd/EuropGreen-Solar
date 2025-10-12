<script setup lang="ts">
import { useAuthStore } from '~/store/auth';
import type { ProspectRequest, ProspectStatus, ProspectSource } from '~/types/requests'

const props = defineProps<{ modelValue: boolean; item: ProspectRequest | null }>()
const emit = defineEmits(['update:modelValue', 'edit'])
const close = () => emit('update:modelValue', false)
const auth = useAuthStore()

// Fonction pour traduire les statuts
const getStatusLabel = (status: ProspectStatus): string => {
    const statusLabels = {
        'new': 'Nouvelle demande',
        'followup': 'Relance nécessaire',
        'info': 'Informations complémentaires',
        'in_progress': 'En cours de traitement',
        'closed': 'Terminé'
    }
    return statusLabels[status] || status
}

// Fonction pour traduire les sources
const getSourceLabel = (source: ProspectSource): string => {
    const sourceLabels = {
        'call_center': 'Centre d\'appels',
        'web_form': 'Formulaire web',
        'client': 'Client',
        'collaborator': 'Collaborateur',
        'commercial': 'Commercial'
    }
    return sourceLabels[source] || source
}
</script>

<template>
    <UModal :open="modelValue" @update:open="(v: boolean) => emit('update:modelValue', v)" title="Détails de la demande"
        :ui="{ title: 'text-xl', content: 'max-w-2xl' }">
        <template #body>
            <div v-if="item" class="space-y-3">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <div class="text-sm text-gray-500">Nom</div>
                        <div class="font-medium">{{ item.last_name }}</div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500">Prénom</div>
                        <div class="font-medium">{{ item.first_name }}</div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500">Email</div>
                        <div class="font-medium">{{ item.email }}</div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500">Téléphone</div>
                        <div class="font-medium">{{ item.phone }}</div>
                    </div>
                    <div class="col-span-2">
                        <div class="text-sm text-gray-500">Adresse</div>
                        <div class="font-medium">{{ item.address }}</div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500">Statut</div>
                        <div class="font-medium">{{ getStatusLabel(item.status) }}</div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500">Type de source</div>
                        <div class="font-medium">{{ getSourceLabel(item.source_type) }}</div>
                    </div>
                    <div v-if="item.source">
                        <div class="text-sm text-gray-500">Source utilisateur</div>
                        <div class="font-medium">{{ item.source.first_name }} {{ item.source.last_name }}</div>
                    </div>
                    <div v-if="item.assigned_to">
                        <div class="text-sm text-gray-500">Chargé d'affaire</div>
                        <div class="font-medium">{{ item.assigned_to.first_name }} {{ item.assigned_to.last_name }}</div>
                    </div>
                    <div v-if="item.housing_type">
                        <div class="text-sm text-gray-500">Type de logement</div>
                        <div class="font-medium">{{ item.housing_type }}</div>
                    </div>
                    <div v-if="item.electricity_bill">
                        <div class="text-sm text-gray-500">Facture d'électricité</div>
                        <UButton as="a" :href="item.electricity_bill" target="_blank" icon="i-heroicons-document"
                            variant="soft" color="primary" label="Voir la facture" />
                    </div>
                    <div v-if="item.appointment_date">
                        <div class="text-sm text-blue-600">Rendez-vous</div>
                        <div class="font-medium">{{ new Date(item.appointment_date).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }) }}</div>
                    </div>
                    <!-- Commissions (superadmin only) -->
                    <div v-if="auth.user?.is_superuser && item.commission_value && (item.source_type === 'collaborator' || item.source_type === 'client')">
                        <div class="text-sm text-gray-500">Commission source</div>
                        <div class="font-medium">{{ item.commission_type === 'percentage' ? `${item.commission_value}%` : `${item.commission_value}€` }}</div>
                    </div>
                    <div v-if="auth.user?.is_superuser && item.sales_commission_value && item.assigned_to">
                        <div class="text-sm text-blue-600">Commission commercial</div>
                        <div class="font-medium">{{ item.sales_commission_type === 'percentage' ? `${item.sales_commission_value}%` : `${item.sales_commission_value}€` }}</div>
                    </div>
                    <div v-if="item.created_by && auth.user?.is_superuser">
                        <div class="text-sm text-gray-500">Créée par</div>
                        <div class="font-medium">{{ item.created_by.first_name }} {{ item.created_by.last_name }}</div>
                    </div>
                </div>
                <div class="flex items-center justify-between pt-4 border-t mt-4">
                    <UButton color="secondary" variant="soft" icon="i-heroicons-pencil-square" label="Modifier"
                        @click="emit('edit')" />
                    <UButton v-if="item.status === 'closed'" color="primary" icon="i-heroicons-arrow-right-circle"
                        label="Transformer en offre" />
                </div>
            </div>
        </template>
    </UModal>
</template>
