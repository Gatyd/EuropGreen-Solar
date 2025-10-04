<script setup lang="ts">
definePageMeta({
    middleware: 'admin'
})

// Composable pour gérer la période
const { selectedPeriod, customRange, periodOptions, queryParams, periodLabel } = useDashboardPeriod()

const refreshKey = ref(0)

// Fonction de refresh manuel
function handleRefresh() {
    refreshKey.value++
}
</script>

<template>
    <div class="sticky top-0 z-50 bg-white border-b border-default">
        <UDashboardNavbar title="Tableau de bord" class="lg:text-2xl font-semibold"
            :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
            <template #trailing>
                <UBadge :label="periodLabel" variant="subtle" color="primary" />
            </template>
        </UDashboardNavbar>
    </div>

    <div class="w-full px-2 sm:px-6 py-6 space-y-6">
        <!-- Header avec filtres -->
        <DashboardHeader :selected-period="selectedPeriod" :custom-range="customRange" :period-options="periodOptions"
            @update:selected-period="selectedPeriod = $event" @update:custom-range="customRange = $event"
            @refresh="handleRefresh" />

        <!-- KPIs Cards -->
        <DashboardOverview :key="`overview-${refreshKey}`" :query-params="queryParams" />

        <!-- Graphiques principaux -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DashboardConversionFunnel :key="`funnel-${refreshKey}`" :query-params="queryParams" />
            <DashboardRevenueChart :key="`revenue-${refreshKey}`" :query-params="queryParams" />
        </div>

        <!-- Sources, Produits et Rapports -->
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <div class="lg:col-span-2">
                <DashboardSourcesChart :key="`sources-${refreshKey}`" :query-params="queryParams" />
            </div>
            <div class="lg:col-span-2">
                <DashboardProductsChart :key="`products-${refreshKey}`" :query-params="queryParams" />
            </div>
            <div class="lg:col-span-1">
                <DashboardReportsButtons :selected-period="selectedPeriod" :custom-range="customRange" />
            </div>
        </div>
    </div>
</template>