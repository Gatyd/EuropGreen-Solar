<script setup lang="ts">
interface Props {
    email: any
    isSelected: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
    select: []
}>()

// Formater la date
function formatDate(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) {
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    } else if (days === 1) {
        return 'Hier'
    } else if (days < 7) {
        return date.toLocaleDateString('fr-FR', { weekday: 'short' })
    } else {
        return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
    }
}

// Extraire le début du texte
function getEmailPreview(email: any): string {
    if (email.plain_content && email.plain_content.trim()) {
        const preview = email.plain_content.substring(0, 195)
        return preview + (email.plain_content.length > 195 ? '...' : '')
    }

    const div = document.createElement('div')
    div.innerHTML = email.html_content
    const text = div.textContent || div.innerText || ''
    const preview = text.substring(0, 195)
    return preview + (text.length > 195 ? '...' : '')
}
</script>

<template>
    <div class="p-4 border-b border-default cursor-pointer hover:bg-gray-50 transition-colors" :class="{
        'bg-primary-50 border-l-4 border-l-primary-500': isSelected
    }" @click="emit('select')">
        <div class="flex justify-between items-start mb-1">
            <h3 class="font-semibold text-sm truncate flex-1">
                {{ email.subject }}
            </h3>
            <span class="text-xs text-gray-500 ml-2 flex-shrink-0">
                {{ formatDate(email.sent_at) }}
            </span>
        </div>
        <p class="text-sm text-gray-600 line-clamp-2">
            {{ getEmailPreview(email) }}
        </p>
        <div v-if="email.has_attachments" class="mt-2">
            <UBadge size="xs" color="neutral" variant="subtle">
                <UIcon name="i-heroicons-paper-clip" class="text-xs" />
            </UBadge>
        </div>
    </div>
</template>
