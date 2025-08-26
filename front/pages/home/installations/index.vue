<script setup lang="ts">
import type { InstallationForm, InstallationStatus } from '~/types/installations'
import apiRequest from '~/utils/apiRequest'

definePageMeta({ layout: 'default' })

const toast = useToast()
const search = ref('')
const dateRange = ref<{ start?: string | null, end?: string | null }>({ start: null, end: null })

const columns: { key: InstallationStatus; title: string }[] = [
    { key: 'technical_visit', title: 'Visite technique' },
    { key: 'representation_mandate', title: 'Mandat de représentation' },
    { key: 'administrative_validation', title: 'Validation administrative' },
    { key: 'installation_completed', title: 'Installation effectuée' },
    { key: 'consuel_visit', title: 'Visite CONSUEL' },
    { key: 'enedis_connection', title: 'Raccordement ENEDIS' },
    { key: 'commissioning', title: 'Mise en service' }
]

const loading = ref(true)
const allItems = ref<InstallationForm[]>([])

const filteredItems = computed<InstallationForm[]>(() => {
    const term = (search.value || '').trim().toLowerCase()
    const start = dateRange.value.start || null
    const end = dateRange.value.end || null
    return allItems.value.filter((it) => {
        const hay = `${it.client_first_name} ${it.client_last_name} ${it.client_address}`.toLowerCase()
        const textOk = term ? hay.includes(term) : true
        const createdDate = (it.created_at || '').slice(0, 10)
        const startOk = start ? createdDate >= start : true
        const endOk = end ? createdDate <= end : true
        return textOk && startOk && endOk
    })
})

const items = computed<Record<InstallationStatus, InstallationForm[]>>(() => {
    const grouped: Record<InstallationStatus, InstallationForm[]> = {
        technical_visit: [],
        representation_mandate: [],
        administrative_validation: [],
        installation_completed: [],
        consuel_visit: [],
        enedis_connection: [],
        commissioning: [],
    }
    for (const it of filteredItems.value) {
        // Sécurise le groupement si un statut inattendu arrive (null/""/inconnu)
        const key = (it.status || 'technical_visit') as InstallationStatus
        if (!grouped[key]) {
            // Aide au debug sans casser l'UI
            console.warn('Statut installation inconnu, fallback vers technical_visit:', it.status, it)
            grouped[key] = []
        }
        grouped[key].push(it)
    }
    return grouped
})

const totalCount = computed(() => filteredItems.value.length)

const fetchAll = async () => {
    loading.value = true
    const data = await apiRequest<InstallationForm[]>(
        () => $fetch('/api/installations/forms/', { credentials: 'include' }),
        toast
    )
    if (data) allItems.value = data
    loading.value = false
}

onMounted(fetchAll)
</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Installations" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #trailing>
                    <UBadge variant="subtle">{{ totalCount }}</UBadge>
                </template>
            </UDashboardNavbar>
        </div>

        <UCard class="mb-4">
            <div class="flex flex-wrap items-end gap-3">
                <UFormField label="Recherche" class="w-full md:w-max lg:w-64">
                    <UInput v-model="search" class="w-full" placeholder="Nom, adresse..." />
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

        <div class="flex gap-4 overflow-x-auto p-4">
            <div v-for="col in columns" :key="col.key">
                <USkeleton v-if="loading" class="h-48 w-[340px]" />
                <InstallationColumn v-else :title="col.title" :status="col.key" :items="items[col.key]"
                    :count="items[col.key].length" />
            </div>
        </div>
    </div>
</template>