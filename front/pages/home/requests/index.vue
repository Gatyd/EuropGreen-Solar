<script setup lang="ts">
import type { ProspectRequest, ProspectStatus } from '~/types/requests'
import DetailsModal from '@/components/request/DetailsModal.vue'
import apiRequest from '~/utils/apiRequest'

definePageMeta({ layout: 'default' })

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

const fetchAll = async () => {
    loading.value = true
    const data = await apiRequest<ProspectRequest[]>(
        () => $fetch('/api/requests/', { credentials: 'include' }),
        toast
    )
    if (data) allItems.value = data
    loading.value = false
}

onMounted(fetchAll)

const onDrop = async (payload: { to: ProspectStatus, item: ProspectRequest }) => {
    const { to, item: card } = payload
    const prev = card.status
    // Si le statut ne change pas, ne rien faire
    if (to === prev) return
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

const submitFromModal = async (form: FormData) => {
    const res = await apiRequest<ProspectRequest>(
        () => $fetch(`/api/requests/${selected.value ? `${selected.value.id}/` : ''}`,
            { method: selected.value ? 'PATCH' : 'POST', body: form, credentials: 'include' }
        ),
        toast
    )
    if (res) {
        toast.add({ title: `Demande ${selected.value ? 'modifiée' : 'créée'} avec succès`, color: 'success', icon: 'i-heroicons-check-circle' })
        creating.value = false
        await fetchAll()
    }
}

const newRequest = () => {
    creating.value = true
    selected.value = null
}

function openDetails(item: any) {
    selected.value = item
    detailsOpen.value = true
}

function convertToOffer(item: ProspectRequest) {
    // TODO: brancher vers le flux d’offre
    toast.add({ title: 'Conversion en offre', description: `${item.last_name} ${item.first_name}`, icon: 'i-heroicons-arrow-right-circle', color: 'primary' })
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
                <UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchAll">Rafraîchir</UButton>
            </div>
        </UCard>

        <ClientOnly>
            <RequestModal :model-value="creating" :payload="selected"
                @update:model-value="v => creating = v" @submit="submitFromModal" />
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