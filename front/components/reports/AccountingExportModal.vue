<script setup lang="ts">
const model = defineModel<boolean>()

const props = defineProps<{
    selectedPeriod: string
    customRange: { start: string; end: string }
}>()

const { downloadFile } = useFileDownload()
const loading = ref(false)

// Formulaire
const form = reactive({
    start_date: '',
    end_date: '',
    status: 'all'
})

// Options de statut
const statusOptions = [
    { value: 'all', label: 'Toutes les factures' },
    { value: 'paid', label: 'Payées uniquement' },
    { value: 'issued', label: 'Émises uniquement' },
    { value: 'partially_paid', label: 'Partiellement payées' }
]

// Calculer les dates en fonction de la période
function getDateRangeFromPeriod(period: string) {
    const end = new Date()
    let start = new Date()

    switch (period) {
        case '7d':
            start.setDate(end.getDate() - 7)
            break
        case '30d':
            start.setDate(end.getDate() - 30)
            break
        case '6m':
            start.setMonth(end.getMonth() - 6)
            break
        case '1y':
            start.setFullYear(end.getFullYear() - 1)
            break
        default:
            start.setDate(end.getDate() - 30) // Par défaut 30 jours
    }

    return {
        start: start.toISOString().split('T')[0],
        end: end.toISOString().split('T')[0]
    }
}

// Mettre à jour les dates quand la période change
watch(() => [props.selectedPeriod, props.customRange], () => {
    updateDatesFromPeriod()
}, { immediate: true, deep: true })

function updateDatesFromPeriod() {
    if (props.selectedPeriod === 'custom' && props.customRange.start && props.customRange.end) {
        // Utiliser la période personnalisée
        form.start_date = props.customRange.start
        form.end_date = props.customRange.end
    } else {
        // Utiliser la période prédéfinie
        const range = getDateRangeFromPeriod(props.selectedPeriod)
        form.start_date = range.start
        form.end_date = range.end
    }
}

async function handleExport(format: 'csv' | 'excel') {
    loading.value = true

    const params: Record<string, string> = {
        start_date: form.start_date,
        end_date: form.end_date,
        status: form.status,
        export_format: format
    }

    await downloadFile('/api/admin-platform/reports/accounting-export/', undefined, params)

    loading.value = false
}
</script>

<template>
    <UModal v-model:open="model" :ui="{ content: 'sm:max-w-lg' }">
        <template #content>
            <UCard>
                <template #header>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <UIcon name="i-heroicons-document-arrow-down" class="text-xl" />
                            <h3 class="text-lg font-semibold">Export Comptable</h3>
                        </div>
                        <UButton color="neutral" variant="ghost" icon="i-heroicons-x-mark" @click="model = false" />
                    </div>
                </template>

                <div class="space-y-4">
                    <!-- Description -->
                    <p class="text-sm text-gray-600">
                        Exportez vos factures au format CSV ou Excel pour les intégrer à votre logiciel de comptabilité.
                    </p>

                    <!-- Formulaire -->
                    <div class="grid grid-cols-10 gap-5">
                        <UFormField label="Date début" class="col-span-5 sm:col-span-3" required>
                            <UInput v-model="form.start_date" type="date" class="w-full" />
                        </UFormField>
                        <UFormField label="Date fin" class="col-span-5 sm:col-span-3" required>
                            <UInput v-model="form.end_date" type="date" class="w-full" />
                        </UFormField>
                        <UFormField label="Statut des factures" class="col-span-10 sm:col-span-4">
                            <USelectMenu v-model="form.status" :items="statusOptions" value-key="value"
                                class="w-full" />
                        </UFormField>
                    </div>

                    <!-- Info -->
                    <UAlert icon="i-heroicons-information-circle" color="primary" variant="subtle"
                        title="Colonnes exportées"
                        description="N° facture, dates, client, montants HT/TVA/TTC, statut, notes" />
                </div>

                <template #footer>
                    <div class="flex items-center justify-end gap-3">
                        <UButton color="neutral" variant="outline" label="Annuler" @click="model = false"
                            :disabled="loading" />
                        <UButton color="success" icon="i-heroicons-document-text" label="Exporter CSV"
                            @click="handleExport('csv')" :loading="loading" />
                        <UButton color="success" icon="i-heroicons-table-cells" label="Exporter Excel"
                            @click="handleExport('excel')" :loading="loading" />
                    </div>
                </template>
            </UCard>
        </template>
    </UModal>
</template>
