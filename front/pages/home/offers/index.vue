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

// Statuts non autorisés au drop direct (processus spécifique)
const blockedStatuses = new Set<OfferStatus>(['quote_sent', 'quote_signed'])

const fetchAll = async (refresh = false) => {
    loading.value = true
    const data = await apiRequest<Offer[]>(
        () => $fetch('/api/offers/', { credentials: 'include' }),
        toast
    )
    if (data) allItems.value = data
    loading.value = false
    if(refresh) {
        toast.add({
            title: 'Données mises à jour',
            description: 'La liste des offres a été rafraîchie avec succès.',
            color: 'success'
        })
    }
}

onMounted(fetchAll)

const onDrop = async (payload: { to: OfferStatus, item: Offer }) => {
    const { to, item: card } = payload
    const prev = card.status
    if (to === prev) return
    if (blockedStatuses.has(to)) {
        toast.add({ title: 'Action non autorisée', description: 'Ce changement de statut suit un autre processus.', color: 'warning', icon: 'i-heroicons-exclamation-triangle' })
        return
    }
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
    editing.value = false
    await fetchAll()
}
</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Offres" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
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
                <UButton variant="ghost" icon="i-heroicons-arrow-path" @click="fetchAll(true)">Rafraîchir</UButton>
            </div>
        </UCard>

        <ClientOnly>
            <OfferModal v-if="selected" v-model="editing" :offer="selected" @submit="submitInlineEdit" />
        </ClientOnly>

        <div class="flex gap-4 overflow-x-auto p-4">
            <div v-for="col in columns" :key="col.key">
                <RequestSkeleton v-if="loading" :title="col.title" />
                <OfferColumn v-else :title="col.title" :status="col.key" :items="items[col.key]"
                    :count="items[col.key].length" @drop="onDrop" @open="openDetails" @submit-quote="fetchAll" />
            </div>
        </div>
    </div>
</template>