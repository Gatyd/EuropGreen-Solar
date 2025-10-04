<script setup lang="ts">
interface Log {
    id: number
    timestamp: string
    action: number
    action_display: string
    object_type: string
    object_app: string
    object_repr: string
    object_pk: string
    changes: Record<string, [any, any]>
    actor_name: string
    actor_email: string | null
    remote_addr: string | null
    additional_data: any
}

const props = defineProps<{
    log: Log
}>()

// Badge variant selon le type d'action
function getActionBadgeColor(action: number): 'success' | 'secondary' | 'error' | 'neutral' {
    const colors: Record<number, 'success' | 'secondary' | 'error' | 'neutral'> = {
        0: 'success',
        1: 'secondary',
        2: 'error',
    }
    return colors[action] || 'neutral'
}

// Traduction des actions
function getActionLabel(actionDisplay: string): string {
    const labels: Record<string, string> = {
        'create': 'Création',
        'update': 'Mise à jour',
        'delete': 'Suppression',
    }
    return labels[actionDisplay.toLowerCase()] || actionDisplay
}

// Icône selon le type d'objet
function getObjectIcon(objectType: string): string {
    const icons: Record<string, string> = {
        user: 'i-heroicons-user',
        prospectrequest: 'i-heroicons-document-text',
        offer: 'i-heroicons-light-bulb',
        quote: 'i-heroicons-document-currency-dollar',
        form: 'i-heroicons-wrench-screwdriver',
        invoice: 'i-heroicons-receipt-percent',
        cerfa16702: 'i-heroicons-document-check',
        consuel: 'i-heroicons-shield-check',
        task: 'i-heroicons-calendar',
        emaillog: 'i-heroicons-envelope',
        technicalvisit: 'i-heroicons-clipboard-document-check',
        representationmandate: 'i-heroicons-document-text',
        administrativevalidation: 'i-heroicons-shield-check',
        installationcompleted: 'i-heroicons-check-circle',
        consuelvisit: 'i-heroicons-clipboard-document-check',
        enedisconnection: 'i-heroicons-bolt',
        commissioning: 'i-heroicons-power',
    }
    return icons[objectType] || 'i-heroicons-cube'
}

// Traduction des types d'objets
function getObjectTypeLabel(objectType: string): string {
    const labels: Record<string, string> = {
        user: 'Utilisateur',
        prospectrequest: 'Demande',
        offer: 'Offre',
        quote: 'Devis',
        quoteline: 'Ligne de devis',
        form: 'Fiche installation',
        invoice: 'Facture',
        invoiceline: 'Ligne de facture',
        cerfa16702: 'CERFA 16702',
        consuel: 'CONSUEL',
        task: 'Tâche',
        emaillog: 'Email',
        product: 'Produit',
        signature: 'Signature',
        technicalvisit: 'Visite technique',
        representationmandate: 'Mandat de représentation',
        administrativevalidation: 'Validation administrative',
        installationcompleted: 'Installation effectuée',
        consuelvisit: 'Visite CONSUEL',
        enedisconnection: 'Raccordement ENEDIS',
        commissioning: 'Mise en service',
    }
    return labels[objectType] || objectType
}

// Formater la date
function formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// Traduction des champs communs
function translateField(field: string): string {
    const translations: Record<string, string> = {
        status: 'Statut',
        first_name: 'Prénom',
        last_name: 'Nom',
        email: 'Email',
        phone: 'Téléphone',
        phone_number: 'Téléphone',
        address: 'Adresse',
        is_active: 'Compte actif',
        accept_invitation: 'Invitation acceptée',
        created_at: 'Date de création',
        updated_at: 'Date de modification',
    }
    return translations[field] || field
}
</script>

<template>
    <UCard class="mt-1">
        <div class="space-y-3">
            <!-- En-tête -->
            <div class="flex items-start justify-between gap-4">
                <div class="flex items-start gap-3 flex-1 min-w-0">
                    <UIcon :name="getObjectIcon(log.object_type)" class="text-2xl text-gray-600 flex-shrink-0" />
                    <div class="min-w-0 flex-1">
                        <div class="flex items-center gap-2 flex-wrap">
                            <UBadge :color="getActionBadgeColor(log.action)" variant="subtle" size="sm">
                                {{ getActionLabel(log.action_display) }}
                            </UBadge>
                            <span class="text-sm font-medium text-gray-700">
                                {{ getObjectTypeLabel(log.object_type) }}
                            </span>
                        </div>
                        <p class="text-sm text-gray-900 mt-1 font-semibold truncate">
                            {{ log.object_repr }}
                        </p>
                    </div>
                </div>

                <div class="flex flex-col items-end gap-1 flex-shrink-0">
                    <span class="text-xs text-gray-500 whitespace-nowrap">
                        {{ formatDate(log.timestamp) }}
                    </span>
                    <span v-if="log.remote_addr" class="text-xs text-gray-400">
                        {{ log.remote_addr }}
                    </span>
                </div>
            </div>

            <!-- Détails des changements (si UPDATE) -->
            <div v-if="log.changes && Object.keys(log.changes).length > 0" class="mt-3">
                <details class="group">
                    <summary
                        class="cursor-pointer text-sm text-gray-600 hover:text-gray-800 flex items-center gap-2 select-none">
                        <UIcon name="i-heroicons-chevron-right"
                            class="transform group-open:rotate-90 transition-transform" />
                        <span class="font-medium">Voir les changements ({{ Object.keys(log.changes).length }})</span>
                    </summary>
                    <div class="mt-3 p-3 bg-gray-50 rounded-lg text-xs space-y-2">
                        <div v-for="([field, values], index) in Object.entries(log.changes)" :key="index"
                            class="border-l-2 border-primary-400 pl-3 py-1">
                            <div class="font-semibold text-gray-700 mb-1">{{ translateField(field) }}</div>
                            <div class="flex items-center gap-2 text-gray-600">
                                <span class="line-through text-red-600 break-all">
                                    {{ (values as any[])[0] || '(vide)' }}
                                </span>
                                <UIcon name="i-heroicons-arrow-right" class="text-xs flex-shrink-0" />
                                <span class="text-green-600 font-medium break-all">
                                    {{ (values as any[])[1] || '(vide)' }}
                                </span>
                            </div>
                        </div>
                    </div>
                </details>
            </div>
        </div>
    </UCard>
</template>
