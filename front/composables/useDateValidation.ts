/**
 * Composable pour la validation ergonomique des dates
 * Permet la saisie libre mais valide intelligemment après saisie complète
 */
export function useDateValidation() {
    const MIN_DATE = '2015-01-01'
    const today = new Date().toISOString().split('T')[0]

    /**
     * Obtient une plage de dates par défaut (30 derniers jours)
     */
    function getDefaultDateRange() {
        const end = new Date()
        const start = new Date()
        start.setDate(start.getDate() - 30)
        
        return {
            start: start.toISOString().split('T')[0],
            end: end.toISOString().split('T')[0]
        }
    }

    /**
     * Valide et ajuste une date de début
     * - Si invalide ou incomplète → renvoie null (utiliser période par défaut)
     * - Si avant 2015 → ajuste à 2015-01-01
     * - Sinon → renvoie la date validée
     */
    function validateStartDate(value: string): string | null {
        // Vérifier que la date est complète (format YYYY-MM-DD = 10 caractères)
        if (!value || value.length !== 10) {
            return null
        }
        
        // Vérifier que la date est valide
        const date = new Date(value)
        if (isNaN(date.getTime())) {
            return null
        }
        
        // Si avant 2015, ajuster à 2015-01-01
        if (date < new Date(MIN_DATE)) {
            return MIN_DATE
        }
        
        return value
    }

    /**
     * Valide et ajuste une date de fin
     * - Si invalide ou incomplète → renvoie null (utiliser période par défaut)
     * - Si après aujourd'hui → ajuste à aujourd'hui
     * - Si avant la date de début → ajuste à la date de début
     * - Sinon → renvoie la date validée
     */
    function validateEndDate(value: string, startDate: string): string | null {
        // Vérifier que la date est complète (format YYYY-MM-DD = 10 caractères)
        if (!value || value.length !== 10) {
            return null
        }
        
        // Vérifier que la date est valide
        const date = new Date(value)
        if (isNaN(date.getTime())) {
            return null
        }
        
        const todayDate = new Date(today)
        const startDateObj = new Date(startDate)
        
        // Si après aujourd'hui, ajuster à aujourd'hui
        if (date > todayDate) {
            return today
        }
        
        // Si avant la date de début, ajuster à la date de début
        if (date < startDateObj) {
            return startDate
        }
        
        return value
    }

    /**
     * Gère le blur sur un champ de date et retourne les dates ajustées
     */
    function handleDateBlur(
        field: 'start' | 'end',
        value: string,
        currentStart: string,
        currentEnd: string
    ): { start: string; end: string } {
        if (field === 'start') {
            const validatedStart = validateStartDate(value)
            if (validatedStart === null) {
                // Date invalide → utiliser période par défaut
                return getDefaultDateRange()
            }
            return { start: validatedStart, end: currentEnd }
        } else {
            const validatedEnd = validateEndDate(value, currentStart)
            if (validatedEnd === null) {
                // Date invalide → utiliser période par défaut
                return getDefaultDateRange()
            }
            return { start: currentStart, end: validatedEnd }
        }
    }

    return {
        MIN_DATE,
        today,
        getDefaultDateRange,
        validateStartDate,
        validateEndDate,
        handleDateBlur
    }
}
