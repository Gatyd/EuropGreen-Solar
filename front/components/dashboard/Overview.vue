<script setup lang="ts">
interface OverviewData {
    active_projects: number
    revenue: {
        total: number
        pending: number
        potential: number
    }
    conversion_rate: number
    commissions_due: number
}

const props = defineProps<{
    queryParams: Record<string, string>
}>()

const toast = useToast()
const loading = ref(true)
const data = ref<OverviewData | null>(null)

// Fetch data
async function fetchData() {
    loading.value = true
    const result = await apiRequest<OverviewData>(
        () => $fetch('/api/admin-platform/dashboard/overview/', {
            credentials: 'include',
            params: props.queryParams
        }),
        toast
    )

    if (result) {
        data.value = result
    }
    loading.value = false
}

// Watch pour recharger quand les params changent
watch(() => props.queryParams, fetchData, { deep: true })

onMounted(fetchData)
</script>

<template>
    <div v-bind="$attrs" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Card 1: Projets actifs -->
        <UCard>
            <template #header>
                <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-600">Projets actifs</span>
                    <UIcon name="i-heroicons-folder-open" class="text-xl text-blue-500" />
                </div>
            </template>

            <div v-if="loading" class="space-y-2">
                <USkeleton class="h-8 w-20" />
                <USkeleton class="h-4 w-32" />
            </div>
            <div v-else-if="data" class="space-y-1">
                <p class="text-3xl font-bold text-gray-900">{{ data.active_projects }}</p>
                <p class="text-xs text-gray-500">En cours de traitement</p>
            </div>
        </UCard>

        <!-- Card 2: Chiffre d'affaires -->
        <UCard>
            <template #header>
                <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-600">Chiffre d'affaires</span>
                    <UIcon name="i-heroicons-currency-euro" class="text-xl text-green-500" />
                </div>
            </template>

            <div v-if="loading" class="space-y-2">
                <USkeleton class="h-8 w-32" />
                <USkeleton class="h-4 w-full" />
            </div>
            <div v-else-if="data" class="space-y-2">
                <p class="text-3xl font-bold text-green-600">{{ formatPrice(data.revenue.total) }} €</p>
                <div class="text-xs text-gray-500 flex items-center gap-2">
                    <div class="flex items-center gap-1">
                        <span>En attente : {{ formatPrice(data.revenue.pending) }} €</span>
                        <UTooltip :delay-duration="0"
                            text="Factures émises mais pas encore payées (ou partiellement payées)">
                            <UIcon name="i-heroicons-information-circle" class="text-gray-400 cursor-help" :size="16" />
                        </UTooltip>
                    </div>
                    <span class="text-gray-300">|</span>
                    <div class="flex items-center gap-1">
                        <span>Potentiel : {{ formatPrice(data.revenue.potential) }} €</span>
                        <UTooltip :delay-duration="0" text="Devis envoyés aux clients mais pas encore signés">
                            <UIcon name="i-heroicons-information-circle" class="text-gray-400 cursor-help" :size="16" />
                        </UTooltip>
                    </div>
                </div>
            </div>
        </UCard>

        <!-- Card 3: Taux de conversion -->
        <UCard>
            <template #header>
                <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-600">Taux de conversion</span>
                    <UIcon name="i-heroicons-chart-bar" class="text-xl text-purple-500" />
                </div>
            </template>

            <div v-if="loading" class="space-y-2">
                <USkeleton class="h-8 w-24" />
                <USkeleton class="h-4 w-28" />
            </div>
            <div v-else-if="data" class="space-y-1">
                <p class="text-3xl font-bold text-purple-600">{{ data.conversion_rate }}%</p>
                <p class="text-xs text-gray-500">Demandes → Installations</p>
            </div>
        </UCard>

        <!-- Card 4: Commissions à verser -->
        <UCard>
            <template #header>
                <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-600">Commissions à verser</span>
                    <UIcon name="i-heroicons-banknotes" class="text-xl text-orange-500" />
                </div>
            </template>

            <div v-if="loading" class="space-y-2">
                <USkeleton class="h-8 w-28" />
                <USkeleton class="h-4 w-24" />
            </div>
            <div v-else-if="data" class="space-y-1">
                <p class="text-3xl font-bold text-orange-600">{{ formatPrice(data.commissions_due) }} €</p>
                <p class="text-xs text-gray-500">Non payées</p>
            </div>
        </UCard>
    </div>
</template>
