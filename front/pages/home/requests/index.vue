<script setup lang="ts">
import type { ProspectRequest, ProspectStatus } from '~/types/requests'
import DetailsModal from '@/components/request/DetailsModal.vue'
import apiRequest from '~/utils/apiRequest'

const toast = useToast()
const creating = ref(false)
const search = ref('')
const dateRange = ref<{ start?: string | null, end?: string | null }>({ start: null, end: null })
const selected = ref<ProspectRequest | null>(null)
const detailsOpen = ref<boolean>(false)

const columns: { key: ProspectStatus; title: string }[] = [
    { key: 'new', title: 'Nouveau' },
    { key: 'followup', title: 'À relancer' },
    { key: 'info', title: 'Demande de renseignement' },
    { key: 'in_progress', title: 'En cours' },
    { key: 'closed', title: 'Clôturé' }
]

const statusLabels: Record<ProspectStatus, string> = {
    new: 'Nouveau',
    followup: 'À relancer',
    info: 'Demande de renseignement',
    in_progress: 'En cours',
    closed: 'Clôturé'
}

const loading = ref(true)
const allItems = ref<ProspectRequest[]>([])

// Filtrage côté front (nom, prénom, email, téléphone, dates)
const filteredItems = computed<ProspectRequest[]>(() => {
    const term = (search.value || '').trim().toLowerCase()
    const start = dateRange.value.start || null
    const end = dateRange.value.end || null
    return allItems.value.filter((it) => {
        // term match
        const hay = `${it.first_name} ${it.last_name} ${it.email} ${it.phone}`.toLowerCase()
        const textOk = term ? hay.includes(term) : true
        // date match (compare sur la date YYYY-MM-DD)
        const createdDate = (it.created_at || '').slice(0, 10)
        const startOk = start ? createdDate >= start : true
        const endOk = end ? createdDate <= end : true
        return textOk && startOk && endOk
    })
})

const items = computed<Record<ProspectStatus, ProspectRequest[]>>(() => {
    const grouped: Record<ProspectStatus, ProspectRequest[]> = {
        new: [], followup: [], info: [], in_progress: [], closed: []
    }
    for (const it of filteredItems.value) {
        grouped[it.status].push(it)
    }
    return grouped
})
const totalCount = computed(() => filteredItems.value.length)

const fetchAll = async (refresh = false) => {
    loading.value = true
    const data = await apiRequest<ProspectRequest[]>(
        () => $fetch('/api/requests/', { credentials: 'include' }),
        toast
    )
    if (data) allItems.value = data
    loading.value = false
    if (refresh) {
        toast.add({
            title: 'Données mises à jour',
            description: 'La liste des prospects a été rafraîchie avec succès.',
            color: 'success'
        })
    }
}

onMounted(async () => {
    await fetchAll()
    
    // Vérifier si un prospect_id est dans l'URL
    const route = useRoute()
    const prospectId = route.query.prospect_id
    if (prospectId) {
        const prospect = allItems.value.find(p => String(p.id) === String(prospectId))
        if (prospect) {
            selected.value = prospect
            detailsOpen.value = true
            // Nettoyer l'URL sans recharger la page
            const router = useRouter()
            router.replace({ query: {} })
        }
    }
})

const onDrop = async (payload: { to: ProspectStatus, item: ProspectRequest }) => {
    const { to, item: card } = payload
    const prev = card.status
    // Si le statut ne change pas, ne rien faire
    if (to === prev) return
    // Si on quitte la colonne 'closed', on reset localement l'indicateur (le backend le fera aussi)
    if (prev === 'closed' && to !== 'closed' && 'converted_decision' in card) {
        card.converted_decision = null as any
    }
    card.status = to
    const res = await apiRequest<ProspectRequest>(
        () => $fetch(`/api/requests/${card.id}/`, { method: 'PATCH', body: { status: to }, credentials: 'include' }),
        toast
    )
    if (!res) {
        // revert UI
        card.status = prev
        await fetchAll()
    } else {
        toast.add({ title: 'Statut modifié avec succès', description: statusLabels[to], color: 'success', icon: 'i-heroicons-check-circle' })
        await fetchAll()
    }
}

const submitFromModal = async (item: ProspectRequest) => {
    creating.value = false
    await fetchAll()
    selected.value = item
}

const newRequest = () => {
    creating.value = true
    selected.value = null
}

function openDetails(item: any) {
    selected.value = item
    detailsOpen.value = true
}

async function convertToOffer(item: ProspectRequest) {
    navigateTo('/home/offers')
}

function openEditFromDetails() {
    if (!selected.value) return
    creating.value = true
}
</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Demandes" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #trailing>
                    <UBadge variant="subtle">{{ totalCount }}</UBadge>
                </template>
                <template #right>
                    <UButton color="primary" label="Nouvelle demande" icon="i-heroicons-plus" class="mx-2"
                        @click="newRequest" />
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
                <UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchAll(true)">Rafraîchir</UButton>
            </div>
        </UCard>

        <ClientOnly>
            <RequestModal :model-value="creating" :payload="selected" @update:model-value="v => creating = v"
                @submit="submitFromModal" />
        </ClientOnly>

        <div class="flex gap-4 overflow-x-auto p-4">
            <div class="" v-for="col in columns" :key="col.key">
                <RequestSkeleton v-if="loading" :title="col.title" />
                <RequestColumn v-else :title="col.title" :status="col.key" :items="items[col.key]"
                    :count="items[col.key].length" @drop="onDrop" @open="openDetails" @convert="convertToOffer" />
            </div>
        </div>

        <DetailsModal v-model="detailsOpen" :item="selected" @edit="openEditFromDetails" />
    </div>
</template>