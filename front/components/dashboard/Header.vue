<script setup lang="ts">
import type { PeriodOption } from '~/composables/useDashboardPeriod'

const props = defineProps<{
    selectedPeriod: string
    customRange: { start: string; end: string }
    periodOptions: PeriodOption[]
}>()

const emit = defineEmits<{
    'update:selectedPeriod': [value: string]
    'update:customRange': [value: { start: string; end: string }]
    'refresh': []
}>()

const { handleDateBlur } = useDateValidation()

const showCustomDatePicker = computed(() => props.selectedPeriod === 'custom')

function handlePeriodChange(value: string) {
    emit('update:selectedPeriod', value)
}

function handleRefresh() {
    emit('refresh')
}

// Valider et ajuster les dates après saisie complète
function onDateBlur(field: 'start' | 'end', value: string) {
    const adjustedRange = handleDateBlur(
        field,
        value,
        props.customRange.start,
        props.customRange.end
    )
    emit('update:customRange', adjustedRange)
}

// Mise à jour immédiate pendant la saisie (sans validation)
function handleDateInput(field: 'start' | 'end', value: string) {
    const newRange = { ...props.customRange, [field]: value }
    emit('update:customRange', newRange)
}
</script>

<template>
    <div v-bind="$attrs" class="flex items-center justify-between gap-4 mb-6">
        <div class="flex items-center gap-3">
            <p class="text-sm text-gray-600">Vue d'ensemble de l'activité</p>
        </div>

        <div class="flex items-center gap-3">
            <!-- Sélecteur de période -->
            <USelectMenu :model-value="periodOptions.find(o => o.value === selectedPeriod)"
                @update:model-value="(val: PeriodOption) => handlePeriodChange(val.value)" :items="periodOptions"
                value-attribute="value" text-attribute="label" class="w-48" />

            <!-- Date picker pour période personnalisée -->
            <div v-if="showCustomDatePicker" class="flex items-center gap-2">
                <input type="date" :value="customRange.start"
                    @input="handleDateInput('start', ($event.target as HTMLInputElement).value)"
                    @blur="onDateBlur('start', ($event.target as HTMLInputElement).value)"
                    class="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                <span class="text-gray-500">→</span>
                <input type="date" :value="customRange.end"
                    @input="handleDateInput('end', ($event.target as HTMLInputElement).value)"
                    @blur="onDateBlur('end', ($event.target as HTMLInputElement).value)"
                    class="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>

            <!-- Bouton refresh -->
            <UButton icon="i-heroicons-arrow-path" color="neutral" variant="ghost" @click="handleRefresh"
                aria-label="Actualiser les données" />
        </div>
    </div>
</template>
