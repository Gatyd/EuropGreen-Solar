/**
 * Composable pour gérer la sélection de période du dashboard.
 * Permet de filtrer les données par période prédéfinie ou personnalisée.
 */

export interface PeriodOption {
    value: string
    label: string
}

export interface DateRange {
    start: string
    end: string
}

export function useDashboardPeriod() {
    const selectedPeriod = ref<string>('30d')
    const customRange = ref<DateRange>({
        start: '',
        end: ''
    })
    
    // Options de période prédéfinies
    const periodOptions: PeriodOption[] = [
        { value: '7d', label: '7 derniers jours' },
        { value: '30d', label: '30 derniers jours' },
        { value: '6m', label: '6 derniers mois' },
        { value: '1y', label: '1 an' },
        { value: 'custom', label: 'Personnalisé' }
    ]
    
    /**
     * Génère les paramètres de requête pour l'API
     */
    const queryParams = computed(() => {
        const params: Record<string, string> = {
            period: selectedPeriod.value
        }
        
        if (selectedPeriod.value === 'custom' && customRange.value.start && customRange.value.end) {
            params.start_date = customRange.value.start
            params.end_date = customRange.value.end
        }
        
        return params
    })
    
    /**
     * Label formaté de la période sélectionnée
     */
    const periodLabel = computed(() => {
        if (selectedPeriod.value === 'custom' && customRange.value.start && customRange.value.end) {
            const start = new Date(customRange.value.start).toLocaleDateString('fr-FR')
            const end = new Date(customRange.value.end).toLocaleDateString('fr-FR')
            return `${start} - ${end}`
        }
        
        const option = periodOptions.find(o => o.value === selectedPeriod.value)
        return option?.label || '30 derniers jours'
    })
    
    return {
        selectedPeriod,
        customRange,
        periodOptions,
        queryParams,
        periodLabel
    }
}
