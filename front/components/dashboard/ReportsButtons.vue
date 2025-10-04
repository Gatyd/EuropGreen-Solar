<script setup lang="ts">
const props = defineProps<{
    selectedPeriod: string
    customRange: { start: string; end: string }
}>()

const toast = useToast()

// Modals
const accountingExportModal = ref(false)
const salesReportModal = ref(false)
const commissionsReportModal = ref(false)
const prospectsReportModal = ref(false)

interface Report {
    id: string
    label: string
    icon: string
}

// Rapports implémentés
const activeReports: Report[] = [
    { id: 'sales', label: 'Rapport des ventes', icon: 'i-heroicons-document-chart-bar' },
    { id: 'accounting', label: 'Export comptable', icon: 'i-heroicons-document-arrow-down' },
    { id: 'commissions', label: 'Rapport des commissions', icon: 'i-heroicons-banknotes' },
    { id: 'prospects', label: 'Rapport des prospects', icon: 'i-heroicons-user-group' }
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
    
    if (reportId === 'sales') {
        salesReportModal.value = true
        return
    }
    
    if (reportId === 'commissions') {
        commissionsReportModal.value = true
        return
    }
    
    if (reportId === 'prospects') {
        prospectsReportModal.value = true
        return
    }

    // Fallback pour rapports non implémentés
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
        <div class="flex flex-row flex-wrap lg:flex-col gap-3">
            <UButton v-for="report in activeReports" :key="report.id" :icon="report.icon" :label="report.label"
                color="neutral" variant="outline" size="sm" class="justify-start flex-1 lg:flex-none"
                @click="handleReportClick(report.id)" />
        </div>

        <!-- Modals -->
        <ReportsAccountingExportModal v-model="accountingExportModal" :selected-period="selectedPeriod"
            :custom-range="customRange" />
        <ReportsSalesReportModal v-model="salesReportModal" :selected-period="selectedPeriod"
            :custom-range="customRange" />
        <ReportsCommissionsReportModal v-model="commissionsReportModal" :selected-period="selectedPeriod"
            :custom-range="customRange" />
        <ReportsProspectsReportModal v-model="prospectsReportModal" :selected-period="selectedPeriod"
            :custom-range="customRange" />
    </UCard>
</template>
