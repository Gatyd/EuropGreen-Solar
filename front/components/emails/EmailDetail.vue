<script setup lang="ts">
interface Props {
    email: any
}
const emit = defineEmits<{
    close: []
}>()
const props = defineProps<Props>()
</script>

<template>
    <div class="flex flex-col h-full">
        <!-- En-tête minimaliste -->
        <div class="px-6 py-3 border-b bg-white">
            <div class="flex items-center justify-between mb-1">
                <h2 class="text-xl font-bold">{{ email.subject }}</h2>
                <UButton icon="i-lucide-x" color="neutral" variant="ghost" @click="emit('close')" />
            </div>
            <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">À :</span>
                <span class="text-sm font-medium">{{ email.recipients_display }}</span>

                <!-- Bouton info avec tooltip -->
                <UPopover mode="hover">
                    <UButton icon="i-heroicons-information-circle" color="neutral" variant="ghost" size="sm" />
                    <template #content>
                        <div class="space-y-2 text-sm p-2">
                            <div>
                                <span class="text-gray-400">De :</span>
                                <span class="ml-2 font-medium">{{ email.from_email }}</span>
                            </div>
                            <div>
                                <span class="text-gray-400">Date :</span>
                                <span class="ml-2">{{ new Date(email.sent_at).toLocaleString('fr-FR') }}</span>
                            </div>
                            <div>
                                <UBadge size="sm" :color="email.send_method === 'mailgun' ? 'primary' : 'neutral'"
                                    variant="subtle">
                                    {{ email.send_method }}
                                </UBadge>
                            </div>
                            <div v-if="email.attachments_info && email.attachments_info.length > 0">
                                <span class="text-gray-400">Pièces jointes :</span>
                                <div class="mt-1 space-y-1">
                                    <div v-for="(attachment, index) in email.attachments_info" :key="index"
                                        class="text-xs ml-2">
                                        <UIcon name="i-heroicons-paper-clip" class="text-xs" />
                                        {{ attachment.filename || attachment.name || `Fichier ${index + 1}` }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                </UPopover>
            </div>
        </div>

        <!-- Contenu HTML de l'email (non-cliquable) -->
        <div class="flex-1 overflow-y-auto p-6 bg-white">
            <div class="email-content" style="pointer-events: none; user-select: text;" v-html="email.html_content">
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Style pour le contenu de l'email */
.email-content :deep(a) {
    pointer-events: none !important;
    cursor: default !important;
}

.email-content :deep(button) {
    pointer-events: none !important;
    cursor: default !important;
}

.email-content :deep(input),
.email-content :deep(textarea),
.email-content :deep(select) {
    pointer-events: none !important;
    cursor: default !important;
}

/* Permettre la sélection de texte */
.email-content {
    -webkit-user-select: text !important;
    -moz-user-select: text !important;
    user-select: text !important;
}
</style>
