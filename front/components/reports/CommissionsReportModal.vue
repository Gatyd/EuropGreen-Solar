<script setup lang="ts">
const model = defineModel<boolean>()

const props = defineProps<{
    selectedPeriod: string
    customRange: { start: string; end: string }
}>()

const { downloadFile } = useFileDownload()
const { handleDateBlur: validateDateBlur } = useDateValidation()
const loading = ref(false)

// Formulaire
const form = reactive({
    start_date: '',
    end_date: '',
    paid_status: 'all'
})

// Options de statut de paiement
const paidStatusOptions = [
    { value: 'all', label: 'Toutes les commissions' },
    { value: 'paid', label: 'Payées uniquement' },
    { value: 'unpaid', label: 'À payer uniquement' }
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
            start.setDate(end.getDate() - 30)
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
        form.start_date = props.customRange.start
        form.end_date = props.customRange.end
    } else {
        const range = getDateRangeFromPeriod(props.selectedPeriod)
        form.start_date = range.start
        form.end_date = range.end
    }
}

// Valider les dates avec le composable
function handleDateBlur(field: 'start_date' | 'end_date') {
    const fieldMap = { start_date: 'start', end_date: 'end' } as const
    const mappedField = fieldMap[field]
    
    const adjustedRange = validateDateBlur(
        mappedField,
        form[field],
        form.start_date,
        form.end_date
    )
    
    form.start_date = adjustedRange.start
    form.end_date = adjustedRange.end
}

async function handleExport() {
    loading.value = true

    const params: Record<string, string> = {
        start_date: form.start_date,
        end_date: form.end_date,
        paid_status: form.paid_status
    }

    await downloadFile('/api/admin-platform/reports/commissions-report/', undefined, params)

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
                            <UIcon name="i-heroicons-banknotes" class="text-xl" />
                            <h3 class="text-lg font-semibold">Rapport des Commissions</h3>
                        </div>
                        <UButton color="neutral" variant="ghost" icon="i-heroicons-x-mark" @click="model = false" />
                    </div>
                </template>

                <div class="space-y-4">
                    <!-- Description -->
                    <p class="text-sm text-gray-600">
                        Générez un rapport détaillé des commissions dues et payées par bénéficiaire.
                    </p>

                    <!-- Formulaire -->
                    <div class="grid grid-cols-10 gap-5">
                        <UFormField label="Date début" class="col-span-5 sm:col-span-3" required>
                            <UInput v-model="form.start_date" type="date" class="w-full" 
                                @blur="handleDateBlur('start_date')" />
                        </UFormField>
                        <UFormField label="Date fin" class="col-span-5 sm:col-span-3" required>
                            <UInput v-model="form.end_date" type="date" class="w-full" 
                                @blur="handleDateBlur('end_date')" />
                        </UFormField>
                        <UFormField label="Statut de paiement" class="col-span-10 sm:col-span-4">
                            <USelectMenu v-model="form.paid_status" :items="paidStatusOptions" value-key="value"
                                class="w-full" />
                        </UFormField>
                    </div>

                    <!-- Info -->
                    <UAlert icon="i-heroicons-information-circle" color="primary" variant="subtle"
                        title="Contenu du rapport"
                        description="Total commissions, payées/à payer, détail par bénéficiaire (apporteur d'affaires et commercial)" />
                </div>

                <template #footer>
                    <div class="flex items-center justify-end gap-3">
                        <UButton color="neutral" variant="outline" label="Annuler" @click="model = false"
                            :disabled="loading" />
                        <UButton icon="i-heroicons-table-cells" label="Télécharger Excel"
                            @click="handleExport()" :loading="loading" />
                    </div>
                </template>
            </UCard>
        </template>
    </UModal>
</template>
