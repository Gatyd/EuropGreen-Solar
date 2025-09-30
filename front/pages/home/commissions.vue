<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import { getPaginationRowModel } from '@tanstack/vue-table'
import { useAuthStore } from '~/store/auth'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UTooltip = resolveComponent('UTooltip')

interface Commission {
    id: string
    client: {
        id: string
        first_name: string
        last_name: string
        email: string
    } | null
    request: {
        id: string
        source_type: string
    } | null
    source: {
        id: string
        first_name: string
        last_name: string
        email: string
        role: string
    } | null
    assigned_to: {
        id: string
        first_name: string
        last_name: string
        email: string
        role: string
    } | null
    commission_amount: number
    commission_paid: boolean
    sales_commission_amount: number
    sales_commission_paid: boolean
    created_at: string
}

const q = ref("")
const toast = useToast()
const loading = ref(true)
const commissions = ref<Commission[]>([])
const table = useTemplateRef('table')
const auth = useAuthStore()

const attributLabels: { [key: string]: string } = {
    client_name: 'Client',
    client_email: 'Email client',
    source_type: 'Type source',
    source_name: 'Source',
    assigned_to_name: 'Commercial',
    source_commission: 'Commission collaborateur',
    sales_commission: 'Commission commercial',
    actions: 'Actions'
}

async function fetchCommissions() {
    loading.value = true
    const result = await apiRequest<Commission[]>(
        () => $fetch(`/api/installations/commissions/list/`, {
            credentials: 'include'
        }),
        toast
    )
    commissions.value = result || []
    loading.value = false
}

async function paySourceCommission(commissionId: string) {
    const result = await apiRequest(
        () => $fetch(`/api/installations/commissions/${commissionId}/pay-source-commission/`, {
            method: 'PATCH',
            credentials: 'include'
        }),
        toast
    )
    if (result) {
        toast.add({
            title: 'Succès',
            description: 'Commission collaborateur marquée comme payée',
            color: 'success'
        })
        await fetchCommissions()
    }
}

async function paySalesCommission(commissionId: string) {
    const result = await apiRequest(
        () => $fetch(`/api/installations/commissions/${commissionId}/pay-sales-commission/`, {
            method: 'PATCH',
            credentials: 'include'
        }),
        toast
    )
    if (result) {
        toast.add({
            title: 'Succès',
            description: 'Commission commercial marquée comme payée',
            color: 'success'
        })
        await fetchCommissions()
    }
}

const sourceTypeLabels: Record<string, string> = {
    collaborator: 'Collaborateur',
    client: 'Client',
    other: 'Autre'
}

const columns: TableColumn<Commission>[] = [{
    accessorKey: 'client_name',
    header: 'Client',
    cell: ({ row }) => {
        const client = row.original.client
        if (!client) return '—'
        return `${client.first_name} ${client.last_name}`
    }
}, 
// {
//     accessorKey: 'client_email',
//     header: 'Email client',
//     cell: ({ row }) => row.original.client?.email || '—'
// }, 
{
    accessorKey: 'source_type',
    header: 'Type source',
    cell: ({ row }) => {
        const type = row.original.request?.source_type
        return type ? (sourceTypeLabels[type] || type) : '—'
    }
}, {
    accessorKey: 'source_name',
    header: 'Source',
    cell: ({ row }) => {
        const source = row.original.source
        if (!source) return '—'
        return `${source.first_name} ${source.last_name}`
    }
}, {
    accessorKey: 'assigned_to_name',
    header: 'Commercial',
    cell: ({ row }) => {
        const assignedTo = row.original.assigned_to
        if (!assignedTo) return '—'
        return `${assignedTo.first_name} ${assignedTo.last_name}`
    }
}, {
    accessorKey: 'source_commission',
    header: 'Commission collaborateur',
    cell: ({ row }) => {
        const amount = row.original.commission_amount
        const isPaid = row.original.commission_paid

        if (!amount || amount <= 0) {
            return h('div', { class: 'text-center' }, '—')
        }

        return h('div', { class: 'flex justify-center' }, [
            h(UBadge, {
                color: isPaid ? 'success' : 'warning',
                label: `${amount} €`,
                variant: 'subtle'
            })
        ])
    }
}, {
    accessorKey: 'sales_commission',
    header: 'Commission commercial',
    cell: ({ row }) => {
        const amount = row.original.sales_commission_amount
        const isPaid = row.original.sales_commission_paid

        if (!amount || amount <= 0) {
            return h('div', { class: 'text-center' }, '—')
        }

        return h('div', { class: 'flex justify-center' }, [
            h(UBadge, {
                color: isPaid ? 'success' : 'warning',
                label: `${amount} €`,
                variant: 'subtle'
            })
        ])
    }
}, {
	id: 'actions',
	header: 'Actions',
	cell: ({ row }) => {
		const items: any[] = []

		// Bouton payer commission collaborateur
		if (row.original.commission_amount > 0 && !row.original.commission_paid) {
			items.push({
				label: 'Payer commission collaborateur',
				icon: 'i-heroicons-check-circle',
				color: 'success',
				onSelect: () => paySourceCommission(row.original.id)
			})
		}

		// Bouton payer commission commercial
		if (row.original.sales_commission_amount > 0 && !row.original.sales_commission_paid) {
			items.push({
				label: 'Payer commission commercial',
				icon: 'i-heroicons-check-badge',
				color: 'primary',
				onSelect: () => paySalesCommission(row.original.id)
			})
		}

		// Si aucune action disponible, afficher un tiret
		if (items.length === 0) {
			return h('span', { class: 'text-gray-400' }, '—')
		}

		// Retourner un dropdown avec les actions disponibles
		return h(
			'div',
			{ class: 'text-right' },
			h(
				UDropdownMenu,
				{
					items: items,
					'aria-label': 'Actions dropdown'
				},
				() =>
					h(UButton, {
						icon: 'i-lucide-ellipsis-vertical',
						color: 'neutral',
						variant: 'ghost',
						class: 'ml-auto',
						'aria-label': 'Actions dropdown'
					})
			)
		)
	}
}]

const pagination = ref({
	pageIndex: 0,
	pageSize: 10
})

onMounted(fetchCommissions)

</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Commissions" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #trailing>
                    <UBadge v-if="commissions?.length as number > 0" :label="commissions?.length" variant="subtle" />
                </template>
            </UDashboardNavbar>
        </div>
        <UDashboardToolbar>
            <template #left>
                <SearchInput v-model="q" />
            </template>

            <template #right>
                <UDropdownMenu :items="table?.tableApi
                    ?.getAllColumns()
                    .filter((column) => column.getCanHide())
                    .map((column) => ({
                        label: attributLabels[column.id] || 'Inconnu',
                        type: 'checkbox' as const,
                        checked: column.getIsVisible(),
                        onUpdateChecked(checked: boolean) {
                            table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
                        },
                        onSelect(e?: Event) {
                            e?.preventDefault()
                        }
                    }))
                    " :content="{ align: 'end' }">
                    <UButton label="Afficher" color="neutral" variant="outline" trailing-icon="i-lucide-chevron-down" />
                </UDropdownMenu>
            </template>
        </UDashboardToolbar>

        <div class="w-full px-2 sm:px-6 space-y-4 pb-4">
            <UTable ref="table" :data="commissions" :columns="columns" v-model:global-filter="q"
                :ui="{ tr: 'data-[expanded=true]:bg-(--ui-bg-elevated)/50' }" class="flex-1" :loading="loading"
                :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
                v-model:pagination="pagination">
            </UTable>

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
    </div>
</template>
