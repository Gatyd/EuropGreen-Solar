<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { h, resolveComponent } from 'vue'
import { getPaginationRowModel } from '@tanstack/vue-table'
import apiRequest from '~/utils/apiRequest'
import type { ProspectRequest, ProspectSource, ProspectStatus } from '~/types/requests'
import { useAuthStore } from '~/store/auth'
import type { NavigationMenuItem } from '@nuxt/ui'

const auth = useAuthStore()
const toast = useToast()
const q = ref('')
const loading = ref(true)
const creating = ref(false)
const deleteModal = ref(false)
const selected = ref<ProspectRequest | null>(null)
const selectedProspect = ref<ProspectRequest | undefined>(undefined)
const items = ref<Array<ProspectRequest & { offer?: { id: string; status: import('~/types/offers').OfferStatus } | null }>>([])
const table = useTemplateRef('table')

const UButton = resolveComponent('UButton')
const UTooltip = resolveComponent('UTooltip')

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

const stageLabel = (it: { offer?: { id: string | null } | null }) => (it.offer && it.offer.id ? 'Offre' : 'Demande')
const stageColor = (it: { offer?: { id: string | null } | null }) => (it.offer && it.offer.id ? 'primary' : 'secondary')

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

type OfferStatus = import('~/types/offers').OfferStatus
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

const prospectSourceLabel: Record<ProspectSource, string> = {
	call_center: 'Centre d\'appels',
	web_form: 'Formulaire web',
	client: 'Client',
	collaborator: 'Collaborateur',
	commercial: 'Commercial'
}

const fetchProspects = async () => {
	loading.value = true
	const data = await apiRequest<ProspectRequest[]>(
		() => $fetch('/api/requests/?scope=prospects', { credentials: 'include' }),
		toast
	)
	items.value = (data || []) as any
	loading.value = false
}

onMounted(fetchProspects)

const newProspect = () => {
	creating.value = true
	selected.value = null
}

const submitFromModal = async (form: FormData) => {
	creating.value = false
	await fetchProspects()
}

const columns: TableColumn<ProspectRequest>[] = [
	{ accessorKey: 'last_name', header: 'Nom', cell: ({ row }) => row.original.last_name },
	{ accessorKey: 'first_name', header: 'Prénom', cell: ({ row }) => row.original.first_name },
	{ accessorKey: 'email', header: 'Email', cell: ({ row }) => row.original.email },
	{
		id: 'stage', header: 'Étape',
		cell: ({ row }) => h(resolveComponent('UBadge') as any, {
			color: stageColor(row.original),
			label: stageLabel(row.original),
			variant: 'subtle'
		})
	},
	{
		id: 'stage_status', header: 'Statut',
		cell: ({ row }) => {
			const it = row.original
			if (it.offer && it.offer.id) {
				const st = it.offer.status as OfferStatus
				return h(resolveComponent('UBadge') as any, { color: offerStatusColor[st], label: offerStatusLabel[st], variant: 'subtle' })
			}
			const st = it.status as ProspectStatus
			return h(resolveComponent('UBadge') as any, { color: requestStatusColor[st], label: requestStatusLabel[st], variant: 'subtle' })
		}
	}
]
if (auth.user?.is_superuser) {
	columns.push(
		{
			accessorKey: 'source_type', header: "Type de source",
			cell: ({ row }) => prospectSourceLabel[row.original.source_type] || 'Inconnu'
		}, {
		accessorKey: 'source', header: "Source",
		cell: ({ row }) => row.original.source ? `${row.original.source.first_name} ${row.original.source.last_name}` : '—'
		}, {
		accessorKey: 'assigned_to', header: "Chargé d'affaire",
		cell: ({ row }) => row.original.assigned_to ? `${row.original.assigned_to.first_name} ${row.original.assigned_to.last_name}` : 'Non assigné'
		}, {
		id: 'actions',
		header: 'Actions',
		cell: ({ row }) => {
			return h(UTooltip, { text: 'Supprimer le prospect', delayDuration: 0 }, () =>
				h(UButton, {
					icon: 'i-heroicons-trash',
					color: 'error',
					variant: 'ghost',
					onClick() {
						selectedProspect.value = row.original
						deleteModal.value = true
					}
				})
			)
		}
	}
	)
}

const pagination = ref({ pageIndex: 0, pageSize: 10 })
</script>

<template>
	<RequestDeleteModal v-model="deleteModal" v-if="selectedProspect" :prospect="selectedProspect" @delete="fetchProspects" />
	<div class="sticky top-0 z-50 bg-white">
		<UDashboardNavbar title="Prospects" class="lg:text-2xl font-semibold"
			:ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
			<template #right>
				<UButton color="primary" icon="i-heroicons-plus" label="Nouveau prospect" @click="newProspect" />
			</template>
		</UDashboardNavbar>

		<UDashboardToolbar class="py-0 px-1.5 overflow-x-auto md:block">
			<UNavigationMenu :items="links" />
		</UDashboardToolbar>

		<UDashboardToolbar class="px-1.5">
			<template #left>
				<SearchInput v-model="q" />
			</template>
			<template #right>
				<UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchProspects">Rafraîchir</UButton>
			</template>
		</UDashboardToolbar>
	</div>

	<ClientOnly>
		<RequestModal :model-value="creating" :payload="selected" @update:model-value="v => creating = v"
			@submit="submitFromModal" />
	</ClientOnly>

	<div class="w-full px-2 sm:px-6 space-y-4 pb-4">
		<UTable sticky ref="table" :data="items" :columns="columns" v-model:global-filter="q"
			class="flex-1 max-h-[400px] lg:max-h-[500px]" :loading="loading"
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