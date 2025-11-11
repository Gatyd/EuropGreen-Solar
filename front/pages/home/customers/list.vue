<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn, TableRow } from '@nuxt/ui'
import type { User } from '~/types'
import { getPaginationRowModel } from '@tanstack/vue-table'
import { useAuthStore } from '~/store/auth'
import type { NavigationMenuItem } from '@nuxt/ui'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UTooltip = resolveComponent('UTooltip')
const AssignInstallerPopover = resolveComponent('InstallationAssignInstallerPopover')
// Etat d'ouverture par ligne (clé: id utilisateur)
const openAssignFor = ref<Record<string, boolean>>({})
const q = ref("")
const toast = useToast()
const loading = ref(true)
const users = ref<User[] | undefined>([])
const table = useTemplateRef('table')
const router = useRouter()
const auth = useAuthStore()
const selectedUser = ref<User | undefined>(undefined)
const deleteModal = ref(false)

const links: NavigationMenuItem[][] = [[{
	icon: 'i-heroicons-user-plus',
	label: "Prospects",
	to: "/home/customers/prospects",
},
{
	icon: 'i-heroicons-user-group',
	label: "Clients",
	to: "/home/customers/list",
}]]

const attributLabels: { [key: string]: string } = {
	first_name: 'Prénom',
	last_name: 'Nom',
	email: 'Email',
	is_active: 'Compte',
	status: 'Statut',
	installer: 'Installateur',
	commission_amount: 'Montant commission',
	commission_paid: 'Statut paiement',
	actions: 'Actions'
}

async function fetchUsers(refresh = false) {
	loading.value = true
	const result = await apiRequest<User[]>(
		() => $fetch(`/api/users/?is_staff=false`, {
			credentials: 'include'
		}),
		toast
	)
	console.log('Fetched users:', result)
	users.value = result || undefined
	loading.value = false
	if (refresh) {
		toast.add({
			title: 'Données mises à jour',
			description: 'La liste des clients a été rafraîchie avec succès.',
			color: 'success'
		})
	}
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
		let defaultActions = [
			h(UTooltip, { text: 'Voir les installations', delayDuration: 0 }, () =>
				h(UButton, {
					icon: 'i-heroicons-wrench-screwdriver', color: 'neutral', variant: 'ghost',
					onClick() {
						const count = row.original.installations_count || 0
						if (count === 1 && row.original.last_installation?.id) {
							router.push({ path: `/home/installations/${row.original.last_installation.id}` })
						} else {
							router.push({ path: '/home/installations', query: { client: row.original.id } })
						}
					}
				})
			),
			h(UTooltip, { text: 'Voir les documents', delayDuration: 0 }, () =>
				h(UButton, {
					icon: 'i-heroicons-document', color: 'neutral', variant: 'ghost',
					onClick() {
						router.push({ path: '/home/documents', query: { client: row.original.id } })
					}
				})
			)
		]
		if (auth.user?.is_superuser) {
			defaultActions.push(
				h(AssignInstallerPopover as any, {
					formId: row.original.last_installation?.id || '',
					'v-model:open': openAssignFor.value[row.original.id] || false,
					onAssigned: async () => {
						await fetchUsers()
					}
				}),
				h(UTooltip, { text: 'Supprimer le client', delayDuration: 0 }, () =>
					h(UButton, {
						icon: 'i-heroicons-trash', 
						color: 'error', 
						variant: 'ghost',
						onClick() {
							selectedUser.value = row.original
							deleteModal.value = true
						}
					})
				)
			)
		}
		return h('div', { class: 'space-x-2' }, defaultActions)
	}
}]

// Colonnes de commission pour les collaborateurs et commerciaux (non-superadmin staff)
if (auth.user?.is_staff && !auth.user?.is_superuser) {
	const isCollaborator = auth.user?.role === 'collaborator'
	const isSales = auth.user?.role === 'sales'

	// Colonne montant de commission (selon le rôle)
	const commissionAmountColumn: TableColumn<User> = {
		accessorKey: 'commission_amount',
		header: 'Montant commission',
		cell: ({ row }) => {
			const installation = row.original.last_installation
			if (!installation) return '—'

			// Collaborateur/Client: afficher commission_amount
			// Commercial: afficher sales_commission_amount
			const amount = isCollaborator
				? installation.commission_amount
				: isSales
					? installation.sales_commission_amount
					: 0

			return amount ? `${amount} €` : '—'
		}
	}

	// Colonne statut paiement (selon le rôle)
	const commissionPaidColumn: TableColumn<User> = {
		accessorKey: 'commission_paid',
		header: 'Statut paiement',
		cell: ({ row }) => {
			const installation = row.original.last_installation
			if (!installation) return h(UBadge, { color: 'neutral', label: 'N/A', variant: 'subtle' })

			// Collaborateur/Client: afficher commission_paid
			// Commercial: afficher sales_commission_paid
			const isPaid = isCollaborator
				? installation.commission_paid
				: isSales
					? installation.sales_commission_paid
					: false

			return h(UBadge, {
				color: isPaid ? 'success' : 'warning',
				label: isPaid ? 'Payée' : 'En attente',
				variant: 'subtle'
			})
		}
	}

	// Insérer après la colonne 'status' et avant 'actions'
	const actionsIndex = columns.findIndex(c => (c as any).id === 'actions')
	const insertIndex = actionsIndex >= 0 ? actionsIndex : columns.length
	columns.splice(insertIndex, 0, commissionAmountColumn, commissionPaidColumn)
}

// Colonne 'installer' ajoutée uniquement pour les superadmins, juste après 'status'
if (auth.user?.is_superuser) {
	const installerColumn: TableColumn<User> = {
		accessorKey: 'installer',
		header: 'Installateur affecté',
		cell: ({ row }) => {
			const inst = row.original.last_installation?.installer
			return inst ? `${inst.first_name} ${inst.last_name}` : '—'
		}
	}
	const statusIndex = columns.findIndex(c => (c as any).accessorKey === 'status' || (c as any).id === 'status')
	const insertIndex = statusIndex >= 0 ? statusIndex + 1 : columns.length - 1
	columns.splice(Math.min(Math.max(insertIndex, 0), columns.length), 0, installerColumn)
}

const pagination = ref({
	pageIndex: 0,
	pageSize: 10
})

onMounted(fetchUsers)

</script>

<template>
	<div>
		<UserDeleteModal v-model="deleteModal" v-if="selectedUser" :user="selectedUser" type="customer" @delete="fetchUsers" />
		<div class="sticky top-0 z-50 bg-white">
			<UDashboardNavbar title="Clients" class="lg:text-2xl font-semibold"
				:ui="{ root: 'h-12 lg:h-(--ui-header-height)' }" />

			<UDashboardToolbar class="py-0 px-1.5 overflow-x-auto md:block">
				<UNavigationMenu :items="links" />
			</UDashboardToolbar>
		</div>

		<UDashboardToolbar class="lg:mt-4 lg:ps-3">
			<template #left>
				<SearchInput v-model="q" />
			</template>

			<template #right>
				<UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchUsers(true)">Rafraîchir</UButton>
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
			<UTable ref="table" :data="users" :columns="columns" v-model:global-filter="q" :ui="{
				tr: 'data-[expanded=true]:bg-(--ui-bg-elevated)/50 cursor-pointer hover:bg-gray-50 transition-colors',
			}" class="flex-1" :loading="loading" :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
				v-model:pagination="pagination"
				@select="(row: TableRow<User>) => router.push({ path: `/home/customers/${row.original.id}`, query: { id: row.original.id } })">
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
