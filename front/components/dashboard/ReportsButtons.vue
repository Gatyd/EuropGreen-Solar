<script setup lang="ts">
const props = defineProps<{
    selectedPeriod: string
    customRange: { start: string; end: string }
}>()

const toast = useToast()

// Modals
const accountingExportModal = ref(false)

type ReportColor = 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'error' | 'neutral'

interface Report {
    id: string
    label: string
    icon: string
    color: ReportColor
}

// Rapports implémentés
const activeReports: Report[] = [
    { id: 'sales', label: 'Rapport des ventes', icon: 'i-heroicons-document-chart-bar', color: 'primary' },
    { id: 'accounting', label: 'Export comptable', icon: 'i-heroicons-document-arrow-down', color: 'success' },
    { id: 'commissions', label: 'Rapport des commissions', icon: 'i-heroicons-banknotes', color: 'warning' },
    { id: 'prospects', label: 'Rapport des prospects', icon: 'i-heroicons-user-group', color: 'info' }
]

// Rapports futurs (commentés)
// const futureReports = [
//     { id: 'installations', label: 'Rapport d\'installations', icon: 'i-heroicons-wrench-screwdriver' },
//     { id: 'products', label: 'Rapport des produits', icon: 'i-heroicons-cube' },
// ]

async function handleReportClick(reportId: string) {
    if (reportId === 'accounting') {
        accountingExportModal.value = true
        return
    }

    // TODO: Implémenter les autres rapports
    toast.add({
        title: 'Génération en cours...',
        description: `Le rapport "${reportId}" sera bientôt disponible`,
        color: 'primary'
    })
    console.log('Génération du rapport:', reportId)
}
</script>

<template>
    <UCard v-bind="$attrs">
        <template #header>
            <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-document-text" class="text-xl text-gray-500" />
                <span class="font-semibold">Rapports</span>
            </div>
        </template>

        <!-- Vertical sur grands écrans (lg:flex-col), horizontal sur petits (flex-row) -->
        <div class="flex flex-row lg:flex-col gap-3">
            <UButton v-for="report in activeReports" :key="report.id" :icon="report.icon" :label="report.label"
                :color="report.color" variant="outline" size="sm" class="justify-start flex-1 lg:flex-none"
                @click="handleReportClick(report.id)" />
        </div>

        <!-- Modals -->
        <ReportsAccountingExportModal v-model="accountingExportModal" :selected-period="selectedPeriod"
            :custom-range="customRange" />
    </UCard>
</template>
