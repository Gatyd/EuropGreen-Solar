<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const toast = useToast()
const loading = ref(true)

// ID de l'utilisateur depuis l'URL
const userId = computed(() => route.query.user_id as string)

// Données de la timeline
const timelineData = ref<any>(null)

// Récupération de la timeline
async function fetchTimeline() {
	if (!userId.value) {
		toast.add({
			title: 'Erreur',
			description: 'ID utilisateur manquant',
			color: 'error'
		})
		router.back()
		return
	}

	loading.value = true
	const result = await apiRequest<any>(
		() => $fetch(`/api/admin-platform/audit-logs/user-timeline/${userId.value}/`, {
			credentials: 'include'
		}),
		toast
	)

	if (result) {
		timelineData.value = result
	}
	loading.value = false
}

// Couleur selon le type d'action
function getActionColor(action: number): string {
	// 0=CREATE (vert), 1=UPDATE (bleu), 2=DELETE (rouge)
	const colors: Record<number, string> = {
		0: 'bg-green-500',
		1: 'bg-blue-500',
		2: 'bg-red-500',
	}
	return colors[action] || 'bg-gray-500'
}

// Badge variant selon le type d'action
function getActionBadgeColor(action: number): 'success' | 'primary' | 'error' | 'neutral' {
	const colors: Record<number, 'success' | 'primary' | 'error' | 'neutral'> = {
		0: 'success',
		1: 'primary',
		2: 'error',
	}
	return colors[action] || 'neutral'
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

// Formater les changements pour l'affichage
function formatChanges(changes: any): string {
	if (!changes || Object.keys(changes).length === 0) return 'Aucun changement détaillé'
	
	const formatted = Object.entries(changes).map(([key, value]: [string, any]) => {
		const [oldVal, newVal] = value
		return `${key}: "${oldVal || '(vide)'}" → "${newVal || '(vide)'}"`
	})
	
	return formatted.join('\n')
}

onMounted(fetchTimeline)
</script>

<template>
	<div>
		<!-- Header -->
		<div class="sticky top-0 z-50 bg-white border-b">
			<UDashboardNavbar class="lg:text-2xl font-semibold"
				:ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
				<template #title>
					<UButton
						icon="i-heroicons-arrow-left"
						color="neutral"
						variant="ghost"
						@click="router.back()"
					/>
					<span>Historique des interactions</span>
				</template>
			</UDashboardNavbar>
		</div>

		<!-- Loading -->
		<div v-if="loading" class="flex justify-center items-center py-20">
			<UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl" />
		</div>

		<!-- Contenu principal -->
		<div v-else-if="timelineData" class="w-full px-2 sm:px-6 py-6 max-w-5xl mx-auto">
			
			<!-- Header utilisateur -->
			<div class="mb-6 p-4 bg-gray-50 rounded-lg">
				<div class="flex items-center gap-3">
					<div class="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
						{{ timelineData.user.full_name?.charAt(0)?.toUpperCase() || 'U' }}
					</div>
					<div>
						<h2 class="text-lg font-bold">{{ timelineData.user.full_name || 'Utilisateur' }}</h2>
						<p class="text-sm text-gray-600">{{ timelineData.user.email }}</p>
					</div>
				</div>
				<div class="mt-3 text-sm text-gray-600">
					<span class="font-semibold">{{ timelineData.count }}</span> événements enregistrés
				</div>
			</div>

			<!-- Timeline -->
			<div v-if="timelineData.logs.length === 0" class="text-center py-12 text-gray-500">
				<UIcon name="i-heroicons-clock" class="text-6xl mb-4 mx-auto" />
				<p>Aucun événement enregistré</p>
			</div>

			<div v-else class="relative">
				<!-- Ligne verticale -->
				<div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

				<!-- Items de la timeline -->
				<div
					v-for="log in timelineData.logs"
					:key="log.id"
					class="relative pl-16 pb-8 last:pb-0"
				>
					<!-- Marker coloré -->
					<div
						class="absolute left-3 w-6 h-6 rounded-full border-4 border-white shadow"
						:class="getActionColor(log.action)"
					/>

					<!-- Carte de l'événement -->
					<UCard>
						<div class="space-y-3">
							<!-- En-tête -->
							<div class="flex items-start justify-between gap-4">
								<div class="flex items-center gap-3 flex-1">
									<UIcon :name="getObjectIcon(log.object_type)" class="text-2xl text-gray-600 flex-shrink-0" />
									<div class="min-w-0 flex-1">
										<div class="flex items-center gap-2 flex-wrap">
											<UBadge :color="getActionBadgeColor(log.action)" variant="subtle">
												{{ log.action_display }}
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
								<span class="text-xs text-gray-500 whitespace-nowrap flex-shrink-0">
									{{ formatDate(log.timestamp) }}
								</span>
							</div>

							<!-- Détails des changements (si UPDATE) -->
							<div v-if="log.changes && Object.keys(log.changes).length > 0" class="mt-3">
								<details class="group">
									<summary class="cursor-pointer text-sm text-gray-600 hover:text-gray-800 flex items-center gap-2">
										<UIcon name="i-heroicons-chevron-right" class="transform group-open:rotate-90 transition-transform" />
										Voir les changements ({{ Object.keys(log.changes).length }})
									</summary>
									<div class="mt-2 p-3 bg-gray-50 rounded text-xs space-y-1.5">
										<div
											v-for="([field, values], index) in Object.entries(log.changes)"
											:key="index"
											class="border-l-2 border-gray-300 pl-3"
										>
											<div class="font-semibold text-gray-700">{{ field }}</div>
											<div class="flex items-center gap-2 text-gray-600 mt-1">
												<span class="line-through text-red-600">{{ (values as any[])[0] || '(vide)' }}</span>
												<UIcon name="i-heroicons-arrow-right" class="text-xs" />
												<span class="text-green-600 font-medium">{{ (values as any[])[1] || '(vide)' }}</span>
											</div>
										</div>
									</div>
								</details>
							</div>

							<!-- Acteur -->
							<div class="flex items-center gap-2 text-xs text-gray-500 pt-2 border-t">
								<UIcon name="i-heroicons-user-circle" />
								<span>
									Par <span class="font-medium text-gray-700">{{ log.actor_name }}</span>
									<span v-if="log.actor_email" class="text-gray-400">({{ log.actor_email }})</span>
								</span>
								<span v-if="log.remote_addr" class="ml-auto text-gray-400">
									{{ log.remote_addr }}
								</span>
							</div>
						</div>
					</UCard>
				</div>
			</div>
		</div>
	</div>
</template>
