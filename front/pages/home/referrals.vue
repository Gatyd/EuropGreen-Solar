<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { h, resolveComponent } from 'vue'
import { getPaginationRowModel } from '@tanstack/vue-table'
import apiRequest from '~/utils/apiRequest'
import type { ProspectStatus } from '~/types/requests'

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

const fetchReferrals = async () => {
    loading.value = true
    const data = await apiRequest<ReferralRequest[]>(
        () => $fetch('/api/requests/', { credentials: 'include' }),
        toast
    )
    items.value = data || []
    loading.value = false
}

onMounted(fetchReferrals)

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR')
}

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
        id: 'status',
        header: 'Statut',
        cell: ({ row }) => {
            const st = row.original.status as ProspectStatus
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
    <div class="sticky top-0 z-50 bg-white">
        <UDashboardNavbar title="Filleuls" class="lg:text-2xl font-semibold"
            :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
            <template #trailing>
                <UBadge v-if="items?.length as number > 0" :label="items?.length" variant="subtle" />
            </template>
            <template #right>

            </template>
        </UDashboardNavbar>
    </div>
    <UDashboardToolbar>
        <template #left>
            <SearchInput v-model="q" />
        </template>
        <template #right>
            <UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchReferrals">Rafraîchir</UButton>
        </template>
    </UDashboardToolbar>

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
