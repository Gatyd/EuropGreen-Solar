<script setup lang="ts">
// Placeholders pour les futures fonctionnalités de rapports
const reports = [
    { id: 'sales', label: 'Rapport des ventes', icon: 'i-heroicons-document-chart-bar' },
    { id: 'installations', label: 'Rapport d\'installations', icon: 'i-heroicons-wrench-screwdriver' },
    { id: 'commissions', label: 'Rapport des commissions', icon: 'i-heroicons-banknotes' },
    { id: 'prospects', label: 'Rapport des prospects', icon: 'i-heroicons-user-group' }
]

function handleReportClick(reportId: string) {
    // TODO: Implémenter la génération de rapports
    console.log('Génération du rapport:', reportId)
}
</script>

<template>
    <UCard>
        <template #header>
            <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-document-text" class="text-xl text-gray-500" />
                <span class="font-semibold">Rapports</span>
                <UBadge label="Bientôt" variant="subtle" color="neutral" size="xs" class="ml-2" />
            </div>
        </template>

        <!-- Vertical sur grands écrans (lg:flex-col), horizontal sur petits (flex-row) -->
        <div class="flex flex-row flex-wrap lg:flex-col gap-3">
            <UButton v-for="report in reports" :key="report.id" :icon="report.icon" :label="report.label"
                color="neutral" variant="outline" size="sm" disabled class="justify-start flex-1 lg:flex-none"
                @click="handleReportClick(report.id)" />
        </div>
    </UCard>
</template>
