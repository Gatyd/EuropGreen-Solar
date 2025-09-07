<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { User } from '~/types'
import { getPaginationRowModel } from '@tanstack/vue-table'

definePageMeta({
	middleware: 'admin'
})

const UBadge = resolveComponent('UBadge')
const q = ref("")
const toast = useToast()
const loading = ref(true)
const users = ref<User[] | undefined>([])
const table = useTemplateRef('table')

const attributLabels: { [key: string]: string } = {
	first_name: 'Prénom',
	last_name: 'Nom',
	email: 'Email',
	role: 'Rôle',
	is_active: 'Compte'
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
	accessorKey: 'role',
	header: 'Rôle',
	cell: ({ row }) => {
		const roleLabels: Record<string, string> = {
			admin: 'Administrateur',
			employee: 'Employé',
			installer: 'Installateur',
			secretary: 'Secrétaire',
			customer: 'Client'
		}
		return roleLabels[row.original.role] || 'Utilisateur'
	}
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
