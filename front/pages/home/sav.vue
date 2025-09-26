<script setup lang="ts">
import apiRequest from '~/utils/apiRequest'

definePageMeta({
    layout: 'default'
})

useSeoMeta({
    title: 'Service Après Vente',
    description: "Assistance, support et service après-vente Europ'Green Solar"
})

const toast = useToast()
const route = useRoute()

const savMessage = ref('')
const savSending = ref(false)
const savSent = ref(false)
const selectedCategory = ref<string | null>(null)

const categories = [
    { key: 'tech', label: 'Problème technique', icon: 'i-heroicons-wrench-screwdriver' },
    { key: 'billing', label: 'Facturation', icon: 'i-heroicons-receipt-percent' },
    { key: 'question', label: 'Question', icon: 'i-heroicons-question-mark-circle' },
    { key: 'appointment', label: 'Rendez-vous', icon: 'i-heroicons-calendar-days' }
]

const selectedCategoryLabel = computed(() => {
    const found = categories.find(c => c.key === selectedCategory.value)
    return found ? found.label : null
})

const charLimit = 5000
const remaining = computed(() => charLimit - savMessage.value.length)

function resetForm() {
    savMessage.value = ''
    selectedCategory.value = null
}

async function submit() {
    if (!savMessage.value.trim()) {
        toast.add({ title: 'Message requis', description: 'Veuillez décrire votre besoin.', color: 'warning' })
        return
    }
    savSending.value = true
    const body: any = { message: savMessage.value }
        if (selectedCategoryLabel.value) body.category = selectedCategoryLabel.value
    if (route && route.fullPath) body.page_url = route.fullPath
    const res = await apiRequest(
        () => $fetch('/api/users/support/', { method: 'POST', credentials: 'include', body }),
        toast
    )
    savSending.value = false
    if (res !== null) {
        savSent.value = true
    }
}

function newRequest() {
    savSent.value = false
    resetForm()
}
</script>

<template>
    <div class="min-h-screen flex flex-col">
        <!-- Header sticky -->
        <div class="sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-(--ui-border)">
            <UDashboardNavbar title="Service Après Vente" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-14 lg:h-(--ui-header-height)' }" />
        </div>

        <div class="flex-1 w-full max-w-7xl mx-auto px-4 lg:px-8 py-8">
            <div>
                <transition name="fade" mode="out-in">
                    <div v-if="!savSent" key="form" class="space-y-6">

                        <div class="grid lg:grid-cols-2 gap-10 lg:gap-12 items-start">
                            <div class="space-y-4">
                                <h2 class="text-lg font-semibold flex items-center gap-2">
                                    <UIcon name="i-heroicons-chat-bubble-left-right" class="text-(--ui-primary)" />
                                    Comment optimiser votre demande ?
                                </h2>
                                <ul class="text-sm space-y-2 list-disc ps-5 marker:text-(--ui-primary)">
                                    <li>Indiquez le contexte (devis, installation, facture...)</li>
                                    <li>Précisez les dates ou références si disponibles</li>
                                    <li>Un seul sujet par demande = traitement plus rapide</li>
                                    <li>Ajoutez la catégorie la plus pertinente</li>
                                </ul>
                            </div>
                            <!-- Catégories -->
                            <div class="space-y-2">
                                <UFormField label="Catégorie (optionnelle)">
                                    <div class="grid grid-cols-2 gap-3">
                                        <button v-for="cat in categories" :key="cat.key" type="button"
                                            class="group relative rounded-lg border text-left p-3 flex items-start gap-3 transition cursor-pointer"
                                            :class="selectedCategory === cat.key ? 'border-(--ui-primary) bg-(--ui-primary)/5' : 'border-(--ui-border) hover:border-(--ui-primary)/60 hover:bg-(--ui-primary)/5'"
                                            @click="selectedCategory = selectedCategory === cat.key ? null : cat.key">
                                            <span
                                                class="h-9 w-9 shrink-0 rounded-md bg-(--ui-primary)/10 text-(--ui-primary) grid place-items-center">
                                                <UIcon :name="cat.icon" class="text-lg" />
                                            </span>
                                            <div class="space-y-0.5">
                                                <div class="text-sm font-medium leading-none">{{ cat.label }}</div>
                                                <div class="text-[11px] text-(--ui-text-muted)">{{ selectedCategory
                                                    === cat.key ? 'Sélectionnée' : 'Choisir' }}</div>
                                            </div>
                                            <span v-if="selectedCategory === cat.key"
                                                class="absolute top-1.5 right-1.5 text-(--ui-primary)">
                                                <UIcon name="i-heroicons-check-circle" />
                                            </span>
                                        </button>
                                    </div>
                                </UFormField>
                            </div>
                        </div>

                        <!-- Message -->
                        <div class="space-y-2">
                            <UFormField label="Votre message" required>
                                <UTextarea v-model="savMessage" :rows="15" :maxlength="charLimit" class="w-full" />
                            </UFormField>
                            <div class="flex justify-between text-[11px] text-(--ui-text-muted)">
                                <span>Décrivez précisément votre besoin.</span>
                                <span :class="remaining < 0 ? 'text-(--ui-error)' : ''">{{ savMessage.length
                                }}/{{ charLimit }}</span>
                            </div>
                        </div>

                        <div class="flex justify-end gap-2 pt-2">
                            <UButton variant="ghost" color="neutral" label="Réinitialiser"
                                :disabled="!savMessage && !selectedCategory" @click="resetForm" />
                            <UButton color="primary" :disabled="!savMessage.trim() || remaining < 0"
                                :loading="savSending" label="Envoyer la demande" icon="i-heroicons-paper-airplane"
                                @click="submit" />
                        </div>
                    </div>
                    <div v-else key="success" class="space-y-8 py-8 text-center">
                        <div
                            class="mx-auto h-16 w-16 rounded-full bg-(--ui-success)/10 text-(--ui-success) grid place-items-center">
                            <UIcon name="i-heroicons-check-badge" class="text-3xl" />
                        </div>
                        <div class="space-y-2">
                            <h2 class="text-2xl font-semibold">Message envoyé</h2>
                            <p class="text-sm text-(--ui-text-muted) max-w-sm mx-auto">Merci ! Nous vous
                                répondrons à votre adresse email. Vous pouvez soumettre une autre demande si
                                nécessaire.</p>
                        </div>
                        <div class="flex justify-center gap-3">
                            <UButton variant="ghost" color="neutral" label="Retour" @click="$router.back()" />
                            <UButton color="primary" label="Nouvelle demande" @click="newRequest" />
                        </div>
                    </div>
                </transition>
            </div>
        </div>
    </div>
    <!-- <div class="grid gap-10 lg:gap-12 items-start"> -->
    <!-- Colonne gauche: informations & bienfaits -->
    <!-- <div class="space-y-8">
                    <div class="space-y-4">
                        <h1 class="text-2xl lg:text-3xl font-semibold tracking-tight">Nous sommes là pour vous aider
                        </h1>
                        <p class="text-(--ui-text-muted) leading-relaxed">
                            Besoin d'une assistance concernant votre projet solaire, un document, une facturation ou un
                            rendez-vous ?
                            Envoyez-nous un message détaillé et notre équipe vous recontactera rapidement par email.
                        </p>
                    </div>

                    <div class="grid sm:grid-cols-2 gap-5">
                        <div v-for="card in [
                            { icon: 'i-heroicons-bolt', title: 'Réponse rapide', desc: 'Notre équipe traite vos demandes avec priorité et transparence.' },
                            { icon: 'i-heroicons-shield-check', title: 'Suivi fiable', desc: 'Chaque demande est historisée afin d’améliorer votre accompagnement.' },
                            { icon: 'i-heroicons-document-text', title: 'Aide documentaire', desc: 'Guides, documents administratifs ou devis : on vous oriente.' },
                            { icon: 'i-heroicons-user-group', title: 'Support humain', desc: 'Un expert vous répond. Pas de chatbot impersonnel.' }
                        ]" :key="card.title"
                            class="group p-4 sm:p-3 rounded-xl border border-(--ui-border) bg-(--ui-bg-elevated)/40 hover:bg-(--ui-bg-elevated) transition">
                            <div class="flex items-start gap-3">
                                <div
                                    class="h-10 min-w-10 rounded-lg bg-gradient-to-br from-(--ui-primary)/90 to-(--ui-primary) text-white grid place-items-center shadow">
                                    <UIcon :name="card.icon" class="text-xl" />
                                </div>
                                <div class="space-y-1">
                                    <h3 class="font-medium leading-none">{{ card.title }}</h3>
                                    <p class="text-xs text-(--ui-text-muted)">{{ card.desc }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div> -->

    <!-- Colonne droite: formulaire -->
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity .25s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>