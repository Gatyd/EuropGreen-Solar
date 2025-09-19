<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { User } from '~/types'
import { getPaginationRowModel } from '@tanstack/vue-table'

definePageMeta({
	middleware: 'admin'
})

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const q = ref("")
const toast = useToast()
const loading = ref(true)
const users = ref<User[] | undefined>([])
const table = useTemplateRef('table')
const router = useRouter()

const attributLabels: { [key: string]: string } = {
	first_name: 'Prénom',
	last_name: 'Nom',
	email: 'Email',
	is_active: 'Compte',
	status: 'Statut',
	actions: 'Actions'
}

async function fetchUsers() {
	loading.value = true
	const result = await apiRequest<User[]>(
		() => $fetch(`/api/users/?is_staff=false`, {
			credentials: 'include'
		}),
		toast
	)
	users.value = result || undefined
	loading.value = false
}

const columns: TableColumn<User>[] = [{
	accessorKey: 'last_name',
	header: 'Nom',
	cell: ({ row }) => row.original.last_name
}, {
	accessorKey: 'first_name',
	header: 'Prénom',
	cell: ({ row }) => row.original.first_name
}, {
	accessorKey: 'email',
	header: 'Email',
	cell: ({ row }) => row.original.email
}, {
	accessorKey: 'is_active',
	header: 'Compte',
	cell: ({ row }) => {
		return h(UBadge, {
			color: !row.original.accept_invitation ? 'warning' : row.original.is_active ? 'success' : 'error',
			label: !row.original.accept_invitation ? 'En attente' : row.original.is_active ? 'Actif' : 'Inactif',
			variant: 'subtle'
		})
	}
}, {
	accessorKey: 'status',
	header: 'Etape',
	cell: ({ row }) => {
		const status = row.original.last_installation?.status
		const labels: Record<string, string> = {
			technical_visit: 'Visite technique',
			representation_mandate: 'Mandat de représentation',
			administrative_validation: 'Validation administrative',
			installation_completed: 'Installation effectuée',
			consuel_visit: 'Visite CONSUEL',
			enedis_connection: 'Raccordement ENEDIS',
			commissioning: 'Mise en service'
		}
		return status ? labels[status] || status : '—'
	}
}, {
	id: 'actions',
	header: 'Actions',
	cell: ({ row }) => {
		const items = [
			{
				label: 'Installations',
				icon: 'i-heroicons-wrench-screwdriver',
				onSelect() {
					const count = row.original.installations_count || 0
					if (count === 1 && row.original.last_installation?.id) {
						router.push({ path: `/home/installations/${row.original.last_installation.id}` })
					} else {
						router.push({ path: '/home/installations', query: { client: row.original.id } })
					}
				}
			},
			{
				label: 'Documents liés',
				icon: 'i-heroicons-document-text'
			}
		]
		return h('div', { class: 'text-center' },
			h(UDropdownMenu, { items, 'aria-label': 'Actions dropdown' }, () =>
				h(UButton, { icon: 'i-lucide-ellipsis-vertical', color: 'neutral', variant: 'ghost', class: 'ml-auto', 'aria-label': 'Actions dropdown' })
			)
		)
	}
}]

const pagination = ref({
	pageIndex: 0,
	pageSize: 10
})

onMounted(fetchUsers)

</script>

<template>
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
		<UTable ref="table" :data="users" :columns="columns" v-model:global-filter="q"
			:ui="{ tr: 'data-[expanded=true]:bg-(--ui-bg-elevated)/50' }" class="flex-1" :loading="loading"
			:pagination-options="{ getPaginationRowModel: getPaginationRowModel() }" v-model:pagination="pagination">
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
</template>
