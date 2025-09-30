<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { h, resolveComponent } from 'vue'
import { getPaginationRowModel } from '@tanstack/vue-table'
import apiRequest from '~/utils/apiRequest'
import type { ProspectRequest, ProspectStatus } from '~/types/requests'

interface ReferralRequest {
    id: string
    last_name: string
    first_name: string
    status: ProspectStatus
    created_at: string
    offer: { id: string; status: string } | null
    installation: {
        commission_amount: string
        commission_paid: boolean
    } | null
}

const toast = useToast()
const q = ref('')
const loading = ref(true)
const creating = ref(false)
const selected = ref<ProspectRequest | null>(null)
const items = ref<ReferralRequest[]>([])
const table = useTemplateRef('table')

const requestStatusColor: Record<ProspectStatus, string> = {
    new: 'neutral',
    followup: 'warning',
    info: 'secondary',
    in_progress: 'primary',
    closed: 'neutral'
}

const requestStatusLabel: Record<ProspectStatus, string> = {
    new: 'Nouveau',
    followup: 'À relancer',
    info: 'Renseignement',
    in_progress: 'En cours',
    closed: 'Clôturé'
}

type OfferStatus = 'to_contact' | 'phone_meeting' | 'meeting' | 'quote_sent' | 'negotiation' | 'quote_signed'

const offerStatusColor: Record<OfferStatus, string> = {
    to_contact: 'neutral',
    phone_meeting: 'secondary',
    meeting: 'secondary',
    quote_sent: 'primary',
    negotiation: 'secondary',
    quote_signed: 'success'
}

const offerStatusLabel: Record<OfferStatus, string> = {
    to_contact: 'À contacter',
    phone_meeting: 'RDV Téléphonique',
    meeting: 'RDV Physique/Visio',
    quote_sent: 'Devis envoyé',
    negotiation: 'Négociation',
    quote_signed: 'Devis signé'
}

const fetchReferrals = async () => {
    loading.value = true
    const data = await apiRequest<ReferralRequest[]>(
        () => $fetch('/api/requests/?scope=all', { credentials: 'include' }),
        toast
    )
    items.value = data || []
    loading.value = false
}

onMounted(fetchReferrals)

const newReferral = () => {
    creating.value = true
    selected.value = null
}

const submitFromModal = async (form: FormData) => {
    creating.value = false
    await fetchReferrals()
}

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR')
}

const stageLabel = (it: ReferralRequest) => (it.offer && it.offer.id ? 'Offre' : 'Demande')
const stageColor = (it: ReferralRequest) => (it.offer && it.offer.id ? 'primary' : 'secondary')

const columns: TableColumn<ReferralRequest>[] = [
    {
        accessorKey: 'last_name',
        header: 'Nom',
        cell: ({ row }) => row.original.last_name
    },
    {
        accessorKey: 'first_name',
        header: 'Prénom',
        cell: ({ row }) => row.original.first_name
    },
    {
        accessorKey: 'created_at',
        header: 'Date de soumission',
        cell: ({ row }) => formatDate(row.original.created_at)
    },
    {
        id: 'stage',
        header: 'Étape',
        cell: ({ row }) => {
            return h(resolveComponent('UBadge') as any, {
                color: stageColor(row.original),
                label: stageLabel(row.original),
                variant: 'subtle'
            })
        }
    },
    {
        id: 'status',
        header: 'Statut',
        cell: ({ row }) => {
            const it = row.original
            // Si une offre existe, afficher son statut
            if (it.offer && it.offer.id) {
                const st = it.offer.status as OfferStatus
                return h(resolveComponent('UBadge') as any, {
                    color: offerStatusColor[st],
                    label: offerStatusLabel[st],
                    variant: 'subtle'
                })
            }
            // Sinon afficher le statut de la demande
            const st = it.status as ProspectStatus
            return h(resolveComponent('UBadge') as any, {
                color: requestStatusColor[st],
                label: requestStatusLabel[st],
                variant: 'subtle'
            })
        }
    },
    {
        id: 'reward',
        header: 'Récompense',
        cell: ({ row }) => {
            const installation = row.original.installation
            if (!installation) {
                return h(resolveComponent('UBadge') as any, {
                    color: 'neutral',
                    label: 'En attente',
                    variant: 'subtle'
                })
            }
            return h(resolveComponent('UBadge') as any, {
                color: 'primary',
                label: `${installation.commission_amount} €`,
                variant: 'subtle'
            })
        }
    },
    {
        id: 'reward_status',
        header: 'Statut récompense',
        cell: ({ row }) => {
            const installation = row.original.installation
            if (!installation) {
                return h(resolveComponent('UBadge') as any, {
                    color: 'neutral',
                    label: 'En attente',
                    variant: 'subtle'
                })
            }
            return h(resolveComponent('UBadge') as any, {
                color: installation.commission_paid ? 'success' : 'warning',
                label: installation.commission_paid ? 'Payée' : 'En attente',
                variant: 'subtle'
            })
        }
    }
]

const pagination = ref({ pageIndex: 0, pageSize: 10 })
</script>

<template>
    <!-- Hero Section avec proposition de valeur -->
    <div
        class="sticky top-0 z-50 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900">
        <div class="px-4 sm:px-6 py-3 lg:py-4">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div class="flex-1 space-y-2">
                    <div class="flex items-center gap-3">
                        <h1 class="text-2xl lg:text-3xl font-bold text-primary-900 dark:text-primary-100">
                            Parrainez un proche et recevez une récompense !
                            <UBadge v-if="items?.length > 0" :label="items.length.toString()" variant="subtle" size="lg"
                                color="primary" />
                        </h1>
                    </div>
                    <p class="text-sm lg:text-base text-primary-700 dark:text-primary-300 max-w-3xl">
                        Récompense versée dès que le projet de votre filleul est finalisé.
                        Votre filleul bénéficiera également d'une réduction sur son installation.
                    </p>
                </div>
                <div class="flex items-center gap-2">
                    <UButton color="primary" size="lg" icon="i-heroicons-user-plus" label="Ajouter un filleul"
                        class="shadow-lg" @click="newReferral" />
                </div>
            </div>
        </div>
    </div>

    <!-- Toolbar de recherche -->
    <UDashboardToolbar>
        <template #left>
            <SearchInput v-model="q" placeholder="Rechercher un filleul..." />
        </template>
        <template #right>
            <UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchReferrals">
                Rafraîchir
            </UButton>
        </template>
    </UDashboardToolbar>

    <!-- Modal de création -->
    <ClientOnly>
        <RequestModal :model-value="creating" :payload="selected" title="Ajouter un filleul"
            description="Renseignez les informations de la personne que vous souhaitez parrainer"
            @update:model-value="v => creating = v" @submit="submitFromModal" />
    </ClientOnly>

    <!-- Tableau des filleuls -->
    <div class="w-full px-2 sm:px-6 space-y-4 pb-4">
        <UTable ref="table" :data="items" :columns="columns" v-model:global-filter="q" class="flex-1" :loading="loading"
            :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }" v-model:pagination="pagination" />
        <div
            class="flex flex-col md:flex-row justify-center gap-4 md:gap-0 items-center md:justify-between border-t border-(--ui-border) pt-4">
            <UFormField :ui="{ root: 'flex items-center' }" label="Lignes par page : ">
                <USelectMenu class="w-20 ms-3" :search-input="false" :items="[10, 20, 30, 40, 50]"
                    v-model="pagination.pageSize" @update:model-value="(p) => table?.tableApi?.setPageSize(p)" />
            </UFormField>
            <UPagination :default-page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
                :items-per-page="table?.tableApi?.getState().pagination.pageSize"
                :total="table?.tableApi?.getFilteredRowModel().rows.length"
                @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)" />
        </div>
    </div>
</template>
