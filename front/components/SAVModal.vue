<script setup lang="ts">
const model = defineModel({ type: Boolean, default: false })

const savSending = ref(false)
const savMessage = ref('')
const savSent = ref(false)
const selectedCategory = ref<string | null>(null)
const categories = [
    { key: 'tech', label: 'Problème technique', icon: 'i-heroicons-wrench-screwdriver' },
    { key: 'billing', label: 'Facturation', icon: 'i-heroicons-receipt-percent' },
    { key: 'question', label: 'Question', icon: 'i-heroicons-question-mark-circle' },
    { key: 'appointment', label: 'Rendez-vous', icon: 'i-heroicons-calendar-days' },
]

const toast = useToast()
const route = useRoute()

const resetForm = () => {
    savMessage.value = ''
    selectedCategory.value = null
}

const onClose = () => {
    model.value = false
    // on laisse le succès pour que la fermeture soit instantanée
    savSent.value = false
    resetForm()
}

const sendSav = async () => {
    if (!savMessage.value.trim()) {
        toast.add({ title: 'Message requis', description: 'Veuillez décrire votre besoin.', color: 'warning' })
        return
    }
    savSending.value = true
    const body: any = { message: savMessage.value }
    if (selectedCategory.value) body.category = selectedCategory.value
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
</script>

<template>
    <UModal v-model:open="model" :ui="{ content: 'sm:max-w-lg w-full p-0 overflow-hidden' }"
        aria-label="Service Après-Vente">
        <template #content>
            <div class="bg-gradient-to-r from-(--ui-primary)/90 to-(--ui-primary) px-5 py-4 text-white">
                <div class="flex items-center gap-3">
                    <img src="/logo_icon.png" alt="Icône Europ'Green Solar" class="h-10 w-auto shrink-0" />
                    <div>
                        <div class="font-semibold">Service Après-Vente</div>
                        <div class="text-white/80 text-xs">Besoin d'aide ? Nous sommes là pour vous.</div>
                    </div>
                </div>
            </div>
            <div class="p-5 space-y-4">
                <div v-if="!savSent" class="space-y-4">
                    <p class="text-sm text-(--ui-text-muted)">Décrivez votre besoin avec quelques détails (dates,
                        références, ...). Nous vous répondrons par email au plus vite.</p>

                    <div>
                        <UFormField label="Votre message">
                            <UTextarea v-model="savMessage" :rows="6" class="w-full" />
                        </UFormField>
                        <div class="flex justify-between text-xs mt-1 text-(--ui-text-muted)">
                            <span>Conseil: soyez précis, cela accélère le traitement.</span>
                            <span>{{ savMessage.length }} caractères</span>
                        </div>
                    </div>

                    <div class="flex justify-end gap-2 pt-1">
                        <UButton variant="ghost" color="neutral" label="Annuler" @click="onClose" />
                        <UButton color="primary" :disabled="!savMessage.trim()" :loading="savSending" label="Envoyer" icon="i-heroicons-paper-airplane"
                            @click="sendSav" />
                    </div>
                </div>

                <div v-else class="space-y-4 text-center py-8">
                    <div
                        class="mx-auto h-14 w-14 rounded-full bg-(--ui-success)/10 text-(--ui-success) grid place-items-center">
                        <UIcon name="i-heroicons-check-circle" class="text-3xl" />
                    </div>
                    <div class="text-lg font-semibold">Message envoyé</div>
                    <p class="text-sm text-(--ui-text-muted)">Merci ! Vous recevrez une réponse à votre adresse email.
                        Notre équipe vous recontactera rapidement.</p>
                    <div class="flex justify-center gap-2">
                        <UButton variant="ghost" color="neutral" label="Fermer" @click="onClose" />
                        <UButton color="primary" label="Nouvelle demande" @click="savSent = false; resetForm()" />
                    </div>
                </div>
            </div>
        </template>
    </UModal>
</template>