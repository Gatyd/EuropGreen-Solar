<script setup lang="ts">
import { useAuthStore } from '~/store/auth'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const loading = ref(true)
const auth = useAuthStore()

// ID du client depuis l'URL
const clientId = computed(() => route.query.id as string)

// Données de la fiche client
const ficheClient = ref<any>(null)

// Récupération des données
async function fetchFicheClient() {
    if (!clientId.value) {
        toast.add({
            title: 'Erreur',
            description: 'ID client manquant',
            color: 'error'
        })
        router.push('/home/customers/list')
        return
    }

    loading.value = true
    const result = await apiRequest<any>(
        () => $fetch(`/api/users/${clientId.value}/fiche/`, {
            credentials: 'include'
        }),
        toast
    )

    if (result) {
        ficheClient.value = result
    } else {
        router.push('/home/customers/list')
    }
    loading.value = false
}

// Formatage des montants
function formatAmount(amount: string | number | null | undefined): string {
    if (!amount) return '—'
    const num = typeof amount === 'string' ? parseFloat(amount) : amount
    return `${num.toFixed(2)} €`
}

// Statuts d'installation avec traductions
const statusLabels: Record<string, string> = {
    technical_visit: 'Visite technique',
    representation_mandate: 'Mandat de représentation',
    administrative_validation: 'Validation administrative',
    installation_completed: 'Installation effectuée',
    consuel_visit: 'Visite CONSUEL',
    enedis_connection: 'Raccordement ENEDIS',
    commissioning: 'Mise en service'
}

// Actions
function handleViewInstallations() {
    const count = ficheClient.value?.installations_count || 0
    if (count === 1 && ficheClient.value?.last_installation?.id) {
        router.push(`/home/installations/${ficheClient.value.last_installation.id}`)
    } else {
        router.push({ path: '/home/installations', query: { client: clientId.value } })
    }
}

function handleViewDocuments() {
    router.push({ path: '/home/documents', query: { client: clientId.value } })
}

function handleEmailHistory() {
    if (ficheClient.value?.user?.email) {
        router.push({
            path: '/home/email-history',
            query: { email: ficheClient.value.user.email }
        })
    }
}

function handleInteractionHistory() {
    toast.add({ title: 'Historique des interactions', description: 'Fonctionnalité à venir', color: 'info' })
}

onMounted(fetchFicheClient)
</script>

<template>
    <div>
        <!-- Header -->
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar class="lg:text-2xl font-semibold" :ui="{ root: 'h-12 lg:h-(--ui-header-height)', title: 'text-lg lg:text-2xl lg:gap-4' }">
                <template #title>
                    <UButton icon="i-heroicons-arrow-left" color="neutral" variant="ghost" class="hidden lg:block"
                        @click="router.push('/home/customers/list')" :ui="{ leadingIcon: 'size-7'}" />
                    <span>Fiche du client</span>
                </template>
            </UDashboardNavbar>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="flex justify-center items-center py-20">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl" />
        </div>

        <!-- Contenu principal -->
        <div v-else-if="ficheClient" class="w-full px-2 sm:px-6 space-y-6 pb-6 pt-4">

            <!-- Coordonnées complètes et informations de contact -->
            <UCard>
                <template #header>
                    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
                        <h2 class="text-xl font-bold">Informations client</h2>

                        <!-- Boutons d'actions -->
                        <div class="flex flex-wrap gap-2">
                            <UButton icon="i-heroicons-wrench-screwdriver" color="neutral" variant="outline"
                                label="Installations" @click="handleViewInstallations" />
                            <UButton icon="i-heroicons-document" color="neutral" variant="outline" label="Documents"
                                @click="handleViewDocuments" />
                            <UButton icon="i-heroicons-envelope" color="neutral" variant="outline"
                                label="Historique emails" @click="handleEmailHistory" />
                            <UButton v-if="auth.user?.is_superuser" icon="i-heroicons-clock" color="neutral"
                                variant="outline" label="Interactions" @click="handleInteractionHistory" />
                        </div>
                    </div>
                </template>

                <div class="space-y-6">
                    <!-- Informations principales - 3 colonnes sur grands écrans -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- Civilité -->
                        <div v-if="ficheClient.last_mandate?.client_civility">
                            <p class="text-sm text-gray-500">Civilité</p>
                            <p class="font-medium">
                                {{ ficheClient.last_mandate.client_civility === 'mme' ? 'Madame' : 'Monsieur' }}
                            </p>
                        </div>

                        <!-- Nom -->
                        <div>
                            <p class="text-sm text-gray-500">Nom</p>
                            <p class="font-medium">{{ ficheClient.user.last_name }}</p>
                        </div>

                        <!-- Prénom -->
                        <div>
                            <p class="text-sm text-gray-500">Prénom</p>
                            <p class="font-medium">{{ ficheClient.user.first_name }}</p>
                        </div>

                        <!-- Email -->
                        <div>
                            <p class="text-sm text-gray-500">Email</p>
                            <p class="font-medium">{{ ficheClient.user.email }}</p>
                        </div>

                        <!-- Téléphone -->
                        <div>
                            <p class="text-sm text-gray-500">Téléphone</p>
                            <p class="font-medium">{{ ficheClient.user.phone_number || '—' }}</p>
                        </div>

                        <!-- Adresse complète - pleine largeur -->
                        <div v-if="ficheClient.last_installation?.client_address" class="lg:col-span-2">
                            <p class="text-sm text-gray-500 mb-1">Adresse complète</p>
                            <p class="font-medium whitespace-pre-line">{{ ficheClient.last_installation.client_address
                                }}
                            </p>
                        </div>

                        <!-- Statut du compte -->
                        <div class="space-y-1">
                            <p class="text-sm text-gray-600">Compte</p>
                            <UBadge :color="ficheClient.user.is_active ? 'success' : 'error'" variant="subtle">
                                {{ ficheClient.user.is_active ? 'Actif' : 'Inactif' }}
                            </UBadge>
                        </div>

                        <!-- Statut d'invitation -->
                        <div class="space-y-1">
                            <p class="text-sm text-gray-600">Invitation</p>
                            <UBadge :color="!ficheClient.user.accept_invitation ? 'warning' : 'success'" variant="subtle">
                                {{ !ficheClient.user.accept_invitation ? 'En attente' : 'Acceptée' }}
                            </UBadge>
                        </div>

                        <!-- Étape actuelle -->
                        <div class="space-y-1">
                            <p class="text-sm text-gray-600">Étape</p>
                            <UBadge :color="ficheClient.last_installation?.status ? 'primary' : 'error'" variant="subtle">
                                {{ ficheClient.last_installation?.status ? statusLabels[ficheClient.last_installation.status] || ficheClient.last_installation.status : 'Aucune installation' }}
                            </UBadge>
                        </div>
                    </div>
                </div>
            </UCard>

            <!-- Informations de parrainage (uniquement pour admin) -->
            <UCard v-if="auth.user?.is_superuser && (ficheClient.commission || ficheClient.filleuls_count > 0)">
                <template #header>
                    <h2 class="text-xl font-bold">Parrainage</h2>
                </template>
                <div class="space-y-4">
                    <!-- Commission -->
                    <div v-if="ficheClient.commission">
                        <p class="text-sm text-gray-500 mb-2">Commission</p>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-xs text-gray-500">Type</p>
                                <p class="font-medium">
                                    {{ ficheClient.commission.type === 'percentage' ? 'Pourcentage' : 'Valeur fixe' }}
                                </p>
                            </div>
                            <div>
                                <p class="text-xs text-gray-500">Valeur</p>
                                <p class="font-medium">
                                    {{ ficheClient.commission.type === 'percentage'
                                        ? `${ficheClient.commission.value}%`
                                        : formatAmount(ficheClient.commission.value)
                                    }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Filleuls -->
                    <div v-if="ficheClient.filleuls_count > 0">
                        <p class="text-sm text-gray-500 mb-2">
                            Filleuls ({{ ficheClient.filleuls_count }})
                        </p>
                        <div class="space-y-2">
                            <div v-for="filleul in ficheClient.filleuls" :key="filleul.id"
                                class="flex justify-between items-center p-2 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer"
                                @click="router.push({ path: '/home/customers/' + filleul.id, query: { id: filleul.id } })">
                                <div>
                                    <p class="font-medium">{{ filleul.first_name }} {{ filleul.last_name }}</p>
                                    <p class="text-sm text-gray-500">{{ filleul.email }}</p>
                                </div>
                                <UIcon name="i-heroicons-chevron-right" class="text-gray-400" />
                            </div>
                        </div>
                    </div>

                    <div v-if="!ficheClient.commission && ficheClient.filleuls_count === 0"
                        class="text-center py-4 text-gray-500">
                        <p>Aucune information de parrainage</p>
                    </div>
                </div>
            </UCard>

        </div>
    </div>
</template>
