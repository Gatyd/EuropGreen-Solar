<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const toast = useToast()
const loading = ref(true)

// Email du client à filtrer
const clientEmail = computed(() => route.query.email as string)

// Liste des emails
const emails = ref<any[]>([])

// Email sélectionné (null par défaut - pas de sélection automatique)
const selectedEmail = ref<any>(null)

// Slideover pour mobile
const isSlideoverOpen = ref(false)

// Récupération des emails
async function fetchEmails() {
    if (!clientEmail.value) {
        toast.add({
            title: 'Erreur',
            description: 'Email client manquant',
            color: 'error'
        })
        router.back()
        return
    }

    loading.value = true
    const result = await apiRequest<any[]>(
        () => $fetch(`/api/admin-platform/email-logs/?email=${encodeURIComponent(clientEmail.value)}`, {
            credentials: 'include'
        }),
        toast
    )

    if (result) {
        emails.value = result
    }
    loading.value = false
}

// Sélectionner un email
function selectEmail(email: any) {
    selectedEmail.value = email

    // Sur mobile, ouvrir le slideover
    if (window.innerWidth < 1024) {
        isSlideoverOpen.value = true
    }
}

const closeEmailDetail = () => {
    isSlideoverOpen.value = false
    selectedEmail.value = null
}

onMounted(fetchEmails)
</script>

<template>
    <div class="overflow-hidden h-full">
        <!-- Header -->
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)', title: 'text-lg lg:text-2xl lg:gap-4' }">
                <template #title>
                    <UButton icon="i-heroicons-arrow-left" color="neutral" variant="ghost" class="hidden lg:block"
                        @click="router.back()" :ui="{ leadingIcon: 'size-7' }" />
                    <span>Historique des emails</span>
                </template>
            </UDashboardNavbar>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="flex justify-center items-center py-20">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl" />
        </div>

        <!-- Contenu principal -->
        <div v-else class="flex h-[calc(100vh-var(--ui-header-height))]">

            <!-- Liste des emails (gauche / plein écran mobile) -->
            <div class="w-full lg:w-96 xl:w-[500px] border-r border-default overflow-y-auto">
                <div v-if="emails.length === 0" class="text-center py-12 text-gray-500">
                    <UIcon name="i-heroicons-inbox" class="text-6xl mb-4 mx-auto" />
                    <p>Aucun email trouvé</p>
                </div>

                <div v-else>
                    <EmailsEmailListItem v-for="email in emails" :key="email.id" :email="email"
                        :is-selected="selectedEmail?.id === email.id" @select="selectEmail(email)" />
                </div>
            </div>

            <!-- Détails de l'email (droite) - Desktop uniquement -->
            <div class="hidden lg:flex flex-1 flex-col overflow-hidden">
                <!-- État vide par défaut -->
                <div v-if="!selectedEmail" class="flex-1 flex items-center justify-center text-gray-400">
                    <div class="text-center">
                        <UIcon name="i-heroicons-envelope-open" class="text-6xl mb-4 mx-auto" />
                        <p class="text-lg">Sélectionnez un email</p>
                        <p class="text-sm mt-2">Cliquez sur un email dans la liste pour voir son contenu</p>
                    </div>
                </div>

                <!-- Détails de l'email sélectionné -->
                <EmailsEmailDetail v-else :email="selectedEmail" @close="closeEmailDetail" />
            </div>
        </div>

        <!-- Slideover pour mobile uniquement -->
        <USlideover v-model:open="isSlideoverOpen" side="right">
            <template #content>
                <EmailsEmailDetail v-if="selectedEmail" :email="selectedEmail" @close="closeEmailDetail" />
            </template>
        </USlideover>
    </div>
</template>
