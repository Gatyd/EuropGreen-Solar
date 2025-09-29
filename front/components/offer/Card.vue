<script setup lang="ts">
import type { Offer } from '~/types/offers'
import type { ProspectStatus } from '~/types/requests';
import apiRequest from "~/utils/apiRequest";

const props = defineProps<{ item: Offer }>()
const emit = defineEmits<{
	(e: 'submit-quote'): void
}>()

const showInstallationModal = ref(false)
const quoteModal = ref(false)
const quoteLoading = ref(false)
const quoteToEdit = ref<any | null>(null)
const previewOpen = ref(false)
// Loading individuel par statut pour le retour vers les demandes
const returningLoadings = ref<Record<ProspectStatus, boolean>>({
	new: false,
	followup: false,
	info: false,
	in_progress: false,
	closed: false
})

const requestItems: { value: ProspectStatus; title: string }[] = [
	{ value: 'followup', title: 'À relancer' },
	{ value: 'info', title: 'Demande de renseignement' },
	{ value: 'in_progress', title: 'En cours' },
	{ value: 'closed', title: 'Clôturé' }
]

const previewDraft = computed(() => {
	const q = props.item?.last_quote as any
	if (!q) {
		return {
			title: '',
			valid_until: null,
			tax_rate: 20,
			lines: [] as Array<{ productId: string; name: string; description: string; unit_price: number; quantity: number; discount_rate: number }>
		}
	}
	return {
		title: q.title || '',
		valid_until: q.valid_until || null,
		tax_rate: Number(q.tax_rate ?? 20),
		lines: (q.lines || []).map((l: any) => ({
			productId: l.product || l.product_id || '',
			name: l.name,
			description: l.description,
			unit_price: Number(l.unit_price ?? 0),
			quantity: Number(l.quantity ?? 0),
			discount_rate: Number(l.discount_rate ?? 0)
		}))
	}
})

const submit = () => {
	navigateTo('/home/installations')
}

const sendQuote = async () => {
	const toast = useToast()
	quoteLoading.value = true
	if (!props.item.last_quote) return
	const res = await apiRequest<any>(
		() => $fetch(`/api/quotes/${props.item.last_quote!.id}/send/`, { method: 'POST', credentials: 'include' }),
		toast
	)
	if (res) {
		toast.add({ title: 'Devis envoyé', color: 'success', icon: 'i-heroicons-paper-airplane' })
		emit('submit-quote')
	}
	quoteLoading.value = false
}

const onMoveToInstallation = () => {
	showInstallationModal.value = true
}

const createQuote = () => {
	quoteToEdit.value = null
	quoteModal.value = true
}

const editQuote = () => {
	quoteToEdit.value = props.item.last_quote
	quoteModal.value = true
}

function onQuoteCreated(_q: any) {
	quoteModal.value = false
	emit('submit-quote')
}

async function returnToRequest(status: ProspectStatus) {
	const toast = useToast()
	returningLoadings.value[status] = true
	const res = await apiRequest<any>(
		() => $fetch(`/api/offers/${props.item.id}/return_to_request/`, {
			method: 'POST',
			credentials: 'include',
			body: { request_status: status }
		}),
		toast
	)
	if (res) {
		toast.add({ title: 'Offre renvoyée vers les demandes', color: 'success', icon: 'i-heroicons-arrow-left-16-solid' })
		emit('submit-quote')
	}
	returningLoadings.value[status] = false
}

// --- Détails projet (texte potentiellement long) ---
const PROJECT_DETAILS_MAX = 15 // nb max de caractères visibles avant popover
const hasProjectDetails = computed(() => !!props.item.project_details && props.item.project_details.trim().length > 0)
const truncatedProjectDetails = computed(() => {
	if (!hasProjectDetails.value) return '—'
	const full = props.item.project_details!.trim()
	if (full.length <= PROJECT_DETAILS_MAX) return full
	return full.slice(0, PROJECT_DETAILS_MAX) + '…'
})

// Notes modals state
const showNotesChronology = ref(false)
const showAddNote = ref(false)

async function refreshOfferNotes() {
	// Refetch offer detail (public endpoint retrieve) then update local item.notes
	try {
		const data = await $fetch(`/api/offers/${props.item.id}/`, { credentials: 'include' }) as Offer
		// @ts-ignore mutate prop object (Card is ephemeral UI container)
		props.item.notes = data.notes || []
	} catch (e) { /* ignore */ }
}
</script>

<template>
	<Teleport to="body">
		<InstallationModal v-if="showInstallationModal" v-model="showInstallationModal" :offer="item"
			@submit="submit" />
		<QuoteModal v-if="quoteModal" v-model="quoteModal" :offer="item" :quote="quoteToEdit || undefined"
			@created="onQuoteCreated" />
		<UModal :open="previewOpen" @update:open="v => (previewOpen = v)" title="Aperçu du devis"
			:ui="{ content: 'max-w-5xl' }">
			<template #body>
				<div v-if="item?.last_quote" class="space-y-4">
					<QuotePreview :offer="item" :quote="item.last_quote" :draft="previewDraft" />
				</div>
			</template>
		</UModal>
		<OfferNoteChronologyModal v-if="showNotesChronology" v-model="showNotesChronology" :offer="item"
			@add-note="() => { showAddNote = true }" />
		<OfferNoteFormModal v-if="showAddNote" v-model="showAddNote" :offer="item"
			@created="() => { refreshOfferNotes(); showNotesChronology = true }" />
	</Teleport>
	<UCard :ui="{ body: 'p-3 sm:p-4' }" class="cursor-grab">
		<UPopover v-if="item.status !== 'quote_signed'" :content="{
			align: 'center',
			side: 'left',
			sideOffset: 8
		}">
			<UButton label="Ramener vers les demandes" icon="i-heroicons-arrow-left-16-solid" size="sm" class="mb-1"
				color="neutral" variant="subtle" @click.stop="" />

			<template #content>
				<div class="flex flex-col gap-3 p-2">
					<UButton v-for="opt in requestItems" :key="opt.value" :label="opt.title" size="sm" variant="subtle"
						color="neutral" :loading="returningLoadings[opt.value]"
						@click.stop="returnToRequest(opt.value)" />
				</div>
			</template>
		</UPopover>
		<div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
			<div class="space-y-1">
				<div class="font-medium">
					{{ item.last_name }} {{ item.first_name }}
				</div>
				<div class="text-sm text-gray-500">
					{{ item.phone }} • {{ item.email }}
				</div>
				<div class="flex gap-2 text-sm text-gray-400 truncate">
					<p>{{ item.address }}</p>
					<span>•</span>
					<!-- Détails projet (popover si tronqué) -->
					<div v-if="hasProjectDetails" class="">
						<UPopover v-if="item.project_details && item.project_details.length > PROJECT_DETAILS_MAX"
							mode="hover">
							<button class="block w-full group" @click.stop="">
								<p
									class="text-sm text-gray-700 dark:text-gray-200 leading-snug line-clamp-4 group-hover:underline group-hover:decoration-dotted group-hover:underline-offset-2">
									{{ truncatedProjectDetails }}
								</p>
							</button>
							<template #content>
								<div class="max-w-sm whitespace-pre-wrap text-sm p-2">
									{{ item.project_details }}
								</div>
							</template>
						</UPopover>
						<p v-else class="text-sm text-gray-500">{{ item.project_details }}</p>
					</div>
				</div>
				<div class="flex gap-2">
					<UButton color="neutral" variant="ghost" size="xs"
						:label="`#${item.notes && item.notes.length ? item.notes.length : 0} note enregistrée${item.notes && item.notes.length > 1 ? 's' : ''}`"
						@click.stop="showNotesChronology = true" />
					<UButton variant="subtle" size="xs" label="Ajouter une note" icon="i-heroicons-plus"
						@click.stop="showAddNote = true" />
				</div>
			</div>
		</div>
		<div class="border rounded-md p-2 mt-2 bg-gray-50 dark:bg-gray-800/50">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm font-medium text-gray-600 dark:text-gray-300">Dernier devis</span>
				<span v-if="item.last_quote" class="text-xs px-2 py-1 rounded-full" :class="{
					'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200': item.last_quote.status === 'draft',
					'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200': item.last_quote.status === 'sent',
					'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-200': item.last_quote.status === 'pending',
					'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200': item.last_quote.status === 'accepted',
					'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200': item.last_quote.status === 'declined'
				}">
					{{
						item.last_quote.status === 'draft' ? 'Brouillon' :
							item.last_quote.status === 'sent' ? 'Envoyé' :
								item.last_quote.status === 'pending' ? 'En attente' :
									item.last_quote.status === 'accepted' ? 'Accepté' :
										item.last_quote.status === 'declined' ? 'Refusé' : item.last_quote.status
					}}
				</span>
			</div>

			<div v-if="item.last_quote" class="flex justify-between items-center">
				<div class="space-y-1 text-sm">
					<div class="text-gray-700 dark:text-gray-200">
						<span class="font-medium">N°:</span> {{ item.last_quote.number }}
					</div>
					<div class="text-gray-700 dark:text-gray-200">
						<span class="font-medium">Version:</span> v{{ item.last_quote.version }}
					</div>
					<div class="text-gray-700 dark:text-gray-200">
						<span class="font-medium">Total:</span> {{ item.last_quote.total }} €
					</div>
				</div>
				<!-- Si le devis est signé (signature présente), afficher l'aperçu au lieu du PDF -->
				<UButton v-if="item.last_quote.signature" variant="ghost" color="neutral" size="xl"
					icon="i-heroicons-eye" @click.stop="previewOpen = true" :title="'Voir l\'aperçu du devis'" />
				<!-- Sinon, lien vers le PDF si disponible -->
				<UButton v-else-if="item.last_quote.pdf" variant="ghost" @click.stop="" color="neutral" size="xl"
					icon="i-heroicons-document" target="_blank" :to="item.last_quote.pdf" />
			</div>

			<div v-else class="text-sm text-gray-500 dark:text-gray-400">
				Aucun devis
			</div>

			<div class="mt-3 flex gap-2 justify-end">
				<UButton v-if="!item.last_quote" color="primary" size="sm" label="Créer le devis"
					@click.stop="createQuote" />
				<template v-else>
					<UButton v-if="item.last_quote.status === 'draft'" color="secondary" size="sm"
						label="Modifier le brouillon" @click.stop="editQuote" />
					<UButton v-if="item.last_quote.status === 'draft'" :loading="quoteLoading" color="primary" size="sm"
						label="Envoyer le devis" @click.stop="sendQuote" />
					<UButton v-else-if="item.last_quote.status === 'pending' || item.last_quote.status === 'sent'"
						color="secondary" size="sm"
						:label="`Modifier le devis${item.last_quote.status === 'sent' ? '' : ' (négociation)'}`"
						@click.stop="editQuote" />
				</template>
			</div>
		</div>
		<div v-if="item.status === 'quote_signed'" class="mt-2 flex justify-end">
			<UButton size="xs" color="primary" variant="solid" icon="i-heroicons-arrow-right-circle"
				label="Déplacer vers installation" @click.stop="onMoveToInstallation" />
		</div>
	</UCard>
</template>
