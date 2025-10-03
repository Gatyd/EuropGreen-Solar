<script setup lang="ts">
import type { TimelineItem } from '@nuxt/ui'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const loading = ref(true)

// ID de l'utilisateur depuis l'URL
const userId = computed(() => route.query.user_id as string)

// Données de la timeline
const timelineData = ref<any>(null)

// Récupération de la timeline
async function fetchTimeline() {
    if (!userId.value) {
        toast.add({
            title: 'Erreur',
            description: 'ID utilisateur manquant',
            color: 'error'
        })
        router.back()
        return
    }

    loading.value = true
    const result = await apiRequest<any>(
        () => $fetch(`/api/admin-platform/audit-logs/user-timeline/${userId.value}/`, {
            credentials: 'include'
        }),
        toast
    )

    if (result) {
        timelineData.value = result
    }
    loading.value = false
}

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

onMounted(fetchTimeline)
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
        <div v-if="loading" class="flex justify-center items-center py-20">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl" />
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
                        <span class="font-semibold">{{ timelineData.count }}</span> événements enregistrés
                    </p>
                </div>
            </div>

            <!-- Timeline -->
            <div v-if="timelineItems.length === 0" class="text-center py-12 text-gray-500">
                <UIcon name="i-heroicons-clock" class="text-6xl mb-4 mx-auto opacity-50" />
                <p class="text-lg">Aucun événement enregistré</p>
            </div>

            <UTimeline v-else :items="timelineItems">
                <template #description="{ item }">
                    <InteractionsInteractionCard :log="item as any" />
                </template>
            </UTimeline>
        </div>
    </div>
</template>