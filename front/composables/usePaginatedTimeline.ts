/**
 * Composable pour gérer une timeline paginée avec chargement progressif.
 * 
 * Fonctionnalités :
 * - Chargement initial de la première page
 * - Accumulation des données lors du "Charger plus"
 * - Gestion des états (loading, loadingMore, hasMore)
 * - Détection automatique de fin de liste
 * 
 * @example
 * const { data, loading, loadingMore, hasMore, loadMore, refresh } = usePaginatedTimeline(userId)
 */

interface PaginatedResponse<T> {
    count: number
    next: string | null
    previous: string | null
    results: T[]
    user?: {
        id: string
        email: string
        full_name: string
    }
}

interface TimelineData {
    user: {
        id: string
        email: string
        full_name: string
    }
    logs: any[]
    count: number
}

export function usePaginatedTimeline(userId: Ref<string> | string) {
    const toast = useToast()
    
    // États réactifs
    const data = ref<TimelineData>({
        user: { id: '', email: '', full_name: '' },
        logs: [],
        count: 0
    })
    const loading = ref(false)
    const loadingMore = ref(false)
    const hasMore = ref(false)
    const nextPage = ref<string | null>(null)
    const currentPage = ref(1)
    
    // Résolution de userId (peut être ref ou string)
    const userIdValue = computed(() => 
        typeof userId === 'string' ? userId : userId.value
    )
    
    /**
     * Charge une page de données (première page ou page suivante)
     */
    async function fetchPage(pageNum: number = 1, append: boolean = false) {
        if (!userIdValue.value) return
        
        const isFirstLoad = pageNum === 1 && !append
        if (isFirstLoad) {
            loading.value = true
        } else {
            loadingMore.value = true
        }
        
        try {
            const response = await apiRequest<PaginatedResponse<any>>(
                () => $fetch(`/api/admin-platform/audit-logs/user-timeline/${userIdValue.value}/`, {
                    credentials: 'include',
                    params: { page: pageNum }
                }),
                toast
            )
            
            if (response) {
                // Mise à jour des infos utilisateur (première fois seulement)
                if (response.user && isFirstLoad) {
                    data.value.user = response.user
                }
                
                // Accumulation ou remplacement des logs
                if (append) {
                    data.value.logs = [...data.value.logs, ...response.results]
                } else {
                    data.value.logs = response.results
                }
                
                // Mise à jour du count total
                data.value.count = response.count
                
                // Gestion de la pagination
                nextPage.value = response.next
                hasMore.value = response.next !== null
                currentPage.value = pageNum
            }
        } catch (error) {
            console.error('Erreur lors du chargement de la timeline:', error)
        } finally {
            loading.value = false
            loadingMore.value = false
        }
    }
    
    /**
     * Charge la page suivante et l'ajoute aux données existantes
     */
    async function loadMore() {
        if (!hasMore.value || loadingMore.value) return
        await fetchPage(currentPage.value + 1, true)
    }
    
    /**
     * Recharge depuis le début (refresh complet)
     */
    async function refresh() {
        data.value.logs = []
        currentPage.value = 1
        nextPage.value = null
        await fetchPage(1, false)
    }
    
    /**
     * Charge la première page au montage
     */
    async function initialize() {
        await fetchPage(1, false)
    }
    
    return {
        // États
        data: readonly(data),
        loading: readonly(loading),
        loadingMore: readonly(loadingMore),
        hasMore: readonly(hasMore),
        currentPage: readonly(currentPage),
        
        // Actions
        loadMore,
        refresh,
        initialize
    }
}
