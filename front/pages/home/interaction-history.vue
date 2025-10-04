<script setup lang="ts">
import type { TimelineItem } from '@nuxt/ui'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// ID de l'utilisateur depuis l'URL
const userId = computed(() => route.query.user_id as string)

// Utiliser le composable de pagination
const {
    data: timelineData,
    loading,
    loadingMore,
    hasMore,
    loadMore: handleLoadMore,
    initialize
} = usePaginatedTimeline(userId)

// Icône selon le type d'action
function getActionIcon(action: number): string {
    const icons: Record<number, string> = {
        0: 'i-heroicons-plus-circle',
        1: 'i-heroicons-pencil-square',
        2: 'i-heroicons-trash',
    }
    return icons[action] || 'i-heroicons-arrow-path'
}

// Formater la date pour l'affichage
function formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// Transformer les logs en items pour UTimeline
const timelineItems = computed<TimelineItem[]>(() => {
    if (!timelineData.value?.logs) return []

    return timelineData.value.logs.map((log: any) => ({
        icon: getActionIcon(log.action),
        date: formatDate(log.timestamp),
        // On stocke le log complet dans une propriété custom
        ...log
    }))
})

// Initialisation au montage
onMounted(async () => {
    if (!userId.value) {
        toast.add({
            title: 'Erreur',
            description: 'ID utilisateur manquant',
            color: 'error'
        })
        router.back()
        return
    }
    await initialize()
})
</script>

<template>
    <div>
        <!-- Header -->
        <div class="sticky top-0 z-50 bg-white border-b border-default">
            <UDashboardNavbar class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)', title: 'text-lg lg:text-2xl lg:gap-4' }">
                <template #title>
                    <UButton icon="i-heroicons-arrow-left" color="neutral" variant="ghost" class="hidden lg:block"
                        @click="router.back()" :ui="{ leadingIcon: 'size-7' }" />
                    <span>Historique des interactions</span>
                </template>
            </UDashboardNavbar>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="w-full px-2 sm:px-6 py-6">
            <!-- Header skeleton -->
            <div class="flex items-center justify-between mb-6 pb-4 border-b border-default">
                <div class="space-y-2">
                    <USkeleton class="h-7 w-48" />
                    <USkeleton class="h-4 w-64" />
                </div>
                <USkeleton class="h-5 w-32" />
            </div>

            <!-- Timeline skeleton -->
            <div class="space-y-6">
                <div v-for="i in 3" :key="i" class="flex gap-4">
                    <div class="flex flex-col items-center">
                        <USkeleton class="h-10 w-10 rounded-full" />
                        <USkeleton class="h-full w-0.5 mt-2" style="min-height: 80px;" />
                    </div>
                    <div class="flex-1">
                        <USkeleton class="h-20 w-full rounded-lg" />
                    </div>
                </div>
            </div>
        </div>

        <!-- Contenu principal -->
        <div v-else-if="timelineData" class="w-full px-2 sm:px-6 py-6">

            <!-- Header utilisateur simplifié -->
            <div class="flex items-center justify-between mb-6 pb-4 border-b border-default">
                <div>
                    <h2 class="text-xl font-bold text-gray-900">
                        {{ timelineData.user.full_name || 'Utilisateur' }}
                    </h2>
                    <p class="text-sm text-gray-600 mt-1">{{ timelineData.user.email }}</p>
                </div>
                <div>
                    <p class="text-sm text-gray-500 mt-2">
                        <span class="font-semibold">{{ timelineData.count }}</span> événement{{ timelineData.count > 1 ?
                        's' :
                        '' }} enregistré{{ timelineData.count > 1 ? 's' : '' }}
                    </p>
                    <p v-if="timelineData.count > timelineItems.length" class="text-xs text-gray-400 mt-1">
                        {{ timelineItems.length }} affichés
                    </p>
                </div>
            </div>

            <!-- Timeline -->
            <div v-if="timelineItems.length === 0" class="text-center py-12 text-gray-500">
                <UIcon name="i-heroicons-clock" class="text-6xl mb-4 mx-auto opacity-50" />
                <p class="text-lg">Aucun événement enregistré</p>
            </div>

            <div v-else>
                <UTimeline :items="timelineItems">
                    <template #description="{ item }">
                        <InteractionsInteractionCard :log="item as any" />
                    </template>
                </UTimeline>

                <!-- Bouton Charger plus / État de fin -->
                <div class="mt-8 flex justify-center">
                    <UButton v-if="hasMore" @click="handleLoadMore" :loading="loadingMore" :disabled="loadingMore"
                        size="lg" color="primary" variant="outline" icon="i-heroicons-arrow-down-circle"
                        class="shadow-sm">
                        {{ loadingMore ? 'Chargement...' : 'Charger plus d\'événements' }}
                    </UButton>

                    <div v-else class="text-center text-gray-500 py-4">
                        <UIcon name="i-heroicons-check-circle" class="text-3xl mb-2 mx-auto text-green-500" />
                        <p class="text-sm font-medium">Fin de l'historique</p>
                        <p class="text-xs text-gray-400 mt-1">Tous les événements ont été chargés</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>