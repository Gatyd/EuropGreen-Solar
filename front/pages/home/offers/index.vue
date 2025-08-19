<script setup lang="ts">
import type { Offer, OfferStatus } from '~/types/offers'
import apiRequest from '~/utils/apiRequest'

definePageMeta({ layout: 'default' })

const toast = useToast()
const editing = ref(false)
const search = ref('')
const dateRange = ref<{ start?: string | null, end?: string | null }>({ start: null, end: null })
const selected = ref<Offer | null>(null)

const columns: { key: OfferStatus; title: string }[] = [
	{ key: 'to_contact', title: 'À contacter' },
	{ key: 'phone_meeting', title: 'RDV Téléphonique' },
	{ key: 'meeting', title: 'RDV Physique/Visio' },
	{ key: 'quote_sent', title: 'Devis envoyé' },
	{ key: 'negotiation', title: 'Négociation' },
	{ key: 'quote_signed', title: 'Devis signé' }
]

const statusLabels: Record<OfferStatus, string> = {
	to_contact: 'À contacter',
	phone_meeting: 'RDV Téléphonique',
	meeting: 'RDV Physique/Visio',
	quote_sent: 'Devis envoyé',
	negotiation: 'Négociation/questions',
	quote_signed: 'Devis signé'
}

const loading = ref(true)
const allItems = ref<Offer[]>([])

const filteredItems = computed<Offer[]>(() => {
	const term = (search.value || '').trim().toLowerCase()
	const start = dateRange.value.start || null
	const end = dateRange.value.end || null
	return allItems.value.filter((it) => {
		const hay = `${it.first_name} ${it.last_name} ${it.email} ${it.phone}`.toLowerCase()
		const textOk = term ? hay.includes(term) : true
		const createdDate = (it.created_at || '').slice(0, 10)
		const startOk = start ? createdDate >= start : true
		const endOk = end ? createdDate <= end : true
		return textOk && startOk && endOk
	})
})

const items = computed<Record<OfferStatus, Offer[]>>(() => {
	const grouped: Record<OfferStatus, Offer[]> = {
		to_contact: [], phone_meeting: [], meeting: [], quote_sent: [], negotiation: [], quote_signed: []
	}
	for (const it of filteredItems.value) {
		grouped[it.status].push(it)
	}
	return grouped
})
const totalCount = computed(() => filteredItems.value.length)

const fetchAll = async () => {
	loading.value = true
	const data = await apiRequest<Offer[]>(
		() => $fetch('/api/offers/', { credentials: 'include' }),
		toast
	)
	if (data) allItems.value = data
	loading.value = false
}

onMounted(fetchAll)

const onDrop = async (payload: { to: OfferStatus, item: Offer }) => {
	const { to, item: card } = payload
	const prev = card.status
	if (to === prev) return
	card.status = to
	const res = await apiRequest<Offer>(
		() => $fetch(`/api/offers/${card.id}/`, { method: 'PATCH', body: { status: to }, credentials: 'include' }),
		toast
	)
	if (!res) {
		card.status = prev
		await fetchAll()
	} else {
		toast.add({ title: 'Statut modifié', description: statusLabels[to], color: 'success', icon: 'i-heroicons-check-circle' })
		await fetchAll()
	}
}

function openDetails(item: Offer) {
	selected.value = item
	editing.value = true
}

async function submitInlineEdit() {
	if (!selected.value) return
	const res = await apiRequest<Offer>(
		() => $fetch(`/api/offers/${selected.value!.id}/`, { method: 'PATCH', body: selected.value, credentials: 'include' }),
		toast
	)
	if (res) {
		toast.add({ title: 'Offre mise à jour', color: 'success', icon: 'i-heroicons-check-circle' })
		editing.value = false
		await fetchAll()
	}
}
</script>

<template>
	<div>
		<div class="sticky top-0 z-50 bg-white">
			<UDashboardNavbar title="Offres" class="lg:text-2xl font-semibold" :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
				<template #trailing>
					<UBadge variant="subtle">{{ totalCount }}</UBadge>
				</template>
				<template #right>
					<!-- Pas de bouton de création -->
				</template>
			</UDashboardNavbar>
		</div>

		<UCard class="mb-4">
			<div class="flex flex-wrap items-end gap-3">
				<UFormField label="Recherche" class="w-full md:w-max lg:w-64">
					<UInput v-model="search" class="w-full" placeholder="Nom, email, téléphone..." />
				</UFormField>
				<UFormField label="Du">
					<UInput v-model="dateRange.start" type="date" />
				</UFormField>
				<UFormField label="Au">
					<UInput v-model="dateRange.end" type="date" />
				</UFormField>
				<UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchAll">Rafraîchir</UButton>
			</div>
		</UCard>

		<ClientOnly>
			<UModal :open="editing" @update:open="v => editing = v" title="Détails de l'offre" :ui="{ title: 'text-xl', content: 'max-w-2xl' }">
				<template #body>
					<div v-if="selected" class="space-y-3">
						<div class="grid grid-cols-2 gap-4">
							<UFormField label="Nom">
								<UInput v-model="selected!.last_name" />
							</UFormField>
							<UFormField label="Prénom">
								<UInput v-model="selected!.first_name" />
							</UFormField>
							<UFormField label="Email">
								<UInput v-model="selected!.email" type="email" />
							</UFormField>
							<UFormField label="Téléphone">
								<UInput v-model="selected!.phone" />
							</UFormField>
							<UFormField label="Adresse" class="col-span-2">
								<UInput v-model="selected!.address" />
							</UFormField>
							<UFormField label="Type de logement">
								<UInput v-model="selected!.housing_type" />
							</UFormField>
							<UFormField label="Détails du projet" class="col-span-2">
								<UTextarea v-model="selected!.project_details" :rows="5" placeholder="Puissance, matériel, remarques..." />
							</UFormField>
						</div>
						<div class="flex justify-end mt-2">
							<UButton color="primary" icon="i-heroicons-check-circle" label="Enregistrer" @click="submitInlineEdit" />
						</div>
					</div>
				</template>
			</UModal>
		</ClientOnly>

		<div class="flex gap-4 overflow-x-auto p-4">
			<div v-for="col in columns" :key="col.key">
				<RequestSkeleton v-if="loading" :title="col.title" />
				<OfferColumn v-else :title="col.title" :status="col.key" :items="items[col.key]"
					:count="items[col.key].length" @drop="onDrop" @open="openDetails" />
			</div>
		</div>
	</div>
	</template>